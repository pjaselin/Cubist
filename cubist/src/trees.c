/*************************************************************************/
/*                                                                       */
/*  Copyright 2010 Rulequest Research Pty Ltd.                           */
/*                                                                       */
/*  This file is part of Cubist GPL Edition, a single-threaded version   */
/*  of Cubist release 2.07.                                              */
/*                                                                       */
/*  Cubist GPL Edition is free software: you can redistribute it and/or  */
/*  modify it under the terms of the GNU General Public License as       */
/*  published by the Free Software Foundation, either version 3 of the   */
/*  License, or (at your option) any later version.                      */
/*                                                                       */
/*  Cubist GPL Edition is distributed in the hope that it will be        */
/*  useful, but WITHOUT ANY WARRANTY; without even the implied warranty  */
/*  of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the     */
/*  GNU General Public License for more details.                         */
/*                                                                       */
/*  You should have received a copy of the GNU General Public License    */
/*  (gpl.txt) along with Cubist GPL Edition.  If not, see                */
/*                                                                       */
/*      <http://www.gnu.org/licenses/>.                                  */
/*                                                                       */
/*************************************************************************/

/*************************************************************************/
/*                                                                       */
/* Routines for displaying, building, saving and restoring trees  */
/* -------------------------------------------------------------  */
/*                                                                       */
/*************************************************************************/

#include "defns.h"
#include "extern.h"

#include "redefine.h"
#include "transform.h"

#define TabSize 4

/*  If lines look like getting too long while a tree is being
    printed, subtrees are broken off and printed separately after
    the main tree is finished  */

int SubTree,               /* highest subtree to be printed */
    SubSpace = 0;          /* maximum subtree encountered */
Tree *SubDef = Nil;        /* pointers to subtrees */
Boolean LastBranch[Width]; /* whether printing last branch of subtree */

/*************************************************************************/
/*                                                                       */
/* Calculate the depth of nodes in a tree in Errors field   */
/*                                                                       */
/*************************************************************************/

void FindDepth(Tree T)
/*   ---------  */
{
  float MaxDepth = 0;
  DiscrValue v;

  if (T->NodeType) {
    ForEach(v, 1, T->Forks) {
      FindDepth(T->Branch[v]);
      if (T->Branch[v]->Utility > MaxDepth) {
        MaxDepth = T->Branch[v]->Utility;
      }
    }
  }

  T->Utility = MaxDepth + 1;
}

/*************************************************************************/
/*                                                                       */
/* Display entire decision tree T      */
/*                                                                       */
/*************************************************************************/

void PrintTree(Tree T, String Title)
/*   ---------  */
{
  int s;

  FindDepth(T);

  SubTree = 0;
  fprintf(Of, "\n%s\n", Title);
  Show(T, 0);
  fprintf(Of, "\n");

  ForEach(s, 1, SubTree) {
    fprintf(Of, "\nSubTree [S%d]\n", s);
    Show(SubDef[s], 0);
    fprintf(Of, "\n");
  }
}

/*************************************************************************/
/*                                                                       */
/* Display the tree T with offset Sh     */
/*                                                                       */
/*************************************************************************/

void Show(Tree T, int Sh)
/*   ---- */
{
  DiscrValue v, MaxV, BrNo = 0, Simplest;
  Attribute Att;

  if (T->NodeType) {
    /*  See whether separate subtree needed  */

    if (T != Nil && Sh && Sh * TabSize + MaxLine(T) > Width) {
      if (++SubTree >= SubSpace) {
        SubSpace += 100;
        if (SubDef)
          Realloc(SubDef, SubSpace, Tree);
        else
          SubDef = Alloc(SubSpace, Tree);
      }

      SubDef[SubTree] = T;
      fprintf(Of, "[S%d]", SubTree);
    } else {
      MaxV = T->Forks;

      /*  Print simplest branches first  */

      while (BrNo < MaxV) {
        Simplest = 1;
        ForEach(v, 2, MaxV) {
          if (T->Branch[v]->Utility < T->Branch[Simplest]->Utility) {
            Simplest = v;
          }
        }

        LastBranch[Sh + 1] = (++BrNo == MaxV);
        ShowBranch(Sh, T, Simplest, BrNo);
        T->Branch[Simplest]->Utility = 1E10;
      }
    }
  } else {
    fprintf(Of, " AV %g (%d:%g)", T->Mean, T->Cases, T->Coeffs);
    fprintf(Of, " [%g", T->Model[0]);
    ForEach(Att, 1, MaxAtt) {
      if (T->Model[Att]) {
        fprintf(Of, " + %g %s", T->Model[Att], AttName[Att]);
      }
    }
    fprintf(Of, "]");
  }
}

/*************************************************************************/
/*                                                                       */
/* Print a node T with offset Sh, branch value v, and continue  */
/*                                                                       */
/*************************************************************************/

void ShowBranch(int Sh, Tree T, DiscrValue v, DiscrValue BrNo)
/*   ----------  */
{
  DiscrValue Pv, Last;
  Attribute Att;
  Boolean FirstValue;
  int TextWidth, Skip, Values = 0, i, Extra;

  Att = T->Tested;

  switch (T->NodeType) {
  case BrDiscr:

    Indent(Sh, BrNo);

    fprintf(Of, "%s = %s:", AttName[Att], AttValName[Att][v]);
    break;

  case BrThresh:

    Indent(Sh, BrNo);

    if (v == 1) {
      fprintf(Of, "%s = N/A:", AttName[Att]);
    } else {
      fprintf(Of, "%s %s %.*g:", AttName[Att], (v == 2 ? "<=" : ">"), PREC,
              T->Cut);
    }
    break;

  case BrSubset:

    /*  Count values at this branch  */

    ForEach(Pv, 1, MaxAttVal[Att]) {
      if (In(Pv, T->Subset[v])) {
        Last = Pv;
        Values++;
      }
    }
    if (!Values)
      return;

    Indent(Sh, BrNo);

    if (Values == 1) {
      fprintf(Of, "%s = %s:", AttName[Att], AttValName[Att][Last]);
      break;
    }

    fprintf(Of, "%s in {", AttName[Att]);
    FirstValue = true;
    Skip = strlen(AttName[Att]) + 5;
    TextWidth = Skip + Sh * TabSize;

    ForEach(Pv, 1, Last) {
      if (In(Pv, T->Subset[v])) {
        Extra = (Pv != Last || T->Branch[v]->NodeType ? 0 : 6);
        if (!FirstValue &&
            TextWidth + strlen(AttValName[Att][Pv]) + 11 + Extra > Width) {
          Indent(Sh, 0);
          ForEach(i, 1, Skip) putc(' ', Of);

          TextWidth = Skip + Sh * TabSize;
          FirstValue = true;
        }

        fprintf(Of, "%s%c", AttValName[Att][Pv], Pv == Last ? '}' : ',');
        TextWidth += strlen(AttValName[Att][Pv]) + 1;
        FirstValue = false;
      }
    }
    putc(':', Of);
  }

  Show(T->Branch[v], Sh + 1);
}

/*************************************************************************/
/*                                                                       */
/* Find the maximum single line size for non-leaf subtree T  */
/*                                                                       */
/*************************************************************************/

int MaxLine(Tree T)
/*  -------  */
{
  Attribute Att;
  DiscrValue v, vv;
  int Ll, One, MaxLl = 0;

  Att = T->Tested;

  /*  First find the max length of the line excluding tested att  */

  ForEach(v, 1, T->Forks) {
    switch (T->NodeType) {
    case BrThresh:
      Ll = 4;
      break;

    case BrDiscr:
      Ll = strlen(AttValName[Att][v]) + 1;
      break;

    case BrSubset: /* difficult! */
      Ll = 0;
      ForEach(vv, 1, MaxAttVal[Att]) {
        if (In(vv, T->Subset[v])) {
          One = strlen(AttValName[Att][vv]) + 6;
          if (One > Ll)
            Ll = One;
        }
      }
    }

    /*  Check whether ends in leaf  */

    if (!T->Branch[v]->NodeType) {
      Ll += 6;
    }

    if (Ll > MaxLl)
      MaxLl = Ll;
  }

  return strlen(AttName[Att]) + 4 + MaxLl;
}

/*************************************************************************/
/*             */
/* Indent Sh columns         */
/*            */
/*************************************************************************/

void Indent(int Sh, int BrNo)
/*   ------  */
{
  int i;

  fprintf(Of, "\n");
  for (i = 1; i <= Sh; i++) {
    fprintf(Of, "%s",
            (i == Sh && BrNo == 1 ? ":..." : LastBranch[i] ? "    " : ":   "));
  }
}

/*************************************************************************/
/*                                                                       */
/* Free up space taken up by tree Node     */
/*                                                                       */
/*************************************************************************/

void FreeTree(Tree T)
/*   --------  */
{
  DiscrValue v;

  if (!T)
    return;

  if (T->NodeType) {
    ForEach(v, 1, T->Forks) { FreeTree(T->Branch[v]); }

    Free(T->Branch);
    T->Branch = Nil;

    if (T->NodeType == BrSubset) {
      FreeVector((void **)T->Subset, 1, T->Forks);
      T->Subset = Nil;
    }
  }

  FreeUnlessNil(T->Model);
  T->Model = Nil;
  FreeUnlessNil(T->MCopy);
  T->MCopy = Nil;
  Free(T);
}

/*************************************************************************/
/*                                                                       */
/* Construct a leaf in a given node     */
/*                                                                       */
/*************************************************************************/

Tree Leaf(CaseCount Cases, double Mean, double SD)
/*   ----  */
{
  Tree Node;

  Node = AllocZero(1, TreeRec);

  Node->NodeType = 0;
  Node->Cases = Cases;
  Node->Mean = Mean;
  Node->SD = SD;

  Node->Model = AllocZero(MaxAtt + 1, double);
  Node->Model[0] = Mean;

  return Node;
}

/*************************************************************************/
/*                                                                       */
/* Insert branches in a node                      */
/*                                                                       */
/*************************************************************************/

void Sprout(Tree T, DiscrValue Branches)
/*   ------  */
{
  T->Forks = Branches;
  T->Branch = Alloc(Branches + 1, Tree);
}

/*************************************************************************/
/*                                                                       */
/* Count the nodes in a tree      */
/*                                                                       */
/*************************************************************************/

int TreeSize(Tree T)
/*  --------  */
{
  int Sum = 1;
  DiscrValue v;

  if (T->NodeType) {
    ForEach(v, 1, T->Forks) { Sum += TreeSize(T->Branch[v]); }

    return Sum;
  }

  return 1;
}

/*************************************************************************/
/*                                                                       */
/* Count the non-null leaves in a tree     */
/*                                                                       */
/*************************************************************************/

int TreeLeaves(Tree T)
/*  ----------  */
{
  int Sum = 0;
  DiscrValue v;

  if (!T || T->Cases < 1)
    return 0;

  if (T->NodeType) {
    ForEach(v, 1, T->Forks) { Sum += TreeLeaves(T->Branch[v]); }

    return Sum;
  }

  return 1;
}

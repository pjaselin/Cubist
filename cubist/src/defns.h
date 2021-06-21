/*************************************************************************/
/*									 */
/*  Copyright 2010 Rulequest Research Pty Ltd.				 */
/*									 */
/*  This file is part of Cubist GPL Edition, a single-threaded version	 */
/*  of Cubist release 2.07.						 */
/*									 */
/*  Cubist GPL Edition is free software: you can redistribute it and/or	 */
/*  modify it under the terms of the GNU General Public License as	 */
/*  published by the Free Software Foundation, either version 3 of the	 */
/*  License, or (at your option) any later version.			 */
/*									 */
/*  Cubist GPL Edition is distributed in the hope that it will be	 */
/*  useful, but WITHOUT ANY WARRANTY; without even the implied warranty	 */
/*  of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the	 */
/*  GNU General Public License for more details.			 */
/*									 */
/*  You should have received a copy of the GNU General Public License	 */
/*  (gpl.txt) along with Cubist GPL Edition.  If not, see		 */
/*									 */
/*      <http://www.gnu.org/licenses/>.					 */
/*									 */
/*************************************************************************/

/*************************************************************************/
/*									 */
/*		Definitions used in Cubist				 */
/*              --------------------------				 */
/*									 */
/*************************************************************************/

#define CUBIST

#define RELEASE "2.07 GPL Edition"

#include <ctype.h>
#include <float.h>
#include <limits.h>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#include "text.h"

/*************************************************************************/
/*									 */
/*		Definitions dependent on cc options			 */
/*									 */
/*************************************************************************/

#define Goodbye(x)                                                             \
  {                                                                            \
    Cleanup();                                                                 \
    rbm_exit((x));                                                             \
  }

#ifdef VerbOpt
#include <assert.h>
#define Verbosity(d, s)                                                        \
  if (VERBOSITY >= d) {                                                        \
    s;                                                                         \
  }
#define Free(x)                                                                \
  {                                                                            \
    free(x);                                                                   \
    x = 0;                                                                     \
  }
#else
#define Verbosity(d, s)
#define Free(x) free(x)
#endif

#ifndef DEBUG
#define assert(x)
#endif /* DEBUG */

/*************************************************************************/
/*									 */
/*		Constants, macros etc.					 */
/*									 */
/*************************************************************************/

#define MINSPLIT 3     /* min branch size for initial tree */
#define MINFRACT 0.001 /* min fraction of cases covered by rule */

#define MAXN 20 /* max neighbors allowing for ties */
#define NNMAX 9 /* upper limit for NN */

#define EVALSAMPLE 10000 /* sampling training data for evaluation */

#define Nil 0 /* null pointer */
#define false 0
#define true 1
#define None -1
#define Epsilon 1E-4
#define Width 80 /* approx max width of output */

#define EXCLUDE 1   /* special attribute status: do not use */
#define SKIP 2      /* do not use in models */
#define DISCRETE 4  /* ditto: collect values as data read */
#define ORDERED 8   /* ditto: ordered discrete values */
#define DATEVAL 16  /* ditto: YYYY/MM/DD or YYYY-MM-DD */
#define STIMEVAL 32 /* ditto: HH:MM:SS */
#define TSTMPVAL 64 /* date time */

#define BrDiscr 1
#define BrThresh 2
#define BrSubset 3

#define Plural(n) ((n) != 1 ? "s" : "")

//#define  Alloc(N,T)		(T *) Pmalloc((N)*sizeof(T))
#define AllocZero(N, T) (T *)Pcalloc(N, sizeof(T))
#define Alloc(N, T) AllocZero(N, T) /* for safety */
#define Realloc(V, N, T) V = (T *)Prealloc(V, (N) * sizeof(T))

#define Max(a, b) ((a) > (b) ? a : b)
#define Min(a, b) ((a) < (b) ? a : b)

#define Log2 0.69314718055994530942
#define Log(x) ((x) <= 0 ? 0.0 : log((double)x) / Log2)

#define Bit(b) (1 << (b))
#define In(b, s) ((s[(b) >> 3]) & Bit((b)&07))
#define ClearBits(n, s) memset(s, 0, n)
#define CopyBits(n, f, t) memcpy(t, f, n)
#define SetBit(b, s) (s[(b) >> 3] |= Bit((b)&07))

#define ForEach(v, f, l) for (v = f; v <= l; ++v)

#define StatBit(a, b) (SpecialStatus[a] & (b))
#define Exclude(a) StatBit(a, EXCLUDE)
#define Skip(a) StatBit(a, EXCLUDE | SKIP)
#define Discrete(a) (MaxAttVal[a] || StatBit(a, DISCRETE))
#define Continuous(a) (!MaxAttVal[a] && !StatBit(a, DISCRETE))
#define Ordered(a) StatBit(a, ORDERED)
#define DateVal(a) StatBit(a, DATEVAL)
#define TimeVal(a) StatBit(a, STIMEVAL)
#define TStampVal(a) StatBit(a, TSTMPVAL)

#define UNKNOWN 1.5777218104420236e-30 /* unlikely value! */
#define NA 1

#define NotApplic(c, a) (DVal(c, a) == NA)
#define NotApplicVal(AV) (AV._discr_val == NA)

#define FreeUnlessNil(p)                                                       \
  if ((p) != Nil)                                                              \
  Free(p)

#define CheckClose(f)                                                          \
  if (f) {                                                                     \
    fclose(f);                                                                 \
    f = Nil;                                                                   \
  }

#define Space(s) (s == ' ' || s == '\n' || s == '\r' || s == '\t')
#define SkipComment while ((c = InChar(f)) != '\n' && c != EOF)

#define P1(x) (rint((x)*10) / 10)

#define Before(n1, n2)                                                         \
  (n1->Tested < n2->Tested || n1->Tested == n2->Tested && n1->Cut < n2->Cut)

#define Swap(a, b)                                                             \
  {                                                                            \
    xab = Case[a];                                                             \
    Case[a] = Case[b];                                                         \
    Case[b] = xab;                                                             \
  }

#define MinAttCoeff(a) (0.01 * GlobalSD / AttSD[a]) /* otherwise zero */

#define NOFILE 0
#define BADATTNAME 1
#define EOFINATT 2
#define SINGLEATTVAL 3
#define BADATTVAL 4
#define BADNUMBER 5
#define DUPATTNAME 6
#define NOMEM 8
#define TOOMANYVALS 9
#define BADDISCRETE 10
#define NOTARGET 11
#define BADTARGET 12
#define LONGNAME 13
#define HITEOF 14
#define MISSNAME 15
#define BADDATE 16
#define BADTIME 17
#define BADTSTMP 18
#define UNKNOWNATT 19
#define BADDEF1 20
#define BADDEF2 21
#define BADDEF3 22
#define SAMEATT 23
#define BADDEF4 24
#define MODELFILE 30
#define CWTATTERR 31

#define READDATA 1
#define GROUPDATA 2
#define ADDMODELS 3
#define SIMPLIFYGROUPS 4
#define FORMRULES 5
#define INDEXINSTANCES 6
#define SETNEIGHBORS 7
#define ASSESSCOMPOSITE 8
#define EVALTRAIN 9
#define READTEST 10
#define EVALTEST 11
#define CLEANUP 12
#define RESULTS 13

/*************************************************************************/
/*									 */
/*		Type definitions					 */
/*									 */
/*************************************************************************/

typedef unsigned char Boolean, BranchType, *Set;
typedef char *String;

typedef int CaseNo, /* data item number */
    CaseCount,      /* count of cases */
    DiscrValue,     /* discrete attribute value (0 = ?) */
    Attribute;      /* attribute number, 1..MaxAtt */

#ifdef USEDOUBLE
typedef double ContValue; /* continuous attribute value */
#define PREC 14           /* precision */
#else
typedef float ContValue; /* continuous attribute value */
#define PREC 7 /* precision */
#endif

/* Attribute values are packed into a union:

     DVal = (int) discrete value
     CVal = (float) continuous value
     SVal = (int) offset in IgnoredVals

   Missing and non-applicable values are:

     discrete:
       not applicable:	DVal = NA
       missing:		DVal = 0
     continuous:
       not applicable:	DVal = NA
       missing:		CVal = UNKNOWN  */

typedef union _attribute_value {
  ContValue _cont_val;
  DiscrValue _discr_val;
} AttValue, *DataRec;

#define CVal(Case, Attribute) Case[Attribute]._cont_val
#define DVal(Case, Attribute) Case[Attribute]._discr_val
#define XDVal(Case, Attribute) (Case[Attribute]._discr_val & 077777777)
#define SVal(Case, Attribute) Case[Attribute]._discr_val
#define Class(Case) (*Case)._cont_val
#define Resid(Case) Case[MaxAtt + 1]._cont_val
#define PredSum(Case) Case[MaxAtt + 1]._cont_val
#define PredCount(Case) Case[MaxAtt + 2]._discr_val
#define PredVal(Case) Case[MaxAtt + 1]._cont_val
#define DRef1(Case) Case[MaxAtt + 1]._cont_val
#define DRef2(Case) Case[MaxAtt + 2]._cont_val

#define CWeight(Case) (CWtAtt ? CVal(Case, CWtAtt) : 1.0)

typedef struct _env_rec {
  double *LocalModel,  /* intermediate regression model */
      *ValFreq,        /* count of items with att value v */
      BrFreq[4],       /* for split */
      *ValSum,         /* sum class values for value v */
      *ValSumSq,       /* ditto sum squares */
      BrSum[4],        /* sum class values for branch b */
      BrSumSq[4];      /* ditto sum squares */
  Boolean *DoNotUse;   /* atts precxluded from model */
  float *Gain;         /* gain from splitting on att */
  ContValue *Bar;      /* best threshold for contin att */
  Boolean *Left;       /* true if v is in left subset */
  Set **Subset;        /* subset s for att a */
  Attribute *ModelAtt; /* atts used in current model */
  int NModelAtt;       /* number ditto */

  double **xTx,       /* [Att][Att] */
      *xTy,           /* [Att] */
      **A,            /* copy of xTx destroyed by inversion */
      *B,             /* copy of xTy ditto */
      *BestModel,     /* for SimplifyModel */
      *Resid,         /* [Case] */
      *PResid,        /* [Case] */
      *Mean,          /* [Att] */
      *Var,           /* [Att] */
      *AvDev;         /* [Att] */
  Boolean *ZeroCoeff, /* true if coeff to be set to zero */
      *SaveZero;      /* for SimplifyModel */
  DataRec *Filtered;  /* items minus outliers */
} EnvRec, *Env;

typedef struct _sort_rec {
  ContValue V, /* attribute value */
      T,       /* target value or residual */
      W;       /* weight */
} SortRec;

typedef struct _treerec *Tree;
typedef struct _treerec {
  BranchType NodeType; /* 0 | BrDiscr | BrThresh | BrSubset */
  CaseCount Cases;     /* no of cases at this node */
  double Mean,         /* average of cases at this node */
      SD,              /* standard dev ditto */
      *Model,          /* model at this node */
      *MCopy;          /* copy used during smoothing */
  Attribute Tested;    /* attribute referenced in test */
  int Forks;           /* number of branches at this node */
  ContValue Cut;       /* threshold for continuous attribute */
  Set *Subset;         /* subsets of discrete values  */
  Tree *Branch;        /* Branch[x] = subtree for outcome x */
  float Params,        /* parameters in this tree */
      Coeffs,          /* coefficients of leaf model */
      TreeErr,         /* error as tree */
      LeafErr,         /* error if replace by leaf */
      Utility;
} TreeRec;

#define Parent(T) T->Branch[0]

typedef int RuleNo; /* rule number */

typedef struct _condrec {
  BranchType NodeType; /* test type (see tree nodes) */
  Attribute Tested;    /* attribute tested */
  ContValue Cut;       /* threshold (if relevant) */
  Set Subset;          /* subset (if relevant) */
  int TestValue;       /* specified outcome of test */
} CondRec, *Condition;

typedef struct _rulerec {
  RuleNo RNo;     /* rule number */
  int MNo,        /* member number for committee models */
      Size;       /* number of conditions */
  Condition *Lhs; /* conditions themselves */
  double *Rhs;    /* model given by rule */
  CaseNo Cover;   /* number of cases covered */
  float Mean,     /* mean value of cases matching rule */
      LoVal,      /* lowest value in data */
      HiVal,      /* highest value in data */
      LoLim,      /* lower bound on predictions */
      HiLim,      /* upper bound on predictions */
      EstErr;     /* estimated error */
} RuleRec, *CRule;

typedef struct _oldrulerec {
  RuleNo RNo;     /* rule number */
  int Size;       /* number of conditions */
  Condition *Lhs; /* conditions themselves */
  double *Rhs;    /* model given by rule */
  CaseNo Cover;   /* number of cases covered */
  float Mean,     /* mean value of cases matching rule */
      LoVal,      /* lowest value in data */
      HiVal,      /* highest value in data */
      LoLim,      /* lower bound on predictions */
      HiLim,      /* upper bound on predictions */
      EstErr;     /* estimated error */
} OldRuleRec;

typedef struct _rulesetrec {
  RuleNo SNRules; /* number of rules */
  CRule *SRule;   /* rules */
} RuleSetRec, *RRuleSet;

typedef struct _indexrec *Index;
typedef struct _indexrec {
  Attribute Tested; /* split attribute for KD-tree */
  ContValue Cut,    /* threshold for continuous atts */
      MinDRef[2],   /* min reference distances */
      MaxDRef[2];   /* max ditto */
  CaseNo IFp, ILp;  /* first and last item at leaf */
  Index *SubIndex;  /* subtrees */
} IndexRec;

typedef struct _nnrec {
  int BestI[MAXN];   /* numbers of best instances */
  float BestD[MAXN], /* distances to best instances */
      *WorstBest,    /* points to worst BestD */
      *AttMinD;      /* min attribute distance from case */
} NNEnvRec;

typedef union _def_val {
  String _s_val;    /* att val for comparison */
  ContValue _n_val; /* number for arith */
} DefVal;

typedef struct _def_elt {
  short _op_code;  /* type of element */
  DefVal _operand; /* string or numeric value */
} DefElt, *Definition;

typedef struct _elt_rec {
  int Fi,    /* index of first char of element */
      Li;    /* last ditto */
  char Type; /* 'B', 'S', or 'N' */
} EltRec;

#define DefOp(DE) DE._op_code
#define DefSVal(DE) DE._operand._s_val
#define DefNVal(DE) DE._operand._n_val

#define OP_ATT 0 /* opcodes */
#define OP_NUM 1
#define OP_STR 2
#define OP_MISS 3
#define OP_AND 10
#define OP_OR 11
#define OP_EQ 20
#define OP_NE 21
#define OP_GT 22
#define OP_GE 23
#define OP_LT 24
#define OP_LE 25
#define OP_SEQ 26
#define OP_SNE 27
#define OP_PLUS 30
#define OP_MINUS 31
#define OP_UMINUS 32
#define OP_MULT 33
#define OP_DIV 34
#define OP_MOD 35
#define OP_POW 36
#define OP_SIN 40
#define OP_COS 41
#define OP_TAN 42
#define OP_LOG 43
#define OP_EXP 44
#define OP_INT 45
#define OP_END 99

/*************************************************************************/
/*									 */
/*		Function prototypes					 */
/*									 */
/*************************************************************************/

/* for R c functions */

void GetRNGstate(void);
void PutRNGstate(void);

/* cubist.c */

int Xmain(int, char *[]);

/* construct.c */

void SingleCttee(void);
void ConstructCttee(void);
RRuleSet ConstructRuleSet(int ModelNo);
void EvaluateCttee(RRuleSet *RS, Boolean Details);
void SampleTrainingCases(void);
void AttributeUsage(void);
void UpdateUsage(CRule R);
void NoteUsed(Attribute Att);

/* getnames.c */

Boolean ReadName(FILE *f, String s, int n, char ColonOpt);
void GetNames(FILE *Nf);
void ExplicitAtt(FILE *Nf);
int Which(String Val, String *List, int First, int Last);
void ListAttsUsed(void);
void FreeNamesData(void);
int InChar(FILE *f);

/* implicitatt.c */

void ImplicitAtt(FILE *Nf);
void ReadDefinition(FILE *f);
void Append(char c);
Boolean Expression(void);
Boolean Conjunct(void);
Boolean SExpression(void);
Boolean AExpression(void);
Boolean Term(void);
Boolean Factor(void);
Boolean Primary(void);
Boolean Atom(void);
Boolean Find(String S);
int FindOne(String *Alt);
Attribute FindAttName(void);
void DefSyntaxError(String Msg);
void DefSemanticsError(int Fi, String Msg, int OpCode);
void Dump(char OpCode, ContValue F, String S, int Fi);
void DumpOp(char OpCode, int Fi);
Boolean UpdateTStack(char OpCode, ContValue F, String S, int Fi);
AttValue EvaluateDef(Definition D, DataRec Case);

/* getdata.c */

void GetData(FILE *Df, Boolean Train, Boolean AllowUnknownTarget);
Boolean ReplaceUnknowns(DataRec Case, Boolean *AttMsg);
DataRec GetDataRec(FILE *Df, Boolean Train);
CaseNo CountData(FILE *Df);
int StoreIVal(String S);
void FreeData(DataRec *Case);
void CheckValue(DataRec Case, Attribute Att);
void FindLimits(Attribute Att, ContValue *Min, ContValue *Max);

/* predict.c */

float PredictValue(RRuleSet *Cttee, DataRec CaseDesc);
float RuleSetPrediction(RRuleSet RS, DataRec CaseDesc);
Boolean Matches(CRule R, DataRec Case);
float LinModel(double *Model, DataRec Case);
float RawLinModel(double *Model, DataRec Case);
void FindPredictedValues(RRuleSet *RS, CaseNo Fp, CaseNo Lp);

/* formtree.c */

void InitialiseEnvData(void);
void FreeEnvData(void);
void FindGlobalProperties(void);
void FormTree(CaseNo, CaseNo, int, Tree *, Tree);
void AddModels(CaseNo Fp, CaseNo Lp, Tree T, Tree Parent);
CaseNo Group(DiscrValue, CaseNo, CaseNo, Tree);
void Divide(Tree Node, CaseNo Fp, CaseNo Lp, int Level);
void AddSplitAtts(Tree T);
void AddDefAtts(void);
void FindModelAtts(double *Model);

/* discr.c */

void EvalDiscreteAtt(Tree, Attribute, CaseNo Fp, CaseNo Lp);
void EvalBinarySplit(Tree, Attribute, CaseNo Fp, CaseNo Lp);
void EvalSubsetSplit(Tree, Attribute, CaseNo Fp, CaseNo Lp);
void DiscreteTest(Tree Node, Attribute Att, Set *Subset);

/* contin.c */

void EvalContinuousAtt(Tree, Attribute, CaseNo Fp, CaseNo Lp);
void ContinTest(Tree Node, Attribute Att, float Cut);
void AdjustAllThresholds(Tree T);
void AdjustThresholds(Tree T, Attribute Att);
ContValue GreatestValueBelow(ContValue Th);

/* sort.c */

void Cachesort(CaseNo Fp, CaseNo Lp);

/* trees.c */

void FindDepth(Tree T);
void PrintTree(Tree T, String Title);
void Show(Tree T, int Sh);
void ShowBranch(int Sh, Tree T, DiscrValue v, DiscrValue BrNo);
int MaxLine(Tree SubTree);
void Indent(int Sh, int BrNo);
void FreeTree(Tree T);
Tree Leaf(CaseCount Cases, double Mean, double SD);
void Sprout(Tree T, DiscrValue Branches);
int TreeSize(Tree T);
int TreeLeaves(Tree T);

/* prunetree.c */

void Prune(Tree T);
void SetProperties(Tree T, Tree Parent);
void UnsproutAndUpdate(Tree Pruned, double ExtraErr, double ExtraParams);
void Unsprout(Tree T);
void SmoothModels(Tree T, Tree Parent, CaseNo Fp, CaseNo Lp);
double ErrVariance(double *Model, CaseNo Fp, CaseNo Lp, double *Err);
double Smooth(double PVal, int PCases, double LVal, int LCases);
void FindErrors(Tree T, CaseNo Fp, CaseNo Lp);
void CValToStr(ContValue CV, Attribute Att, String DS);
Boolean FindWeakestSubtree(Tree T);
float TreeValue(Tree T, DataRec Case);
float MedianResid(CaseNo Fp, CaseNo Lp, double Want);

/* regress.c */

void Regress(CaseNo Fp, CaseNo Lp, double *Model);
void BuildTables(CaseNo Fp, CaseNo Lp);
void Solve(double *Model);
void FindActiveAtts(void);
void AddRow(double *Model, short From, short To, double Factor);
void ExchangeRow(double *Model, short From, short To);
int CountCoeffs(double *Model);
void SimplifyModel(DataRec *D, CaseNo Fp, CaseNo Lp, double *Model);

/* stats.c */

double AverageDev(float Mean, CaseNo Fp, CaseNo Lp);
double SD(double N, double Sum, double SumSq);
double ComputeGain(Tree Node);
double AverageErr(DataRec *D, CaseNo Fp, CaseNo Lp, double *Model);
double EstimateErr(double Val, double NData, float NParam);

/* utility.c */

void PrintHeader(String Title);
char ProcessOption(int Argc, char **Argv, char *Str);
void *Pmalloc(size_t Bytes);
void *Prealloc(void *Present, size_t Bytes);
void *Pcalloc(size_t Number, unsigned int Size);
DataRec NewCase(void);
void FreeCases(void);
void FreeLastCase(DataRec Case);
void FreeVector(void **V, int First, int Last);
double KRandom(void);
void ResetKR(int KRInit);
void Error(int ErrNo, String S1, String S2);
String CaseLabel(CaseNo N);
FILE *GetFile(String Extension, String RW);
double ExecTime(void);
int Denominator(ContValue Val);
int FracBase(Attribute Att);
int GetInt(String S, int N);
int DateToDay(String DS);
void DayToDate(int DI, String Date);
int TimeToSecs(String TS);
void SecsToTime(int Secs, String Time);
void SetTSBase(int y);
int TStampToMins(String TS);
void Cleanup(void);
#ifdef UTF8
int UTF8CharWidth(unsigned char *U);
int wcwidth(wchar_t ucs);
int wcswidth(const wchar_t *pwcs, size_t n);
#endif

/* formrules.c */

RRuleSet FormRules(Tree T);
void TreeParameters(Tree T, int D);
void Scan(Tree T);
void PushCondition(void);
void PopCondition(void);
void PruneRule(Condition Cond[], float InitCoeffs);
void UpdateCount(int d, CaseNo i, double *Total, double *PredErr);
void ProcessLists(void);
void AddToList(CaseNo *List, CaseNo N);
void DeleteFromList(CaseNo *Before, CaseNo N);
int SingleFail(CaseNo i);
void RemoveBias(CRule R, int Coeffs);
void OrderRules(void);
void FreeFormRuleData(void);

/* rules.c */

Boolean NewRule(Condition Cond[], int NConds, Boolean *Deleted, CaseNo Cover,
                float Mean, float LoVal, float HiVal, float EstErr,
                double *Model);
Boolean SameRule(RuleNo r, Condition Cond[], int NConds);
void ReleaseRule(CRule R);
void FreeCttee(RRuleSet *Cttee);
void PrintRules(RRuleSet, String);
void PrintRule(CRule R);
void PrintCondition(Condition C);
Boolean Satisfies(DataRec CaseDesc, Condition OneCond);

/* modelfiles.c */

void CheckFile(String Extension, Boolean Write);
void WriteFilePrefix(String Extension);
void ReadFilePrefix(String Extension);
void SaveDiscreteNames(void);
void SaveCommittee(RRuleSet *Cttee, String Extension);
void SaveRules(RRuleSet RS);
void AsciiOut(String Pre, String S);
void ReadHeader(void);
RRuleSet *GetCommittee(String Extension);
RRuleSet InRules(void);
CRule InRule(void);
Condition InCondition(void);
int ReadProp(char *Delim);
String RemoveQuotes(String S);
Set MakeSubset(Attribute Att);

/* update.c (Unix) or frontend.c (WIN32) */

void NotifyStage(int);
void Progress(float);

/* instance.c */

void InitialiseInstances(RRuleSet *Cttee);
void SetParameters(RRuleSet *Cttee);
void CheckForms(RRuleSet *Cttee);
void CopyInstances(void);
float NNEstimate(RRuleSet *Cttee, DataRec Case);
float Distance(DataRec Case1, DataRec Case2, float Thresh);
void CheckDistance(DataRec Case, CaseNo Saved);
void FindNearestNeighbors(DataRec Case);
float AverageNeighbors(RRuleSet *Cttee, DataRec Case);
Index BuildIndex(CaseNo Fp, CaseNo Lp);
void ScanIndex(DataRec Case, Index Node, float MinD);
void SwapInstance(CaseNo A, CaseNo B);
void FreeIndex(Index Node);
void FreeInstances(void);

/*  xval.c  */

void CrossVal(void);
void Prepare(void);
void Shuffle(int *);
void Summary(void);

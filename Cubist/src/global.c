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
/*  General data for Cubist      */
/*  -----------------------      */
/*                                                                       */
/*************************************************************************/

#include "defns.h"

#include "redefine.h"
#include "transform.h"

Attribute ClassAtt = 0, /* attribute to use as class */
    LabelAtt = 0,       /* attribute to use as case ID */
    CWtAtt = 0;         /* attribute to use as case weight */

char *IgnoredVals = 0; /* values of labels and atts marked ignore */
int IValsSize = 0,     /* size of above */
    IValsOffset = 0;   /* index of first free char */

int MaxAtt,          /* max att number */
    MaxDiscrVal = 3, /* max discrete values for any att */
    Precision,       /* decimal places for target */
    MaxLabel = 0,    /* max characters in case label */
    LineNo = 0,      /* input line number */
    ErrMsgs = 0,     /* errors found */
    AttExIn = 0,     /* attribute exclusions/inclusions */
    TSBase = 0;      /* base day for time stamps */

CaseNo MaxCase = -1; /* max data item number */

DataRec *Case; /* data items */

DataRec *SaveCase = Nil, /* original case order for better caching */
    *Blocked = Nil;      /* cross-validation blocks */
CaseNo SaveMaxCase;      /* original number of cases  */

DiscrValue *MaxAttVal = Nil, /* number of values for each att */
    *Modal = Nil;            /* most frequent value for discr att */

char *SpecialStatus = Nil; /* special att treatment */

Definition *AttDef = Nil;     /* definitions of implicit atts */
Attribute **AttDefUses = Nil; /* list of attributes used by definition */

String *AttName = Nil,  /* att names */
    **AttValName = Nil; /* att value names */

FILE *Of = 0; /* output file */
String FileStem = "undefined";

ContValue *AttMean = Nil,       /* means of att values */
    *AttSD = Nil,               /* std dev ditto */
        *AttMaxVal = Nil,       /* maximum value in training data */
            *AttMinVal = Nil,   /* minimum ditto */
                *AttPref = Nil, /* preference value */
    Ceiling,                    /* max allowable global prediction */
    Floor,                      /* min allowable global prediction */
    AvCWt;                      /* average case weight */

float ErrReduction = 1; /* benefit of committee model */

double *AttUnit = Nil; /* units in which attribute reported */

int *AttPrec = Nil; /* Attribute precision  */

DataRec *Instance = Nil, /* training cases */
    Ref[2];              /* reference points */
CaseNo MaxInstance = -1; /* highest instance */
Index KDTree = Nil;      /* index of same */
NNEnvRec GNNEnv;         /* global NN environment */
float *RSPredVal = Nil;  /* tabulated RS predictions */

/*************************************************************************/
/*                                                                       */
/*   Global data for Cubist used for building model trees   */
/*   ----------------------------------------------------   */
/*                                                                       */
/*************************************************************************/

EnvRec GEnv; /* global environment */

Tree TempMT = Nil; /* intermediate model tree */

SortRec *SRec = Nil; /* cache for sorting */

float GlobalMean, /* mean of entire training set  */
    GlobalSD,     /* std dev of entire training set */
    GlobalErr;    /* av abs error over training set */

char Fn[512]; /* file name */

FILE *Mf = 0, /* file for saving models  */
    *Pf = 0;  /* file for predicted test values */

/*************************************************************************/
/*                                                                       */
/* Global data for constructing and applying rules    */
/*      -----------------------------------------------    */
/*                                                                       */
/*************************************************************************/

CRule *Rule = Nil; /* current rules */
RuleNo NRules;     /* number of rules */
int RuleSpace;     /* space currently allocated for rules */

RRuleSet *Cttee = Nil;

/*************************************************************************/
/*                                                                       */
/*  Global parameters for Cubist     */
/*  ----------------------------     */
/*                                                                       */
/*************************************************************************/

int VERBOSITY = 0, /* verbosity level (0 = none) */
    FOLDS = 10,    /* cross-validation folds */
    NN = 0,        /* nearest neighbors to use */
    MEMBERS = 1;   /* members in committee */

float MAXD; /* max distance for close neighbors */

Boolean XVAL = 0,     /* true if perform crossvalidation */
    CHOOSEMODE = 0,   /* choose whether to use instances */
    USEINSTANCES = 0, /* using instances */
    UNBIASED = 0;     /* correct any rule bias */

float SAMPLE = 0.0;   /* sample training proportion */
int KRInit = 0;       /* KRandom initializer for SAMPLE */
Boolean LOCK = false; /* true if sample locked */

CaseCount MINITEMS; /* min rule coverage */
int MAXRULES = 100; /* max number of rules */

float EXTRAP = 0.1; /* allowed extrapolation from models */

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
/*		Data defined in global.c				 */
/*		------------------------				 */
/*									 */
/*************************************************************************/

extern	Attribute
		ClassAtt,
		LabelAtt,
		CWtAtt;

extern	 char	*IgnoredVals;
extern	 int	IValsSize,
		IValsOffset;

extern	int	MaxAtt,
		MaxDiscrVal,
		Precision,
		MaxLabel,
		LineNo,
		ErrMsgs,
		AttExIn,
		TSBase;
	
extern	CaseNo	MaxCase;
	
extern	DataRec *Case;
	
extern	DataRec *SaveCase,
		*Blocked;
extern	CaseNo	SaveMaxCase;
	
extern	DiscrValue
		*MaxAttVal,
		*Modal;
	
extern	char	*SpecialStatus;
	
extern	Definition
		*AttDef;
extern	Attribute
		**AttDefUses;
	
extern	String	*AttName,
		**AttValName;
	
extern	FILE	*Of;
extern	String	FileStem;
	
extern	ContValue
		*AttMean,
		*AttSD,
		*AttMaxVal,
		*AttMinVal,
		*AttPref,
		Ceiling,
		Floor,
		AvCWt;

extern	float	ErrReduction;
	
double		*AttUnit;

extern	int	*AttPrec;

extern	DataRec *Instance,
		Ref[2];
extern	CaseNo	MaxInstance;
extern	Index	KDTree;
extern	NNEnvRec
		GNNEnv;
extern	float	*RSPredVal;

extern	EnvRec	GEnv;

extern	Tree	TempMT;

extern	SortRec	*SRec;
	
extern	float	GlobalMean,
		GlobalSD,
		GlobalErr;
	
extern	char	Fn[512];
	
extern	FILE	*Mf,
		*Pf;
	
extern	CRule	*Rule;
extern	RuleNo	NRules;
extern	int	RuleSpace;
	
extern	RRuleSet
		*Cttee;
	
	
extern	int	VERBOSITY,
		FOLDS,
		NN,
		MEMBERS;
	
extern	float	MAXD;
	
extern	Boolean	XVAL,
		CHOOSEMODE,
		USEINSTANCES,
		UNBIASED;
	
extern	float	SAMPLE;
extern	int	KRInit;
extern	Boolean	LOCK;
	
extern	CaseCount
		MINITEMS;
extern	int	MAXRULES;

extern	float	EXTRAP;

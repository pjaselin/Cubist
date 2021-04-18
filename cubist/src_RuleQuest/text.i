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
/*	Text strings for UTF-8 internationalization			 */
/*	-------------------------------------------			 */
/*									 */
/*************************************************************************/



	/*  General stuff  */

//#define UTF8		 	/* uncomment if using UTF-8 */

#ifdef UTF8
#define	 CharWidth(S)		UTF8CharWidth(S)
#else
#define	 CharWidth(S)		(int) strlen(S)
#endif


	/*  Strings with width/format restrictions  */
	/*  (W = width when printed) */

#define	 F_AvErr		"    Average  |error|         "	/* W=29 */
#define	 F_RelErr		"    Relative |error|         "	/* W=29 */
#define	 F_CorrCoeff		"    Correlation coefficient  "	/* W=29 */
#define	 F_Actual		"   Actual"			/* W=9 */
#define	 F_Predicted		"Predicted"			/* W=9 */
#define	 F_Value		"    Value"			/* W=9 */
#define  F_Case			"Case"				/* any W */
#define	 F_UCase		"----"				/* w same */


	/*  Strings of arbitrary length  */

#define	 T_Cubist		"Cubist"
#define	 TX_Release(n)		"Release " n

#define	 T_OptHeader		"\n    Options:\n"
#define	 T_OptApplication	"\tApplication `%s'\n"
#define	 T_OptMaxRules		"\tMaximum of %d rules\n"
#define	 T_OptExtrap		"\tPermit extrapolation of %g%%\n"
#define	 T_OptUseInst		"\tUse instances with rules\n"
#define	 T_OptAllowInst		"\tAllow use of instances with rules\n"
#define	 TX_NNeighbors(n)	"\tUse %d nearest neighbor%s\n", n, Plural(n)
#define	 T_NoBias		"\tUnbiased rules\n"
#define	 T_OptSampling		"\tUse %g%% of data for training\n"
#define	 T_OptSeed		"\tRandom seed %d\n"
#define	 T_OptXval		"\t%d-fold cross-validation\n"
#define	 T_OptCttee		"\t%d-member committee model\n"
#define	 T_UnregnizedOpt	"\n    **  Unrecognised option %s %s\n"
#define	 T_SummaryOpts		"    **  Summary of options for cubist:\n"
#define	 T_ListOpts		"\t-f <filestem>\tapplication filestem\n"\
				"\t-r <integer>\tmaximum number of rules\n"\
				"\t-e <percent>\tmaximum extrapolation\n"\
				"\t-i\t\tuse instances and rules\n"\
				"\t-a\t\tallow use of instances and rules\n"\
				"\t-n <integer>\tnumber of nearest neighbors\n"\
				"\t-u\t\tprefer unbiased rules\n"\
				"\t-S <percent>\ttraining sample percentage\n"\
				"\t-I <integer>\trandom seed for sampling\n"\
				"\t-X <folds>\tcross-validate\n"\
				"\t-C <members>\tcommittee model\n"\
				"\t-h\t\tprint this message\n"
#define	 T_TargetAtt		"\n    Target attribute `%s'\n"
#define	 TX_ReadData(c,a,f)	"\nRead %d cases (%d attributes) from"\
					" %s.data\n", c, a, f
#define	 TX_ReadTest(c,f)	"Read %d cases from %s.test\n", c, f
#define	 T_CWtAtt		"Using relative case weighting\n"
#define	 T_AttributesIn		"\nAttributes included:\n"
#define	 T_AttributesOut	"\nAttributes excluded:\n"
#define	 T_EvalTrain		"\n\nEvaluation on training data (%d cases%s):\n"
#define	 T_AttUsage		"\n\n\tAttribute usage:\n"\
				"\t  Conds  Model\n\n"
#define	 T_EvalTest		"\nEvaluation on test data (%d cases):\n"
#define	 T_Time			"\n\nTime: %.1f secs\n"

#define	 T_IgnoreNATarget	"\n*** Ignoring cases with N/A target value\n"
#define	 T_IgnoreBadTarget	"\n*** Ignoring cases with unknown or N/A target value\n"
#define	 T_NoCases		"*** No cases with known target values\n"

#define	 T_ReplaceUnknowns	"\n    Replacing unknown attribute values:\n"
#define	 T_NoAppVals		"ignoring (no applicable values)"
#define	 T_By			"by"
#define	 T_SettingNNeighbors	"\n\nSetting number of nearest neighbors to %d\n"
#define	 T_SuggestComposite	"Recommend using rules and instances\n"
#define	 T_SuggestRules		"Recommend using rules only\n"

#define	 T_Rule			"Rule"
#define	 TX_RInfo(c,p,m,l,h,e)	": [%d cases, mean %.*f, range %.7g to %.7g, "\
				"est err %.*f]\n\n",c,p,m,l,h,p,e
#define	 T_If			"if"
#define	 T_Then			"then"
#define	 T_ElementOf		"in"
#define	 T_InRange		"in"
#define	 T_IsUnknown		" is unknown\n"

#define	 T_Default		"\n(Default value %.*f)\n\n"
#define	 T_Summary		"Summary"
#define	 T_FoldsReduced		"\n*** folds reduced to number of cases\n"
#define	 T_Fold			"Fold"
#define	 T_EvalHoldOut		"\nEvaluation on hold-out data (%d cases):\n"
#define	 T_MeanErrMag		"Mean |error|"

#define	 TX_Line(l,f)		"*** line %d of `%s':\n    ", l, f
#define	 E_NOFILE(f,e)		"cannot open file %s%s\n", f, e
#define	 E_ForWrite		" for writing"
#define	 E_BADATTNAME		"`:' or `:=' expected after attribute name"\
					" `%s'\n"
#define	 E_EOFINATT		"unexpected eof while reading attribute `%s'\n"
#define	 E_SINGLEATTVAL(a,v)	"attribute `%s' has only one value `%s'\n",\
					a, v
#define	 E_DUPATTNAME		"multiple attributes with name `%s'\n"
#define	 E_CWTATTERR		"case weight attribute must be continuous\n"
#define	 E_BADATTVAL(v,a)	"bad value of `%s' for attribute `%s'\n", v, a
#define	 E_BADNUMBER(a)		"value of `%s' changed to `?'\n", a
#define	 E_NOMEM		"unable to allocate sufficient memory\n"
#define	 E_TOOMANYVALS(a,n)	"too many values for attribute `%s'"\
					" (max %d)\n", a, n
#define	 E_BADDISCRETE		"bad number of discrete values for attribute"\
					" `%s'\n"
#define	 E_NOTARGET		"target attribute `%s' not found\n"
#define	 E_BADTARGET		"target attribute `%s' is not numeric\n"
#define	 E_LONGNAME		"overlength name: check data file formats\n"
#define	 E_HITEOF		"unexpected end of file\n"
#define	 E_MISSNAME		"missing name or value before `%s'\n"
#define	 E_BADTSTMP(d,a)	"bad timestamp `%s' for attribute `%s'\n", d, a
#define	 E_BADDATE(d,a)		"bad date `%s' for attribute `%s'\n", d, a
#define	 E_BADTIME(d,a)		"bad time `%s' for attribute `%s'\n", d, a
#define	 E_UNKNOWNATT		"unknown attribute name `%s'\n"
#define	 E_BADDEF1(a,s,x)	"in definition of attribute `%s':\n"\
					"\tat `%.12s': expect %s\n", a, s, x
#define	 E_BADDEF2(a,s,x)	"in definition of attribute `%s':\n"\
					"\t`%s': %s\n", a, s, x
#define	 E_SAMEATT(a,b)		"[warning] attribute `%s' is identical to"\
					" attribute `%s'\n", a, b
#define	 E_BADDEF3		"cannot define target attribute `%s'\n"
#define	 E_BADDEF4		"[warning] target attribute appears in"\
					" definition of attribute `%s':\n"
#define	 EX_MODELFILE(f)	"file %s incompatible with .names file\n", f
#define	 E_MFATT		"undefined or excluded attribute"
#define	 E_MFATTVAL		"undefined attribute value"
#define	 E_MFEOF		"unexpected eof"
#define	 T_ErrorLimit		"\nError limit exceeded\n"
#define	 TX_IllegalValue(v,l,h)	"\t** illegal value %g -- "\
				"should be between %g and %g\n", v, l, h

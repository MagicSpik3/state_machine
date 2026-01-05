"""
A comprehensive corpus of SPSS/PSPP syntax used to stress-test 
the State Machine's parsing capabilities.
"""

COMPREHENSIVE_SCOPE_CORPUS = """
* ----------------------------------------------------------------;
* PART 1: Variable Declaration & Initialization;
* ----------------------------------------------------------------.

NUMERIC ID (F8.0).
STRING Gender (A10).
COMPUTE Age = 0.
COMPUTE Income_2023 = -1.

* ----------------------------------------------------------------;
* PART 2: Basic Transformation;
* ----------------------------------------------------------------.

* Simple assignment.
COMPUTE Age = 25.

* Arithmetic with whitespace mess.
   COMPUTE   Income_2023  =  50000  +  ( 100 * 12 ).

* ----------------------------------------------------------------;
* PART 3: Conditional Logic (The "Parser Wall");
* ----------------------------------------------------------------.

* Single line IF.
IF (Gender = 'M') COMPUTE Description = 'Male'.

* Nested Logic (DO IF / ELSE IF / END IF).
DO IF (Age < 18).
    COMPUTE Age_Group = 1.
    RECODE Description ('Male'='Boy') ('Female'='Girl').
ELSE IF (Age >= 18 AND Age < 65).
    COMPUTE Age_Group = 2.
    COMPUTE Taxable = 1.
ELSE.
    COMPUTE Age_Group = 3.
END IF.

* ----------------------------------------------------------------;
* PART 4: RECODE Variations;
* ----------------------------------------------------------------.

* Recode INTO new variable.
RECODE Income_2023 (Lowest thru 20000 = 1) (Else = 0) INTO Poverty_Flag.

* Recode In-Place (modifies existing version).
RECODE Gender ('m'='M') ('f'='F').

* ----------------------------------------------------------------;
* PART 5: Passthrough (Should be ignored by State Machine);
* ----------------------------------------------------------------.

EXECUTE.
FREQUENCIES VARIABLES=Age_Group /ORDER=ANALYSIS.
GRAPH /BAR(SIMPLE)=MEAN(Income_2023) BY Age_Group.
"""

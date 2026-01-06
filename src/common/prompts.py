# src/common/prompts.py

DESCRIBE_NODE_PROMPT = (
    "You are a Business Analyst. Describe this logic step in ONE sentence.\n"
    "Context: {node_id} depends on {dependencies}\n"
    "Code: {source}\n"
    "Description:"
)

GENERATE_TITLE_PROMPT = (
    "Summarize these variables into a 3-5 word Title.\n"
    "Variables: {variables}\n"
    "Title:"
)



REFINE_CODE_PROMPT = (
    "You are an expert R and SPSS migration engineer. \n"
    "Refactor the following R code which was auto-generated from SPSS. \n"
    "GOALS:\n"
    "1. **Readability:** Combine consecutive `mutate()` calls into single blocks where possible.\n"
    "2. **Logic:** Convert nested `if_else()` or repeated conditional updates into `case_when()`.\n"
    "3. **Dates:** Replace 'DATE.MDY(m,d,y)' with 'make_date(y,m,d)'. IMPORTANT: SPSS is (M,D,Y), R is (Y,M,D).\n"
    "4. **Syntax:** Ensure pipes ('%>%') are valid and 'NA' is used for missing values.\n"
    "5. **Cleanliness:** Remove '# TODO' comments if the logic is handled.\n"
    "OUTPUT ONLY THE CODE. No markdown, no explanation.\n\n"
    "Code to Fix:\n"
    "```r\n"
    "{code}\n"
    "```"
)
import re
from typing import List, Tuple

class RosettaStone:
    """
    The Single Source of Truth for translating SPSS functions to R.
    """
    
    TRANSLATIONS = {
        "$SYSMIS": "NA",
        "TRUNC": "trunc",
        "MAX": "pmax",
        "MIN": "pmin",
        "MEAN": "mean",
        "SUM": "sum",
        "RTRIM": "str_trim",
        "LTRIM": "str_trim",
        "CONCAT": "paste0",
        "NUMBER": "as.numeric", # Fallback if regex fails
    }

    @staticmethod
    def _split_args(expression: str) -> List[str]:
        """
        Splits a string by commas, but ignores commas inside parentheses.
        Ex: "trunc(a,b), c" -> ["trunc(a,b)", "c"]
        """
        args = []
        current_arg = []
        paren_depth = 0
        
        for char in expression:
            if char == '(':
                paren_depth += 1
                current_arg.append(char)
            elif char == ')':
                paren_depth -= 1
                current_arg.append(char)
            elif char == ',' and paren_depth == 0:
                args.append("".join(current_arg).strip())
                current_arg = []
            else:
                current_arg.append(char)
        
        if current_arg:
            args.append("".join(current_arg).strip())
            
        return args

    @staticmethod
    def translate_expression(expression: str) -> str:
        # 1. Constants
        expression = expression.replace("$SYSMIS", "NA")

        # 2. Complex Replacements (DATE.MDY)
        date_pattern = re.compile(r"(?i)DATE\.MDY\s*\((.*)\)")
        match = date_pattern.search(expression)
        if match:
            # ... (keep existing DATE logic) ...
            inner_content = match.group(1)
            args = RosettaStone._split_args(inner_content)
            if len(args) == 3:
                m, d, y = args
                m = RosettaStone.translate_expression(m)
                d = RosettaStone.translate_expression(d)
                y = RosettaStone.translate_expression(y)
                original_span = match.group(0)
                expression = expression.replace(original_span, f"make_date({y}, {m}, {d})")

        # 3. MOD(a, b) -> (a %% b)
        if "MOD(" in expression.upper():
            expression = re.sub(r"(?i)MOD\(([^,]+),([^)]+)\)", r"(\1 %%\2)", expression)

        # 4. NUMBER(x, fmt) -> as.numeric(x)  <--- MOVED UP & FIXED
        # Regex: NUMBER followed by paren, group 1 (var), comma, group 2 (format), close paren
        # We replace it with "as.numeric(\1)"
        if "NUMBER(" in expression.upper():
             expression = re.sub(r"(?i)NUMBER\(([^,]+),\s*[^)]+\)", r"as.numeric(\1)", expression)

        # 5. Standard Function Mapping
        # Replace FUNC( with new_func(
        # We REMOVE 'NUMBER' from this list to prevent it from overwriting if the regex above missed something 
        # (or we keep it as fallback, but the regex above usually handles it).
        
        # Explicitly define simple maps (excluding NUMBER to avoid conflict)
        simple_maps = {
            "TRUNC": "trunc",
            "MAX": "pmax",
            "MIN": "pmin",
            "MEAN": "mean",
            "SUM": "sum",
            "RTRIM": "str_trim",
            "LTRIM": "str_trim",
            "CONCAT": "paste0"
        }
        
        for spss_name, r_name in simple_maps.items():
            expression = re.sub(rf"(?i)\b{spss_name}\(", f"{r_name}(", expression)
            
        return expression


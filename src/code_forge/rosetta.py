import re
from typing import List

class RosettaStone:
    """
    The Single Source of Truth for translating SPSS functions to R.
    Handles nested expressions, argument swapping, and syntax mapping.
    """
    
    # 1. Simple 1-to-1 replacements
    TRANSLATIONS = {
        "$SYSMIS": "NA",
        "TRUNC": "trunc",
        "MAX": "pmax",
        "MIN": "pmin",
        "MEAN": "mean",
        "SUM": "sum",
        "RTRIM": "trimws", # Use base R trimws
        "LTRIM": "trimws",
        "CONCAT": "paste0",
        "ABS": "abs",
        "SQRT": "sqrt",
        "RND": "round",
        "NUMBER": "as.numeric", # Fallback
    }

    @staticmethod
    def _split_args(expression: str) -> List[str]:
        """
        Splits a string by commas, but ignores commas inside parentheses.
        Crucial for nested functions like DATE.MDY(MOD(a,b), c, d).
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
        if not expression:
            return "NA"

        # 0. Basic Cleanup
        expr = expression.replace("$SYSMIS", "NA")
        
        # 1. Handle Operators
        # FIX: Use Regex to replace single '=' with '==' ONLY if not preceded/followed by other operators.
        # This prevents >= becoming >==
        # Lookbehind (?<!...) checks previous char is NOT <, >, !, or =
        # Lookahead (?!=) checks next char is NOT =
        expr = re.sub(r"(?<![<>!=])=(?!=)", "==", expr)

        # 2. Handle DATE.MDY(m, d, y) -> make_date(y, m, d)
        while "DATE.MDY" in expr.upper():
            start_idx = expr.upper().find("DATE.MDY")
            if start_idx == -1: break
            
            open_paren = expr.find("(", start_idx)
            if open_paren == -1: break
            
            # Find balanced closing paren
            count = 1
            close_paren = -1
            for i in range(open_paren + 1, len(expr)):
                if expr[i] == '(': count += 1
                elif expr[i] == ')': count -= 1
                
                if count == 0:
                    close_paren = i
                    break
            
            if close_paren == -1: break # Malformed
            
            # Extract content: "m, d, y"
            full_match = expr[start_idx:close_paren+1]
            content = expr[open_paren+1:close_paren]
            
            # Parse Args with nesting support
            args = RosettaStone._split_args(content)
            
            if len(args) == 3:
                m, d, y = args
                # Recursively translate arguments
                m = RosettaStone.translate_expression(m)
                d = RosettaStone.translate_expression(d)
                y = RosettaStone.translate_expression(y)
                
                # Reconstruct as R function: make_date(y, m, d)
                replacement = f"make_date({y}, {m}, {d})"
                expr = expr.replace(full_match, replacement)
            else:
                # Fallback
                expr = expr.replace("DATE.MDY", "make_date")
                break

        # 3. Handle NUMBER(x, fmt) -> as.numeric(x)
        expr = re.sub(r"(?i)NUMBER\s*\(([^,]+)\s*,[^)]+\)", r"as.numeric(\1)", expr)

        # 4. Handle MOD(a, b) -> (a %% b)
        expr = re.sub(r"(?i)MOD\s*\((.+?),\s*(.+?)\)", r"(\1 %% \2)", expr)

        # 5. Generic Dictionary Replacements
        for spss_name, r_name in RosettaStone.TRANSLATIONS.items():
            expr = re.sub(rf"(?i)\b{spss_name}\b", r_name, expr)

        return expr
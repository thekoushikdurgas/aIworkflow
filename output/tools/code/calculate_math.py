"""
Safely evaluate mathematical expressions.
"""

import math

def calculate_math(expression: str) -> str:
    """
    Safely evaluate mathematical expressions.
    
    Args:
        expression: Mathematical expression to evaluate (e.g., "2 + 3 * 4")
    
    Returns:
        Result of the calculation or error message
    """
    try:
        # Whitelist of allowed characters and functions
        allowed_chars = set("0123456789+-*/.() ")
        allowed_functions = {
            'sin': math.sin, 'cos': math.cos, 'tan': math.tan,
            'log': math.log, 'log10': math.log10, 'sqrt': math.sqrt,
            'abs': abs, 'round': round, 'pow': pow,
            'pi': math.pi, 'e': math.e
        }
        
        # Check for allowed characters
        if not all(c in allowed_chars or c.isalpha() for c in expression):
            return "Error: Expression contains disallowed characters"
        
        # Prepare safe namespace
        safe_dict = {"__builtins__": {}}
        safe_dict.update(allowed_functions)
        
        # Evaluate expression
        result = eval(expression, safe_dict)
        return f"Result: {result}"
        
    except Exception as e:
        return f"Error calculating '{expression}': {str(e)}"

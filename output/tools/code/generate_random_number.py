"""
Generate a random number within a specified range.
"""

import random

def generate_random_number(min_value: int = 1, max_value: int = 100) -> str:
    """
    Generate a random number within a specified range.
    
    Args:
        min_value: Minimum value (inclusive)
        max_value: Maximum value (inclusive)
    
    Returns:
        Random number as a string
    """
    try:
        # Convert to integers if they're not already
        min_val = int(min_value)
        max_val = int(max_value)
        
        if min_val > max_val:
            return "Error: Minimum value cannot be greater than maximum value"
        
        random_num = random.randint(min_val, max_val)
        return f"Random number between {min_val} and {max_val}: {random_num}"
        
    except Exception as e:
        return f"Error generating random number: {str(e)}"

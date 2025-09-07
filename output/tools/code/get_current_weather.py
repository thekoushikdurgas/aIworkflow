"""
Get current weather information for a location.
"""

import random

def get_current_weather(location: str, unit: str = "celsius") -> str:
    """
    Get current weather information for a location.
    
    Args:
        location: The city and state/country, e.g. "San Francisco, CA" or "London, UK"
        unit: Temperature unit, either "celsius" or "fahrenheit"
    
    Returns:
        Weather information as a formatted string
    """
    try:
        # This is a mock implementation - in real use, integrate with a weather API
        temp_c = random.randint(-10, 35)
        temp_f = int(temp_c * 9/5 + 32)
        
        conditions = ["sunny", "cloudy", "rainy", "partly cloudy", "foggy"]
        condition = random.choice(conditions)
        
        humidity = random.randint(30, 90)
        wind_speed = random.randint(5, 25)
        
        temp = temp_c if unit == "celsius" else temp_f
        temp_unit = "°C" if unit == "celsius" else "°F"
        
        return f"""Weather in {location}:
- Temperature: {temp}{temp_unit}
- Condition: {condition}
- Humidity: {humidity}%
- Wind Speed: {wind_speed} km/h

Note: This is simulated weather data. For real weather, integrate with a weather API service."""
        
    except Exception as e:
        return f"Error getting weather for {location}: {str(e)}"

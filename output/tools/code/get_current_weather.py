"""
Get current weather information for a location.
"""

import random
import json

def get_current_weather(location: str, unit: str = "celsius") -> str:
    """
    Get current weather information for a location.
    
    Args:
        location: The city and state/country, e.g. "San Francisco, CA" or "London, UK"
        unit: Temperature unit, either "celsius" or "fahrenheit"
    
    Returns:
        weather_report (string): Formatted weather information (plain_text format)
        temperature (number): Current temperature in specified unit
        conditions (string): Weather conditions (sunny, cloudy, etc.) (plain_text format)
        location_info (string): Information about the location queried (plain_text format)
    """
    try:
        # This is a mock implementation - in real use, integrate with a weather API
        temp_c = random.randint(-10, 35)
        temp_f = int(temp_c * 9/5 + 32)
        
        conditions_list = ["sunny", "cloudy", "rainy", "partly cloudy", "foggy"]
        condition = random.choice(conditions_list)
        
        humidity = random.randint(30, 90)
        wind_speed = random.randint(5, 25)
        
        temp = temp_c if unit == "celsius" else temp_f
        temp_unit = "°C" if unit == "celsius" else "°F"
        
        weather_report = f"""Weather in {location}:
- Temperature: {temp}{temp_unit}
- Condition: {condition}
- Humidity: {humidity}%
- Wind Speed: {wind_speed} km/h

Note: This is simulated weather data. For real weather, integrate with a weather API service."""
        
        result = {
            "weather_report": weather_report,
            "temperature": temp,
            "conditions": condition,
            "location_info": f"Weather data retrieved for {location} in {unit} units"
        }
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        error_result = {
            "weather_report": f"Error getting weather for {location}: {str(e)}",
            "temperature": None,
            "conditions": "error",
            "location_info": f"Failed to retrieve weather for {location}"
        }
        return json.dumps(error_result, indent=2)

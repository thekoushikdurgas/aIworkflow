"""
Get current date and time in specified timezone.
"""

import datetime
import json

def get_current_time(timezone: str = "UTC") -> str:
    """
    Get current date and time.
    
    Args:
        timezone: Timezone (e.g., "UTC", "US/Pacific", "Europe/London")
    
    Returns:
        current_datetime (string): Current date and time in specified timezone (plain_text format)
        timezone_info (string): Information about the timezone used (plain_text format)
        iso_format (string): Date and time in ISO format (plain_text format)
        timestamp (number): Unix timestamp
    """
    try:
        try:
            import pytz
            
            if timezone == "UTC":
                tz = pytz.UTC
            else:
                tz = pytz.timezone(timezone)
                
            now = datetime.datetime.now(tz)
            
            result = {
                "current_datetime": f"{now.strftime('%Y-%m-%d %H:%M:%S')} {timezone}",
                "timezone_info": f"Time retrieved for timezone: {timezone}",
                "iso_format": now.isoformat(),
                "timestamp": now.timestamp()
            }
            
            return json.dumps(result, indent=2)
        
        except ImportError:
            # Fallback if pytz is not available
            now = datetime.datetime.now()
            result = {
                "current_datetime": f"{now.strftime('%Y-%m-%d %H:%M:%S')} (system local)",
                "timezone_info": f"pytz not available, showing system local time instead of {timezone}",
                "iso_format": now.isoformat(),
                "timestamp": now.timestamp()
            }
            return json.dumps(result, indent=2)
        
    except Exception as e:
        # Fallback to system time
        now = datetime.datetime.now()
        error_result = {
            "current_datetime": f"{now.strftime('%Y-%m-%d %H:%M:%S')} (system local)",
            "timezone_info": f"Error with timezone {timezone}: {str(e)}",
            "iso_format": now.isoformat(),
            "timestamp": now.timestamp()
        }
        return json.dumps(error_result, indent=2)

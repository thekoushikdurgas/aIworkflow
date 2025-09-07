"""
Get current date and time in specified timezone.
"""

import datetime

def get_current_time(timezone: str = "UTC") -> str:
    """
    Get current date and time.
    
    Args:
        timezone: Timezone (e.g., "UTC", "US/Pacific", "Europe/London")
    
    Returns:
        Current date and time as a formatted string
    """
    try:
        try:
            import pytz
            
            if timezone == "UTC":
                tz = pytz.UTC
            else:
                tz = pytz.timezone(timezone)
                
            now = datetime.datetime.now(tz)
            
            return f"""Current time:
- Date: {now.strftime('%Y-%m-%d')}
- Time: {now.strftime('%H:%M:%S')}
- Timezone: {timezone}
- Day of week: {now.strftime('%A')}
- ISO format: {now.isoformat()}"""
        
        except ImportError:
            # Fallback if pytz is not available
            now = datetime.datetime.now()
            return f"""Current time (system local):
- Date: {now.strftime('%Y-%m-%d')}
- Time: {now.strftime('%H:%M:%S')}
- Day of week: {now.strftime('%A')}

Note: pytz not available, showing system local time instead of {timezone}"""
        
    except Exception as e:
        # Fallback to system time
        now = datetime.datetime.now()
        return f"""Current time (system local):
- Date: {now.strftime('%Y-%m-%d')}
- Time: {now.strftime('%H:%M:%S')}
- Day of week: {now.strftime('%A')}

Note: Error with timezone {timezone}: {str(e)}"""

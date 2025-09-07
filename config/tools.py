"""
Tool definitions and configuration for function calling.

This module contains predefined tools and utilities for managing
custom functions that can be called by the AI models.
"""

import json
import requests
import datetime
import math
import random
import os
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from pathlib import Path

@dataclass
class ToolParameter:
    """Definition of a tool parameter."""
    name: str
    type: str  # 'string', 'number', 'integer', 'boolean', 'array', 'object'
    description: str
    required: bool = True
    enum: Optional[List[Any]] = None
    default: Optional[Any] = None

@dataclass 
class ToolDefinition:
    """Complete tool definition for function calling."""
    name: str
    description: str
    parameters: List[ToolParameter] = field(default_factory=list)
    function: Optional[Callable] = None
    category: str = "general"
    enabled: bool = True
    
    def to_gemini_schema(self) -> Dict[str, Any]:
        """Convert to Gemini function calling schema."""
        properties = {}
        required = []
        
        for param in self.parameters:
            prop_def = {
                "type": param.type,
                "description": param.description
            }
            
            if param.enum:
                prop_def["enum"] = param.enum
                
            if param.default is not None:
                prop_def["default"] = param.default
                
            properties[param.name] = prop_def
            
            if param.required:
                required.append(param.name)
        
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required
            }
        }

# Predefined tool functions

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
        import random
        
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

def get_current_time(timezone: str = "UTC") -> str:
    """
    Get current date and time.
    
    Args:
        timezone: Timezone (e.g., "UTC", "US/Pacific", "Europe/London")
    
    Returns:
        Current date and time as a formatted string
    """
    try:
        import pytz
        from datetime import datetime
        
        if timezone == "UTC":
            tz = pytz.UTC
        else:
            tz = pytz.timezone(timezone)
            
        now = datetime.now(tz)
        
        return f"""Current time:
- Date: {now.strftime('%Y-%m-%d')}
- Time: {now.strftime('%H:%M:%S')}
- Timezone: {timezone}
- Day of week: {now.strftime('%A')}
- ISO format: {now.isoformat()}"""
        
    except Exception as e:
        # Fallback to system time
        now = datetime.datetime.now()
        return f"""Current time (system local):
- Date: {now.strftime('%Y-%m-%d')}
- Time: {now.strftime('%H:%M:%S')}
- Day of week: {now.strftime('%A')}

Note: {str(e)}"""

def search_web(query: str, num_results: int = 3) -> str:
    """
    Search the web for information (mock implementation).
    
    Args:
        query: Search query
        num_results: Number of results to return (1-10)
    
    Returns:
        Search results as formatted text
    """
    # This is a mock implementation
    # In real use, you would integrate with a search API like Google Custom Search
    
    mock_results = [
        {
            "title": f"Result about {query}",
            "url": f"https://example.com/search?q={query.replace(' ', '+')}",
            "snippet": f"This is a mock search result for '{query}'. In a real implementation, this would contain actual web search results."
        },
        {
            "title": f"More information on {query}",
            "url": f"https://wikipedia.org/search?q={query.replace(' ', '+')}",
            "snippet": f"Additional mock information about '{query}'. Real implementation would use APIs like Google Custom Search, Bing Search, or DuckDuckGo."
        },
        {
            "title": f"{query} - Latest Updates",
            "url": f"https://news.example.com/{query.replace(' ', '-')}",
            "snippet": f"Latest news and updates about '{query}'. This would contain real-time information from web sources."
        }
    ]
    
    num_results = min(max(1, num_results), len(mock_results))
    results = mock_results[:num_results]
    
    formatted_results = f"Search results for '{query}':\n\n"
    for i, result in enumerate(results, 1):
        formatted_results += f"{i}. **{result['title']}**\n"
        formatted_results += f"   URL: {result['url']}\n"
        formatted_results += f"   {result['snippet']}\n\n"
    
    formatted_results += "Note: These are mock search results. For real web search, integrate with a search API service."
    
    return formatted_results

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
        if min_value > max_value:
            return "Error: Minimum value cannot be greater than maximum value"
        
        random_num = random.randint(min_value, max_value)
        return f"Random number between {min_value} and {max_value}: {random_num}"
        
    except Exception as e:
        return f"Error generating random number: {str(e)}"

def file_operations(operation: str, filename: str, content: str = "") -> str:
    """
    Perform basic file operations (read, write, list).
    
    Args:
        operation: Operation type ("read", "write", "list", "exists")
        filename: File path (relative to output directory)
        content: Content to write (for write operation)
    
    Returns:
        Result of the file operation
    """
    try:
        base_dir = Path("output/temp")
        base_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = base_dir / filename
        
        # Security check - ensure file is within base directory
        if not str(file_path.resolve()).startswith(str(base_dir.resolve())):
            return "Error: File path not allowed for security reasons"
        
        if operation == "read":
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                return f"Content of {filename}:\n{content}"
            else:
                return f"Error: File {filename} does not exist"
                
        elif operation == "write":
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return f"Successfully wrote to {filename}"
            
        elif operation == "list":
            files = [f.name for f in base_dir.iterdir() if f.is_file()]
            return f"Files in directory:\n" + "\n".join(files) if files else "No files found"
            
        elif operation == "exists":
            exists = file_path.exists()
            return f"File {filename} {'exists' if exists else 'does not exist'}"
            
        else:
            return f"Error: Unknown operation '{operation}'. Use: read, write, list, exists"
            
    except Exception as e:
        return f"File operation error: {str(e)}"

def create_default_tools() -> Dict[str, ToolDefinition]:
    """Create default tool definitions."""
    tools = {}
    
    # Weather tool
    tools["get_weather"] = ToolDefinition(
        name="get_current_weather",
        description="Get current weather information for a specified location",
        parameters=[
            ToolParameter("location", "string", "The city and state/country (e.g., 'San Francisco, CA')"),
            ToolParameter("unit", "string", "Temperature unit", required=False, 
                         enum=["celsius", "fahrenheit"], default="celsius")
        ],
        function=get_current_weather,
        category="information"
    )
    
    # Math calculator
    tools["calculator"] = ToolDefinition(
        name="calculate_math",
        description="Safely evaluate mathematical expressions and calculations",
        parameters=[
            ToolParameter("expression", "string", "Mathematical expression to calculate (e.g., '2 + 3 * 4', 'sqrt(25)')")
        ],
        function=calculate_math,
        category="utility"
    )
    
    # Time tool
    tools["get_time"] = ToolDefinition(
        name="get_current_time",
        description="Get current date and time in specified timezone",
        parameters=[
            ToolParameter("timezone", "string", "Timezone (e.g., 'UTC', 'US/Pacific', 'Europe/London')", 
                         required=False, default="UTC")
        ],
        function=get_current_time,
        category="information"
    )
    
    # Web search (mock)
    tools["web_search"] = ToolDefinition(
        name="search_web",
        description="Search the web for information (mock implementation for demo)",
        parameters=[
            ToolParameter("query", "string", "Search query"),
            ToolParameter("num_results", "integer", "Number of results to return", 
                         required=False, default=3)
        ],
        function=search_web,
        category="information"
    )
    
    # Random number generator
    tools["random_number"] = ToolDefinition(
        name="generate_random_number",
        description="Generate a random number within a specified range",
        parameters=[
            ToolParameter("min_value", "integer", "Minimum value (inclusive)", 
                         required=False, default=1),
            ToolParameter("max_value", "integer", "Maximum value (inclusive)", 
                         required=False, default=100)
        ],
        function=generate_random_number,
        category="utility"
    )
    
    # File operations
    tools["file_ops"] = ToolDefinition(
        name="file_operations",
        description="Perform basic file operations (read, write, list files)",
        parameters=[
            ToolParameter("operation", "string", "Operation type", 
                         enum=["read", "write", "list", "exists"]),
            ToolParameter("filename", "string", "File path relative to temp directory"),
            ToolParameter("content", "string", "Content to write (for write operation)", 
                         required=False, default="")
        ],
        function=file_operations,
        category="utility"
    )
    
    return tools

def get_default_tools() -> Dict[str, ToolDefinition]:
    """Get the default set of tools."""
    return create_default_tools()

def get_tools_by_category(category: str) -> Dict[str, ToolDefinition]:
    """Get tools filtered by category."""
    all_tools = get_default_tools()
    return {name: tool for name, tool in all_tools.items() if tool.category == category}

def get_tool_categories() -> List[str]:
    """Get list of available tool categories."""
    all_tools = get_default_tools()
    categories = set(tool.category for tool in all_tools.values())
    return sorted(list(categories))

def validate_tool_call(tool_name: str, parameters: Dict[str, Any]) -> tuple[bool, str]:
    """Validate a tool call with its parameters."""
    tools = get_default_tools()
    
    if tool_name not in tools:
        return False, f"Unknown tool: {tool_name}"
    
    tool = tools[tool_name]
    
    # Check required parameters
    required_params = [p.name for p in tool.parameters if p.required]
    missing_params = [p for p in required_params if p not in parameters]
    
    if missing_params:
        return False, f"Missing required parameters: {', '.join(missing_params)}"
    
    # Check parameter types (basic validation)
    for param in tool.parameters:
        if param.name in parameters:
            value = parameters[param.name]
            
            if param.type == "integer" and not isinstance(value, int):
                try:
                    parameters[param.name] = int(value)
                except ValueError:
                    return False, f"Parameter '{param.name}' must be an integer"
            
            elif param.type == "number" and not isinstance(value, (int, float)):
                try:
                    parameters[param.name] = float(value)
                except ValueError:
                    return False, f"Parameter '{param.name}' must be a number"
            
            elif param.type == "boolean" and not isinstance(value, bool):
                if isinstance(value, str):
                    parameters[param.name] = value.lower() in ['true', '1', 'yes', 'on']
                else:
                    return False, f"Parameter '{param.name}' must be a boolean"
    
    return True, "Valid"

def execute_tool(tool_name: str, parameters: Dict[str, Any]) -> str:
    """Execute a tool with given parameters."""
    # Validate first
    is_valid, message = validate_tool_call(tool_name, parameters)
    if not is_valid:
        return f"Tool validation failed: {message}"
    
    tools = get_default_tools()
    tool = tools.get(tool_name)
    
    if not tool or not tool.function:
        return f"Tool '{tool_name}' not found or not executable"
    
    try:
        # Execute the tool function
        result = tool.function(**parameters)
        return result
        
    except Exception as e:
        return f"Tool execution error: {str(e)}"

def save_custom_tools(tools: Dict[str, ToolDefinition], 
                     file_path: str = "config/custom_tools.json") -> bool:
    """Save custom tool definitions to file."""
    try:
        config_dir = Path(file_path).parent
        config_dir.mkdir(parents=True, exist_ok=True)
        
        # Convert tools to serializable format
        tools_data = {}
        for name, tool in tools.items():
            tools_data[name] = {
                "name": tool.name,
                "description": tool.description,
                "parameters": [
                    {
                        "name": p.name,
                        "type": p.type,
                        "description": p.description,
                        "required": p.required,
                        "enum": p.enum,
                        "default": p.default
                    }
                    for p in tool.parameters
                ],
                "category": tool.category,
                "enabled": tool.enabled
            }
        
        with open(file_path, 'w') as f:
            json.dump(tools_data, f, indent=2)
        
        return True
        
    except Exception as e:
        print(f"Error saving custom tools: {e}")
        return False

def load_custom_tools(file_path: str = "config/custom_tools.json") -> Dict[str, ToolDefinition]:
    """Load custom tool definitions from file."""
    tools = {}
    
    if not Path(file_path).exists():
        return tools
    
    try:
        with open(file_path, 'r') as f:
            tools_data = json.load(f)
        
        for name, tool_data in tools_data.items():
            parameters = []
            for param_data in tool_data.get("parameters", []):
                parameters.append(ToolParameter(
                    name=param_data["name"],
                    type=param_data["type"],
                    description=param_data["description"],
                    required=param_data.get("required", True),
                    enum=param_data.get("enum"),
                    default=param_data.get("default")
                ))
            
            tools[name] = ToolDefinition(
                name=tool_data["name"],
                description=tool_data["description"],
                parameters=parameters,
                category=tool_data.get("category", "custom"),
                enabled=tool_data.get("enabled", True)
            )
    
    except Exception as e:
        print(f"Error loading custom tools: {e}")
    
    return tools

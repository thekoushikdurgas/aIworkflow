#!/usr/bin/env python3
"""Test script to validate all updated tools return proper JSON structure."""

import sys
import json
from pathlib import Path

# Add output tools to path
sys.path.append(str(Path('output/tools/code')))

def test_tool(tool_name, tool_function, *args):
    """Test a tool and validate its JSON output structure."""
    try:
        result = tool_function(*args)
        parsed = json.loads(result)
        print(f"✅ {tool_name} - JSON output valid")
        print(f"   Keys: {list(parsed.keys())}")
        return True
    except json.JSONDecodeError as e:
        print(f"❌ {tool_name} - Invalid JSON: {e}")
        print(f"   Raw output: {result[:100]}...")
        return False
    except Exception as e:
        print(f"❌ {tool_name} - Error: {e}")
        return False

def main():
    """Run tests on all updated tools."""
    print("🧪 Testing Updated Tools\n" + "="*50)
    
    # Import all tools
    from text_list_processor import text_list_processor
    from calculate_math import calculate_math
    from task_list_manager import task_list_manager
    from number_list_analyzer import number_list_analyzer
    from file_operations import file_operations
    from generate_random_number import generate_random_number
    from get_current_time import get_current_time
    from get_current_weather import get_current_weather
    from search_web import search_web
    
    tests_passed = 0
    total_tests = 0
    
    # Test each tool
    tests = [
        ("text_list_processor", text_list_processor, ['hello', 'world'], 'uppercase'),
        ("calculate_math", calculate_math, '2 + 3 * 4'),
        ("task_list_manager", task_list_manager, ['task1', 'task2'], [True, False], True),
        ("number_list_analyzer", number_list_analyzer, [1, 2, 3, 4, 5], True),
        ("file_operations", file_operations, 'list', 'dummy.txt'),
        ("generate_random_number", generate_random_number, 1, 10),
        ("get_current_time", get_current_time, 'UTC'),
        ("get_current_weather", get_current_weather, 'New York', 'celsius'),
        ("search_web", search_web, 'Python programming', 2),
    ]
    
    for test_data in tests:
        tool_name = test_data[0]
        tool_function = test_data[1]
        args = test_data[2:]
        
        if test_tool(tool_name, tool_function, *args):
            tests_passed += 1
        total_tests += 1
        print()
    
    print(f"🎯 Test Results: {tests_passed}/{total_tests} tools passed")
    if tests_passed == total_tests:
        print("🎉 All tools successfully return structured JSON!")
    else:
        print("⚠️  Some tools need attention")

if __name__ == "__main__":
    main()

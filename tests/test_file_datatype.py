#!/usr/bin/env python3
"""Test script to validate file datatype implementation."""

import json
import os

def test_file_tools():
    """Test that file tools are properly configured."""
    print('🧪 Testing File Datatype Implementation')
    print('='*50)
    
    tools = ['file_analyzer.json', 'text_file_reader.json']
    tools_dir = 'output/tools'
    
    for tool_file in tools:
        path = os.path.join(tools_dir, tool_file)
        try:
            with open(path, 'r') as f:
                tool_config = json.load(f)
            
            print(f'✅ {tool_file}: Valid JSON')
            
            # Check for file parameters
            input_params = tool_config.get('input_parameters', [])
            file_params = [p for p in input_params if p.get('type') == 'file']
            if file_params:
                print(f'   📁 Found {len(file_params)} file parameter(s)')
                for fp in file_params:
                    print(f'      - {fp.get("name")}: {fp.get("description")}')
            
            print()
        except Exception as e:
            print(f'❌ {tool_file}: Error - {e}')
            print()

def test_tool_workshop_validation():
    """Test that tool workshop validates file parameters."""
    print('🔍 Testing Tool Workshop Validation')
    print('='*40)
    
    # Test validation function
    try:
        import sys
        sys.path.append('src/ui')
        from tool_workshop import ToolWorkshopInterface
        from config.settings import AppSettings
        
        workshop = ToolWorkshopInterface(AppSettings())
        
        # Test file parameter validation
        test_config = {
            "name": "test_file_tool",
            "description": "Test file tool",
            "category": "test",
            "input_parameters": [
                {
                    "name": "test_file",
                    "type": "file",
                    "description": "Test file parameter",
                    "required": True
                }
            ],
            "output_parameters": [
                {
                    "name": "result",
                    "type": "string",
                    "description": "Test result",
                    "format": "plain_text"
                }
            ]
        }
        
        is_valid, message = workshop.validate_tool_config(test_config)
        if is_valid:
            print('✅ File parameter validation: PASSED')
        else:
            print(f'❌ File parameter validation: FAILED - {message}')
        
    except Exception as e:
        print(f'❌ Tool workshop test failed: {e}')

if __name__ == "__main__":
    test_file_tools()
    print()
    test_tool_workshop_validation()
    print()
    print('🎯 File datatype implementation test complete!')

"""
Tool workshop interface for function calling and custom tools.
"""

import streamlit as st
import json
import os
import importlib.util
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from config.settings import AppSettings, save_json_config

class ToolWorkshopInterface:
    """Tool workshop interface component."""
    
    def __init__(self, settings: AppSettings):
        self.settings = settings
        self.tools_dir = Path("output/tools")
        self.code_dir = self.tools_dir / "code"
        
    def load_tool_config(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """Load tool configuration from JSON file."""
        config_file = self.tools_dir / f"{tool_name}.json"
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                st.error(f"Error loading {tool_name}.json: {e}")
        return None
    
    def save_tool_config(self, tool_name: str, config: Dict[str, Any]) -> bool:
        """Save tool configuration to JSON file."""
        try:
            self.tools_dir.mkdir(parents=True, exist_ok=True)
            config_file = self.tools_dir / f"{tool_name}.json"
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
            return True
        except Exception as e:
            st.error(f"Error saving {tool_name}.json: {e}")
            return False
    
    def load_all_tools(self) -> Dict[str, Dict[str, Any]]:
        """Load all tool configurations from the tools directory."""
        tools = {}
        if not self.tools_dir.exists():
            return tools
            
        for json_file in self.tools_dir.glob("*.json"):
            tool_name = json_file.stem
            config = self.load_tool_config(tool_name)
            if config:
                tools[tool_name] = config
        return tools
    
    def import_tool_function(self, tool_name: str) -> Optional[callable]:
        """Import and return the tool function from its Python file."""
        try:
            code_file = self.code_dir / f"{tool_name}.py"
            if not code_file.exists():
                return None
                
            spec = importlib.util.spec_from_file_location(tool_name, code_file)
            if spec is None or spec.loader is None:
                return None
                
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Try to get the function with the same name as the tool
            if hasattr(module, tool_name):
                return getattr(module, tool_name)
            
            # If not found, try to find any function in the module
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if callable(attr) and not attr_name.startswith('_'):
                    return attr
                    
        except Exception as e:
            st.error(f"Error importing {tool_name}: {e}")
        return None
    
    def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> str:
        """Execute a tool with given parameters."""
        tool_function = self.import_tool_function(tool_name)
        if not tool_function:
            return f"Error: Could not load function for {tool_name}"
            
        try:
            result = tool_function(**parameters)
            return str(result)
        except Exception as e:
            return f"Error executing {tool_name}: {e}"
    
    def toggle_tool_status(self, tool_name: str) -> bool:
        """Toggle the enabled status of a tool."""
        config = self.load_tool_config(tool_name)
        if config:
            config['enabled'] = not config.get('enabled', True)
            return self.save_tool_config(tool_name, config)
        return False
    
    def create_new_tool(self, tool_config: Dict[str, Any], code: str) -> bool:
        """Create a new tool with configuration and code."""
        tool_name = tool_config.get('name')
        if not tool_name:
            return False
            
        try:
            # Save configuration
            if not self.save_tool_config(tool_name, tool_config):
                return False
                
            # Save code
            self.code_dir.mkdir(parents=True, exist_ok=True)
            code_file = self.code_dir / f"{tool_name}.py"
            with open(code_file, 'w') as f:
                f.write(code)
                
            return True
        except Exception as e:
            st.error(f"Error creating tool {tool_name}: {e}")
            return False
    
    def render_available_tools_section(self, all_tools):
        """Render the available tools section."""
        st.markdown("## 🛠️ Available Tools")
        
        if not all_tools:
            st.info("No tools found in output/tools/ directory. Create some tools to get started!")
            return
            
        # Display loaded tools
        for tool_name, tool_config in all_tools.items():
            with st.expander(f"🔧 {tool_name}", expanded=False):
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    st.markdown(f"**Description:** {tool_config.get('description', 'No description')}")
                    st.caption(f"Category: {tool_config.get('category', 'unknown')}")
                    
                    # Show parameters
                    params = tool_config.get('parameters', [])
                    if params:
                        st.markdown("**Parameters:**")
                        for param in params:
                            required_text = " *(required)*" if param.get('required', False) else " *(optional)*"
                            param_name = param.get('name', 'unknown')
                            param_type = param.get('type', 'unknown')
                            param_desc = param.get('description', 'No description')
                            st.caption(f"• `{param_name}` ({param_type}){required_text}: {param_desc}")
                
                with col2:
                    enabled = tool_config.get('enabled', True)
                    if enabled:
                        st.success("✅ Enabled")
                    else:
                        st.warning("❌ Disabled")
                
                with col3:
                    # Toggle button (functional)
                    if st.button("Toggle", key=f"toggle_{tool_name}"):
                        if self.toggle_tool_status(tool_name):
                            st.success(f"Toggled {tool_name}")
                            st.rerun()
                        else:
                            st.error(f"Failed to toggle {tool_name}")
                    
                    # Check if code file exists
                    code_file = self.code_dir / f"{tool_name}.py"
                    if code_file.exists():
                        st.caption("✅ Code file exists")
                    else:
                        st.caption("❌ Code file missing")
    
    def render_custom_tools_section(self, all_tools):
        """Render the custom tools management section."""
        st.markdown("## 🎯 Custom Tools")
        
        tab1, tab2 = st.tabs(["📋 Manage Tools", "➕ Add New Tool"])
        
        with tab1:
            self.render_manage_tools_tab(all_tools)
        
        with tab2:
            self.render_add_tool_tab(all_tools)
    
    def render_manage_tools_tab(self, all_tools):
        """Render the manage tools tab."""
        st.markdown("### Manage Existing Tools")
        
        if all_tools:
            for tool_name, tool_config in all_tools.items():
                with st.expander(f"📝 Edit {tool_name}", expanded=False):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.json(tool_config)
                        
                    with col2:
                        if st.button("🗑️ Delete", key=f"delete_{tool_name}"):
                            try:
                                # Delete JSON config
                                config_file = self.tools_dir / f"{tool_name}.json"
                                if config_file.exists():
                                    config_file.unlink()
                                
                                # Delete Python code
                                code_file = self.code_dir / f"{tool_name}.py"
                                if code_file.exists():
                                    code_file.unlink()
                                
                                st.success(f"Deleted {tool_name}")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error deleting {tool_name}: {e}")
        else:
            st.info("No tools found. Create one in the 'Add New Tool' tab.")
    
    def render_add_tool_tab(self, all_tools):
        """Render the add new tool tab."""
        st.markdown("### 🔨 Create Custom Tool")
        
        with st.form("custom_tool_form"):
            tool_name = st.text_input(
                "Tool Name",
                placeholder="my_custom_tool",
                help="Function name (use lowercase with underscores)"
            )
            
            tool_description = st.text_area(
                "Description",
                placeholder="What does this tool do?",
                height=80
            )
            
            tool_category = st.selectbox(
                "Category",
                ["utility", "information", "analysis", "creative", "custom"]
            )
            
            # Parameters section - simplified for now, can be expanded later
            st.markdown("#### Parameters")
            
            param_name = st.text_input("Parameter Name", placeholder="input_text")
            param_type = st.selectbox("Parameter Type", ["string", "number", "integer", "boolean", "array", "object"])
            param_description = st.text_input("Parameter Description", placeholder="The input text to process")
            param_required = st.checkbox("Required Parameter", value=True)
            
            # Function code
            function_code = st.text_area(
                "Function Code (Python)",
                value=f'''"""
{tool_description or "Custom tool function."}
"""

def {tool_name or "my_custom_tool"}({param_name or "input_text"}):
    """
    {tool_description or "Process the input."}
    
    Args:
        {param_name or "input_text"}: {param_description or "The input to process"}
    
    Returns:
        str: The processed result
    """
    try:
        # Your code here
        result = f"Processed: {{{param_name or "input_text"}}}"
        return result
    except Exception as e:
        return f"Error: {{e}}"''',
                height=250,
                help="Write the Python function code"
            )
            
            submitted = st.form_submit_button("💾 Save Custom Tool")
            
            if submitted:
                if tool_name and tool_description and function_code:
                    # Validate tool name
                    if not tool_name.replace('_', '').isalnum():
                        st.error("❌ Tool name should only contain letters, numbers, and underscores")
                    elif tool_name in all_tools:
                        st.error("❌ Tool name already exists")
                    else:
                        # Create tool definition
                        new_tool_config = {
                            "name": tool_name,
                            "description": tool_description,
                            "category": tool_category,
                            "parameters": [
                                {
                                    "name": param_name,
                                    "type": param_type,
                                    "description": param_description,
                                    "required": param_required
                                }
                            ] if param_name else [],
                            "code": f"{tool_name}.py",
                            "enabled": True
                        }
                        
                        # Save the tool
                        if self.create_new_tool(new_tool_config, function_code):
                            st.success("✅ Custom tool created successfully!")
                            st.json(new_tool_config)
                            st.balloons()
                            st.rerun()
                        else:
                            st.error("❌ Failed to create tool")
                else:
                    st.error("❌ Please fill in all required fields")
    
    def render_tool_testing_section(self, all_tools):
        """Render the tool testing section."""
        st.markdown("## 🧪 Test Tools")
        
        if all_tools:
            with st.expander("🧪 Tool Tester", expanded=False):
                # Select tool to test
                tool_names = list(all_tools.keys())
                selected_tool = st.selectbox("Select Tool to Test", tool_names)
                
                if selected_tool:
                    tool_config = all_tools[selected_tool]
                    parameters = tool_config.get('parameters', [])
                    
                    # Create input fields for each parameter
                    param_values = {}
                    for param in parameters:
                        param_name = param.get('name', '')
                        param_type = param.get('type', 'string')
                        param_desc = param.get('description', '')
                        param_required = param.get('required', False)
                        
                        label = f"{param_name}"
                        if param_required:
                            label += " *"
                        
                        if param_type == "string":
                            param_values[param_name] = st.text_input(
                                label, 
                                placeholder=param_desc,
                                key=f"test_{selected_tool}_{param_name}"
                            )
                        elif param_type in ["number", "integer"]:
                            param_values[param_name] = st.number_input(
                                label,
                                value=0,
                                key=f"test_{selected_tool}_{param_name}"
                            )
                            if param_type == "integer":
                                param_values[param_name] = int(param_values[param_name])
                        elif param_type == "boolean":
                            param_values[param_name] = st.checkbox(
                                label,
                                key=f"test_{selected_tool}_{param_name}"
                            )
                        else:
                            param_values[param_name] = st.text_input(
                                label,
                                placeholder=f"Enter {param_type} value",
                                key=f"test_{selected_tool}_{param_name}"
                            )
                    
                    # Test button
                    if st.button(f"🧪 Test {selected_tool}"):
                        # Validate required parameters
                        missing_params = []
                        for param in parameters:
                            if param.get('required', False):
                                param_name = param.get('name', '')
                                if not param_values.get(param_name):
                                    missing_params.append(param_name)
                        
                        if missing_params:
                            st.error(f"❌ Missing required parameters: {', '.join(missing_params)}")
                        else:
                            # Execute the tool
                            with st.spinner(f"Testing {selected_tool}..."):
                                try:
                                    result = self.execute_tool(selected_tool, param_values)
                                    st.success("✅ Tool executed successfully!")
                                    st.text_area("Result:", value=result, height=150, disabled=True)
                                except Exception as e:
                                    st.error(f"❌ Tool execution failed: {e}")
        else:
            st.info("No tools available to test. Create some tools first!")
    
    def render_usage_statistics_section(self, all_tools):
        """Render the usage statistics section."""
        st.markdown("## 📈 Tool Usage")
        
        with st.expander("📊 Usage Statistics", expanded=False):
            # Real statistics based on available tools
            if all_tools:
                # Simple usage chart (could be extended with actual usage tracking)
                usage_data = {}
                for tool_name in all_tools.keys():
                    # Mock usage data - in real implementation, track actual usage
                    import random
                    usage_data[tool_name] = random.randint(0, 20)
                
                st.bar_chart(usage_data)
                st.caption("Simulated tool usage statistics (in real implementation, track actual usage)")
            else:
                st.info("No tools available for statistics.")
    
    def render_import_export_section(self, all_tools):
        """Render the import/export section."""
        st.markdown("## 📦 Import/Export")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Export tools configuration
            if all_tools:
                tools_config = {
                    "tools": all_tools,
                    "export_timestamp": str(st.session_state.get('export_timestamp', 'unknown'))
                }
                
                st.download_button(
                    "📤 Export Tools Config",
                    data=json.dumps(tools_config, indent=2),
                    file_name="tools_config.json",
                    mime="application/json",
                    use_container_width=True
                )
            else:
                st.info("No tools to export")
        
        with col2:
            # Import tools configuration
            uploaded_config = st.file_uploader(
                "📥 Import Tools Config",
                type=['json'],
                help="Upload a previously exported tools configuration"
            )
            
            if uploaded_config:
                try:
                    config_data = json.load(uploaded_config)
                    st.success("✅ Configuration loaded!")
                    
                    # Show preview
                    imported_tools = config_data.get('tools', {})
                    if imported_tools:
                        st.json(imported_tools)
                        
                        if st.button("📥 Apply Imported Configuration"):
                            # Import each tool
                            imported_count = 0
                            for tool_name, tool_config in imported_tools.items():
                                if self.save_tool_config(tool_name, tool_config):
                                    imported_count += 1
                                    
                                    # If there's code in the config, create a basic Python file
                                    if tool_config.get('code'):
                                        basic_code = f'''"""
{tool_config.get('description', 'Imported tool')}
"""

def {tool_name}():
    """
    {tool_config.get('description', 'Imported tool function')}
    """
    return "This is an imported tool. Please implement the actual functionality."
'''
                                        code_file = self.code_dir / f"{tool_name}.py"
                                        self.code_dir.mkdir(parents=True, exist_ok=True)
                                        with open(code_file, 'w') as f:
                                            f.write(basic_code)
                            
                            if imported_count > 0:
                                st.success(f"✅ Imported {imported_count} tools successfully!")
                                st.rerun()
                            else:
                                st.error("❌ Failed to import tools")
                    else:
                        st.warning("No tools found in the configuration file")
                        
                except Exception as e:
                    st.error(f"❌ Invalid configuration file: {e}")
    
    def render(self):
        """Render the tool workshop interface."""
        
        st.markdown("# 🔧 Tool Workshop")
        st.markdown("Manage function calling and custom tools for AI interactions.")
        
        # # Function calling configuration
        # function_calling_enabled = self.render_function_calling_section()
        
        st.markdown("---")
        
        # Load all available tools
        all_tools = self.load_all_tools()
        
        # Available tools section
        self.render_available_tools_section(all_tools)
        
        st.markdown("---")
        
        # Custom tools section
        self.render_custom_tools_section(all_tools)
        
        st.markdown("---")
        
        # Tool testing section
        self.render_tool_testing_section(all_tools)
        
        # Tool usage statistics
        st.markdown("---")
        self.render_usage_statistics_section(all_tools)
        
        # Export/Import tools
        st.markdown("---")
        self.render_import_export_section(all_tools)

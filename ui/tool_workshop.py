"""
Tool workshop interface for function calling and custom tools.
"""

import streamlit as st
import json
import os
import importlib.util
import sys
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
from config.settings import AppSettings, save_json_config
from utils.storage import StoragePaths, read_json, write_json

class ToolWorkshopInterface:
    """Tool workshop interface component."""
    
    def __init__(self, settings: AppSettings):
        self.settings = settings
        self.tools_dir = StoragePaths.ROOT_MAP["@tools"]
        self.code_dir = self.tools_dir / "code"
        
    def load_tool_config(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """Load tool configuration from JSON file."""
        data = read_json("@tools", f"{tool_name}.json")
        return data
    
    def save_tool_config(self, tool_name: str, config: Dict[str, Any]) -> bool:
        """Save tool configuration to JSON file."""
        try:
            return write_json("@tools", f"{tool_name}.json", config)
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
        start_time = time.time()
        tool_function = self.import_tool_function(tool_name)
        if not tool_function:
            error_msg = f"Error: Could not load function for {tool_name}"
            self._record_tool_history(tool_name, parameters, error_msg, False, start_time)
            return error_msg
            
        try:
            result = tool_function(**parameters)
            result_str = str(result)
            self._record_tool_history(tool_name, parameters, result_str, True, start_time)
            return result_str
        except Exception as e:
            error_msg = f"Error executing {tool_name}: {e}"
            self._record_tool_history(tool_name, parameters, error_msg, False, start_time)
            return error_msg

    def _record_tool_history(self, tool_name: str, parameters: Dict[str, Any], result: str, success: bool, start_time: float) -> None:
        """Append tool execution history to current session in memory and on disk."""
        try:
            duration = max(0.0, time.time() - start_time)
            entry = {
                "timestamp": time.time(),
                "tool_name": tool_name,
                "parameters": parameters,
                "result": result[:2000] if isinstance(result, str) else str(result),
                "execution_time": round(duration, 3),
                "success": success
            }

            # In-memory history on session state
            if "tool_history" not in st.session_state:
                st.session_state.tool_history = []
            st.session_state.tool_history.append(entry)
            # # Keep memory list bounded
            # if len(st.session_state.tool_history) > 200:
            #     st.session_state.tool_history = st.session_state.tool_history[-200:]

            # Also append to current session JSON on disk
            session_id = st.session_state.get("current_session_id")
            if session_id:
                import os
                os.makedirs("output/sessions", exist_ok=True)
                session_path = f"output/sessions/{session_id}.json"
                session_data = {}
                try:
                    if os.path.exists(session_path):
                        with open(session_path, "r", encoding="utf-8") as f:
                            session_data = json.load(f)
                except Exception:
                    session_data = {}

                history_list = session_data.get("tool_history", [])
                history_list.append(entry)
                # Bound the on-disk list too
                if len(history_list) > 500:
                    history_list = history_list[-500:]
                session_data["tool_history"] = history_list

                try:
                    with open(session_path, "w", encoding="utf-8") as f:
                        json.dump(session_data, f, indent=2, ensure_ascii=False)
                except Exception:
                    # Avoid breaking execution due to logging failure
                    pass
        except Exception:
            # Never raise from logger
            pass
    
    def _render_array_parameter_input(self, param_name: str, label: str, param_desc: str, selected_tool: str, item_type: str = 'string') -> List[Any]:
        """Render dynamic array/list parameter input interface."""
        # Initialize session state for this parameter's list items
        list_key = f"test_{selected_tool}_{param_name}_list"
        if list_key not in st.session_state:
            st.session_state[list_key] = []
        
        st.markdown(f"**{label}**")
        if param_desc:
            st.caption(param_desc)
        
        # Display current list items
        current_list = st.session_state[list_key]
        if current_list:
            st.markdown("**Current items:**")
            for i, item in enumerate(current_list):
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.text(f"{i+1}. {item}")
                with col2:
                    if st.button("🗑️", key=f"remove_{list_key}_{i}", help="Remove item"):
                        st.session_state[list_key].pop(i)
                        st.rerun()
        else:
            st.info("No items added yet")
        
        # Add new item interface
        st.markdown("**Add new item:**")
        col1, col2 = st.columns([3, 1])
        
        with col1:
            if item_type in ['string']:
                new_item = st.text_input(
                    "New item",
                    key=f"new_item_{list_key}",
                    placeholder="Enter text item",
                    label_visibility="collapsed"
                )
            elif item_type in ['number', 'integer']:
                new_item = st.number_input(
                    "New item",
                    key=f"new_item_{list_key}",
                    label_visibility="collapsed"
                )
                if item_type == 'integer':
                    new_item = int(new_item)
            elif item_type == 'boolean':
                new_item = st.checkbox(
                    "New boolean item",
                    key=f"new_item_{list_key}",
                    label_visibility="collapsed"
                )
            else:
                # Default to string input for unknown types
                new_item = st.text_input(
                    "New item",
                    key=f"new_item_{list_key}",
                    placeholder=f"Enter {item_type} item",
                    label_visibility="collapsed"
                )
        
        with col2:
            if st.button("➕ Add", key=f"add_item_{list_key}"):
                if item_type in ['string'] and new_item.strip():
                    st.session_state[list_key].append(new_item)
                    # Clear the input by triggering rerun
                    st.rerun()
                elif item_type in ['number', 'integer', 'boolean']:
                    st.session_state[list_key].append(new_item)
                    st.rerun()
                elif new_item:  # For other types, just check if not empty
                    st.session_state[list_key].append(new_item)
                    st.rerun()
                else:
                    st.error("Please enter a value")
        
        # Clear all button
        if current_list:
            if st.button("🗑️ Clear All", key=f"clear_all_{list_key}"):
                st.session_state[list_key] = []
                st.rerun()
        
        return current_list
    
    def _render_parameter_section(self, param_type: str, parameters: List[Dict[str, Any]]):
        """Render input or output parameter section."""
        section_title = "Input" if param_type == "input" else "Output"
        
        # Display existing parameters
        if parameters:
            st.markdown(f"**Current {section_title} Parameters:**")
            for i, param in enumerate(parameters):
                with st.expander(f"{section_title} {i+1}: {param.get('name', 'Unnamed')}", expanded=False):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.markdown(f"**Name:** {param.get('name', 'N/A')}")
                        param_type_display = param.get('type', 'N/A')
                        if param.get('type') == 'array' and param.get('item_type'):
                            param_type_display += f" (items: {param.get('item_type')})"
                        st.markdown(f"**Type:** {param_type_display}")
                        st.markdown(f"**Description:** {param.get('description', 'N/A')}")
                        
                        if param_type == "input":
                            st.markdown(f"**Required:** {'Yes' if param.get('required', False) else 'No'}")
                        else:
                            format_value = param.get('format', 'Not specified')
                            st.markdown(f"**Format:** {format_value}")
                    
                    with col2:
                        remove_clicked = st.form_submit_button("🗑️ Remove", key=f"remove_{param_type}_param_{i}")
                        if remove_clicked:
                            parameters.pop(i)
                            st.rerun()
        else:
            st.info(f"No {section_title.lower()} parameters added yet")
        
        # Add new parameter section
        st.markdown(f"**Add New {section_title} Parameter:**")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            new_param_name = st.text_input(
                "Parameter Name", 
                placeholder=f"{param_type}_data" if param_type == "input" else "result",
                key=f"new_{param_type}_param_name"
            )
            # Organize types by category for better UX
            type_options = [
                "--- Python Built-in Types ---",
                "str", "int", "float", "complex",      # Text and Numeric
                "list", "tuple", "range",              # Sequence
                "dict", "set", "frozenset",            # Mapping and Set  
                "bool", "bytes", "bytearray", "memoryview",  # Boolean and Binary
                "file",                                # File upload
                "NoneType",                            # None type
                "--- Legacy JSON Types ---",
                "string", "number", "integer", "boolean", "array", "object"
            ]
            
            new_param_type = st.selectbox(
                "Parameter Type", 
                type_options,
                key=f"new_{param_type}_param_type",
                help="Choose from Python built-in data types or legacy JSON-compatible types"
            )
            
            # Show item type selector for collection parameters
            new_param_item_type = None
            if new_param_type in ["array", "list", "tuple", "set", "frozenset"]:
                collection_name = new_param_type if new_param_type != "array" else "array"
                
                item_type_options = [
                    "--- Python Types ---",
                    "str", "int", "float", "complex", "bool", "bytes",
                    "--- Legacy Types ---", 
                    "string", "number", "integer", "boolean"
                ]
                
                new_param_item_type = st.selectbox(
                    f"{collection_name.title()} Item Type",
                    item_type_options,
                    key=f"new_{param_type}_param_item_type",
                    help=f"What type of items will this {collection_name} contain?"
                )
            
            new_param_description = st.text_input(
                "Parameter Description", 
                placeholder=f"The {param_type} data to process" if param_type == "input" 
                           else f"The {param_type} result from processing",
                key=f"new_{param_type}_param_description"
            )
            
            # Input-specific fields
            if param_type == "input":
                new_param_required = st.checkbox(
                    "Required Parameter", 
                    value=True,
                    key=f"new_{param_type}_param_required"
                )
            
            # Output-specific fields
            if param_type == "output":
                new_param_format = st.selectbox(
                    "Output Format",
                    ["plain_text", "json", "markdown", "xml", "csv"],
                    key=f"new_{param_type}_param_format",
                    help="Format of the output data"
                )
        
        with col2:
            add_param_clicked = st.form_submit_button(f"➕ Add {section_title}", key=f"add_{param_type}_parameter")
            clear_all_clicked = st.form_submit_button("🗑️ Clear All", key=f"clear_all_{param_type}_params")
            
            if add_param_clicked:
                if new_param_name and not new_param_type.startswith("---"):
                    # Check for duplicate parameter names within this parameter type
                    existing_names = [p.get('name', '') for p in parameters]
                    if new_param_name in existing_names:
                        st.error(f"❌ {section_title} parameter name already exists")
                    else:
                        new_param = {
                            "name": new_param_name,
                            "type": new_param_type,
                            "description": new_param_description
                        }
                        
                        # Add item_type for collection parameters
                        if new_param_type in ["array", "list", "tuple", "set", "frozenset"] and new_param_item_type and not new_param_item_type.startswith("---"):
                            new_param["item_type"] = new_param_item_type
                        
                        # Add type-specific fields
                        if param_type == "input":
                            new_param["required"] = new_param_required
                        else:
                            new_param["format"] = new_param_format
                        
                        parameters.append(new_param)
                        st.success(f"✅ Added {section_title.lower()} parameter: {new_param_name}")
                        st.rerun()
                else:
                    st.error("❌ Please enter a parameter name")
            
            if clear_all_clicked:
                parameters.clear()
                st.rerun()
    
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
    
    def validate_tool_config(self, tool_config: Dict[str, Any]) -> tuple[bool, str]:
        """Validate tool configuration with input/output parameter support."""
        required_fields = ['name', 'description', 'category']
        # Enhanced Python data type support
        valid_types = [
            'str', 'int', 'float', 'complex',  # Text and Numeric types
            'list', 'tuple', 'range',          # Sequence types  
            'dict', 'set', 'frozenset',        # Mapping and Set types
            'bool', 'bytes', 'bytearray', 'memoryview',  # Boolean and Binary types
            'file',                            # File upload type
            'NoneType',                        # None type
            # Legacy JSON-compatible aliases for backward compatibility
            'string', 'number', 'integer', 'boolean', 'array', 'object'
        ]
        valid_item_types = [
            'str', 'int', 'float', 'complex', 'bool', 'bytes',
            # Legacy aliases
            'string', 'number', 'integer', 'boolean'
        ]
        valid_output_formats = ['plain_text', 'json', 'markdown', 'xml', 'csv']
        
        for field in required_fields:
            if not tool_config.get(field):
                return False, f"Missing required field: {field}"
        
        # Validate name format
        name = tool_config.get('name', '')
        if not name.replace('_', '').isalnum():
            return False, "Tool name should only contain letters, numbers, and underscores"
        
        # Support both old 'parameters' and new 'input_parameters/output_parameters' structures
        input_parameters = tool_config.get('input_parameters', tool_config.get('parameters', []))
        output_parameters = tool_config.get('output_parameters', [])
        
        # Validate input parameters
        if input_parameters:
            validation_result = self._validate_parameter_list(
                input_parameters, 'input', valid_types, valid_item_types
            )
            if not validation_result[0]:
                return validation_result
        
        # Validate output parameters
        if output_parameters:
            validation_result = self._validate_parameter_list(
                output_parameters, 'output', valid_types, valid_item_types, valid_output_formats
            )
            if not validation_result[0]:
                return validation_result
        
        return True, "Valid"
    
    def _validate_parameter_list(self, parameters: List[Dict], param_type: str, valid_types: List[str], 
                                valid_item_types: List[str], valid_output_formats: List[str] = None) -> tuple[bool, str]:
        """Validate a list of parameters (input or output)."""
        param_names = []
        
        for i, param in enumerate(parameters):
            param_num = i + 1
            
            # Check required parameter fields
            if not param.get('name'):
                return False, f"{param_type.title()} parameter {param_num} missing name"
            if not param.get('type'):
                return False, f"{param_type.title()} parameter {param_num} missing type"
            
            param_name = param.get('name', '')
            param_type_value = param.get('type', '')
            
            # Validate parameter name format
            if not param_name.replace('_', '').isalnum():
                return False, f"{param_type.title()} parameter {param_num} name '{param_name}' should only contain letters, numbers, and underscores"
            
            # Check for duplicate parameter names
            if param_name in param_names:
                return False, f"Duplicate {param_type} parameter name: '{param_name}'"
            param_names.append(param_name)
            
            # Validate parameter type
            if param_type_value not in valid_types:
                return False, f"{param_type.title()} parameter {param_num} has invalid type '{param_type_value}'. Valid types: {', '.join(valid_types)}"
            
            # Enhanced validation for collection parameters (array, list, tuple, set, frozenset)
            if param_type_value in ['array', 'list', 'tuple', 'set', 'frozenset']:
                item_type = param.get('item_type')
                if item_type and item_type not in valid_item_types:
                    collection_name = param_type_value if param_type_value != 'array' else 'array'
                    return False, f"{param_type.title()} parameter {param_num} {collection_name} item_type '{item_type}' is invalid. Valid item types: {', '.join(valid_item_types)}"
                
                # Optional: Check for array-specific constraints
                min_items = param.get('min_items')
                max_items = param.get('max_items')
                
                if min_items is not None:
                    if not isinstance(min_items, int) or min_items < 0:
                        return False, f"{param_type.title()} parameter {param_num} min_items must be a non-negative integer"
                
                if max_items is not None:
                    if not isinstance(max_items, int) or max_items < 1:
                        return False, f"{param_type.title()} parameter {param_num} max_items must be a positive integer"
                    
                    if min_items is not None and max_items < min_items:
                        return False, f"{param_type.title()} parameter {param_num} max_items cannot be less than min_items"
            
            # Validate required field for input parameters only
            if param_type == 'input':
                required = param.get('required')
                if required is not None and not isinstance(required, bool):
                    return False, f"Input parameter {param_num} 'required' field must be boolean"
            
            # Validate format field for output parameters
            if param_type == 'output' and valid_output_formats:
                format_value = param.get('format')
                if format_value and format_value not in valid_output_formats:
                    return False, f"Output parameter {param_num} has invalid format '{format_value}'. Valid formats: {', '.join(valid_output_formats)}"
        
        return True, "Valid"
    
    def validate_tool_code(self, code: str, tool_name: str) -> tuple[bool, str]:
        """Validate tool code."""
        if not code.strip():
            return False, "Code cannot be empty"
        
        # Check if function exists
        if f"def {tool_name}(" not in code:
            return False, f"Code must contain function definition: def {tool_name}("
        
        # Basic syntax check (can be enhanced)
        try:
            compile(code, f"<{tool_name}>", "exec")
            return True, "Valid"
        except SyntaxError as e:
            return False, f"Syntax error: {e}"
        except Exception as e:
            return False, f"Code validation error: {e}"
    
    def render_available_tools_section(self, all_tools):
        """Render the available tools section."""
        st.markdown("### 🛠️ Available Tools")
        
        if not all_tools:
            st.info("No tools found in output/tools/ directory. Create some tools to get started!")
            return
            
        # Display loaded tools
        for tool_name, tool_config in all_tools.items():
            with st.expander(f"🔧 {tool_name}", expanded=False):
                col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                
                with col1:
                    st.markdown(f"**Description:** {tool_config.get('description', 'No description')}")
                    st.caption(f"Category: {tool_config.get('category', 'unknown')}")
                    
                    # Show parameters - support both old and new structures
                    input_params = tool_config.get('input_parameters', tool_config.get('parameters', []))
                    output_params = tool_config.get('output_parameters', [])
                    
                    if input_params:
                        st.markdown("**📥 Input Parameters:**")
                        for param in input_params:
                            required_text = " *(required)*" if param.get('required', False) else " *(optional)*"
                            param_name = param.get('name', 'unknown')
                            param_type = param.get('type', 'unknown')
                            param_desc = param.get('description', 'No description')
                            
                            # Enhanced type display for collections
                            if param_type in ['array', 'list', 'tuple', 'set', 'frozenset'] and param.get('item_type'):
                                param_type_display = f"{param_type}[{param.get('item_type')}]"
                            else:
                                param_type_display = param_type
                                
                            st.caption(f"• `{param_name}` ({param_type_display}){required_text}: {param_desc}")
                    
                    if output_params:
                        st.markdown("**📤 Output Parameters:**")
                        for param in output_params:
                            param_name = param.get('name', 'unknown')
                            param_type = param.get('type', 'unknown')
                            param_desc = param.get('description', 'No description')
                            format_info = param.get('format', 'plain_text')
                            
                            # Enhanced type display for collections
                            if param_type in ['array', 'list', 'tuple', 'set', 'frozenset'] and param.get('item_type'):
                                param_type_display = f"{param_type}[{param.get('item_type')}]"
                            else:
                                param_type_display = param_type
                                
                            st.caption(f"• `{param_name}` ({param_type_display}, {format_info}): {param_desc}")
                    
                    if not input_params and not output_params:
                        st.caption("No parameters defined")

                    # Quick execute form
                    st.markdown("---")
                    st.markdown("**⚡ Quick Execute**")
                    with st.form(f"quick_exec_{tool_name}"):
                        param_values = {}
                        for param in input_params:
                            pname = param.get('name', '')
                            ptype = param.get('type', 'string')
                            pdesc = param.get('description', '')
                            preq = param.get('required', False)
                            label = f"{pname}{' *' if preq else ''}"

                            if ptype in ["string", "str"]:
                                param_values[pname] = st.text_input(label, placeholder=pdesc, key=f"qe_{tool_name}_{pname}")
                            elif ptype in ["number", "float"]:
                                param_values[pname] = st.number_input(label, key=f"qe_{tool_name}_{pname}")
                            elif ptype in ["integer", "int"]:
                                v = st.number_input(label, step=1, key=f"qe_{tool_name}_{pname}")
                                param_values[pname] = int(v)
                            elif ptype in ["boolean", "bool"]:
                                param_values[pname] = st.checkbox(label, key=f"qe_{tool_name}_{pname}")
                            elif ptype in ["array", "list", "tuple", "set", "frozenset"]:
                                raw = st.text_area(
                                    label + " (JSON array)",
                                    placeholder=pdesc or "[1,2,3] or [\"a\",\"b\"]",
                                    key=f"qe_{tool_name}_{pname}"
                                )
                                try:
                                    arr = json.loads(raw) if raw.strip() else []
                                    if not isinstance(arr, list):
                                        arr = []
                                except Exception:
                                    arr = []
                                    st.warning(f"Invalid JSON for {pname}; using empty list")
                                if ptype == "tuple":
                                    param_values[pname] = tuple(arr)
                                elif ptype == "set":
                                    param_values[pname] = set(arr)
                                elif ptype == "frozenset":
                                    param_values[pname] = frozenset(arr)
                                else:
                                    param_values[pname] = list(arr)
                            elif ptype == "range":
                                c1, c2, c3 = st.columns(3)
                                with c1:
                                    start = st.number_input(f"{label} - Start", value=0, step=1, key=f"qe_{tool_name}_{pname}_start")
                                with c2:
                                    stop = st.number_input(f"{label} - Stop", value=10, step=1, key=f"qe_{tool_name}_{pname}_stop")
                                with c3:
                                    step = st.number_input(f"{label} - Step", value=1, step=1, key=f"qe_{tool_name}_{pname}_step")
                                param_values[pname] = range(int(start), int(stop), int(step))
                            elif ptype in ["object", "dict"]:
                                raw = st.text_area(label, placeholder=pdesc or '{"key":"value"}', key=f"qe_{tool_name}_{pname}")
                                try:
                                    param_values[pname] = json.loads(raw) if raw.strip() else {}
                                except Exception:
                                    param_values[pname] = {}
                                    st.warning(f"Invalid JSON for {pname}; using empty object")
                            elif ptype in ["bytes", "bytearray"]:
                                txt = st.text_input(label, placeholder=pdesc, key=f"qe_{tool_name}_{pname}")
                                param_values[pname] = (txt.encode('utf-8') if ptype == 'bytes' else bytearray(txt.encode('utf-8'))) if txt else (b'' if ptype == 'bytes' else bytearray())
                            elif ptype == "memoryview":
                                txt = st.text_input(label, placeholder=pdesc, key=f"qe_{tool_name}_{pname}")
                                param_values[pname] = memoryview(txt.encode('utf-8')) if txt else memoryview(b'')
                            elif ptype == "file":
                                up = st.file_uploader(label, key=f"qe_{tool_name}_{pname}")
                                if up is not None:
                                    content = up.read()
                                    param_values[pname] = {"name": up.name, "content": content, "type": up.type, "size": len(content)}
                                else:
                                    param_values[pname] = None
                            elif ptype == "NoneType":
                                st.info(f"{label}: This parameter will be set to None")
                                param_values[pname] = None
                            else:
                                param_values[pname] = st.text_input(label, placeholder=f"Enter {ptype} value", key=f"qe_{tool_name}_{pname}")

                        run_clicked = st.form_submit_button("▶️ Execute", type="primary")

                    if run_clicked:
                        # Validate requireds
                        missing = [p.get('name','') for p in input_params if p.get('required', False) and not param_values.get(p.get('name',''))]
                        if missing:
                            st.error(f"Missing required: {', '.join(missing)}")
                        else:
                            with st.spinner(f"Running {tool_name}..."):
                                result = self.execute_tool(tool_name, param_values)
                                # Try parse JSON
                                try:
                                    parsed = json.loads(result)
                                    st.json(parsed)
                                except Exception:
                                    st.text_area("Result", value=result, height=150, disabled=True)
                
                with col2:
                    enabled = tool_config.get('enabled', True)
                    if enabled:
                        st.success("✅ Enabled")
                    else:
                        st.warning("❌ Disabled")
                    
                    # Toggle button
                    if st.button("Toggle", key=f"toggle_{tool_name}"):
                        if self.toggle_tool_status(tool_name):
                            st.success(f"Toggled {tool_name}")
                            st.rerun()
                        else:
                            st.error(f"Failed to toggle {tool_name}")
                
                with col3:
                    # Check if code file exists
                    code_file = self.code_dir / f"{tool_name}.py"
                    if code_file.exists():
                        st.caption("✅ Code exists")
                    else:
                        st.caption("❌ Code missing")
                    
                    # Edit buttons
                    if st.button("📝 Edit Config", key=f"edit_config_{tool_name}"):
                        st.session_state[f"editing_config_{tool_name}"] = True
                        st.rerun()
                    
                    if st.button("🐍 Edit Code", key=f"edit_code_{tool_name}"):
                        st.session_state[f"editing_code_{tool_name}"] = True
                        st.rerun()
                
                with col4:
                    # Delete button with confirmation
                    if st.button("🗑️ Delete", key=f"delete_{tool_name}"):
                        st.session_state[f"confirm_delete_{tool_name}"] = True
                        st.rerun()
                
                # Handle editing states
                if st.session_state.get(f"editing_config_{tool_name}", False):
                    self.render_edit_config_interface(tool_name, tool_config)
                
                if st.session_state.get(f"editing_code_{tool_name}", False):
                    self.render_edit_code_interface(tool_name)
                
                if st.session_state.get(f"confirm_delete_{tool_name}", False):
                    self.render_delete_confirmation(tool_name)
    
    def render_edit_config_interface(self, tool_name, tool_config):
        """Render the edit configuration interface."""
        st.markdown("---")
        st.markdown(f"### 📝 Editing Configuration: {tool_name}")
        
        with st.form(f"edit_config_form_{tool_name}"):
            col1, col2 = st.columns(2)
            
            with col1:
                new_name = st.text_input(
                    "Tool Name",
                    value=tool_config.get('name', tool_name),
                    key=f"edit_name_{tool_name}"
                )
                
                new_description = st.text_area(
                    "Description",
                    value=tool_config.get('description', ''),
                    height=80,
                    key=f"edit_desc_{tool_name}"
                )
                
                new_category = st.selectbox(
                    "Category",
                    ["utility", "information", "analysis", "creative", "custom"],
                    index=["utility", "information", "analysis", "creative", "custom"].index(
                        tool_config.get('category', 'utility')
                    ),
                    key=f"edit_category_{tool_name}"
                )
            
            with col2:
                new_enabled = st.checkbox(
                    "Enabled",
                    value=tool_config.get('enabled', True),
                    key=f"edit_enabled_{tool_name}"
                )
                
                # Parameters editing
                st.markdown("**Parameters:**")
                params = tool_config.get('parameters', [])
                
                if params:
                    for i, param in enumerate(params):
                        with st.expander(f"Parameter {i+1}: {param.get('name', 'unknown')}", expanded=False):
                            col1, col2 = st.columns([3, 1])
                            
                            with col1:
                                st.markdown(f"**Name:** {param.get('name', 'N/A')}")
                                st.markdown(f"**Type:** {param.get('type', 'N/A')}")
                                st.markdown(f"**Description:** {param.get('description', 'N/A')}")
                                st.markdown(f"**Required:** {'Yes' if param.get('required', False) else 'No'}")
                            
                            with col2:
                                st.caption("Parameter editing not yet implemented")
                                st.caption("Delete and recreate tool to modify parameters")
                else:
                    st.info("No parameters defined for this tool")
            
            col1, col2, _ = st.columns(3)
            
            with col1:
                if st.form_submit_button("💾 Save Changes", type="primary"):
                    # Update configuration
                    updated_config = {
                        "name": new_name,
                        "description": new_description,
                        "category": new_category,
                        "enabled": new_enabled,
                        "parameters": params,  # Keep existing parameters for now
                        "code": f"{new_name}.py"
                    }
                    
                    if self.save_tool_config(new_name, updated_config):
                        # If name changed, delete old file
                        if new_name != tool_name:
                            old_config_file = self.tools_dir / f"{tool_name}.json"
                            if old_config_file.exists():
                                old_config_file.unlink()
                        
                        st.success("✅ Configuration updated!")
                        st.session_state[f"editing_config_{tool_name}"] = False
                        st.rerun()
                    else:
                        st.error("❌ Failed to save configuration")
            
            with col2:
                if st.form_submit_button("❌ Cancel"):
                    st.session_state[f"editing_config_{tool_name}"] = False
                    st.rerun()
    
    def render_edit_code_interface(self, tool_name):
        """Render the edit code interface."""
        st.markdown("---")
        st.markdown(f"### 🐍 Editing Code: {tool_name}")
        
        # Load current code
        code_file = self.code_dir / f"{tool_name}.py"
        current_code = ""
        
        if code_file.exists():
            try:
                with open(code_file, 'r', encoding='utf-8') as f:
                    current_code = f.read()
            except Exception as e:
                st.error(f"Error reading code file: {e}")
        else:
            current_code = f'''"""
{tool_name} function implementation.
"""

def {tool_name}():
    """
    {tool_name} function.
    """
    return "Function not implemented yet."
'''
        
        with st.form(f"edit_code_form_{tool_name}"):
            new_code = st.text_area(
                "Python Code",
                value=current_code,
                height=400,
                key=f"edit_code_content_{tool_name}",
                help="Edit the Python function code"
            )
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.form_submit_button("💾 Save Code", type="primary"):
                    # Validate code before saving
                    is_valid, message = self.validate_tool_code(new_code, tool_name)
                    
                    if is_valid:
                        try:
                            # Save the code
                            self.code_dir.mkdir(parents=True, exist_ok=True)
                            with open(code_file, 'w', encoding='utf-8') as f:
                                f.write(new_code)
                            
                            st.success("✅ Code updated successfully!")
                            st.session_state[f"editing_code_{tool_name}"] = False
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Failed to save code: {e}")
                    else:
                        st.error(f"❌ Code validation failed: {message}")
            
            with col2:
                if st.form_submit_button("🧪 Test Code"):
                    # Validate and test code
                    is_valid, message = self.validate_tool_code(new_code, tool_name)
                    
                    if is_valid:
                        try:
                            # Try to compile and execute a basic test
                            compile(new_code, f"<{tool_name}>", "exec")
                            st.success("✅ Code syntax is valid!")
                            
                            # Try to import the function (basic test)
                            import tempfile
                            import sys
                            
                            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_file:
                                temp_file.write(new_code)
                                temp_file.flush()
                                
                                spec = importlib.util.spec_from_file_location(tool_name, temp_file.name)
                                if spec and spec.loader:
                                    module = importlib.util.module_from_spec(spec)
                                    spec.loader.exec_module(module)
                                    
                                    if hasattr(module, tool_name):
                                        st.success("✅ Function can be imported successfully!")
                                    else:
                                        st.warning("⚠️ Function defined but not found in module")
                                
                                # Clean up
                                import os
                                os.unlink(temp_file.name)
                                
                        except Exception as e:
                            st.error(f"❌ Code test failed: {e}")
                    else:
                        st.error(f"❌ Code validation failed: {message}")
            
            with col3:
                if st.form_submit_button("❌ Cancel"):
                    st.session_state[f"editing_code_{tool_name}"] = False
                    st.rerun()
    
    def render_delete_confirmation(self, tool_name):
        """Render delete confirmation dialog."""
        st.markdown("---")
        st.markdown(f"### 🗑️ Delete Tool: {tool_name}")
        
        st.warning(f"⚠️ Are you sure you want to delete '{tool_name}'? This action cannot be undone.")
        
        col1, col2, _ = st.columns(3)
        
        with col1:
            if st.button("✅ Yes, Delete", key=f"confirm_delete_yes_{tool_name}", type="primary"):
                try:
                    # Delete JSON config
                    config_file = self.tools_dir / f"{tool_name}.json"
                    if config_file.exists():
                        config_file.unlink()
                    
                    # Delete Python code
                    code_file = self.code_dir / f"{tool_name}.py"
                    if code_file.exists():
                        code_file.unlink()
                    
                    st.success(f"✅ Deleted {tool_name}")
                    st.session_state[f"confirm_delete_{tool_name}"] = False
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error deleting {tool_name}: {e}")
        
        with col2:
            if st.button("❌ Cancel", key=f"confirm_delete_no_{tool_name}"):
                st.session_state[f"confirm_delete_{tool_name}"] = False
                st.rerun()
    
    def render_custom_tools_section(self, all_tools):
        """Render the custom tools management section."""
        st.markdown("### ➕ Add New Tool")
        
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
            
            # Parameters section - Input/Output parameters support
            st.markdown("#### Parameters")
            
            # Initialize parameter lists in session state
            if 'tool_input_parameters' not in st.session_state:
                st.session_state.tool_input_parameters = []
            if 'tool_output_parameters' not in st.session_state:
                st.session_state.tool_output_parameters = []
            
            # Create tabs for input and output parameters
            input_tab, output_tab = st.tabs(["📥 Input Parameters", "📤 Output Parameters"])
            
            with input_tab:
                self._render_parameter_section("input", st.session_state.tool_input_parameters)
            
            with output_tab:
                self._render_parameter_section("output", st.session_state.tool_output_parameters)
            
            # Function code generation
            def generate_function_code(tool_name, tool_description, input_parameters, output_parameters):
                """Generate function code based on input and output parameters."""
                if not input_parameters:
                    return f'''"""
{tool_description or "Custom tool function."}
"""

def {tool_name or "my_custom_tool"}():
    """
    {tool_description or "Process the input."}
    
    Returns:
        str: The processed result
    """
    try:
        # Your code here
        result = "Function executed successfully"
        return result
    except Exception as e:
        return f"Error: {{e}}"'''
                
                # Generate parameter list
                param_list = []
                args_doc = []
                
                for param in input_parameters:
                    param_name = param.get('name', 'param')
                    param_type = param.get('type', 'string')
                    param_desc = param.get('description', 'Parameter')
                    param_required = param.get('required', True)
                    item_type = param.get('item_type', 'string')
                    
                    # Enhanced type hints for all Python data types
                    if param_type in ['array', 'list', 'tuple', 'set', 'frozenset']:
                        # Map item types to Python type hints
                        item_type_hint_map = {
                            'string': 'str', 'str': 'str',
                            'number': 'float', 'float': 'float', 
                            'integer': 'int', 'int': 'int',
                            'boolean': 'bool', 'bool': 'bool',
                            'complex': 'complex', 'bytes': 'bytes'
                        }
                        item_type_hint = item_type_hint_map.get(item_type, 'str')
                        
                        # Generate proper collection type hints
                        if param_type == 'array':
                            type_hint = f"List[{item_type_hint}]"
                        elif param_type == 'list':
                            type_hint = f"List[{item_type_hint}]"
                        elif param_type == 'tuple':
                            type_hint = f"Tuple[{item_type_hint}, ...]"
                        elif param_type == 'set':
                            type_hint = f"Set[{item_type_hint}]"
                        elif param_type == 'frozenset':
                            type_hint = f"FrozenSet[{item_type_hint}]"
                    else:
                        # Map all Python data types to proper type hints
                        type_hint_map = {
                            # Legacy JSON types
                            'string': 'str', 'number': 'float', 'integer': 'int', 
                            'boolean': 'bool', 'object': 'Dict[str, Any]',
                            # Python built-in types
                            'str': 'str', 'int': 'int', 'float': 'float', 'complex': 'complex',
                            'bool': 'bool', 'dict': 'Dict[str, Any]', 'range': 'range',
                            'bytes': 'bytes', 'bytearray': 'bytearray', 'memoryview': 'memoryview',
                            'file': 'Dict[str, Any]',  # File objects as dictionary
                            'NoneType': 'None'
                        }
                        type_hint = type_hint_map.get(param_type, 'str')
                    
                    if not param_required:
                        # Provide appropriate default values for optional parameters
                        if param_type in ['array', 'list']:
                            param_list.append(f"{param_name}: {type_hint} = None")
                        elif param_type == 'tuple':
                            param_list.append(f"{param_name}: {type_hint} = None")
                        elif param_type in ['set', 'frozenset']:
                            param_list.append(f"{param_name}: {type_hint} = None")
                        elif param_type in ['dict', 'object']:
                            param_list.append(f"{param_name}: {type_hint} = None")
                        elif param_type == 'range':
                            param_list.append(f"{param_name}: {type_hint} = None")
                        elif param_type in ['str', 'string']:
                            param_list.append(f"{param_name}: {type_hint} = None")
                        elif param_type in ['int', 'integer']:
                            param_list.append(f"{param_name}: {type_hint} = None")
                        elif param_type in ['float', 'number']:
                            param_list.append(f"{param_name}: {type_hint} = None")
                        elif param_type == 'complex':
                            param_list.append(f"{param_name}: {type_hint} = None")
                        elif param_type in ['bool', 'boolean']:
                            param_list.append(f"{param_name}: {type_hint} = None")
                        elif param_type in ['bytes', 'bytearray', 'memoryview']:
                            param_list.append(f"{param_name}: {type_hint} = None")
                        elif param_type == 'file':
                            param_list.append(f"{param_name}: {type_hint} = None")
                        elif param_type == 'NoneType':
                            param_list.append(f"{param_name}: {type_hint} = None")
                        else:
                            param_list.append(f"{param_name}: {type_hint} = None")
                    else:
                        param_list.append(f"{param_name}: {type_hint}")
                    
                    # Enhanced documentation for collection parameters
                    if param_type in ['array', 'list', 'tuple', 'set', 'frozenset']:
                        collection_name = param_type if param_type != 'array' else 'list'
                        args_doc.append(f"        {param_name}: {param_desc} ({collection_name} of {item_type} items)")
                    elif param_type == 'range':
                        args_doc.append(f"        {param_name}: {param_desc} (range object)")
                    elif param_type in ['bytes', 'bytearray', 'memoryview']:
                        args_doc.append(f"        {param_name}: {param_desc} ({param_type} object)")
                    elif param_type == 'complex':
                        args_doc.append(f"        {param_name}: {param_desc} (complex number)")
                    elif param_type == 'file':
                        args_doc.append(f"        {param_name}: {param_desc} (uploaded file object with name, content, type, size)")
                    else:
                        args_doc.append(f"        {param_name}: {param_desc}")
                
                param_string = ", ".join(param_list)
                args_doc_string = "\n".join(args_doc)
                
                # Generate enhanced examples with list-specific logic
                example_params = []
                list_processing_examples = []
                
                for param in input_parameters:
                    param_name = param.get('name', 'param')
                    param_type = param.get('type', 'string')
                    item_type = param.get('item_type', 'string')
                    
                    if param_type == 'array':
                        # Generate list processing example
                        if item_type == 'string':
                            list_processing_examples.append(f"        # Process {param_name} list")
                            list_processing_examples.append(f"        if {param_name}:")
                            list_processing_examples.append(f"            processed_{param_name} = [item.strip().upper() for item in {param_name}]")
                            list_processing_examples.append(f"            result += f\"Processed {{len({param_name})}} items: {{', '.join(processed_{param_name})}}\"")
                        elif item_type in ['number', 'integer']:
                            list_processing_examples.append(f"        # Process {param_name} list")
                            list_processing_examples.append(f"        if {param_name}:")
                            list_processing_examples.append(f"            total = sum({param_name})")
                            list_processing_examples.append(f"            avg = total / len({param_name}) if {param_name} else 0")
                            list_processing_examples.append("            result += f\"Sum: {total}, Average: {avg:.2f}\"")
                        else:
                            list_processing_examples.append(f"        # Process {param_name} list")
                            list_processing_examples.append(f"        if {param_name}:")
                            list_processing_examples.append(f"            result += f\"Processing {{len({param_name})}} {item_type} items\"")
                        
                        if param.get('required', True):
                            example_params.append(f"len({param_name})")
                        else:
                            example_params.append(f"len({param_name}) if {param_name} else 0")
                    elif param_type == 'file':
                        # Generate file processing example
                        list_processing_examples.append(f"        # Process {param_name} file")
                        list_processing_examples.append(f"        if {param_name}:")
                        list_processing_examples.append(f"            file_name = {param_name}.get('name', 'unknown')")
                        list_processing_examples.append(f"            file_size = {param_name}.get('size', 0)")
                        list_processing_examples.append(f"            file_type = {param_name}.get('type', 'unknown')")
                        list_processing_examples.append(f"            file_content = {param_name}.get('content', b'')")
                        list_processing_examples.append(f"            result += f\"File: {{file_name}} ({{file_size}} bytes, {{file_type}})\"")
                        
                        if param.get('required', True):
                            example_params.append(f"{param_name}.get('name', 'no_file') if {param_name} else 'no_file'")
                        else:
                            example_params.append(f"{param_name}.get('name', 'no_file') if {param_name} else 'no_file'")
                    else:
                        if param.get('required', True):
                            example_params.append(f"{param_name}")
                        else:
                            example_params.append(f"{param_name} if {param_name} else 'default'")
                
                example_usage = ", ".join(example_params)
                list_processing_code = "\n".join(list_processing_examples) if list_processing_examples else "        # Your processing logic here"
                
                # Generate output documentation
                output_doc_lines = []
                if output_parameters:
                    for param in output_parameters:
                        param_name = param.get('name', 'result')
                        param_type = param.get('type', 'string')
                        param_desc = param.get('description', 'Processing result')
                        format_info = f" ({param.get('format', 'plain_text')} format)" if param.get('format') else ""
                        
                        if param_type == 'array' and param.get('item_type'):
                            param_type += f"[{param.get('item_type')}]"
                        
                        output_doc_lines.append(f"        {param_name} ({param_type}): {param_desc}{format_info}")
                
                output_doc_string = "\n".join(output_doc_lines) if output_doc_lines else "        str: The processed result"
                
                # Add imports for type hints based on parameter types
                needed_imports = set()
                for param in input_parameters:
                    param_type = param.get('type', 'string')
                    if param_type in ['array', 'list']:
                        needed_imports.add('List')
                    elif param_type == 'tuple':
                        needed_imports.add('Tuple')
                    elif param_type == 'set':
                        needed_imports.add('Set')
                    elif param_type == 'frozenset':
                        needed_imports.add('FrozenSet')
                    elif param_type in ['dict', 'object']:
                        needed_imports.update(['Dict', 'Any'])
                    elif param_type == 'file':
                        needed_imports.update(['Dict', 'Any'])
                
                imports = ""
                if needed_imports:
                    imports = f"from typing import {', '.join(sorted(needed_imports))}\n\n"
                
                return f'''{imports}"""
{tool_description or "Custom tool function."}
"""

def {tool_name or "my_custom_tool"}({param_string}):
    """
    {tool_description or "Process the input."}
    
    Args:
{args_doc_string}
    
    Returns:
{output_doc_string}
    """
    try:
        result = ""
        
{list_processing_code}
        
        # Return the final result
        if not result:
            result = f"Function executed successfully with parameters: {example_usage}"
        
        return result
    except Exception as e:
        return f"Error: {{e}}"'''
            
            # Generate function code using both input and output parameters
            generated_code = generate_function_code(
                tool_name, 
                tool_description, 
                st.session_state.tool_input_parameters,
                st.session_state.tool_output_parameters
            )
            
            # Code generation controls
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown("**Function Code:**")
            
            with col2:
                regenerate_clicked = st.form_submit_button("🔄 Regenerate Code", key="regenerate_code")
                if regenerate_clicked:
                    st.rerun()
            
            function_code = st.text_area(
                "Function Code (Python)",
                value=generated_code,
                height=300,
                help="Write the Python function code. The code above is auto-generated based on your parameters."
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
                        # Create tool definition with input/output parameters
                        new_tool_config = {
                            "name": tool_name,
                            "description": tool_description,
                            "category": tool_category,
                            "input_parameters": st.session_state.tool_input_parameters.copy(),
                            "output_parameters": st.session_state.tool_output_parameters.copy(),
                            "code": f"{tool_name}.py",
                            "enabled": True
                        }
                        
                        # Save the tool
                        if self.create_new_tool(new_tool_config, function_code):
                            st.success("✅ Custom tool created successfully!")
                            st.json(new_tool_config)
                            st.balloons()
                            # Clear parameters after successful creation
                            st.session_state.tool_input_parameters = []
                            st.session_state.tool_output_parameters = []
                            st.rerun()
                        else:
                            st.error("❌ Failed to create tool")
                else:
                    st.error("❌ Please fill in all required fields")
    
    def render_tool_testing_section(self, all_tools):
        """Render the tool testing section."""
        st.markdown("### 🧪 Test Tools")
        
        if all_tools:
            with st.expander("🧪 Tool Tester", expanded=False):
                # Select tool to test
                tool_names = list(all_tools.keys())
                selected_tool = st.selectbox("Select Tool to Test", tool_names)
                
                if selected_tool:
                    tool_config = all_tools[selected_tool]
                    # Support both old 'parameters' and new 'input_parameters' structures
                    input_parameters = tool_config.get('input_parameters', tool_config.get('parameters', []))
                    output_parameters = tool_config.get('output_parameters', [])
                    
                    # Display output parameter information if available
                    if output_parameters:
                        st.markdown("### 📤 Expected Output")
                        with st.expander("Output Parameters", expanded=False):
                            for param in output_parameters:
                                param_name = param.get('name', 'result')
                                param_type = param.get('type', 'string')
                                param_desc = param.get('description', 'Processing result')
                                format_info = param.get('format', 'plain_text')
                                
                                type_display = param_type
                                if param_type == 'array' and param.get('item_type'):
                                    type_display += f"[{param.get('item_type')}]"
                                
                                st.markdown(f"**{param_name}** ({type_display}, {format_info} format): {param_desc}")
                    
                    st.markdown("### 📥 Input Parameters")
                    with st.form(f"test_tool_form_{selected_tool}"):
                        # Create input fields for each parameter
                        param_values = {}
                        for param in input_parameters:
                            param_name = param.get('name', '')
                            param_type = param.get('type', 'string')
                            param_desc = param.get('description', '')
                            param_required = param.get('required', False)
                            
                            label = f"{param_name}"
                            if param_required:
                                label += " *"
                            
                            # Handle Python built-in data types
                            if param_type in ["string", "str"]:
                                param_values[param_name] = st.text_input(
                                    label, 
                                    placeholder=param_desc,
                                    key=f"test_{selected_tool}_{param_name}"
                                )
                            elif param_type in ["number", "integer", "int", "float"]:
                                if param_type in ["integer", "int"]:
                                    param_values[param_name] = st.number_input(
                                        label,
                                        value=0,
                                        step=1,
                                    key=f"test_{selected_tool}_{param_name}"
                                )
                                    param_values[param_name] = int(param_values[param_name])
                                else:  # number, float
                                    param_values[param_name] = st.number_input(
                                        label,
                                        value=0.0,
                                        key=f"test_{selected_tool}_{param_name}"
                                    )
                            elif param_type == "complex":
                                complex_input = st.text_input(
                                    label,
                                    placeholder="1+2j",
                                    key=f"test_{selected_tool}_{param_name}",
                                    help="Enter complex number (e.g., 1+2j)"
                                )
                                try:
                                    param_values[param_name] = complex(complex_input) if complex_input else 0j
                                except ValueError:
                                    st.error(f"Invalid complex number for '{param_name}'")
                                    param_values[param_name] = 0j
                            elif param_type in ["boolean", "bool"]:
                                param_values[param_name] = st.checkbox(
                                    label,
                                    key=f"test_{selected_tool}_{param_name}"
                                )
                            elif param_type in ["array", "list", "tuple", "set", "frozenset"]:
                                # Advanced collection parameter handler
                                collection_data = self._render_array_parameter_input(
                                    param_name, label, param_desc, selected_tool, param.get('item_type', 'string')
                                )
                                # Convert to appropriate Python type
                                if param_type == "tuple":
                                    param_values[param_name] = tuple(collection_data)
                                elif param_type == "set":
                                    param_values[param_name] = set(collection_data)
                                elif param_type == "frozenset":
                                    param_values[param_name] = frozenset(collection_data)
                                else:  # array, list
                                    param_values[param_name] = list(collection_data)
                            elif param_type == "range":
                                col1, col2, col3 = st.columns(3)
                                with col1:
                                    start = st.number_input(f"{label} - Start", value=0, step=1, key=f"test_{selected_tool}_{param_name}_start")
                                with col2:
                                    stop = st.number_input(f"{label} - Stop", value=10, step=1, key=f"test_{selected_tool}_{param_name}_stop")
                                with col3:
                                    step = st.number_input(f"{label} - Step", value=1, step=1, key=f"test_{selected_tool}_{param_name}_step")
                                param_values[param_name] = range(int(start), int(stop), int(step))
                            elif param_type in ["object", "dict"]:
                                # JSON object parameter handler
                                try:
                                    json_input = st.text_area(
                                        label,
                                        placeholder='{"key": "value"}',
                                        key=f"test_{selected_tool}_{param_name}",
                                        help="Enter valid JSON object"
                                    )
                                    if json_input.strip():
                                        param_values[param_name] = json.loads(json_input)
                                    else:
                                        param_values[param_name] = {}
                                except json.JSONDecodeError:
                                    st.error(f"Invalid JSON for parameter '{param_name}'")
                                    param_values[param_name] = {}
                            elif param_type in ["bytes", "bytearray"]:
                                bytes_input = st.text_input(
                                    label,
                                    placeholder="Hello World",
                                    key=f"test_{selected_tool}_{param_name}",
                                    help="Enter text to convert to bytes"
                                )
                                if param_type == "bytes":
                                    param_values[param_name] = bytes_input.encode('utf-8') if bytes_input else b''
                                else:  # bytearray
                                    param_values[param_name] = bytearray(bytes_input.encode('utf-8')) if bytes_input else bytearray()
                            elif param_type == "memoryview":
                                bytes_input = st.text_input(
                                    label,
                                    placeholder="Hello World",
                                    key=f"test_{selected_tool}_{param_name}",
                                    help="Enter text to create memoryview"
                                )
                                param_values[param_name] = memoryview(bytes_input.encode('utf-8')) if bytes_input else memoryview(b'')
                            elif param_type == "file":
                                # File upload parameter handler
                                uploaded_file = st.file_uploader(
                                    label,
                                    key=f"test_{selected_tool}_{param_name}",
                                    help="Upload a file from your local system"
                                )
                                if uploaded_file is not None:
                                    # Read file content once
                                    file_content = uploaded_file.read()
                                    # Create a file-like object with necessary attributes
                                    param_values[param_name] = {
                                        'name': uploaded_file.name,
                                        'content': file_content,
                                        'type': uploaded_file.type,
                                        'size': len(file_content)
                                    }
                                    # Show file info
                                    st.info(f"📁 Uploaded: {uploaded_file.name} ({len(file_content)} bytes)")
                                else:
                                    param_values[param_name] = None
                            elif param_type == "NoneType":
                                st.info(f"{label}: This parameter will be set to None")
                                param_values[param_name] = None
                            else:
                                # Fallback for unknown types
                                param_values[param_name] = st.text_input(
                                    label,
                                    placeholder=f"Enter {param_type} value",
                                    key=f"test_{selected_tool}_{param_name}"
                                )
                        
                        # Test button
                        test_clicked = st.form_submit_button(f"🧪 Test {selected_tool}", type="primary")
                        
                        if test_clicked:
                            # Validate required parameters
                            missing_params = []
                            for param in input_parameters:
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
        st.markdown("### 📈 Tool Usage")
        
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
        st.markdown("### 📦 Import/Export")
        
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
        
        # Load all available tools
        all_tools = self.load_all_tools()
        
        # Create tabs
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "🛠️ Available Tools", 
            "➕ Add New Tool", 
            "🧪 Test Tools", 
            "📈 Tool Usage", 
            "📦 Import/Export"
        ])
        
        with tab1:
            self.render_available_tools_section(all_tools)
        
        with tab2:
            self.render_custom_tools_section(all_tools)
        
        with tab3:
            self.render_tool_testing_section(all_tools)
        
        with tab4:
            self.render_usage_statistics_section(all_tools)
        
        with tab5:
            self.render_import_export_section(all_tools)

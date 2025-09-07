"""
Model configuration interface for the GenAI Agent.
"""

import streamlit as st
import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from config.settings import AppSettings, save_json_config
from utils.storage import StoragePaths, read_json, write_json

class ModelConfigInterface:
    """Model configuration interface component."""
    
    def __init__(self, settings: AppSettings):
        self.settings = settings
        self.templates_dir = StoragePaths.ROOT_MAP["@templates"]
        
    def load_template(self, template_name: str) -> Optional[Dict[str, Any]]:
        """Load template configuration from file."""
        try:
            return read_json("@templates", f"{template_name}.json")
        except Exception as e:
            st.error(f"Error loading template {template_name}: {e}")
            return None
    
    def load_all_templates(self) -> Dict[str, Dict[str, Any]]:
        """Load all available templates."""
        templates = {}
        if not self.templates_dir.exists():
            return templates
            
        for template_file in self.templates_dir.glob("*.json"):
            template_name = template_file.stem
            template_config = self.load_template(template_name)
            if template_config:
                templates[template_name] = template_config
        return templates
    
    def apply_template(self, template_config: Dict[str, Any]):
        """Apply template configuration to session state."""
        try:
            # Apply model selection
            if 'model_selection' in template_config:
                model_sel = template_config['model_selection']
                if 'primary_model' in model_sel:
                    st.session_state.config_model = model_sel['primary_model']
            
            # Apply generation parameters
            if 'generation_parameters' in template_config:
                gen_params = template_config['generation_parameters']
                st.session_state.config_temperature = gen_params.get('temperature', 0.7)
                st.session_state.config_top_p = gen_params.get('top_p', 0.95)
                st.session_state.config_top_k = gen_params.get('top_k', 40)
                st.session_state.config_max_tokens = gen_params.get('max_output_tokens', 2048)
                st.session_state.config_thinking_budget = gen_params.get('thinking_budget', 0)
            
            # Apply system instruction
            if 'system_instruction' in template_config:
                st.session_state.config_system_instruction = template_config['system_instruction']
            
            # Apply safety settings
            if 'safety_settings' in template_config:
                safety = template_config['safety_settings']
                st.session_state.safety_hate_speech = safety.get('hate_speech', 'BLOCK_MEDIUM_AND_ABOVE')
                st.session_state.safety_dangerous_content = safety.get('dangerous_content', 'BLOCK_MEDIUM_AND_ABOVE')
                st.session_state.safety_harassment = safety.get('harassment', 'BLOCK_MEDIUM_AND_ABOVE')
                st.session_state.safety_sexually_explicit = safety.get('sexually_explicit', 'BLOCK_MEDIUM_AND_ABOVE')
            
            return True
        except Exception as e:
            st.error(f"Error applying template: {e}")
            return False
    
    def save_template(self, template_name: str, template_config: Dict[str, Any]) -> bool:
        """Save template configuration to file."""
        try:
            return write_json("@templates", f"{template_name}.json", template_config)
        except Exception as e:
            st.error(f"Error saving template {template_name}: {e}")
            return False
        
    def render(self):
        """Render the model configuration interface."""
        
        st.markdown("# ⚙️ Model Configuration")
        st.markdown("Configure model parameters and behavior settings.")
        
        # Get JSON config
        json_config = getattr(self.settings, '_json_config', {})
        model_config = json_config.get('model', {})
        
        # Fix safety_settings if it's a JSON string
        if 'safety_settings' in model_config and isinstance(model_config['safety_settings'], str):
            try:
                import json
                model_config['safety_settings'] = json.loads(model_config['safety_settings'])
            except json.JSONDecodeError:
                # If parsing fails, use default safety settings
                model_config['safety_settings'] = {
                    'hate_speech': 'BLOCK_MEDIUM_AND_ABOVE',
                    'dangerous_content': 'BLOCK_MEDIUM_AND_ABOVE',
                    'harassment': 'BLOCK_MEDIUM_AND_ABOVE',
                    'sexually_explicit': 'BLOCK_MEDIUM_AND_ABOVE'
                }
        
        # Model Selection Section
        st.markdown("## 🤖 Model Selection")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Available models with descriptions
            model_options = {
                "gemini-2.5-pro": "🎓 Most powerful for complex reasoning",
                "gemini-2.5-flash": "⚡ Best balance of speed and capability",
                "gemini-2.5-flash-lite": "🚀 Fastest and most cost-effective",
                "gemini-2.0-flash": "🔄 Latest stable model"
            }
            
            current_model = model_config.get('selected_model', 'gemini-2.5-flash')
            
            selected_model = st.selectbox(
                "Primary Model",
                options=list(model_options.keys()),
                index=list(model_options.keys()).index(current_model) if current_model in model_options else 1,
                format_func=lambda x: f"{x} - {model_options[x]}",
                key="config_model"
            )
            
            # Model info
            st.info(f"**Selected:** {selected_model}")
            
        with col2:
            # Model capabilities
            st.markdown("### 🎯 Capabilities")
            
            if "pro" in selected_model:
                st.success("✅ Advanced reasoning")
                st.success("✅ Long context")
                st.success("✅ Thinking mode")
                st.success("✅ Multimodal")
            elif "flash" in selected_model:
                st.success("✅ Fast responses")
                st.success("✅ Balanced performance")
                st.success("✅ Multimodal")
                if "lite" not in selected_model:
                    st.success("✅ Thinking mode")
            
            # Pricing info
            pricing_info = {
                "gemini-2.5-pro": "Input: $1.25/1M tokens, Output: $10.00/1M tokens",
                "gemini-2.5-flash": "Input: $0.30/1M tokens, Output: $2.50/1M tokens",
                "gemini-2.5-flash-lite": "Input: $0.10/1M tokens, Output: $0.40/1M tokens",
                "gemini-2.0-flash": "Input: $0.10/1M tokens, Output: $0.40/1M tokens"
            }
            
            st.caption(f"💰 **Pricing:** {pricing_info.get(selected_model, 'Contact for pricing')}")
        
        st.markdown("---")
        
        # Generation Parameters Section
        st.markdown("## 🎛️ Generation Parameters")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            temperature = st.slider(
                "🌡️ Temperature",
                min_value=0.0,
                max_value=2.0,
                value=float(model_config.get('temperature', 0.7)),
                step=0.1,
                help="Controls randomness. Lower = more focused, Higher = more creative",
                key="config_temperature"
            )
            
            top_p = st.slider(
                "🎯 Top-P",
                min_value=0.0,
                max_value=1.0,
                value=float(model_config.get('top_p', 0.95)),
                step=0.05,
                help="Controls diversity via nucleus sampling",
                key="config_top_p"
            )
        
        with col2:
            top_k = st.slider(
                "🔢 Top-K",
                min_value=1,
                max_value=100,
                value=int(model_config.get('top_k', 40)),
                step=1,
                help="Limits vocabulary to top K tokens",
                key="config_top_k"
            )
            
            max_tokens = st.number_input(
                "📏 Max Output Tokens",
                min_value=1,
                max_value=65536,
                value=int(model_config.get('max_output_tokens', 2048)),
                step=100,
                help="Maximum length of generated response",
                key="config_max_tokens"
            )
        
        with col3:
            thinking_budget = st.number_input(
                "🧠 Thinking Budget",
                min_value=0,
                max_value=10000,
                value=int(model_config.get('thinking_budget', 0)),
                step=100,
                help="Reasoning steps (0 = disabled, higher = more reasoning)",
                key="config_thinking_budget"
            )
            
            if "2.5" in selected_model:
                if thinking_budget == 0:
                    st.info("💡 Thinking disabled for faster responses")
                else:
                    st.success(f"🧠 Thinking enabled ({thinking_budget} budget)")
            else:
                st.warning("⚠️ Thinking not supported in this model")
        
        st.markdown("---")
        
        # System Instructions Section
        st.markdown("## 💬 System Instructions")
        st.markdown("Define the AI's personality, behavior, and response style.")
        
        current_instruction = model_config.get('system_instruction', '')
        
        system_instruction = st.text_area(
            "System Instruction",
            value=current_instruction,
            height=150,
            placeholder="You are a helpful AI assistant. Be concise and accurate in your responses...",
            help="This instruction is sent with every message to guide the AI's behavior",
            key="config_system_instruction"
        )
        
        # System instruction templates
        st.markdown("### 📋 Configuration Templates")
        st.markdown("Load complete model configurations from templates:")
        
        # Load all available templates
        available_templates = self.load_all_templates()
        
        if available_templates:
            template_cols = st.columns(3)
            
            for i, (template_key, template_config) in enumerate(available_templates.items()):
                with template_cols[i % 3]:
                    template_name = template_config.get('name', template_key.replace('_', ' ').title())
                    template_icon = template_config.get('icon', '📝')
                    
                    if st.button(f"{template_icon} {template_name}", key=f"template_{i}", use_container_width=True):
                        if self.apply_template(template_config):
                            st.success(f"✅ Applied {template_name} template!")
                            st.rerun()
                        else:
                            st.error(f"❌ Failed to apply {template_name} template")
        else:
            st.warning("⚠️ No templates found in output/templates/ directory")
        
        st.markdown("---")
        
        # Safety Settings Section
        st.markdown("## 🛡️ Safety Settings")
        
        safety_settings = model_config.get('safety_settings', {})
        
        st.markdown("Configure content filtering levels:")
        
        safety_categories = [
            ("hate_speech", "Hate Speech", "BLOCK_MEDIUM_AND_ABOVE"),
            ("dangerous_content", "Dangerous Content", "BLOCK_MEDIUM_AND_ABOVE"),
            ("harassment", "Harassment", "BLOCK_MEDIUM_AND_ABOVE"),
            ("sexually_explicit", "Sexually Explicit", "BLOCK_MEDIUM_AND_ABOVE")
        ]
        
        updated_safety = {}
        
        for key, label, default in safety_categories:
            current_setting = safety_settings.get(key, default)
            
            setting = st.selectbox(
                f"🛡️ {label}",
                options=["BLOCK_NONE", "BLOCK_ONLY_HIGH", "BLOCK_MEDIUM_AND_ABOVE", "BLOCK_LOW_AND_ABOVE"],
                index=["BLOCK_NONE", "BLOCK_ONLY_HIGH", "BLOCK_MEDIUM_AND_ABOVE", "BLOCK_LOW_AND_ABOVE"].index(current_setting),
                key=f"safety_{key}"
            )
            
            updated_safety[key] = setting
        
        st.markdown("---")
        
        # Template Management Section
        st.markdown("## 📚 Template Management")
        
        tab1, tab2, tab3 = st.tabs(["💾 Save as Template", "📋 Manage Templates", "📦 Import/Export"])
        
        with tab1:
            st.markdown("### Save Current Configuration as Template")
            
            with st.form("save_template_form"):
                template_name = st.text_input(
                    "Template Name",
                    placeholder="my_custom_template",
                    help="Use lowercase with underscores"
                )
                
                template_display_name = st.text_input(
                    "Display Name",
                    placeholder="My Custom Template"
                )
                
                template_description = st.text_area(
                    "Description",
                    placeholder="Description of this template's purpose...",
                    height=80
                )
                
                template_icon = st.text_input(
                    "Icon (Emoji)",
                    value="🎯",
                    max_chars=2
                )
                
                template_category = st.selectbox(
                    "Category",
                    ["general", "technical", "creative", "business", "education", "programming", "custom"]
                )
                
                if st.form_submit_button("💾 Save Template"):
                    if template_name and template_display_name:
                        # Create template config from current settings
                        new_template = {
                            "name": template_display_name,
                            "description": template_description,
                            "icon": template_icon,
                            "category": template_category,
                            "tags": [template_category],
                            "function_calling_enabled": True,
                            "function_calling_tools": [],
                            "model_selection": {
                                "primary_model": selected_model,
                                "capabilities": [],
                                "pricing": {}
                            },
                            "generation_parameters": {
                                "temperature": temperature,
                                "top_p": top_p,
                                "top_k": top_k,
                                "max_output_tokens": max_tokens,
                                "thinking_budget": thinking_budget
                            },
                            "system_instruction": system_instruction,
                            "safety_settings": updated_safety
                        }
                        
                        if self.save_template(template_name, new_template):
                            st.success(f"✅ Template '{template_display_name}' saved successfully!")
                            st.balloons()
                        else:
                            st.error("❌ Failed to save template")
                    else:
                        st.error("❌ Please provide template name and display name")
        
        with tab2:
            st.markdown("### Existing Templates")
            
            templates = self.load_all_templates()
            if templates:
                for template_key, template_config in templates.items():
                    with st.expander(f"{template_config.get('icon', '📝')} {template_config.get('name', template_key)}", expanded=False):
                        col1, col2 = st.columns([3, 1])
                        
                        with col1:
                            st.markdown(f"**Description:** {template_config.get('description', 'No description')}")
                            st.markdown(f"**Category:** {template_config.get('category', 'unknown')}")
                            st.markdown(f"**Model:** {template_config.get('model_selection', {}).get('primary_model', 'Not specified')}")
                            
                            # Show generation parameters
                            gen_params = template_config.get('generation_parameters', {})
                            if gen_params:
                                st.markdown("**Parameters:**")
                                st.caption(f"Temperature: {gen_params.get('temperature', 'N/A')}, "
                                         f"Top-P: {gen_params.get('top_p', 'N/A')}, "
                                         f"Max Tokens: {gen_params.get('max_output_tokens', 'N/A')}")
                        
                        with col2:
                            if st.button("🗑️ Delete", key=f"delete_template_{template_key}"):
                                try:
                                    template_file = self.templates_dir / f"{template_key}.json"
                                    if template_file.exists():
                                        template_file.unlink()
                                        st.success(f"Deleted {template_config.get('name', template_key)}")
                                        st.rerun()
                                except Exception as e:
                                    st.error(f"Failed to delete template: {e}")
            else:
                st.info("No templates found.")
        
        with tab3:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### Export Templates")
                templates = self.load_all_templates()
                if templates:
                    st.download_button(
                        "📤 Export All Templates",
                        data=json.dumps(templates, indent=2),
                        file_name="model_templates.json",
                        mime="application/json",
                        use_container_width=True
                    )
                else:
                    st.info("No templates to export")
            
            with col2:
                st.markdown("### Import Templates")
                uploaded_templates = st.file_uploader(
                    "📥 Import Templates",
                    type=['json'],
                    help="Upload a templates JSON file"
                )
                
                if uploaded_templates:
                    try:
                        templates_data = json.load(uploaded_templates)
                        st.success("✅ Templates file loaded!")
                        st.json(templates_data)
                        
                        if st.button("📥 Import Templates"):
                            imported_count = 0
                            for template_name, template_config in templates_data.items():
                                if self.save_template(template_name, template_config):
                                    imported_count += 1
                            
                            if imported_count > 0:
                                st.success(f"✅ Imported {imported_count} templates!")
                                st.rerun()
                            else:
                                st.error("❌ Failed to import templates")
                    except Exception as e:
                        st.error(f"❌ Invalid templates file: {e}")
        
        st.markdown("---")
        
        # Save Configuration
        st.markdown("## 💾 Save Configuration")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("💾 Save Settings", type="primary", use_container_width=True):
                config_updates = {
                    'model': {
                        'selected_model': selected_model,
                        'temperature': temperature,
                        'top_p': top_p,
                        'top_k': top_k,
                        'max_output_tokens': max_tokens,
                        'thinking_budget': thinking_budget,
                        'system_instruction': system_instruction,
                        'safety_settings': json.dumps(updated_safety)
                    }
                }
                
                if save_json_config(config_updates):
                    st.success("✅ Configuration saved successfully!")
                    st.balloons()
                else:
                    st.error("❌ Failed to save configuration")
        
        with col2:
            if st.button("🔄 Reset to Defaults", use_container_width=True):
                default_config = {
                    'model': {
                        'selected_model': 'gemini-2.5-flash',
                        'temperature': 0.7,
                        'top_p': 0.95,
                        'top_k': 40,
                        'max_output_tokens': 2048,
                        'thinking_budget': 0,
                        'system_instruction': '',
                        'safety_settings': json.dumps({})
                    }
                }
                
                if save_json_config(default_config):
                    st.success("✅ Reset to defaults!")
                    st.rerun()
                else:
                    st.error("❌ Failed to reset configuration")
        
        with col3:
            # Export configuration
            config_export = {
                'model_config': {
                    'selected_model': selected_model,
                    'temperature': temperature,
                    'top_p': top_p,
                    'top_k': top_k,
                    'max_output_tokens': max_tokens,
                    'thinking_budget': thinking_budget,
                    'system_instruction': system_instruction,
                    'safety_settings': updated_safety
                }
            }
            
            st.download_button(
                "📤 Export Config",
                data=json.dumps(config_export, indent=2),
                file_name="model_config.json",
                mime="application/json",
                use_container_width=True
            )
        
        # Configuration Preview
        with st.expander("👁️ Configuration Preview", expanded=False):
            st.json({
                "model": selected_model,
                "temperature": temperature,
                "top_p": top_p,
                "top_k": top_k,
                "max_output_tokens": max_tokens,
                "thinking_budget": thinking_budget,
                "system_instruction": system_instruction[:100] + "..." if len(system_instruction) > 100 else system_instruction,
                "safety_settings": updated_safety
            })

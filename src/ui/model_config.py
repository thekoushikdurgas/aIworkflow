"""
Model configuration interface for the GenAI Agent.
"""

import streamlit as st
import json
from config.settings import AppSettings, save_json_config

class ModelConfigInterface:
    """Model configuration interface component."""
    
    def __init__(self, settings: AppSettings):
        self.settings = settings
        
    def render(self):
        """Render the model configuration interface."""
        
        st.markdown("# ⚙️ Model Configuration")
        st.markdown("Configure model parameters and behavior settings.")
        
        # Get JSON config
        json_config = getattr(self.settings, '_json_config', {})
        model_config = json_config.get('model', {})
        
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
        st.markdown("### 📋 Quick Templates")
        
        templates = {
            "Default Assistant": "You are a helpful AI assistant. Be concise, accurate, and friendly in your responses.",
            "Technical Expert": "You are a technical expert. Provide detailed, accurate technical information with examples and best practices.",
            "Creative Writer": "You are a creative writing assistant. Help with storytelling, character development, and creative expression.",
            "Code Assistant": "You are a programming assistant. Provide clean, well-commented code with explanations and best practices.",
            "Teacher": "You are an educational assistant. Explain concepts clearly, use examples, and encourage learning.",
            "Business Analyst": "You are a business analyst. Provide data-driven insights and strategic recommendations."
        }
        
        template_cols = st.columns(3)
        
        for i, (name, template) in enumerate(templates.items()):
            with template_cols[i % 3]:
                if st.button(f"📝 {name}", key=f"template_{i}", use_container_width=True):
                    st.session_state.config_system_instruction = template
                    st.rerun()
        
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

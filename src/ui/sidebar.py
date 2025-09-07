"""
Sidebar component for the GenAI Agent.
"""

import streamlit as st
from config.settings import AppSettings
import os
import subprocess
import platform



def check_prerequisites():
    """Check if required API keys and dependencies are available."""
    missing_items = []
    
    # Check for API keys
    google_api_key = os.getenv('GOOGLE_API_KEY') or os.getenv('GEMINI_API_KEY')
    vertex_project = os.getenv('GOOGLE_CLOUD_PROJECT')
    
    if not google_api_key and not vertex_project:
        missing_items.append("Google API Key or Vertex AI project configuration")
    
    # Check for required directories
    required_dirs = ['output', 'output/logs', 'output/sessions', 'output/media']
    for dir_path in required_dirs:
        if not os.path.exists(dir_path):
            try:
                os.makedirs(dir_path, exist_ok=True)
            except Exception as e:
                missing_items.append(f"Unable to create directory {dir_path}: {str(e)}")
    
    return missing_items
def render_header():
    """Render the application header."""
    settings = st.session_state.get('settings', AppSettings())
    
    # col1, col2, col3 = st.columns([1, 2, 1])
    
    # with col2:
    st.markdown(f"""
        <div style="text-align: center; padding: 1rem 0;">
            <h1 style="margin: 0; color: #1f77b4;">
                {settings.app_icon} {settings.app_title}
            </h1>
            <p style="margin: 0.5rem 0 0 0; color: #666; font-size: 1.1rem;">
                Powered by Google GenAI SDK
            </p>
        </div>
    """, unsafe_allow_html=True)

def render_setup_warning(missing_items):
    """Render setup warnings for missing prerequisites."""
    st.warning("⚠️ Setup Required")
    
    with st.expander("Configuration Issues", expanded=True):
        st.markdown("### Missing Configuration:")
        for item in missing_items:
            st.markdown(f"- ❌ {item}")
        
        st.markdown("### Setup Instructions:")
        st.markdown("""
        1. **Copy the config template:**
           ```bash
           cp config_template.env .env
           ```
        
        2. **Set your API key:**
           ```bash
           export GOOGLE_API_KEY="your-api-key-here"
           ```
           
        3. **Or configure Vertex AI:**
           ```bash
           export GOOGLE_CLOUD_PROJECT="your-project-id"
           export GOOGLE_CLOUD_LOCATION="us-central1"
           gcloud auth application-default login
           ```
        
        4. **Restart the application**
        """)

def render_footer():
    """Render the application footer."""
    st.markdown("---")
    
    # col1, col2, col3 = st.columns([1, 2, 1])
    
    # with col2:
    st.markdown("""
        <div style="text-align: center; padding: 1rem 0; color: #666; font-size: 0.9rem;">
            <p>Built with ❤️ using 
            <a href="https://streamlit.io" target="_blank">Streamlit</a> and 
            <a href="https://ai.google.dev/gemini-api/docs" target="_blank">Google GenAI SDK</a>
            </p>
            <p>⚠️ Remember to check pricing for video generation and other premium features</p>
        </div>
    """, unsafe_allow_html=True)
def render_sidebar():
    """Render the application sidebar."""
    
    with st.sidebar:
        # st.markdown("## ⚙️ Quick Settings")
        
        # Get current settings
        settings = st.session_state.get('settings', AppSettings())
        json_config = getattr(settings, '_json_config', {})
        
        # Check prerequisites
        missing_items = check_prerequisites()
        
        if missing_items:
            render_header()
            render_setup_warning(missing_items)
            return
        # Render main interface
        render_header()
        
        # Navigation section
        st.markdown("### 🧭 Navigation")
        
        # Page options with emojis
        page_options = [
            "Chat",
            "Model Config", 
            "Media Studio",
            "Tool Workshop",
            "Sessions"
        ]
        
        page_icons = {
            "Chat": "🗣️",
            "Model Config": "⚙️", 
            "Media Studio": "🎨",
            "Tool Workshop": "🔧",
            "Sessions": "📝"
        }
        
        # Get current page
        current_page = st.session_state.get('current_page', 'Chat')
        
        # Create radio button navigation
        selected_page = st.radio(
            "Choose a page:",
            page_options,
            index=page_options.index(current_page) if current_page in page_options else 0,
            format_func=lambda x: f"{page_icons.get(x, '📄')} {x}",
            key="sidebar_navigation"
        )
        
        # Update session state if page changed
        if selected_page != current_page:
            st.session_state.current_page = selected_page
            st.rerun()
        
        st.markdown("---")
        
        # # Model selection
        # st.markdown("### 🤖 Model")
        
        # available_models = [
        #     "gemini-2.5-pro", 
        #     "gemini-2.5-flash", 
        #     "gemini-2.5-flash-lite",
        #     "gemini-2.0-flash"
        # ]
        
        current_model = json_config.get('model', {}).get('selected_model', 'gemini-2.5-flash')
        
        # selected_model = st.selectbox(
        #     "Select Model",
        #     available_models,
        #     index=available_models.index(current_model) if current_model in available_models else 1,
        #     key="sidebar_model"
        # )
        
        # # Temperature slider
        # current_temp = json_config.get('model', {}).get('temperature', 0.7)
        # temperature = st.slider(
        #     "Temperature",
        #     min_value=0.0,
        #     max_value=2.0,
        #     value=float(current_temp),
        #     step=0.1,
        #     key="sidebar_temperature"
        # )
        
        # # Save settings if changed
        # if (selected_model != current_model or 
        #     abs(temperature - current_temp) > 0.05):
            
        #     from config.settings import save_json_config
        #     config_updates = {
        #         'model': {
        #             'selected_model': selected_model,
        #             'temperature': temperature
        #         }
        #     }
            
        #     if save_json_config(config_updates):
        #         st.success("✅ Settings saved!")
        #         st.rerun()
        
        # st.markdown("---")
        
        # Feature toggles
        # st.markdown("### 🔧 Features")
        
        # function_calling = json_config.get('chat', {}).get('enable_function_calling', False)
        # new_function_calling = st.checkbox(
        #     "Enable Function Calling",
        #     value=function_calling,
        #     key="sidebar_functions"
        # )
        
        # if new_function_calling != function_calling:
        #     from config.settings import save_json_config
        #     config_updates = {
        #         'chat': {
        #             'enable_function_calling': new_function_calling
        #         }
        #     }
        #     save_json_config(config_updates)
        #     st.rerun()
        
        # st.markdown("---")
        
        # System info
        st.markdown("### 📊 Status")
        
        # API connection status
        api_key = json_config.get('auth', {}).get('api_key', '')
        if api_key:
            st.success("🔑 API Key Configured")
        else:
            st.error("❌ No API Key")
        
        # Current model info
        st.info(f"🤖 Model: {current_model}")
        
        st.markdown("---")
        
        # Quick actions
        st.markdown("### 🚀 Quick Actions")
        
        if st.button("🗑️ Clear Cache", use_container_width=True):
            # Clear session state cache
            for key in st.session_state.keys():
                if key.startswith('cache_'):
                    del st.session_state[key]
            st.success("Cache cleared!")
        
        if st.button("📁 Open Output Folder", use_container_width=True):
            
            output_dir = "output"
            os.makedirs(output_dir, exist_ok=True)
            
            try:
                if platform.system() == "Windows":
                    subprocess.run(["explorer", output_dir])
                elif platform.system() == "Darwin":  # macOS
                    subprocess.run(["open", output_dir])
                else:  # Linux
                    subprocess.run(["xdg-open", output_dir])
                st.success("Output folder opened!")
            except:
                st.info(f"Output folder: {os.path.abspath(output_dir)}")
        
        st.markdown("---")
        
        # Footer
        st.markdown("""
        <div style="text-align: center; color: #666; font-size: 0.8rem;">
            <p>🤖 GenAI Agent v1.0</p>
            <p>Powered by Google GenAI SDK</p>
        </div>
        """, unsafe_allow_html=True)
        # Render footer
        render_footer()

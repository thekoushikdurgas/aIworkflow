#!/usr/bin/env python3
"""
🤖 Streamlit GenAI Agent

A comprehensive AI agent built with Streamlit and Google's GenAI SDK.
Supports multimodal conversations, media generation, and advanced AI capabilities.

Author: AI Assistant
License: Apache 2.0
"""

import streamlit as st
import os
import sys
from pathlib import Path

# # Add src directory to Python path
# src_path = Path(__file__).parent / "src"
# sys.path.insert(0, str(src_path))

# Import core components
from config.settings import AppSettings, load_settings
from src.utils.logger import setup_logging, get_logger
from src.ui.sidebar import render_sidebar
from src.ui.chat_interface import ChatInterface
from src.ui.model_config import ModelConfigInterface
from src.ui.media_studio import MediaStudioInterface
from src.ui.tool_workshop import ToolWorkshopInterface
from src.ui.session_manager import SessionManagerInterface

# Configure Streamlit page
st.set_page_config(
    page_title="🤖 GenAI Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://ai.google.dev/gemini-api/docs',
        'Report a bug': None,
        'About': """
        # 🤖 GenAI Agent
        
        A comprehensive AI agent built with Google's GenAI SDK.
        
        **Features:**
        - 🗣️ Multimodal chat (text, images, audio, video)
        - 🎨 Media generation (Imagen & Veo)
        - 🔧 Function calling & tools
        - ⚙️ Advanced model configuration
        - 📝 Session management
        
        Built with ❤️ using Streamlit and Google's GenAI SDK
        """
    }
)

# Initialize logging
logger = get_logger(__name__)

def initialize_app():
    """Initialize the application with settings and logging."""
    try:
        # Load settings
        settings = load_settings()
        
        # Initialize session state
        if 'settings' not in st.session_state:
            st.session_state.settings = settings
            
        if 'initialized' not in st.session_state:
            st.session_state.initialized = True
            st.session_state.current_page = "Chat"
            st.session_state.user_authenticated = True  # Simple auth for now
            
        # Setup logging
        setup_logging(settings.log_level, settings.log_directory)
        
        logger.info("Application initialized successfully")
        return True
        
    except Exception as e:
        st.error(f"Failed to initialize application: {str(e)}")
        logger.error(f"Application initialization failed: {str(e)}")
        return False


# def render_navigation():
#     """Render the main navigation."""
#     st.markdown("---")
    
#     # Create navigation tabs
#     tabs = ["🗣️ Chat", "⚙️ Model Config", "🎨 Media Studio", "🔧 Tool Workshop", "📝 Sessions"]
    
#     # Use columns for navigation
#     cols = st.columns(len(tabs))
    
#     for i, (col, tab) in enumerate(zip(cols, tabs)):
#         with col:
#             tab_name = tab.split(" ", 1)[1]  # Remove emoji for internal use
#             if st.button(tab, key=f"nav_{i}", use_container_width=True):
#                 st.session_state.current_page = tab_name
#                 st.rerun()

def render_main_content():
    """Render the main content area based on current page."""
    current_page = st.session_state.get('current_page', 'Chat')
    settings = st.session_state.get('settings', AppSettings())
    
    try:
        if current_page == "Chat":
            chat_interface = ChatInterface(settings)
            chat_interface.render()
            
        elif current_page == "Model Config":
            config_interface = ModelConfigInterface(settings)
            config_interface.render()
            
        elif current_page == "Media Studio":
            media_interface = MediaStudioInterface(settings)
            media_interface.render()
            
        elif current_page == "Tool Workshop":
            tool_interface = ToolWorkshopInterface(settings)
            tool_interface.render()
            
        elif current_page == "Sessions":
            session_interface = SessionManagerInterface(settings)
            session_interface.render()
            
        else:
            st.error(f"Unknown page: {current_page}")
            
    except Exception as e:
        st.error(f"Error rendering {current_page}: {str(e)}")
        logger.error(f"Error rendering page {current_page}: {str(e)}")

def main():
    """Main application entry point."""
    try:
        # Initialize application
        initialize_app();
        # if not initialize_app():
        #     return
        
        
        # Render sidebar
        render_sidebar()
        
        # # Render navigation
        # render_navigation()
        
        # Render main content
        render_main_content()
        
        
    except Exception as e:
        st.error(f"Application error: {str(e)}")
        
        if st.session_state.get('settings', {}).get('debug_mode', False):
            st.exception(e)
        
        logger.error(f"Application error: {str(e)}")

if __name__ == "__main__":
    main()

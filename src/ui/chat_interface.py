"""
Main chat interface for the GenAI Agent.
"""

import streamlit as st
import time
import json
from typing import List, Dict, Any
from config.settings import AppSettings, save_json_config
from src.utils.logger import get_logger
import traceback

logger = get_logger(__name__)

# Constants
MEDIA_ERROR_KEYWORDS = ["MediaFileStorageError", "Bad filename"]

class ChatInterface:
    """Main chat interface component."""
    
    def __init__(self, settings: AppSettings):
        self.settings = settings
        
    def _clear_stale_media_references(self):
        """Clear any stale media file references from session state."""
        try:
            # Check if there are any file references that might be causing issues
            for i, message in enumerate(st.session_state.get('chat_history', [])):
                if message.get("role") == "user" and "files" in message:
                    # Keep the file names but remove any actual file objects
                    if isinstance(message["files"], list):
                        # If files list contains actual file objects, convert to names only
                        file_names = []
                        for file_ref in message["files"]:
                            if hasattr(file_ref, 'name'):
                                file_names.append(file_ref.name)
                            elif isinstance(file_ref, str):
                                file_names.append(file_ref)
                        message["files"] = file_names
            
            logger.info("Cleared stale media references from session state")
            return True
        except Exception as e:
            logger.error(f"Error clearing stale media references: {str(e)}")
            return False

    def render(self):
        """Render the chat interface."""
        
        st.markdown("# 🗣️ Chat with AI")
        
        # Initialize chat history in session state
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []
            
        if "current_session_id" not in st.session_state:
            st.session_state.current_session_id = f"session_{int(time.time())}"
        
        # Clear any stale media references on initialization
        self._clear_stale_media_references()
        
        # Get JSON config
        json_config = getattr(self.settings, '_json_config', {})
        
        # Chat configuration bar
        with st.expander("💡 Chat Settings", expanded=False):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                # Model selection (synced with sidebar)
                available_models = [
                    "gemini-2.5-pro", 
                    "gemini-2.5-flash", 
                    "gemini-2.5-flash-lite",
                    "gemini-2.0-flash"
                ]
                
                current_model = json_config.get('model', {}).get('selected_model', 'gemini-2.5-flash')
                selected_model = st.selectbox(
                    "Model",
                    available_models,
                    index=available_models.index(current_model) if current_model in available_models else 1,
                    key="chat_model"
                )
            
            with col2:
                # System instruction
                system_instruction = st.text_area(
                    "System Instruction",
                    value=json_config.get('model', {}).get('system_instruction', ''),
                    height=100,
                    key="chat_system_instruction",
                    help="Set the AI's behavior and personality"
                )
            
            with col3:
                # Advanced settings
                temperature = st.slider(
                    "Temperature",
                    min_value=0.0,
                    max_value=2.0,
                    value=float(json_config.get('model', {}).get('temperature', 0.7)),
                    step=0.1,
                    key="chat_temperature"
                )
                
                thinking_budget = st.number_input(
                    "Thinking Budget",
                    min_value=0,
                    max_value=10000,
                    value=int(json_config.get('model', {}).get('thinking_budget', 0)),
                    step=100,
                    key="chat_thinking_budget",
                    help="0 = no thinking, higher = more reasoning"
                )
                
                enable_streaming = json_config.get('chat', {}).get('stream_responses', True)
                stream_responses = st.checkbox(
                    "Stream Responses",
                    value=enable_streaming,
                    key="chat_streaming"
                )
        # Function calling configuration
        with st.expander("🔧 Function Calling", expanded=False):
            """Render the function calling configuration section."""
            # Get JSON config
            json_config = getattr(self.settings, '_json_config', {})
            chat_config = json_config.get('chat', {})
            
            # Function calling status
            function_calling_enabled = chat_config.get('enable_function_calling', False)
            
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown("## 🔧 Function Calling")
                
                new_function_calling = st.checkbox(
                    "Enable Function Calling",
                    value=function_calling_enabled,
                    help="Allow AI to call custom functions and tools"
                )
                
                if new_function_calling != function_calling_enabled:
                    config_updates = {
                        'chat': {
                            'enable_function_calling': new_function_calling
                        }
                    }
                    
                    if save_json_config(config_updates):
                        st.success("✅ Function calling setting updated!")
                        st.rerun()
            
            with col2:
                if function_calling_enabled:
                    st.success("🟢 Function Calling Enabled")
                else:
                    st.warning("🔴 Function Calling Disabled")
        
        # Use function_calling_enabled IN _handle_user_message
        
        # File upload section
        st.markdown("### 📁 Attach Files (Optional)")
        uploaded_files = st.file_uploader(
            "Choose files to include in your message",
            accept_multiple_files=True,
            type=['png', 'jpg', 'jpeg', 'gif', 'webp', 'mp4', 'mov', 'avi', 'mp3', 'wav', 'pdf', 'txt', 'md'],
            key="chat_file_upload"
        )
        
        # Display uploaded files
        if uploaded_files:
            try:
                st.info(f"📎 {len(uploaded_files)} file(s) attached")
                for file in uploaded_files:
                    file_size = len(file.getvalue()) / (1024 * 1024)  # MB
                    st.caption(f"• {file.name} ({file_size:.1f} MB)")
            except Exception as e:
                if any(keyword in str(e) for keyword in MEDIA_ERROR_KEYWORDS):
                    st.warning(f"📎 {len(uploaded_files)} file(s) attached ⚠️ (some files may no longer be available)")
                    logger.warning(f"Media file error in uploaded files display: {str(e)}")
                else:
                    st.error(f"Error displaying uploaded files: {str(e)}")
                    logger.error(f"Error displaying uploaded files: {str(e)}")
        
        # Chat history display
        st.markdown("### 💬 Conversation")
        
        # Display chat messages
        for i, message in enumerate(st.session_state.chat_history):
            try:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])
                    
                    # Show file attachments for user messages
                    if message["role"] == "user" and "files" in message:
                        st.caption(f"📎 {len(message['files'])} file(s): {', '.join(message['files'])}")
                    
                    # Show metadata
                    if "metadata" in message:
                        with st.expander("📊 Details", expanded=False):
                            meta = message["metadata"]
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                if "model" in meta:
                                    st.caption(f"🤖 Model: {meta['model']}")
                                if "tokens" in meta:
                                    st.caption(f"🔢 Tokens: {meta['tokens']}")
                            
                            with col2:
                                if "response_time" in meta:
                                    st.caption(f"⏱️ Time: {meta['response_time']:.1f}s")
                                if "thinking_time" in meta:
                                    st.caption(f"🧠 Thinking: {meta['thinking_time']:.1f}s")
                            
                            with col3:
                                if "cost" in meta:
                                    st.caption(f"💰 Cost: ${meta['cost']:.4f}")
                                if "cached" in meta and meta["cached"]:
                                    st.caption("⚡ Cached")
            except Exception as e:
                # Handle media file storage errors gracefully
                if any(keyword in str(e) for keyword in MEDIA_ERROR_KEYWORDS):
                    with st.chat_message(message["role"]):
                        st.markdown(message["content"])
                        if message["role"] == "user" and "files" in message:
                            st.caption(f"📎 {len(message['files'])} file(s): {', '.join(message['files'])} ⚠️ (files no longer available)")
                        logger.warning(f"Media file error in chat message {i}: {str(e)}")
                else:
                    st.error(f"Error displaying message {i+1}: {str(e)}")
                    logger.error(f"Error displaying chat message {i}: {str(e)}")
        
        # Chat input
        user_input = st.chat_input("Type your message here...")
        
        # Process user input
        if user_input:
            self._handle_user_message(
                user_input, 
                uploaded_files,
                selected_model,
                temperature,
                thinking_budget,
                system_instruction,
                stream_responses,
                function_calling_enabled
            )
        
        # Chat actions
        st.markdown("---")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("🗑️ Clear Chat", use_container_width=True):
                st.session_state.chat_history = []
                st.rerun()
        
        with col2:
            if st.button("💾 Save Chat", use_container_width=True):
                self._save_chat_session()
                st.success("Chat saved!")
        
        with col3:
            if st.button("📤 Export Chat", use_container_width=True):
                self._export_chat()
        
        with col4:
            if st.button("🔄 New Session", use_container_width=True):
                st.session_state.current_session_id = f"session_{int(time.time())}"
                st.session_state.chat_history = []
                st.success("New session started!")
                st.rerun()
        
        # Additional utility actions
        col5, _, _, _ = st.columns(4)
        
        with col5:
            if st.button("🔧 Fix Media Errors", use_container_width=True, help="Clear stale media file references"):
                if self._clear_stale_media_references():
                    st.success("✅ Cleared stale media references!")
                    st.rerun()
                else:
                    st.error("❌ Failed to clear media references")
    
    def _handle_user_message(self, user_input: str, uploaded_files, model: str, 
                           temperature: float, thinking_budget: int, 
                           system_instruction: str, stream_responses: bool,
                           function_calling_enabled: bool):
        """Handle user message and get AI response."""
        
        try:
            # Add user message to chat
            user_message = {
                "role": "user",
                "content": user_input,
                "timestamp": time.time()
            }
            
            if uploaded_files:
                user_message["files"] = [f.name for f in uploaded_files]
            
            st.session_state.chat_history.append(user_message)
            
            # Display user message immediately
            with st.chat_message("user"):
                try:
                    st.markdown(user_input)
                    if uploaded_files:
                        st.caption(f"📎 {len(uploaded_files)} file(s) attached")
                except Exception as e:
                    if any(keyword in str(e) for keyword in MEDIA_ERROR_KEYWORDS):
                        st.markdown(user_input)
                        if uploaded_files:
                            st.caption(f"📎 {len(uploaded_files)} file(s) attached ⚠️ (files no longer available)")
                        logger.warning(f"Media file error in user message display: {str(e)}")
                    else:
                        st.error(f"Error displaying user message: {str(e)}")
                        logger.error(f"Error displaying user message: {str(e)}")
            
            # Prepare AI response
            with st.chat_message("assistant"):
                response_placeholder = st.empty()
                metadata_placeholder = st.empty()
                
                start_time = time.time()
                
                # Mock AI response (replace with actual GenAI API call)
                if stream_responses:
                    response_text = self._get_streaming_response(
                        user_input, model, temperature, thinking_budget, 
                        system_instruction, response_placeholder
                    )
                else:
                    response_text = self._get_response(
                        user_input, model, temperature, thinking_budget, system_instruction
                    )
                    response_placeholder.markdown(response_text)
                
                response_time = time.time() - start_time
                
                # Calculate mock metadata
                estimated_tokens = len(user_input.split()) + len(response_text.split())
                estimated_cost = estimated_tokens * 0.0001  # Mock cost calculation
                
                metadata = {
                    "model": model,
                    "response_time": response_time,
                    "tokens": estimated_tokens,
                    "cost": estimated_cost,
                    "temperature": temperature,
                    "thinking_budget": thinking_budget
                }
                
                # Add AI response to chat history
                ai_message = {
                    "role": "assistant",
                    "content": response_text,
                    "timestamp": time.time(),
                    "metadata": metadata
                }
                
                st.session_state.chat_history.append(ai_message)
                
                # Show metadata
                with metadata_placeholder.expander("📊 Response Details", expanded=False):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.caption(f"🤖 Model: {model}")
                        st.caption(f"🔢 Tokens: {estimated_tokens}")
                    
                    with col2:
                        st.caption(f"⏱️ Time: {response_time:.1f}s")
                        st.caption(f"🌡️ Temperature: {temperature}")
                    
                    with col3:
                        st.caption(f"💰 Cost: ${estimated_cost:.4f}")
                        if thinking_budget > 0:
                            st.caption(f"🧠 Thinking: {thinking_budget}")
                
                # Log the interaction
                logger.info(f"Chat interaction - Model: {model}, Tokens: {estimated_tokens}, Time: {response_time:.2f}s")
                
        except Exception as e:
            st.error(f"Error processing message: {str(e)}")
            logger.error(f"Chat error: {str(e)}")
    
    def _get_response(self, user_input: str, model: str, temperature: float, 
                     thinking_budget: int, system_instruction: str) -> str:
        """Get AI response (mock implementation)."""
        
        # This is a mock response - replace with actual GenAI API call
        import random
        
        responses = [
            f"Thank you for your message: '{user_input}'. I'm using the {model} model with temperature {temperature}.",
            f"I understand you're asking about '{user_input}'. Let me help you with that using {model}.",
            f"Based on your input '{user_input}', here's my response using {model} at temperature {temperature}.",
            "This is a mock response. In a real implementation, this would use the Google GenAI SDK to generate actual AI responses.",
            f"Your message has been processed by {model}. The thinking budget is set to {thinking_budget}."
        ]
        
        # Simulate processing time
        time.sleep(random.uniform(0.5, 2.0))
        
        response = random.choice(responses)
        
        if system_instruction:
            response += f"\n\n*Note: I'm following the system instruction: '{system_instruction[:100]}...'*"
        
        return response
    
    def _get_streaming_response(self, user_input: str, model: str, temperature: float,
                              thinking_budget: int, system_instruction: str, 
                              placeholder) -> str:
        """Get streaming AI response (mock implementation)."""
        
        # Mock streaming response
        full_response = self._get_response(user_input, model, temperature, thinking_budget, system_instruction)
        
        # Simulate streaming by revealing text gradually
        displayed_text = ""
        for word in full_response.split():
            displayed_text += word + " "
            placeholder.markdown(displayed_text + "▊")
            time.sleep(0.05)  # Simulate streaming delay
        
        # Final display without cursor
        placeholder.markdown(displayed_text)
        return displayed_text.strip()
    
    def _save_chat_session(self):
        """Save current chat session."""
        try:
            import os
            import json
            
            os.makedirs("output/sessions", exist_ok=True)
            
            session_data = {
                "session_id": st.session_state.current_session_id,
                "timestamp": time.time(),
                "chat_history": st.session_state.chat_history,
                "settings": {
                    "model": st.session_state.get("chat_model"),
                    "temperature": st.session_state.get("chat_temperature"),
                    "thinking_budget": st.session_state.get("chat_thinking_budget")
                }
            }
            
            filename = f"output/sessions/{st.session_state.current_session_id}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Chat session saved: {filename}")
            
        except Exception as e:
            st.error(f"Error saving session: {str(e)}")
            logger.error(f"Session save error: {str(e)}")
    
    def _export_chat(self):
        """Export chat as downloadable file."""
        try:
            import json
            from datetime import datetime
            
            export_data = {
                "exported_at": datetime.now().isoformat(),
                "session_id": st.session_state.current_session_id,
                "chat_history": st.session_state.chat_history,
                "message_count": len(st.session_state.chat_history),
                "settings": getattr(self.settings, '_json_config', {})
            }
            
            # Create download button
            export_json = json.dumps(export_data, indent=2, ensure_ascii=False)
            
            st.download_button(
                label="📥 Download Chat JSON",
                data=export_json,
                file_name=f"chat_export_{st.session_state.current_session_id}.json",
                mime="application/json"
            )
            
        except Exception as e:
            st.error(f"Error exporting chat: {str(e)}")
            logger.error(f"Chat export error: {str(e)}")

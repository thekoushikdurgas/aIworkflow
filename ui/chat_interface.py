"""
Main chat interface for the GenAI Agent.
"""

import streamlit as st
import time
import json
from typing import List, Dict, Any
from config.settings import AppSettings, save_json_config
from utils.logger import get_logger
import traceback
from pathlib import Path
from utils.storage import StoragePaths, read_json
from contextlib import suppress

# Optional GenAI client import (fallback to mock if unavailable)
with suppress(Exception):
    from core.client import GenAIClient  # type: ignore

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
        # Derived runtime configuration with sane defaults
        model_cfg = json_config.get('model', {})
        chat_cfg = json_config.get('chat', {})
        ui_cfg = json_config.get('ui', {})
        selected_model = model_cfg.get('selected_model', 'gemini-2.5-flash')
        try:
            temperature = float(model_cfg.get('temperature', 0.7))
        except Exception:
            temperature = 0.7
        try:
            thinking_budget = int(model_cfg.get('thinking_budget', 0))
        except Exception:
            thinking_budget = 0
        system_instruction = model_cfg.get('system_instruction', '')
        stream_responses = bool(chat_cfg.get('stream_responses', True))
        function_calling_enabled = bool(chat_cfg.get('enable_function_calling', False))
        
        # Top controls: theme, model, reasoning, system instruction
        with st.container():
            cols = st.columns([3, 3, 3, 3])
            with cols[0]:
                st.markdown("### ⚙️ Configuration")
                current_theme = ui_cfg.get('theme', 'Light')
                theme_options = ["Light", "Dark", "Auto"]
                theme_sel = st.selectbox("Theme", options=theme_options, index=theme_options.index(current_theme) if current_theme in theme_options else 0)
                if theme_sel != current_theme:
                    if save_json_config({'ui': {'theme': theme_sel}}):
                        st.toast("Theme updated", icon="✅")
                        st.rerun()
            with cols[1]:
                st.markdown("### 🤖 Model")
                available_models = [
                    "gemini-2.5-pro",
                    "gemini-2.5-flash",
                    "gemini-2.5-flash-lite",
                    "gemini-2.0-flash"
                ]
                selected_model = st.selectbox("Model", available_models, index=available_models.index(selected_model) if selected_model in available_models else 1, key="chat_model")
                temperature = st.slider("Temperature", 0.0, 2.0, value=temperature, step=0.1, key="chat_temperature")
            with cols[2]:
                st.markdown("### 🧠 Reasoning & Stream")
                thinking_budget = st.number_input("Thinking Budget", min_value=0, max_value=10000, value=thinking_budget, step=100, key="chat_thinking_budget")
                stream_responses = st.checkbox("Stream Responses", value=stream_responses, key="chat_streaming")
            with cols[3]:
                st.markdown("### 📜 System Instruction")
                system_instruction = st.text_area("", value=system_instruction, height=120, key="chat_system_instruction")
            # Persist if any changes
            if save_json_config({
                'model': {
                    'selected_model': selected_model,
                    'temperature': float(temperature),
                    'thinking_budget': int(thinking_budget),
                    'system_instruction': system_instruction
                },
                'chat': {
                    'stream_responses': bool(stream_responses)
                }
            }):
                pass

        # Templates, tools, workflows
        with st.expander("📋 Templates & Resources", expanded=False):
            templates_dir = StoragePaths.ROOT_MAP["@templates"]
            available_templates = []
            try:
                if templates_dir.exists():
                    for tf in templates_dir.glob("*.json"):
                        try:
                            cfg = read_json("@templates", f"{tf.stem}.json")
                            available_templates.append((tf.stem, cfg))
                        except Exception:
                            pass
            except Exception:
                pass
            if available_templates:
                tpl_names = [cfg.get('name', key.replace('_',' ').title()) for key, cfg in available_templates]
                sel_idx = st.selectbox("Apply Template", options=list(range(len(available_templates))), format_func=lambda i: tpl_names[i], key="chat_tpl_select")
                if st.button("Apply Template", key="apply_tpl_btn"):
                    tkey, tcfg = available_templates[sel_idx]
                    gen = tcfg.get('generation_parameters', {})
                    updates = {
                        'model': {
                            'selected_model': tcfg.get('model_selection', {}).get('primary_model', selected_model),
                            'temperature': float(gen.get('temperature', temperature)),
                            'thinking_budget': int(gen.get('thinking_budget', thinking_budget)),
                            'system_instruction': tcfg.get('system_instruction', system_instruction)
                        }
                    }
                    if save_json_config(updates):
                        st.success("✅ Applied template")
                        st.rerun()
            else:
                st.caption("No templates found in output/templates/")

            tools_dir = StoragePaths.ROOT_MAP["@tools"]
            tool_items = []
            try:
                if tools_dir.exists():
                    for jf in tools_dir.glob("*.json"):
                        try:
                            cfg = read_json("@tools", f"{jf.stem}.json")
                            tool_items.append((jf.stem, cfg))
                        except Exception:
                            pass
            except Exception:
                pass
            if tool_items:
                st.selectbox("Available Tools", options=[name for name, _ in sorted(tool_items)], key="chat_tool_select")

            workflows_dir = StoragePaths.ROOT_MAP["@workflows"]
            workflow_items = []
            try:
                if workflows_dir.exists():
                    for jf in workflows_dir.glob("*.json"):
                        try:
                            cfg = read_json("@workflows", f"{jf.stem}.json")
                            workflow_items.append((jf.stem, cfg))
                        except Exception:
                            pass
            except Exception:
                pass
            if workflow_items:
                st.selectbox("Available Workflows", options=[name for name, _ in sorted(workflow_items)], key="chat_workflow_select")
        # # Function calling configuration
        # with st.expander("🔧 Function Calling", expanded=False):
        #     """Render the function calling configuration section."""
        #     # Get JSON config
        #     json_config = getattr(self.settings, '_json_config', {})
        #     chat_config = json_config.get('chat', {})
            
        #     # Function calling status
        #     function_calling_enabled = chat_config.get('enable_function_calling', False)
            
        #     col1, col2 = st.columns([3, 1])
            
        #     with col1:
        #         st.markdown("## 🔧 Function Calling")
                
        #         new_function_calling = st.checkbox(
        #             "Enable Function Calling",
        #             value=function_calling_enabled,
        #             help="Allow AI to call custom functions and tools"
        #         )
                
        #         if new_function_calling != function_calling_enabled:
        #             config_updates = {
        #                 'chat': {
        #                     'enable_function_calling': new_function_calling
        #                 }
        #             }
                    
        #             if save_json_config(config_updates):
        #                 st.success("✅ Function calling setting updated!")
        #                 st.rerun()
            
        #     with col2:
        #         if function_calling_enabled:
        #             st.success("🟢 Function Calling Enabled")
        #         else:
        #             st.warning("🔴 Function Calling Disabled")
            
            # # List all tools
            # st.markdown("---")
            # st.markdown("### 🛠️ Available Tools")
            # tools_dir = StoragePaths.ROOT_MAP["@tools"]
            # tool_items = []
            # try:
            #     if tools_dir.exists():
            #         for jf in tools_dir.glob("*.json"):
            #             try:
            #                 cfg = read_json("@tools", f"{jf.stem}.json")
            #                 tool_items.append((jf.stem, cfg))
            #             except Exception:
            #                 pass
            # except Exception:
            #     pass
            
            # if tool_items:
            #     for name, cfg in sorted(tool_items, key=lambda x: x[0]):
            #         with st.expander(f"🔧 {name}", expanded=False):
            #             st.caption(cfg.get('description', 'No description'))
            #             st.caption(f"Category: {cfg.get('category', 'unknown')}")
            #             enabled = cfg.get('enabled', True)
            #             st.caption("Status: " + ("✅ Enabled" if enabled else "❌ Disabled"))
            #             # Show parameters brief if present
            #             input_params = cfg.get('input_parameters', cfg.get('parameters', []))
            #             output_params = cfg.get('output_parameters', [])
            #             if input_params:
            #                 st.markdown("**📥 Inputs:**")
            #                 for p in input_params:
            #                     pname = p.get('name', 'param')
            #                     ptype = p.get('type', 'string')
            #                     req = " (required)" if p.get('required', False) else ""
            #                     st.caption(f"• {pname}: {ptype}{req}")
            #             if output_params:
            #                 st.markdown("**📤 Outputs:**")
            #                 for p in output_params:
            #                     pname = p.get('name', 'result')
            #                     ptype = p.get('type', 'string')
            #                     fmt = p.get('format', 'plain_text')
            #                     st.caption(f"• {pname}: {ptype} ({fmt})")
            # else:
            #     st.caption("No tools found in output/tools/")
        
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
                           system_instruction: str, stream_responses: bool):
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
                
                # Try real GenAI response; fallback to mock
                response_text = None
                try:
                    if 'GenAIClient' in globals():
                        client = GenAIClient(self.settings)
                        cfg = {
                            'temperature': float(temperature),
                            'max_output_tokens': int(self.settings.default_max_tokens),
                        }
                        if thinking_budget and thinking_budget > 0:
                            cfg['thinking_budget'] = int(thinking_budget)
                        prompt = user_input if not system_instruction else f"{system_instruction}\n\nUser: {user_input}"
                        if stream_responses:
                            chunks = client.generate_content_stream(model=model, contents=prompt, config=cfg)
                            collected = []
                            for chunk in chunks:
                                if chunk.text:
                                    collected.append(chunk.text)
                                    response_placeholder.markdown(" ".join(collected) + "▊")
                            response_text = " ".join(collected).strip()
                        else:
                            res = client.generate_content(model=model, contents=prompt, config=cfg)
                            response_text = (res.text or "").strip()
                            response_placeholder.markdown(response_text)
                    else:
                        raise RuntimeError("GenAIClient unavailable")
                except Exception:
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

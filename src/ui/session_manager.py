"""
Session management interface for the GenAI Agent.
"""

import streamlit as st
import json
import os
from datetime import datetime
from config.settings import AppSettings

class SessionManagerInterface:
    """Session management interface component."""
    
    def __init__(self, settings: AppSettings):
        self.settings = settings
        
    def render(self):
        """Render the session management interface."""
        
        st.markdown("# 📝 Session Manager")
        st.markdown("Manage your chat sessions and conversation history.")
        
        # Session overview
        self._render_session_overview()
        
        st.markdown("---")
        
        # Session list
        self._render_session_list()
        
        st.markdown("---")
        
        # Session management actions
        self._render_session_actions()
    
    def _render_session_overview(self):
        """Render session overview statistics."""
        
        st.markdown("## 📊 Session Overview")
        
        # Get sessions directory
        sessions_dir = "output/sessions"
        os.makedirs(sessions_dir, exist_ok=True)
        
        # Count sessions
        session_files = [f for f in os.listdir(sessions_dir) if f.endswith('.json')]
        total_sessions = len(session_files)
        
        # Current session info
        current_session_id = st.session_state.get('current_session_id', 'Unknown')
        current_messages = len(st.session_state.get('chat_history', []))
        
        # Display metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📁 Total Sessions", total_sessions)
        
        with col2:
            st.metric("💬 Current Messages", current_messages)
        
        with col3:
            st.metric("🆔 Current Session", current_session_id.split('_')[-1] if '_' in current_session_id else current_session_id)
        
        with col4:
            # Auto-save status
            json_config = getattr(self.settings, '_json_config', {})
            auto_save = json_config.get('ui', {}).get('auto_save', True)
            st.metric("💾 Auto-Save", "ON" if auto_save else "OFF")
    
    def _render_session_list(self):
        """Render the list of saved sessions."""
        
        st.markdown("## 📋 Saved Sessions")
        
        sessions_dir = "output/sessions"
        session_files = [f for f in os.listdir(sessions_dir) if f.endswith('.json')]
        
        if not session_files:
            st.info("📭 No saved sessions found. Start chatting to create your first session!")
            return
        
        # Sort sessions by modification time (newest first)
        session_files.sort(key=lambda f: os.path.getmtime(os.path.join(sessions_dir, f)), reverse=True)
        
        # Display sessions
        for session_file in session_files:
            session_path = os.path.join(sessions_dir, session_file)
            
            try:
                with open(session_path, 'r', encoding='utf-8') as f:
                    session_data = json.load(f)
                
                session_id = session_data.get('session_id', 'Unknown')
                timestamp = session_data.get('timestamp', 0)
                chat_history = session_data.get('chat_history', [])
                settings = session_data.get('settings', {})
                
                # Format timestamp
                if timestamp:
                    session_date = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
                else:
                    session_date = "Unknown"
                
                # Session preview
                message_count = len(chat_history)
                last_message = ""
                if chat_history:
                    last_msg = chat_history[-1]
                    last_message = last_msg.get('content', '')[:100] + "..." if len(last_msg.get('content', '')) > 100 else last_msg.get('content', '')
                
                # Session card
                with st.expander(f"💬 {session_id} ({message_count} messages)", expanded=False):
                    
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.markdown(f"**📅 Date:** {session_date}")
                        st.markdown(f"**💬 Messages:** {message_count}")
                        if last_message:
                            st.markdown(f"**💭 Last Message:** {last_message}")
                        
                        # Model used
                        model_used = settings.get('model', 'Unknown')
                        if model_used:
                            st.markdown(f"**🤖 Model:** {model_used}")
                    
                    with col2:
                        # Action buttons
                        if st.button(f"📥 Load", key=f"load_{session_id}"):
                            self._load_session(session_data)
                        
                        if st.button(f"📤 Export", key=f"export_{session_id}"):
                            self._export_session(session_data)
                        
                        if st.button(f"🗑️ Delete", key=f"delete_{session_id}", type="secondary"):
                            if st.session_state.get(f"confirm_delete_{session_id}", False):
                                self._delete_session(session_path)
                                st.rerun()
                            else:
                                st.session_state[f"confirm_delete_{session_id}"] = True
                                st.warning("Click again to confirm deletion")
                    
                    # Show conversation preview
                    if st.checkbox(f"👁️ Preview Conversation", key=f"preview_{session_id}"):
                        st.markdown("### 💬 Conversation Preview")
                        
                        for i, message in enumerate(chat_history[-5:]):  # Show last 5 messages
                            role = message.get('role', 'unknown')
                            content = message.get('content', '')
                            
                            if role == 'user':
                                st.markdown(f"**👤 User:** {content}")
                            elif role == 'assistant':
                                st.markdown(f"**🤖 Assistant:** {content}")
                        
                        if len(chat_history) > 5:
                            st.caption(f"... and {len(chat_history) - 5} more messages")
            
            except Exception as e:
                st.error(f"❌ Error loading session {session_file}: {str(e)}")
    
    def _render_session_actions(self):
        """Render session management actions."""
        
        st.markdown("## 🔧 Session Actions")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("### 💾 Save & Export")
            
            if st.button("💾 Save Current Session", use_container_width=True):
                self._save_current_session()
            
            if st.button("📤 Export All Sessions", use_container_width=True):
                self._export_all_sessions()
        
        with col2:
            st.markdown("### 📥 Import & Restore")
            
            uploaded_session = st.file_uploader(
                "Import Session",
                type=['json'],
                help="Upload a previously exported session file"
            )
            
            if uploaded_session:
                try:
                    session_data = json.load(uploaded_session)
                    
                    if st.button("📥 Import Session"):
                        self._load_session(session_data)
                        st.success("✅ Session imported successfully!")
                        
                except Exception as e:
                    st.error(f"❌ Error importing session: {str(e)}")
        
        with col3:
            st.markdown("### 🗑️ Cleanup")
            
            if st.button("🗑️ Clear Current Session", use_container_width=True):
                st.session_state.chat_history = []
                st.session_state.current_session_id = f"session_{int(datetime.now().timestamp())}"
                st.success("✅ Current session cleared!")
                st.rerun()
            
            if st.button("🗑️ Delete All Sessions", use_container_width=True, type="secondary"):
                if st.session_state.get("confirm_delete_all", False):
                    self._delete_all_sessions()
                    st.success("✅ All sessions deleted!")
                    st.rerun()
                else:
                    st.session_state["confirm_delete_all"] = True
                    st.warning("⚠️ Click again to confirm deletion of ALL sessions")
        
        # Session settings
        st.markdown("---")
        st.markdown("## ⚙️ Session Settings")
        
        json_config = getattr(self.settings, '_json_config', {})
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Auto-save setting
            current_auto_save = json_config.get('ui', {}).get('auto_save', True)
            
            auto_save = st.checkbox(
                "💾 Auto-save sessions",
                value=current_auto_save,
                help="Automatically save chat sessions"
            )
            
            if auto_save != current_auto_save:
                from config.settings import save_json_config
                config_updates = {
                    'ui': {
                        'auto_save': auto_save
                    }
                }
                
                if save_json_config(config_updates):
                    st.success("✅ Auto-save setting updated!")
                    st.rerun()
        
        with col2:
            # Max history setting
            max_history = st.number_input(
                "📝 Max messages per session",
                min_value=10,
                max_value=1000,
                value=100,
                step=10,
                help="Maximum number of messages to keep in memory"
            )
    
    def _save_current_session(self):
        """Save the current chat session."""
        try:
            os.makedirs("output/sessions", exist_ok=True)
            
            session_data = {
                "session_id": st.session_state.get('current_session_id'),
                "timestamp": datetime.now().timestamp(),
                "chat_history": st.session_state.get('chat_history', []),
                "settings": {
                    "model": st.session_state.get("chat_model"),
                    "temperature": st.session_state.get("chat_temperature"),
                    "thinking_budget": st.session_state.get("chat_thinking_budget")
                }
            }
            
            filename = f"output/sessions/{session_data['session_id']}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, indent=2, ensure_ascii=False)
            
            st.success(f"✅ Session saved: {filename}")
            
        except Exception as e:
            st.error(f"❌ Error saving session: {str(e)}")
    
    def _load_session(self, session_data):
        """Load a session into the current chat."""
        try:
            st.session_state.current_session_id = session_data.get('session_id')
            st.session_state.chat_history = session_data.get('chat_history', [])
            
            # Load settings if available
            settings = session_data.get('settings', {})
            if 'model' in settings:
                st.session_state.chat_model = settings['model']
            if 'temperature' in settings:
                st.session_state.chat_temperature = settings['temperature']
            if 'thinking_budget' in settings:
                st.session_state.chat_thinking_budget = settings['thinking_budget']
            
            st.success(f"✅ Session loaded: {len(st.session_state.chat_history)} messages")
            
        except Exception as e:
            st.error(f"❌ Error loading session: {str(e)}")
    
    def _export_session(self, session_data):
        """Export a session as downloadable JSON."""
        try:
            session_json = json.dumps(session_data, indent=2, ensure_ascii=False)
            session_id = session_data.get('session_id', 'unknown')
            
            st.download_button(
                label="📥 Download Session",
                data=session_json,
                file_name=f"session_{session_id}.json",
                mime="application/json"
            )
            
        except Exception as e:
            st.error(f"❌ Error exporting session: {str(e)}")
    
    def _export_all_sessions(self):
        """Export all sessions as a single file."""
        try:
            sessions_dir = "output/sessions"
            all_sessions = []
            
            for session_file in os.listdir(sessions_dir):
                if session_file.endswith('.json'):
                    session_path = os.path.join(sessions_dir, session_file)
                    with open(session_path, 'r', encoding='utf-8') as f:
                        session_data = json.load(f)
                        all_sessions.append(session_data)
            
            export_data = {
                "export_timestamp": datetime.now().isoformat(),
                "total_sessions": len(all_sessions),
                "sessions": all_sessions
            }
            
            export_json = json.dumps(export_data, indent=2, ensure_ascii=False)
            
            st.download_button(
                label="📥 Download All Sessions",
                data=export_json,
                file_name=f"all_sessions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
            
        except Exception as e:
            st.error(f"❌ Error exporting all sessions: {str(e)}")
    
    def _delete_session(self, session_path):
        """Delete a specific session file."""
        try:
            os.remove(session_path)
            st.success("✅ Session deleted!")
            
        except Exception as e:
            st.error(f"❌ Error deleting session: {str(e)}")
    
    def _delete_all_sessions(self):
        """Delete all session files."""
        try:
            sessions_dir = "output/sessions"
            deleted_count = 0
            
            for session_file in os.listdir(sessions_dir):
                if session_file.endswith('.json'):
                    session_path = os.path.join(sessions_dir, session_file)
                    os.remove(session_path)
                    deleted_count += 1
            
            st.success(f"✅ Deleted {deleted_count} sessions!")
            
        except Exception as e:
            st.error(f"❌ Error deleting sessions: {str(e)}")

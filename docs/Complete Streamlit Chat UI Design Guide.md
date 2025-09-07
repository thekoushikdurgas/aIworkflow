<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

# Complete Streamlit Chat UI Design Guide

Based on comprehensive research of Streamlit documentation and online examples, I've created a complete guide for designing chat UIs in Streamlit Python. Here's everything you need to build professional chat interfaces:

## Core Chat Elements

Streamlit provides several specialized components for building conversational applications:

**st.chat_message**: Creates containers for displaying chat messages with built-in styling and avatar support. It accepts parameters for the author name ("user", "assistant", "ai", "human", or custom strings), custom avatars, and width settings.[^1][^2][^3]

**st.chat_input**: Displays a chat input widget that can be pinned to the bottom of the app or used inline within containers. It supports file uploads, character limits, placeholder text, and custom styling.[^2]

**st.write_stream**: Enables typewriter effects for streaming responses, perfect for creating ChatGPT-like experiences.[^4][^1]

## Five Complete Chat UI Examples

### 1. Basic Echo Chat Bot

The simplest implementation that demonstrates core concepts:

```python
import streamlit as st

st.title("Echo Bot")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("What is up?"):
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    response = f"Echo: {prompt}"
    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        st.markdown(response)
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})
```

### 2. Streaming Chat with Typewriter Effect

Adds realistic streaming responses with customizable speed:

```python
import streamlit as st
import random
import time

# Streamed response emulator
def response_generator():
    response = random.choice([
        "Hello there! How can I assist you today?",
        "Hi, human! Is there anything I can help you with?",
        "Do you need help?",
    ])
    for word in response.split():
        yield word + " "
        time.sleep(0.05)

st.title("Simple Chat with Streaming")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("What is up?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        response = st.write_stream(response_generator())
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})
```

### 3. Advanced Chat with Custom Styling and File Upload

Features comprehensive customization with CSS styling, file uploads, and enhanced UI elements:

```python
import streamlit as st
import time

st.set_page_config(
    page_title="Advanced Chat App",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    .chat-container {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 10px;
        margin: 5px 0;
    }
    
    .user-message {
        background-color: #e8f4fd;
        padding: 10px;
        border-radius: 10px;
        margin: 5px 0;
        border-left: 4px solid #1f77b4;
    }
    
    .assistant-message {
        background-color: #f0f8e8;
        padding: 10px;
        border-radius: 10px;
        margin: 5px 0;
        border-left: 4px solid #2ca02c;
    }
    
    .stChatInput > div > div > input {
        background-color: #ffffff;
        border: 2px solid #1f77b4;
        border-radius: 20px;
        padding: 10px 15px;
    }
</style>
""", unsafe_allow_html=True)

# Custom avatars
USER_AVATAR = "👤"
ASSISTANT_AVATAR = "🤖"

st.title("🤖 Advanced AI Chat Assistant")

# Sidebar for settings and file upload
with st.sidebar:
    st.header("⚙️ Settings")
    
    # Model selection  
    model_choice = st.selectbox(
        "Choose AI Model",
        ["GPT-4", "GPT-3.5-turbo", "Claude", "Gemini"],
        index=0
    )
    
    # Temperature setting
    temperature = st.slider("Temperature", 0.0, 1.0, 0.7, 0.1)
    
    # File upload section
    st.header("📎 File Upload")
    uploaded_files = st.file_uploader(
        "Upload documents",
        type=["txt", "pdf", "docx", "csv"],
        accept_multiple_files=True
    )
    
    if uploaded_files:
        st.success(f"Uploaded {len(uploaded_files)} file(s)")
        for file in uploaded_files:
            st.write(f"📄 {file.name}")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! I'm your AI assistant. How can I help you today?"}
    ]

# Display chat messages with custom styling
for message in st.session_state.messages:
    if message["role"] == "user":
        with st.chat_message("user", avatar=USER_AVATAR):
            st.markdown(f'<div class="user-message">{message["content"]}</div>', 
                       unsafe_allow_html=True)
    else:
        with st.chat_message("assistant", avatar=ASSISTANT_AVATAR):
            st.markdown(f'<div class="assistant-message">{message["content"]}</div>', 
                       unsafe_allow_html=True)

# Enhanced chat input with file support
prompt = st.chat_input(
    "Type your message here...",
    accept_file=True,
    file_type=["jpg", "jpeg", "png", "pdf", "txt"]
)

# Handle user input
if prompt:
    # Handle text and file input
    if hasattr(prompt, 'text') and prompt.text:
        user_message = prompt.text
        files = getattr(prompt, 'files', [])
    else:
        user_message = str(prompt)
        files = []
    
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": user_message})
    
    # Display user message
    with st.chat_message("user", avatar=USER_AVATAR):
        st.markdown(f'<div class="user-message">{user_message}</div>', 
                   unsafe_allow_html=True)
        
        # Display uploaded files if any
        if files:
            st.write("📎 Uploaded files:")
            for file in files:
                if file.type.startswith('image/'):
                    st.image(file, width=200)
                else:
                    st.write(f"📄 {file.name}")

    # Generate assistant response with streaming
    with st.chat_message("assistant", avatar=ASSISTANT_AVATAR):
        with st.spinner("Thinking..."):
            time.sleep(1)
            
            if "hello" in user_message.lower():
                response = f"Hello! I'm using the {model_choice} model with temperature {temperature}. How can I assist you today?"
            else:
                response = f"Thanks for your message! This is a simulated response using {model_choice}."
            
            # Stream the response
            message_placeholder = st.empty()
            full_response = ""
            for chunk in response.split():
                full_response += chunk + " "
                time.sleep(0.02)
                message_placeholder.markdown(f'<div class="assistant-message">{full_response}▌</div>', 
                                           unsafe_allow_html=True)
            
            message_placeholder.markdown(f'<div class="assistant-message">{full_response}</div>', 
                                       unsafe_allow_html=True)
    
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})
```

### 4. Multiple Chat Windows with Sidebar Management

Implements multiple conversation threads with sidebar navigation:

```python
import streamlit as st
import time
from datetime import datetime

st.set_page_config(
    page_title="Multi-Chat App",
    page_icon="💬",
    layout="wide"
)

# Initialize session states
if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = {
        "chat_1": {
            "name": "General Chat",
            "messages": [{"role": "assistant", "content": "Hello! This is your general chat assistant."}],
            "created": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
    }

if "active_chat" not in st.session_state:
    st.session_state.active_chat = "chat_1"

# Sidebar for chat management
with st.sidebar:
    st.title("💬 Chat Sessions")
    
    # New chat button
    if st.button("➕ New Chat", use_container_width=True):
        chat_id = f"chat_{len(st.session_state.chat_sessions) + 1}"
        st.session_state.chat_sessions[chat_id] = {
            "name": f"Chat {len(st.session_state.chat_sessions) + 1}",
            "messages": [{"role": "assistant", "content": "Hello! How can I help you in this new chat?"}],
            "created": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        st.session_state.active_chat = chat_id
        st.rerun()
    
    st.markdown("---")
    
    # Display chat sessions
    for chat_id, chat_data in st.session_state.chat_sessions.items():
        col1, col2 = st.columns([3, 1])
        
        with col1:
            if st.button(
                f"💬 {chat_data['name']}", 
                key=f"select_{chat_id}",
                use_container_width=True,
                type="primary" if chat_id == st.session_state.active_chat else "secondary"
            ):
                st.session_state.active_chat = chat_id
                st.rerun()
        
        with col2:
            if st.button("🗑️", key=f"delete_{chat_id}", help="Delete chat"):
                if len(st.session_state.chat_sessions) > 1:
                    del st.session_state.chat_sessions[chat_id]
                    if st.session_state.active_chat == chat_id:
                        st.session_state.active_chat = list(st.session_state.chat_sessions.keys())[^0]
                    st.rerun()

# Main chat interface
active_chat = st.session_state.chat_sessions[st.session_state.active_chat]

# Display chat messages for active chat
chat_container = st.container(height=400)
with chat_container:
    for message in active_chat["messages"]:
        if message["role"] == "user":
            with st.chat_message("user", avatar="👤"):
                st.markdown(message["content"])
        else:
            with st.chat_message("assistant", avatar="🤖"):
                st.markdown(message["content"])

# Chat input
if prompt := st.chat_input(f"Message {active_chat['name']}..."):
    # Add user message to active chat
    st.session_state.chat_sessions[st.session_state.active_chat]["messages"].append({
        "role": "user", 
        "content": prompt
    })
    
    # Generate and add assistant response
    response = f"Thanks for your message in {active_chat['name']}! This is a simulated response."
    st.session_state.chat_sessions[st.session_state.active_chat]["messages"].append({
        "role": "assistant", 
        "content": response
    })
    
    st.rerun()
```

### 5. OpenAI ChatGPT-like Integration

Full integration with OpenAI API for production-ready chat applications:

```python
import streamlit as st
from openai import OpenAI

st.title("ChatGPT-like Clone")

# Set OpenAI API key from Streamlit secrets
# Add your API key to .streamlit/secrets.toml:
# OPENAI_API_KEY = "your-api-key-here"
try:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
except:
    st.error("Please add your OpenAI API key to .streamlit/secrets.toml")
    st.stop()

# Set a default model
if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("What is up?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        try:
            stream = client.chat.completions.create(
                model=st.session_state["openai_model"],
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ],
                stream=True,
            )
            response = st.write_stream(stream)
        except Exception as e:
            response = f"Error: {str(e)}"
            st.error(response)
    
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})
```

## Advanced Customization Features

### Custom Avatars and Styling

You can customize avatars using emojis, image URLs, or local images:[^5][^6]

```python
# Emoji avatars
with st.chat_message("user", avatar="👤"):
    st.write("User message")

# Custom image avatars  
with st.chat_message("assistant", avatar="https://via.placeholder.com/40"):
    st.write("Assistant message")
```

### CSS Styling and Themes

Streamlit now supports enhanced CSS customization. You can style chat elements using:[^7][^8]

```python
st.markdown("""
<style>
    .stChatInput > div > div > input {
        background-color: #ffffff;
        border: 2px solid #1f77b4;
        border-radius: 20px;
    }
    
    .stChatMessage {
        background-color: #f0f2f6;
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)
```

### File Upload Integration

The latest Streamlit versions support file uploads directly in chat input:[^2]

```python
prompt = st.chat_input(
    "Send a message or upload a file",
    accept_file=True,
    file_type=["jpg", "png", "pdf", "txt"]
)

if prompt and prompt.files:
    for file in prompt.files:
        st.image(file) if file.type.startswith('image/') else st.write(f"File: {file.name}")
```

## Best Practices and Design Patterns

### Session State Management

Always initialize session state properly and use structured data formats:[^9][^10]

```python
if "messages" not in st.session_state:
    st.session_state.messages = []

# Use consistent message structure
message_format = {"role": "user|assistant", "content": "message text"}
```

### Performance Optimization

- Initialize session state only once per session[^11]
- Use efficient message history management[^12]
- Implement proper error handling for API calls[^13]
- Consider rate limiting for production applications[^10]

### User Experience Enhancements

- Provide visual feedback during processing with `st.spinner()`[^12]
- Implement chat history export functionality[^12]
- Add clear chat and session management features[^14]
- Use appropriate loading states and error messages[^13]

This comprehensive guide provides everything needed to build professional chat UIs in Streamlit, from basic implementations to advanced features with real-time streaming, file uploads, and API integrations. The examples demonstrate progressive complexity and can be adapted for various use cases including customer support, AI assistants, and collaborative chat applications.
<span style="display:none">[^100][^101][^102][^103][^104][^105][^106][^107][^108][^109][^15][^16][^17][^18][^19][^20][^21][^22][^23][^24][^25][^26][^27][^28][^29][^30][^31][^32][^33][^34][^35][^36][^37][^38][^39][^40][^41][^42][^43][^44][^45][^46][^47][^48][^49][^50][^51][^52][^53][^54][^55][^56][^57][^58][^59][^60][^61][^62][^63][^64][^65][^66][^67][^68][^69][^70][^71][^72][^73][^74][^75][^76][^77][^78][^79][^80][^81][^82][^83][^84][^85][^86][^87][^88][^89][^90][^91][^92][^93][^94][^95][^96][^97][^98][^99]</span>

<div style="text-align: center">⁂</div>

[^1]: <https://docs.streamlit.io/develop/api-reference/chat>

[^2]: <https://docs.streamlit.io/develop/api-reference/chat/st.chat_input>

[^3]: <https://docs.streamlit.io/develop/api-reference/chat/st.chat_message>

[^4]: <https://docs.streamlit.io/develop/api-reference>

[^5]: <https://discuss.streamlit.io/t/change-default-avatars-in-st-chat/49142>

[^6]: <https://blog.streamlit.io/build-your-own-notion-chatbot/>

[^7]: <https://pythonandvba.com/blog/style_your_streamlit_app_with_custom_css/>

[^8]: <https://github.com/microsoft/Streamlit_UI_Template>

[^9]: <https://python.langchain.com/docs/integrations/memory/streamlit_chat_message_history/>

[^10]: <https://discuss.streamlit.io/t/question-regarding-session-management-for-chatbots-with-multiple-users/69117>

[^11]: <https://blog.streamlit.io/best-practices-for-building-genai-apps-with-streamlit/>

[^12]: <https://blog.futuresmart.ai/building-a-user-friendly-interface-with-streamlit-for-our-rag-chatbot>

[^13]: <https://docs.streamlit.io/develop/tutorials/chat-and-llm-apps/build-conversational-apps>

[^14]: <https://dev.to/jamesbmour/streamlit-part-7-build-a-chat-interface-51mo>

[^15]: <https://ijsrem.com/download/design-and-implementation-of-a-fine-tuned-llama-based-ai-chatbot-with-voice-and-text-interaction-using-streamlit-and-ollama/>

[^16]: <https://ieeexplore.ieee.org/document/10730503/>

[^17]: <https://onepetro.org/specet/proceedings/24CET/1-24CET/D011S014R004/543164>

[^18]: <https://ieeexplore.ieee.org/document/10430271/>

[^19]: <https://arxiv.org/html/2501.13468v1>

[^20]: <http://arxiv.org/pdf/2410.00006.pdf>

[^21]: <https://arxiv.org/pdf/1802.09055.pdf>

[^22]: <https://arxiv.org/pdf/2412.08646.pdf>

[^23]: <https://arxiv.org/pdf/1902.09022.pdf>

[^24]: <https://arxiv.org/ftp/arxiv/papers/2106/2106.14704.pdf>

[^25]: <http://arxiv.org/pdf/2403.05568.pdf>

[^26]: <https://arxiv.org/pdf/2304.12998.pdf>

[^27]: <http://arxiv.org/pdf/2307.07924.pdf>

[^28]: <https://arxiv.org/pdf/2305.05662.pdf>

[^29]: <https://arxiv.org/pdf/2111.00570.pdf>

[^30]: <https://arxiv.org/pdf/2306.08401.pdf>

[^31]: <http://arxiv.org/pdf/2401.00475.pdf>

[^32]: <http://arxiv.org/pdf/2408.08291.pdf>

[^33]: <https://arxiv.org/pdf/2305.20062.pdf>

[^34]: <https://arxiv.org/pdf/2301.05843.pdf>

[^35]: <https://discuss.streamlit.io/t/place-content-beneath-st-chat-input-element/51075>

[^36]: <https://github.com/streamlit/streamlit/issues/8564>

[^37]: <https://www.youtube.com/watch?v=J4wanZwjqFg>

[^38]: <https://discuss.streamlit.io/t/when-using-st-chat-input-inside-st-columns-chat-box-moves-up-how-to-keep-it-stuck-to-the-bottom/61578>

[^39]: <https://towardsdatascience.com/build-your-own-chatgpt-like-app-with-streamlit-20d940417389/>

[^40]: <https://discuss.streamlit.io/t/how-to-create-multiple-chat-input-in-same-app/82405>

[^41]: <https://www.youtube.com/watch?v=jYY24eNTYNg>

[^42]: <https://discuss.streamlit.io/t/chat-history-in-st-chat-input/47926>

[^43]: <https://towardsdatascience.com/step-by-step-guide-to-build-and-deploy-an-llm-powered-chat-with-memory-in-streamlit/>

[^44]: <https://pypi.org/project/streamlit-chat/>

[^45]: <https://attempto.blog/blog/langchain-chat-with-your-data-ui/>

[^46]: <https://docs.streamlit.io>

[^47]: <https://discuss.streamlit.io/t/chat-interface-ui/51941>

[^48]: <https://ieeexplore.ieee.org/document/10652626/>

[^49]: <https://www.semanticscholar.org/paper/a5c6ea37c66f9776b428d7a108692a2096051322>

[^50]: <https://arxiv.org/abs/2502.08756>

[^51]: <https://link.springer.com/10.1007/978-3-319-15687-3_3>

[^52]: <https://www.semanticscholar.org/paper/a9bf28b32596b60b814ae9fcb301eda9075fb686>

[^53]: <https://ieeexplore.ieee.org/document/11085390/>

[^54]: <http://link.springer.com/10.1007/978-1-4302-5858-2>

[^55]: <http://link.springer.com/10.1007/978-1-4302-6365-4_5>

[^56]: <http://link.springer.com/10.1007/978-3-540-70816-2_8>

[^57]: <https://www.semanticscholar.org/paper/c9f7089fd6bac5b65464737e80a1c5d7fa90dc9a>

[^58]: <https://arxiv.org/pdf/2009.03101.pdf>

[^59]: <https://arxiv.org/pdf/2301.06474.pdf>

[^60]: <https://arxiv.org/pdf/2302.07406.pdf>

[^61]: <https://www.mdpi.com/2078-2489/13/5/236/pdf?version=1653664375>

[^62]: <http://arxiv.org/pdf/2401.09051.pdf>

[^63]: <http://arxiv.org/pdf/2303.07839.pdf>

[^64]: <https://discuss.streamlit.io/t/st-write-typewritter/43111>

[^65]: <https://stackoverflow.com/questions/78091501/streamlit-st-write-stream-function-removes-all-newline-characters-in-the-respons>

[^66]: <https://blog.streamlit.io/designing-streamlit-apps-for-the-user-part-ii/>

[^67]: <https://discuss.streamlit.io/t/any-way-to-slow-st-write-stream/84237>

[^68]: <https://www.reddit.com/r/LangChain/comments/1dngwkn/langgraph_streamlit_state_management/>

[^69]: <https://discuss.streamlit.io/t/streaming-in-chat-but-without-typewriter-effect/63112>

[^70]: <https://discuss.streamlit.io/t/how-to-create-a-chat-history-on-the-side-bar-just-like-chatgpt/59492>

[^71]: <https://dev-kit.io/blog/python/streamlit-real-time-design-patterns-creating-interactive-and-dynamic-data-visualizations>

[^72]: <https://discuss.streamlit.io/t/testing-a-chat-history-for-streamlit-need-your-suggestions/80631>

[^73]: <https://www.deeplearningnerds.com/create-a-chatbot-gui-with-streamlit-in-python-a-step-by-step-guide/>

[^74]: <https://discuss.streamlit.io/t/seeking-help-to-restore-streaming-mode-text-display-in-streamlit-after-openai-update/61671>

[^75]: <https://uxdesign.cc/designing-for-ai-engineers-what-ui-patterns-and-principles-you-need-to-know-8b16a5b62a61>

[^76]: <https://docs.streamlit.io/develop/api-reference/write-magic/st.write_stream>

[^77]: <https://python.plainenglish.io/how-to-use-a-typewriter-effect-in-your-streamlit-app-c4c300f6f5bd>

[^78]: <https://arxiv.org/html/2406.13093>

[^79]: <https://arxiv.org/html/2306.09864>

[^80]: <https://arxiv.org/html/2503.11978v1>

[^81]: <https://arxiv.org/html/2310.02739v2>

[^82]: <https://arxiv.org/pdf/2311.06772.pdf>

[^83]: <http://arxiv.org/pdf/2405.00954.pdf>

[^84]: <https://arxiv.org/html/2304.00334>

[^85]: <http://arxiv.org/pdf/2502.13133.pdf>

[^86]: <https://dl.acm.org/doi/pdf/10.1145/3613904.3642472>

[^87]: <https://www.aclweb.org/anthology/W18-5027.pdf>

[^88]: <https://arxiv.org/pdf/2311.17917.pdf>

[^89]: <https://arxiv.org/html/2308.04830v3>

[^90]: <https://arxiv.org/pdf/2304.11093.pdf>

[^91]: <https://arxiv.org/abs/2211.07818>

[^92]: <https://arxiv.org/pdf/2312.15430.pdf>

[^93]: <https://arxiv.org/html/2503.08165v1>

[^94]: <https://arxiv.org/pdf/2503.01158.pdf>

[^95]: <https://arxiv.org/pdf/2108.09355.pdf>

[^96]: <http://arxiv.org/pdf/2405.15758.pdf>

[^97]: <http://arxiv.org/pdf/2311.15230.pdf>

[^98]: <https://github.com/sbslee/streamlit-openai>

[^99]: <https://dev.to/jamesbmour/building-an-advanced-streamlit-chatbot-with-openai-integration-a-comprehensive-guide-part-3-59d6>

[^100]: <https://www.youtube.com/watch?v=jbJpAdGlKVY>

[^101]: <https://www.youtube.com/watch?v=6fs80o7Xm4I>

[^102]: <https://www.akratech.in/enhancing-streamlit-apps-with-custom-html-and-css/>

[^103]: <https://discuss.streamlit.io/t/how-to-implement-a-three-column-layout-in-chat-input/59466>

[^104]: <https://discuss.streamlit.io/t/how-can-i-change-the-css-of-the-chatbot/64301>

[^105]: <https://www.youtube.com/watch?v=B1SRA7wGQH8>

[^106]: <https://discuss.streamlit.io/t/introducing-streamlit-openai-a-streamlit-component-for-building-powerful-openai-chat-interfaces/114742>

[^107]: <https://discuss.streamlit.io/t/css-styling-the-color-of-st-chat-input/60470>

[^108]: <https://docs.streamlit.io/develop/api-reference/layout/st.sidebar>

[^109]: <https://docs.streamlit.io/develop/concepts/configuration/theming>

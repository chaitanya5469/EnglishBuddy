import requests
import streamlit as st
from datetime import datetime
import subprocess
import time
import os

# Start FastAPI server in background (only once)
if 'server_started' not in st.session_state:
    try:
        subprocess.Popen(["uvicorn", "serve:app", "--host", "0.0.0.0", "--port", "8000"])
        time.sleep(3)  # Wait for server to start
        st.session_state.server_started = True
    except Exception as e:
        st.error(f"Failed to start server: {e}")

# Page configuration
st.set_page_config(
    page_title="English Buddy",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for beautiful styling with dark/light mode support
st.markdown("""
<style>
    /* Main container styling */
    .main {
        padding: 2rem;
    }
    
    /* Header styling */
    .header-container {
        text-align: center;
        padding: 2rem 0;
        margin-bottom: 2rem;
        border-bottom: 2px solid;
        border-image: linear-gradient(90deg, #667eea 0%, #764ba2 100%) 1;
    }
    
    .app-title {
        font-size: 3rem;
        font-weight: 700;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    
    .app-subtitle {
        font-size: 1.2rem;
        opacity: 0.7;
    }
    
    /* Chat message styling */
    .chat-container {
        max-width: 800px;
        margin: 0 auto;
        padding: 1rem;
    }
    
    .message {
        padding: 1rem 1.5rem;
        margin: 1rem 0;
        border-radius: 1rem;
        animation: fadeIn 0.3s ease-in;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        margin-left: 2rem;
        box-shadow: 0 4px 6px rgba(102, 126, 234, 0.3);
    }
    
    .bot-message {
        background: var(--bot-message-bg);
        border: 1px solid var(--bot-message-border);
        margin-right: 2rem;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    /* Dark mode variables */
    @media (prefers-color-scheme: dark) {
        :root {
            --bot-message-bg: #262730;
            --bot-message-border: #3d3d4a;
        }
    }
    
    /* Light mode variables */
    @media (prefers-color-scheme: light) {
        :root {
            --bot-message-bg: #f7f7f8;
            --bot-message-border: #e5e5e8;
        }
    }
    
    .message-header {
        font-weight: 600;
        margin-bottom: 0.5rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .message-time {
        font-size: 0.75rem;
        opacity: 0.7;
    }
    
    .message-content {
        line-height: 1.6;
    }
    
    /* Input area styling */
    .input-container {
        position: sticky;
        bottom: 0;
        background: var(--background-color);
        padding: 1.5rem 0;
        border-top: 1px solid var(--border-color);
        margin-top: 2rem;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        border-radius: 0.5rem;
        font-weight: 600;
        transition: transform 0.2s, box-shadow 0.2s;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(102, 126, 234, 0.4);
    }
    
    /* Clear chat button */
    .clear-button {
        text-align: center;
        margin: 1rem 0;
    }
    
    /* Empty state */
    .empty-state {
        text-align: center;
        padding: 4rem 2rem;
        opacity: 0.6;
    }
    
    .empty-state-icon {
        font-size: 4rem;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state for conversation history
if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'input_key' not in st.session_state:
    st.session_state.input_key = 0

# Get API URL from environment, default to localhost for development
API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")

def get_groq_response(input_text):
    """Send request to the API and get response"""
    json_body = {
        "input": {
            "text": input_text
        },
        "config": {},
        "kwargs": {}
    }
    try:
        response = requests.post(f"{API_URL}/chain/invoke", json=json_body, timeout=30)
        result = response.json()
        
        if 'output' in result:
            return result['output']
        return result
    except Exception as e:
        return f"Error: Unable to connect to the server. {str(e)}"

def display_message(role, content, timestamp):
    """Display a chat message with styling"""
    message_class = "user-message" if role == "user" else "bot-message"
    icon = "👤" if role == "user" else "🤖"
    role_name = "You" if role == "user" else "English Buddy"
    
    st.markdown(f"""
    <div class="message {message_class}">
        <div class="message-header">
            <span>{icon}</span>
            <span>{role_name}</span>
            <span class="message-time">{timestamp}</span>
        </div>
        <div class="message-content">{content}</div>
    </div>
    """, unsafe_allow_html=True)

# Header
st.markdown("""
<div class="header-container">
    <div class="app-title">💬 English Buddy</div>
    <div class="app-subtitle">Your AI-powered English learning companion</div>
</div>
""", unsafe_allow_html=True)

# Main chat container
st.markdown('<div class="chat-container">', unsafe_allow_html=True)

# Display conversation history
if st.session_state.messages:
    for message in st.session_state.messages:
        display_message(message['role'], message['content'], message['timestamp'])
else:
    st.markdown("""
    <div class="empty-state">
        <div class="empty-state-icon">💭</div>
        <div>Start a conversation by typing a message below!</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# Clear chat button
col1, col2, col3 = st.columns([1, 1, 1])
with col2:
    if st.button("🗑️ Clear Chat", use_container_width=True) and st.session_state.messages:
        st.session_state.messages = []
        st.session_state.input_key += 1
        st.rerun()

# Input area
st.markdown("---")
col1, col2 = st.columns([5, 1])

with col1:
    input_text = st.text_input(
        "Message",
        placeholder="Type your message here...",
        label_visibility="collapsed",
        key=f"user_input_{st.session_state.input_key}"
    )

with col2:
    send_button = st.button("Send", use_container_width=True)

# Handle message sending
if send_button and input_text.strip():
    # Get current timestamp
    timestamp = datetime.now().strftime("%H:%M")
    
    # Add user message to history
    st.session_state.messages.append({
        'role': 'user',
        'content': input_text,
        'timestamp': timestamp
    })
    
    # Get bot response
    with st.spinner("Thinking..."):
        bot_response = get_groq_response(input_text)
    
    # Add bot response to history
    st.session_state.messages.append({
        'role': 'bot',
        'content': bot_response,
        'timestamp': datetime.now().strftime("%H:%M")
    })
    
    # Increment key to clear input field
    st.session_state.input_key += 1
    
    # Rerun to update the display
    st.rerun()
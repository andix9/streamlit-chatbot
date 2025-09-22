import streamlit as st
import requests
import json
from datetime import datetime
import time
import re

# Page configuration
st.set_page_config(
    page_title="AI Chatbot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .stApp {
        max-width: 1200px;
        margin: 0 auto;
    }
    .chat-container {
        border-radius: 10px;
        padding: 20px;
        background-color: #f0f2f6;
    }
    .user-message {
        background-color: #2e7dea;
        color: white;
        padding: 10px;
        border-radius: 15px;
        margin: 5px 0;
    }
    .bot-message {
        background-color: white;
        padding: 10px;
        border-radius: 15px;
        margin: 5px 0;
    }
    .sidebar .sidebar-content {
        background-color: #f0f2f6;
    }
    </style>
    """, unsafe_allow_html=True)

def clean_response(content):
    """Clean up AI response by removing common markup tokens and formatting issues"""
    if not content:
        return ""
    
    # Remove common model tokens
    tokens_to_remove = [
        "<s>", "</s>", "<|s|>", "<|/s|>",
        "[OUT]", "[/OUT]", "[INST]", "[/INST]",
        "<|im_start|>", "<|im_end|>",
        "<|assistant|>", "<|user|>", "<|system|>",
        "<<SYS>>", "<</SYS>>",
        "###", "Assistant:", "Human:", "User:"
    ]
    
    for token in tokens_to_remove:
        content = content.replace(token, "")
    
    # Remove extra whitespace and clean up
    content = re.sub(r'\s+', ' ', content)  # Replace multiple spaces with single space
    content = content.strip()
    
    return content

def get_ai_response(messages_payload, model, temperature):
    api_key = st.secrets["OPENROUTER_API_KEY"]
    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            },
            data=json.dumps({
                "model": model,
                "messages": messages_payload,
                "max_tokens": 1000,
                "temperature": temperature,
            })
        )
        if response.status_code != 200:
            st.error(f"Error: {response.text}")
            return None
        content = response.json()["choices"][0]["message"]["content"]
        # Clean up common markup tokens and formatting
        content = clean_response(content)
        return content
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None

# Sidebar
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/0/04/ChatGPT_logo.svg", width=100)
    st.title("Settings")
    
    # Model selection with descriptions
    model_options = {
        "Mistral 7B (Free)": {
            "id": "mistralai/mistral-7b-instruct:free",
            "description": "Powerful open-source model with good general capabilities"
        },
        "DeepSeek V3 (Free)": {
            "id": "deepseek/deepseek-chat-v3-0324:free",
            "description": "Advanced model with strong reasoning abilities"
        },
        "Llama 3.1 8B (Free)": {
            "id": "meta-llama/llama-3.1-8b-instruct:free",
            "description": "Meta's latest model with broad knowledge"
        },
        "Grok 3 (Free)": {
            "id": "x-ai/grok-4-fast:free",
            "description": "Grok 3 is a powerful model with strong reasoning abilities"
        }
    }

    selected_model_name = st.selectbox(
        "Select Model",
        options=list(model_options.keys()),
        index=0,
    )
    st.caption(model_options[selected_model_name]["description"])
    
    # Temperature slider
    temperature = st.slider("Temperature", 0.0, 1.0, 0.7, 0.1,
                          help="Higher values make the output more random, lower values make it more focused")
    
    # Clear chat button
    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.session_state.message_count = 0
        st.rerun()

# Main chat interface
st.title("🤖 AI Chatbot")
st.markdown("---")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "message_count" not in st.session_state:
    st.session_state.message_count = 0

# Chat container
chat_container = st.container()
with chat_container:
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# User input
prompt = st.chat_input("Type your message here...")
if prompt:
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.session_state.message_count += 1
    
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get AI response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            messages_for_api = st.session_state.messages.copy()
            selected_model_id = model_options[selected_model_name]["id"]
            ai_response = get_ai_response(messages_for_api, selected_model_id, temperature)
            
            if ai_response:
                # Add typing effect
                message_placeholder = st.empty()
                full_response = ""
                for chunk in ai_response.split():
                    full_response += chunk + " "
                    time.sleep(0.05)
                    message_placeholder.markdown(full_response + "▌")
                message_placeholder.markdown(full_response)
                
                # Store assistant response
                st.session_state.messages.append({"role": "assistant", "content": ai_response})
                st.session_state.message_count += 1
            else:
                st.error("Failed to get AI response")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center'>
        <p>Made with ❤️ using Streamlit</p>
        <p>Current time: {}</p>
    </div>
    """.format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
    unsafe_allow_html=True
)
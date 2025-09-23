import streamlit as st
import requests
import json
from datetime import datetime
import time
import re

# Page configuration
st.set_page_config(
    page_title="Andika's Chatbot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Sidebar
with st.sidebar:
    # Ganti logo (pakai URL/ path gambar Anda)
    st.image("https://upload.wikimedia.org/wikipedia/commons/0/04/ChatGPT_logo.svg", width=100)
    st.title("⚙️ Settings")

    # Mode gelap / terang
    dark_mode = st.toggle("🌙 Dark Mode", value=False)

    # Pilihan model
    model_options = {
        "Mistral 7B (Free)": 
            {"id": "mistralai/mistral-7b-instruct:free", 
            "description": "Powerful open-source model with good general capabilities"
            },
        "DeepSeek V3.1 (Free)": 
            {"id": "deepseek/deepseek-chat-v3.1:free", 
            "description": "Advanced model with strong reasoning abilities"
            },
        "OpenAI: gpt-oss-20b (free)": 
            {"id": "openai/gpt-oss-20b:free", 
            "description": "Meta's latest model with broad knowledge"
            },
        "Grok 3 (Free)": 
            {"id": "x-ai/grok-4-fast:free", 
            "description": "Grok 3 is a powerful model with strong reasoning abilities"
            }
    }

    selected_model_name = st.selectbox("🧠 Select Model", list(model_options.keys()), index=0)
    st.caption(model_options[selected_model_name]["description"])

    temperature = st.slider("🎛️ Temperature", 0.0, 1.0, 0.7, 0.1)

    if st.button("🧹 Clear Chat History"):
        st.session_state["chat_histories"][model_options[selected_model_name]["id"]] = []
        st.rerun()

# CSS Theme (Light & Dark mode)
if dark_mode:
    bg_color = "#1e1e1e"
    text_color = "#f5f5f5"
    user_bg = "linear-gradient(135deg, #0078ff, #0056b3)"
    bot_bg = "#2d2d2d"
else:
    bg_color = "linear-gradient(135deg, #f9f9f9 0%, #eef2f7 100%)"
    text_color = "#2d3436"
    user_bg = "linear-gradient(135deg, #2e7dea, #1b5cb8)"
    bot_bg = "#f8f9fa"

st.markdown(f"""
    <style>
    .stApp {{
        max-width: 1200px;
        margin: 0 auto;
        font-family: 'Segoe UI', sans-serif;
        background: {bg_color};
        color: {text_color};
    }}
    .user-message {{
        background: {user_bg};
        color: white;
        padding: 12px 16px;
        border-radius: 18px;
        margin: 8px 0;
        max-width: 80%;
    }}
    .bot-message {{
        background: {bot_bg};
        padding: 12px 16px;
        border-radius: 18px;
        margin: 8px 0;
        max-width: 80%;
    }}
    h1, h2, h3 {{
        font-weight: 600;
        color: {text_color};
    }}
    </style>
    """, unsafe_allow_html=True)

# Function untuk bersihkan response
def clean_response(content):
    if not content:
        return ""
    tokens_to_remove = [
        "<s>", "</s>", "<|s|>", "<|/s|>", "[OUT]", "[/OUT]", "[INST]", "[/INST]",
        "<|im_start|>", "<|im_end|>", "<|assistant|>", "<|user|>", "<|system|>",
        "<<SYS>>", "<</SYS>>", "###", "Assistant:", "Human:", "User:"
    ]
    for token in tokens_to_remove:
        content = content.replace(token, "")
    return re.sub(r'\s+', ' ', content).strip()

# Function untuk API call
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
        return clean_response(response.json()["choices"][0]["message"]["content"])
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None

# Session state untuk multi-model chat history
if "chat_histories" not in st.session_state:
    st.session_state["chat_histories"] = {}

selected_model_id = model_options[selected_model_name]["id"]
if selected_model_id not in st.session_state["chat_histories"]:
    st.session_state["chat_histories"][selected_model_id] = []

# Main chat interface
st.title("🤖 Andika's Chatbot")
st.write("Ask me anything, and I'll try my best to help you!")
st.markdown("---")

chat_container = st.container()
with chat_container:
    for message in st.session_state["chat_histories"][selected_model_id]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

prompt = st.chat_input("💬 Type your message here...")
if prompt:
    st.session_state["chat_histories"][selected_model_id].append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("🤔 Thinking..."):
            messages_for_api = st.session_state["chat_histories"][selected_model_id].copy()
            ai_response = get_ai_response(messages_for_api, selected_model_id, temperature)

            if ai_response:
                message_placeholder = st.empty()
                full_response = ""
                for chunk in ai_response.split():
                    full_response += chunk + " "
                    time.sleep(0.04)
                    message_placeholder.markdown(full_response + "▌")
                message_placeholder.markdown(full_response)

                st.session_state["chat_histories"][selected_model_id].append({"role": "assistant", "content": ai_response})
            else:
                st.error("⚠️ Failed to get AI response")

# Footer
st.markdown("---")
st.markdown(
    f"""
    <div style='text-align: center; font-size: 14px;'>
        <p>Made with ❤️ by Andika using Streamlit</p>
        <p>🕒 Current time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
    </div>
    """,
    unsafe_allow_html=True
)

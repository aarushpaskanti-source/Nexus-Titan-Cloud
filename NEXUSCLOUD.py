import streamlit as st
from google import genai
from google.genai import types
import datetime
import json
import os

# --- 1. CONFIG & SETTINGS ---
API_KEY = st.secrets["GEMINI_KEY"]

st.set_page_config(page_title="NEXUS TITAN", page_icon="⚡", layout="wide")

# --- 2. PERSISTENT MEMORY FUNCTIONS ---
MEMORY_FILE = "cloud_memory.json"

def load_memory():
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r") as f:
                return json.load(f)
        except: return {"Main Chat": []}
    return {"Main Chat": []}

def save_memory(data):
    with open(MEMORY_FILE, "w") as f:
        json.dump(data, f)

# --- 3. INITIALIZE STATE ---
if "all_chats" not in st.session_state:
    st.session_state.all_chats = load_memory()
if "current_chat" not in st.session_state:
    st.session_state.current_chat = "Main Chat"
if "ai_name" not in st.session_state:
    st.session_state.ai_name = "NEXUS TITAN"

# --- 4. THE SIDEBAR (CHATS & SETTINGS) ---
with st.sidebar:
    st.title("⚡ NEXUS CORE")
    
    # --- CHAT MANAGEMENT ---
    st.subheader("🗂️ Your Chats")
    if st.button("➕ Start New Chat", use_container_width=True):
        new_name = f"Chat {len(st.session_state.all_chats) + 1}"
        st.session_state.all_chats[new_name] = []
        st.session_state.current_chat = new_name
        save_memory(st.session_state.all_chats)
        st.rerun()
    
    st.divider()
    for chat_name in list(st.session_state.all_chats.keys()):
        cols = st.columns([0.8, 0.2])
        if cols[0].button(chat_name, key=f"btn_{chat_name}", use_container_width=True):
            st.session_state.current_chat = chat_name
            st.rerun()
        if cols[1].button("🗑️", key=f"del_{chat_name}"):
            if len(st.session_state.all_chats) > 1:
                del st.session_state.all_chats[chat_name]
                st.session_state.current_chat = list(st.session_state.all_chats.keys())[0]
                save_memory(st.session_state.all_chats)
                st.rerun()

    st.divider()
    
    # --- SETTINGS MENU ---
    with st.expander("⚙️ AI Personalization"):
        st.session_state.ai_name = st.text_input("AI Display Name", value=st.session_state.ai_name)
        creativity = st.slider("Creativity Level (Temp)", 0.0, 1.0, 0.7)
        st.info(f"Owner: Aarush Paskanti")

# --- 5. CHAT ENGINE ---
client = genai.Client(api_key=API_KEY)
current_messages = st.session_state.all_chats[st.session_state.current_chat]

# Header
st.title(f"⚡ {st.session_state.ai_name}")
st.caption(f"Active Chat: {st.session_state.current_chat} | Created by Aarush Paskanti")

# First Greeting
if len(current_messages) == 0:
    hr = datetime.datetime.now().hour
    greet = "Good morning" if hr < 12 else "Good afternoon" if hr < 18 else "Good evening"
    current_messages.append({"role": "model", "text": f"{greet}, Macha! {st.session_state.ai_name} Cloud Core is ready."})
    save_memory(st.session_state.all_chats)

# Display Messages
for msg in current_messages:
    role = "assistant" if msg["role"] == "model" else "user"
    with st.chat_message(role):
        st.markdown(msg["text"])

# Input
if prompt := st.chat_input(f"Message {st.session_state.ai_name}..."):
    current_messages.append({"role": "user", "text": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        status = st.empty()
        status.markdown("TITAN IS THINKING... ⚙️")
        
        try:
            gemini_history = [types.Content(role=m["role"], parts=[types.Part.from_text(text=m["text"])]) for m in current_messages[:-1]]
            
            chat = client.chats.create(
                model='gemini-2.0-flash',
                history=gemini_history,
                config=types.GenerateContentConfig(
                    system_instruction=f"You are {st.session_state.ai_name}, an elite AI created and owned by Aarush Paskanti. Be brilliant at JEE Science and Python.",
                    temperature=creativity
                )
            )
            
            response = chat.send_message(prompt)
            status.markdown(response.text)
            current_messages.append({"role": "model", "text": response.text})
            save_memory(st.session_state.all_chats)
            
        except Exception as e:
            status.error(f"Error: {e}")

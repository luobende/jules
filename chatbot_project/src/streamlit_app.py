# chatbot_project/src/streamlit_app.py

import streamlit as st
import sys
import os
import json # For JSON export
from datetime import datetime # For unique filenames

# 1. Path Setup for Imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.chatbot import Chatbot
from config.config import load_config

# 2. App Title
st.title("💬 Configurable Chatbot")

# --- Helper functions for Export ---
def _prepare_text_export(messages: list) -> str:
    """Formats conversation history into a plain text string."""
    export_string = ""
    for message in messages:
        role = message["role"].capitalize()
        content = message["content"]
        export_string += f"{role}: {content}\n\n"
    return export_string.strip()

def _prepare_json_export(messages: list) -> str:
    """Formats conversation history into a JSON string."""
    return json.dumps(messages, indent=2)

# --- Configuration and Initialization ---
if 'chatbot_initialized' not in st.session_state:
    st.session_state.chatbot_initialized = False
    st.session_state.api_key = None
    st.session_state.base_url = None
    st.session_state.configured_models = []
    st.session_state.available_models = []
    st.session_state.selected_model = None 

# Load configuration only once
if not st.session_state.chatbot_initialized:
    config_file_path = os.path.join(project_root, 'config', 'config.ini')
    
    original_stdout = sys.stdout
    sys.stdout = open(os.devnull, 'w')
    api_key, base_url, configured_models_list = load_config(config_file_path=config_file_path)
    sys.stdout.close()
    sys.stdout = original_stdout

    st.session_state.api_key = api_key
    st.session_state.base_url = base_url
    st.session_state.configured_models = configured_models_list

    if not st.session_state.api_key or not st.session_state.base_url:
        st.error("🔴 API Key or Base URL not configured. Please set them via environment variables or update `config/config.ini`.")
        st.warning("Ensure `config/config.ini` is in the `config` directory, or env vars `OPENAI_API_KEY` and `OPENAI_BASE_URL` are set.")
        st.stop()
    else:
        st.session_state.chatbot_instance = Chatbot(api_key=st.session_state.api_key, base_url=st.session_state.base_url)
        st.session_state.chatbot_initialized = True
        if st.session_state.configured_models:
            st.session_state.available_models = st.session_state.configured_models
        else:
            st.session_state.available_models = ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"] 
            st.sidebar.info("No models configured. Using default list. Configure in `config/config.ini` or via `OPENAI_MODELS` env var.")

        if not st.session_state.selected_model and st.session_state.available_models:
            st.session_state.selected_model = st.session_state.available_models[0]
        
        st.success(f"Chatbot initialized. Default instance model: {st.session_state.chatbot_instance.model}", icon="✅")


# --- Sidebar UI Elements ---
if st.session_state.chatbot_initialized:
    # Model Selection
    if st.session_state.available_models:
        if st.session_state.selected_model not in st.session_state.available_models:
            st.session_state.selected_model = st.session_state.available_models[0]
            
        try:
            current_model_index = st.session_state.available_models.index(st.session_state.selected_model)
        except ValueError:
            current_model_index = 0 

        selected_model_from_ui = st.sidebar.selectbox(
            "Choose a Model:",
            options=st.session_state.available_models,
            index=current_model_index,
            key="model_select_key" 
        )
        
        if selected_model_from_ui != st.session_state.selected_model:
            st.session_state.selected_model = selected_model_from_ui
            st.sidebar.success(f"Model changed to: {st.session_state.selected_model}", icon="🔄")

        st.sidebar.info(f"Using model: **{st.session_state.selected_model}**")
    else:
        st.sidebar.warning("No models available for selection.")

    st.sidebar.markdown("---") 

    # Clear Chat History Button
    if st.sidebar.button("Clear Chat History", key="clear_chat_button"):
        st.session_state.messages = []
        st.sidebar.success("Chat history cleared!", icon="🗑️")
        st.experimental_rerun()

    st.sidebar.markdown("---") # Separator before export buttons

    # Export Conversation Buttons
    st.sidebar.subheader("Export Conversation")
    
    # Disable buttons if no messages
    export_disabled = not st.session_state.get("messages", [])

    # Generate a unique part for the filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # TXT Export
    plain_text_data = _prepare_text_export(st.session_state.get("messages", []))
    st.sidebar.download_button(
        label="Export as TXT",
        data=plain_text_data,
        file_name=f"conversation_{timestamp}.txt",
        mime="text/plain",
        key="export_txt_button",
        disabled=export_disabled,
        help="Exports the current chat conversation to a plain text file."
    )

    # JSON Export
    json_data = _prepare_json_export(st.session_state.get("messages", []))
    st.sidebar.download_button(
        label="Export as JSON",
        data=json_data,
        file_name=f"conversation_{timestamp}.json",
        mime="application/json",
        key="export_json_button",
        disabled=export_disabled,
        help="Exports the current chat conversation to a JSON file."
    )


# --- Chat History Management and Display ---
if "messages" not in st.session_state:
    st.session_state.messages = [] # Ensure messages list exists

for message in st.session_state.messages: # Use .get for safety, though initialized above
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# --- User Input and Chatbot Response ---
if prompt := st.chat_input("What's on your mind?"):
    if not st.session_state.chatbot_initialized:
        st.error("Chatbot is not initialized. Please check configuration.")
        st.stop()
    if not st.session_state.selected_model and st.session_state.available_models: 
        st.error("No model selected. Please choose a model from the sidebar.")
        st.stop()
    if not st.session_state.available_models: 
        st.error("No models available or configured. Cannot send message.")
        st.stop()

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        with st.spinner(f"Thinking with {st.session_state.selected_model}... 🤔"):
            history_for_api = st.session_state.messages[:-1]

            original_stdout_chatbot = sys.stdout
            sys.stdout = open(os.devnull, 'w')
            response = st.session_state.chatbot_instance.send_message(
                message_content=prompt,
                conversation_history=history_for_api,
                model_name=st.session_state.selected_model 
            )
            sys.stdout.close()
            sys.stdout = original_stdout_chatbot

            if response:
                message_placeholder.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
            else:
                message_placeholder.error("😕 Sorry, I couldn't get a response. Check console for details.")

# --- Sidebar Information ---
st.sidebar.markdown("---")
st.sidebar.info("Conversation history is session-based. Refreshing the page clears history. Model changes apply to new messages.")

# For debugging:
# if st.sidebar.checkbox("Show Session State Details"):
#    st.sidebar.write(st.session_state)

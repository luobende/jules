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
# Initialize session state variables if they don't exist
default_session_state = {
    'chatbot_initialized': False,
    'api_key': None,
    'base_url': None,
    'configured_models_list': [], # From config file/env
    'dynamic_models_list': None,  # From API endpoint
    'ui_model_options': [],       # Final list for UI selectbox
    'model_source_info': "",      # Info about where the model list came from
    'selected_model': None,
    'messages': []
}
for key, value in default_session_state.items():
    if key not in st.session_state:
        st.session_state[key] = value

# Load configuration and initialize chatbot only once
if not st.session_state.chatbot_initialized:
    config_file_path = os.path.join(project_root, 'config', 'config.ini')
    
    original_stdout = sys.stdout
    sys.stdout = open(os.devnull, 'w') # Suppress prints from load_config
    api_key, base_url, configured_models = load_config(config_file_path=config_file_path)
    sys.stdout.close() # Restore stdout
    sys.stdout = original_stdout

    st.session_state.api_key = api_key
    st.session_state.base_url = base_url
    st.session_state.configured_models_list = configured_models # Store manually configured models

    if not st.session_state.api_key or not st.session_state.base_url:
        st.error("🔴 API Key or Base URL not configured. Please set them via environment variables or update `config/config.ini`.")
        st.warning("Ensure `config/config.ini` is in the `config` directory, or env vars `OPENAI_API_KEY` and `OPENAI_BASE_URL` are set.")
        st.stop()
    else:
        st.session_state.chatbot_instance = Chatbot(api_key=st.session_state.api_key, base_url=st.session_state.base_url)
        st.session_state.chatbot_initialized = True
        st.success(f"Chatbot initialized. Default instance model: {st.session_state.chatbot_instance.model}", icon="✅")

        # Fetch dynamic models and determine UI options (runs once after chatbot init)
        original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w') # Suppress prints from get_available_models
        dynamic_models = st.session_state.chatbot_instance.get_available_models()
        sys.stdout.close() # Restore stdout
        sys.stdout = original_stdout
        
        st.session_state.dynamic_models_list = dynamic_models # Store dynamic models (can be None)

        # Prioritization Logic for UI model options
        default_models_for_ui = ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"] # Hardcoded default
        
        api_fetch_failed = st.session_state.dynamic_models_list is None

        if st.session_state.dynamic_models_list and len(st.session_state.dynamic_models_list) > 0:
            st.session_state.ui_model_options = st.session_state.dynamic_models_list
            st.session_state.model_source_info = "Models loaded from API."
        elif st.session_state.configured_models_list and len(st.session_state.configured_models_list) > 0:
            st.session_state.ui_model_options = st.session_state.configured_models_list
            source_msg = "Using manually configured model list."
            if api_fetch_failed:
                source_msg = "Failed to load from API. " + source_msg
            st.session_state.model_source_info = source_msg
        else:
            st.session_state.ui_model_options = default_models_for_ui
            source_msg = "Using default model list."
            if api_fetch_failed:
                source_msg = "Failed to load from API & no manual config. " + source_msg
            st.session_state.model_source_info = source_msg
        
        # Set initial selected_model based on the final ui_model_options
        if not st.session_state.selected_model and st.session_state.ui_model_options:
            st.session_state.selected_model = st.session_state.ui_model_options[0]
        elif st.session_state.selected_model not in st.session_state.ui_model_options and st.session_state.ui_model_options:
            # If previous selection is no longer valid, default to first available
            st.session_state.selected_model = st.session_state.ui_model_options[0]


# --- Sidebar UI Elements ---
if st.session_state.chatbot_initialized:
    st.sidebar.caption(st.session_state.model_source_info)

    # Model Selection
    if st.session_state.ui_model_options:
        # Ensure selected_model is valid, default if not
        if st.session_state.selected_model not in st.session_state.ui_model_options:
            st.session_state.selected_model = st.session_state.ui_model_options[0]
            # Consider st.experimental_rerun() if immediate UI update for selected_model is critical before next interaction
            
        try:
            current_model_index = st.session_state.ui_model_options.index(st.session_state.selected_model)
        except ValueError: # Should not happen if above logic is correct
            current_model_index = 0 

        selected_model_from_ui = st.sidebar.selectbox(
            "Choose a Model:",
            options=st.session_state.ui_model_options,
            index=current_model_index,
            key="model_select_key" 
        )
        
        if selected_model_from_ui != st.session_state.selected_model:
            st.session_state.selected_model = selected_model_from_ui
            st.sidebar.success(f"Model changed to: {st.session_state.selected_model}", icon="🔄")

        st.sidebar.info(f"Using model: **{st.session_state.selected_model}**")
    else: # No models available from any source
        st.sidebar.warning("No models available for selection. Chat functionality may be limited.")
        st.session_state.selected_model = None # Ensure no model is selected

    st.sidebar.markdown("---") 

    # Clear Chat History Button
    if st.sidebar.button("Clear Chat History", key="clear_chat_button"):
        st.session_state.messages = []
        st.sidebar.success("Chat history cleared!", icon="🗑️")
        st.experimental_rerun()

    st.sidebar.markdown("---") 

    # Export Conversation Buttons
    st.sidebar.subheader("Export Conversation")
    export_disabled = not st.session_state.messages
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    plain_text_data = _prepare_text_export(st.session_state.messages)
    st.sidebar.download_button(
        label="Export as TXT", data=plain_text_data, file_name=f"conversation_{timestamp}.txt",
        mime="text/plain", key="export_txt_button", disabled=export_disabled,
        help="Exports the current chat conversation to a plain text file."
    )

    json_data = _prepare_json_export(st.session_state.messages)
    st.sidebar.download_button(
        label="Export as JSON", data=json_data, file_name=f"conversation_{timestamp}.json",
        mime="application/json", key="export_json_button", disabled=export_disabled,
        help="Exports the current chat conversation to a JSON file."
    )

# --- Chat History Display ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- User Input and Chatbot Response ---
if prompt := st.chat_input("What's on your mind?"):
    if not st.session_state.chatbot_initialized:
        st.error("Chatbot is not initialized. Please check configuration.")
        st.stop()
    if not st.session_state.selected_model: # Covers case where ui_model_options was empty
        st.error("No model selected or available. Please choose a model or check configuration.")
        st.stop()

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        with st.spinner(f"Thinking with {st.session_state.selected_model}... 🤔"):
            history_for_api = st.session_state.messages[:-1]

            original_stdout_chatbot = sys.stdout
            sys.stdout = open(os.devnull, 'w') # Suppress prints from send_message
            response = st.session_state.chatbot_instance.send_message(
                message_content=prompt,
                conversation_history=history_for_api,
                model_name=st.session_state.selected_model 
            )
            sys.stdout.close() # Restore stdout
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

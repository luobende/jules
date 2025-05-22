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
st.title("💬 Configurable Chatbot with Context Management")

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
    'configured_models_list': [], 
    'dynamic_models_list': None,  
    'ui_model_options': [],       
    'model_source_info': "",      
    'selected_model': None,
    'full_chat_history': [], # Renamed from 'messages'
    'knowledge_base_summary': "", # New for context management
    'context_config': {}, # New for context management parameters
    'model_config_params': {} # New for model-specific parameters like max_tokens
}
for key, value in default_session_state.items():
    if key not in st.session_state:
        st.session_state[key] = value

# Migrate old 'messages' to 'full_chat_history' if it exists
if "messages" in st.session_state and "full_chat_history" not in st.session_state:
    st.session_state.full_chat_history = st.session_state.messages
    del st.session_state.messages
elif "messages" in st.session_state and "full_chat_history" in st.session_state and not st.session_state.full_chat_history and st.session_state.messages:
    # If full_chat_history was initialized empty but old messages exist
    st.session_state.full_chat_history = st.session_state.messages
    del st.session_state.messages


# Load configuration and initialize chatbot only once
if not st.session_state.chatbot_initialized:
    config_file_path = os.path.join(project_root, 'config', 'config.ini')
    
    original_stdout = sys.stdout
    sys.stdout = open(os.devnull, 'w') 
    (api_key, base_url, configured_models,
     ctx_thresh_perc, ctx_send_perc, summ_prompt,
     summ_model, max_recent_summ, assumed_max_tokens) = load_config(config_file_path=config_file_path)
    sys.stdout.close() 
    sys.stdout = original_stdout

    st.session_state.api_key = api_key
    st.session_state.base_url = base_url
    st.session_state.configured_models_list = configured_models

    # Store context management and model config parameters
    st.session_state.context_config = {
        "threshold_percentage": ctx_thresh_perc,
        "send_percentage": ctx_send_perc,
        "summary_prompt_template": summ_prompt,
        "model_for_summarization": summ_model,
        "max_recent_after_summary": max_recent_summ,
        # Add other context related params if they get added to load_config
        'max_tokens_for_summary': 250, # Default, can be made configurable
        'temperature_for_summary': 0.3 # Default, can be made configurable
    }
    st.session_state.model_config_params = {
        "max_tokens": assumed_max_tokens 
    }

    if not st.session_state.api_key or not st.session_state.base_url:
        st.error("🔴 API Key or Base URL not configured. Please check environment variables or `config/config.ini`.")
        st.stop()
    else:
        st.session_state.chatbot_instance = Chatbot(api_key=st.session_state.api_key, base_url=st.session_state.base_url)
        st.session_state.chatbot_initialized = True
        st.success(f"Chatbot initialized. Default instance model: {st.session_state.chatbot_instance.model}", icon="✅")

        original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')
        dynamic_models = st.session_state.chatbot_instance.get_available_models()
        sys.stdout.close() 
        sys.stdout = original_stdout
        
        st.session_state.dynamic_models_list = dynamic_models

        default_models_for_ui = ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"]
        api_fetch_failed = st.session_state.dynamic_models_list is None

        if st.session_state.dynamic_models_list and len(st.session_state.dynamic_models_list) > 0:
            st.session_state.ui_model_options = st.session_state.dynamic_models_list
            st.session_state.model_source_info = "Models loaded from API."
        elif st.session_state.configured_models_list and len(st.session_state.configured_models_list) > 0:
            st.session_state.ui_model_options = st.session_state.configured_models_list
            st.session_state.model_source_info = "Using manually configured model list." + (" (API fetch failed)" if api_fetch_failed else "")
        else:
            st.session_state.ui_model_options = default_models_for_ui
            st.session_state.model_source_info = "Using default model list." + (" (API fetch/manual config failed)" if api_fetch_failed else "")
        
        if not st.session_state.selected_model and st.session_state.ui_model_options:
            st.session_state.selected_model = st.session_state.ui_model_options[0]
        elif st.session_state.selected_model not in st.session_state.ui_model_options and st.session_state.ui_model_options:
            st.session_state.selected_model = st.session_state.ui_model_options[0]


# --- Sidebar UI Elements ---
if st.session_state.chatbot_initialized:
    st.sidebar.caption(st.session_state.model_source_info)

    if st.session_state.ui_model_options:
        if st.session_state.selected_model not in st.session_state.ui_model_options:
            st.session_state.selected_model = st.session_state.ui_model_options[0]
            
        try:
            current_model_index = st.session_state.ui_model_options.index(st.session_state.selected_model)
        except ValueError: 
            current_model_index = 0 

        selected_model_from_ui = st.sidebar.selectbox(
            "Choose a Model:", options=st.session_state.ui_model_options,
            index=current_model_index, key="model_select_key" 
        )
        
        if selected_model_from_ui != st.session_state.selected_model:
            st.session_state.selected_model = selected_model_from_ui
            st.sidebar.success(f"Model changed to: {st.session_state.selected_model}", icon="🔄")

        st.sidebar.info(f"Using model: **{st.session_state.selected_model}**")
    else: 
        st.sidebar.warning("No models available for selection.")
        st.session_state.selected_model = None

    st.sidebar.markdown("---") 

    if st.sidebar.button("Clear Chat History", key="clear_chat_button"):
        st.session_state.full_chat_history = []
        st.session_state.knowledge_base_summary = "" # Reset summary as well
        st.sidebar.success("Chat history and summary cleared!", icon="🗑️")
        st.experimental_rerun()

    st.sidebar.markdown("---") 
    st.sidebar.subheader("Export Conversation")
    export_disabled = not st.session_state.full_chat_history
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    plain_text_data = _prepare_text_export(st.session_state.full_chat_history)
    st.sidebar.download_button(
        label="Export as TXT", data=plain_text_data, file_name=f"conversation_{timestamp}.txt",
        mime="text/plain", key="export_txt_button", disabled=export_disabled,
        help="Exports the current chat conversation to a plain text file."
    )
    json_data = _prepare_json_export(st.session_state.full_chat_history)
    st.sidebar.download_button(
        label="Export as JSON", data=json_data, file_name=f"conversation_{timestamp}.json",
        mime="application/json", key="export_json_button", disabled=export_disabled,
        help="Exports the current chat conversation to a JSON file."
    )
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("Current Summary Tokens")
    summary_tokens = st.session_state.chatbot_instance._count_tokens(st.session_state.knowledge_base_summary, st.session_state.selected_model or "gpt-3.5-turbo")
    st.sidebar.caption(f"Summary: {summary_tokens} tokens")


# --- Chat History Display ---
for message in st.session_state.full_chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- User Input and Chatbot Response ---
if prompt := st.chat_input("What's on your mind?"):
    if not st.session_state.chatbot_initialized:
        st.error("Chatbot is not initialized. Please check configuration.")
        st.stop()
    if not st.session_state.selected_model: 
        st.error("No model selected or available. Please choose a model or check configuration.")
        st.stop()

    st.session_state.full_chat_history.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        with st.spinner(f"Thinking with {st.session_state.selected_model}... 🤔"):
            
            current_model_config = {
                "name": st.session_state.selected_model,
                "max_tokens": st.session_state.model_config_params.get('max_tokens', 4096) # Default if not set
            }
            
            # Ensure context_config has all necessary keys, potentially from defaults if not in file
            complete_context_config = {
                "threshold_percentage": st.session_state.context_config.get('threshold_percentage', 0.75),
                "send_percentage": st.session_state.context_config.get('send_percentage', 0.85),
                "summary_prompt_template": st.session_state.context_config.get('summary_prompt_template', "Summarize: {text}"),
                "model_for_summarization": st.session_state.context_config.get('model_for_summarization', "gpt-3.5-turbo"),
                "max_recent_after_summary": st.session_state.context_config.get('max_recent_after_summary', 5),
                "max_tokens_for_summary": st.session_state.context_config.get('max_tokens_for_summary', 250),
                "temperature_for_summary": st.session_state.context_config.get('temperature_for_summary', 0.3)
            }

            original_stdout_chatbot = sys.stdout
            sys.stdout = open(os.devnull, 'w')
            ai_response, updated_summary, effective_api_history = st.session_state.chatbot_instance.send_message(
                new_user_prompt=prompt,
                full_conversation_history=st.session_state.full_chat_history[:-1], # Send history *before* current prompt
                current_summary=st.session_state.knowledge_base_summary,
                model_config=current_model_config,
                context_management_config=complete_context_config
            )
            sys.stdout.close() 
            sys.stdout = original_stdout_chatbot

            if ai_response:
                message_placeholder.markdown(ai_response)
                st.session_state.full_chat_history.append({"role": "assistant", "content": ai_response})
                st.session_state.knowledge_base_summary = updated_summary # Update summary
                # Optionally log or display effective_api_history for debugging
                # print(f"DEBUG: Effective API history sent: {effective_api_history}", file=sys.stderr)
            else:
                message_placeholder.error("😕 Sorry, I couldn't get a response. Check console for details.")
                # Remove the user's last message if the bot failed to respond, to allow retry
                if st.session_state.full_chat_history and st.session_state.full_chat_history[-1]["role"] == "user":
                    st.session_state.full_chat_history.pop()


# --- Sidebar Information ---
st.sidebar.markdown("---")
st.sidebar.info("Conversation history is session-based. Refreshing the page clears history & summary. Model changes apply to new messages.")

# For debugging:
# if st.sidebar.checkbox("Show Session State Details"):
#    st.sidebar.write(st.session_state)

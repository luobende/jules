# chatbot_project/src/streamlit_app.py

import streamlit as st
import sys
import os

# 1. Path Setup for Imports
# Ensure 'src' and 'config' can be found for module imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
# No need to add src/ and config/ explicitly if project_root is added,
# as imports like 'from src.chatbot import Chatbot' will work.

from src.chatbot import Chatbot
from config.config import load_config

# 2. App Title
st.title("💬 Configurable Chatbot")

# 3. Load Configuration and Initialize Chatbot
# Use session state to store chatbot instance and avoid re-initialization on every interaction
if 'chatbot_initialized' not in st.session_state:
    st.session_state.chatbot_initialized = False

if not st.session_state.chatbot_initialized:
    # Determine the path to config.ini relative to this file (streamlit_app.py in src/)
    # It should be in ../config/config.ini
    config_file_path = os.path.join(project_root, 'config', 'config.ini')
    
    # Suppress print statements from load_config during Streamlit execution
    # by temporarily redirecting stdout. This is a bit of a hack for cleaner UI.
    original_stdout = sys.stdout
    sys.stdout = open(os.devnull, 'w')
    api_key, base_url = load_config(config_file_path=config_file_path)
    sys.stdout.close() # Close the devnull stream
    sys.stdout = original_stdout # Restore stdout

    if not api_key or not base_url:
        st.error("🔴 API Key or Base URL not configured. Please set them via environment variables or create/update `config/config.ini` based on `config/config.ini.template`.")
        st.warning("Please ensure `config/config.ini` is in the `config` directory, or environment variables `OPENAI_API_KEY` and `OPENAI_BASE_URL` are set.")
        st.stop()
    else:
        st.session_state.chatbot_instance = Chatbot(api_key=api_key, base_url=base_url)
        st.session_state.chatbot_initialized = True
        st.success(f"Chatbot initialized successfully. Using model: {st.session_state.chatbot_instance.model}", icon="✅")


# 4. Initialize Chat History in Session State
if "messages" not in st.session_state:
    st.session_state.messages = []

# 5. Display Chat History
# Iterate through a copy of messages for safe modification if needed, though not strictly necessary here
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 6. User Input
if prompt := st.chat_input("What's on your mind?"):
    # Add user's message to history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user's message immediately
    with st.chat_message("user"):
        st.markdown(prompt)

    # 7. Get Chatbot Response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        with st.spinner("Thinking... 🤔"):
            # Prepare conversation_history for the API call.
            # This should be all messages *before* the current user prompt was added.
            # The Chatbot class's send_message method takes `message_content` (the new prompt)
            # and `conversation_history` (list of previous messages).
            
            # Corrected history preparation:
            # The history sent to the API should be all messages currently in session_state.messages
            # *before* the latest user message was appended.
            # However, `send_message` expects the current prompt as `message_content`,
            # and the preceding messages as `conversation_history`.
            
            # Let's get the history *before* the current user prompt was appended.
            # The current st.session_state.messages already includes the user's latest prompt.
            # So, history_for_api should be all messages *except* the last one.
            history_for_api = st.session_state.messages[:-1] # All but the last message

            # Suppress print statements from chatbot.send_message for cleaner UI
            original_stdout_chatbot = sys.stdout
            sys.stdout = open(os.devnull, 'w')
            response = st.session_state.chatbot_instance.send_message(
                message_content=prompt, # The current user input
                conversation_history=history_for_api
            )
            sys.stdout.close() # Close the devnull stream
            sys.stdout = original_stdout_chatbot # Restore stdout

            if response:
                message_placeholder.markdown(response)
                # Add assistant's response to history
                st.session_state.messages.append({"role": "assistant", "content": response})
            else:
                # Error messages from chatbot.py are printed to console,
                # here we show a UI message.
                message_placeholder.error("😕 Sorry, I couldn't get a response. Please check the console for more details or try again.")
                # Optionally, remove the user's last message if the bot failed, or keep it.
                # For now, we keep it to show the attempt.
                # To remove: st.session_state.messages.pop() (if user's message was the last one added)

# For debugging: Show session state
# if st.sidebar.checkbox("Show Session State"):
#    st.sidebar.write(st.session_state)

st.sidebar.info("This chatbot maintains conversation history for the current session. Refreshing the page will clear the history and reinitialize the chatbot if needed.")

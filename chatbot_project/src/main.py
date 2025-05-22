# chatbot_project/src/main.py

import sys
import os

# Adjust the Python path to include the project root directory
# This allows for absolute imports from 'src' and 'config'
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from config.config import load_config
from src.chatbot import Chatbot

def main():
    """
    Main function to run the chatbot application.
    """
    print("Starting chatbot application...")

    # Construct the path to config.ini relative to this file (main.py in src/)
    # config_file_path = os.path.join(project_root, 'config', 'config.ini')
    # Simpler relative path assuming main.py is in src/ and config.ini is in config/
    config_file_path = '../config/config.ini'


    print(f"Attempting to load configuration from: {os.path.abspath(os.path.join(os.path.dirname(__file__), config_file_path))}")
    api_key, base_url = load_config(config_file_path=config_file_path)

    if not api_key:
        print("CRITICAL: API Key is not configured. Please set OPENAI_API_KEY environment variable or create/update config/config.ini.")
        print("Exiting application.")
        return
    if not base_url:
        print("CRITICAL: Base URL is not configured. Please set OPENAI_BASE_URL environment variable or create/update config/config.ini.")
        print("Exiting application.")
        return

    print("Configuration loaded successfully.")
    bot = Chatbot(api_key=api_key, base_url=base_url)
    print(f"Chatbot initialized with model: {bot.model}")
    print("Type 'exit' to quit the chat.")

    conversation_history = []

    while True:
        user_input = input("You: ")
        if user_input.lower() == 'exit':
            print("Exiting chatbot. Goodbye!")
            break

        if not user_input.strip():
            print("Chatbot: Please enter a message.")
            continue

        assistant_reply = bot.send_message(user_input, conversation_history=conversation_history)

        if assistant_reply:
            print(f"Chatbot: {assistant_reply}")
            # Add user message and assistant reply to history
            conversation_history.append({"role": "user", "content": user_input})
            conversation_history.append({"role": "assistant", "content": assistant_reply})
        else:
            # Error messages are printed by the Chatbot class's send_message method
            print("Chatbot: I encountered an issue. Please try again.")
            # Optionally, you might want to stop or offer to retry
            # For simplicity, we continue the loop here.

if __name__ == '__main__':
    main()

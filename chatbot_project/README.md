# Configurable OpenAI-Compatible Chatbot

## Overview

This project provides a simple yet configurable chatbot that interacts with OpenAI-compatible chat completion APIs. It offers both a command-line interface (CLI) and an interactive web UI built with Streamlit. It's designed to be easy to set up and use, allowing users to connect to various API providers by configuring the `base_url` and `api_key`. The chatbot supports conversation history, allowing for more contextual interactions in both interfaces. The Streamlit UI features advanced context management to handle long conversations.

## Features

*   **OpenAI API Compatibility**: Works with any chat completion API endpoint that follows the OpenAI specification (e.g., OpenAI's official API, locally hosted models with compatible interfaces).
*   **Dual Interfaces**:
    *   **Interactive Web UI (Streamlit)**:
        *   Real-time chat interface.
        *   **Dynamic Model Selection**: The list of available language models is primarily fetched from the API provider's `/models` endpoint.
            *   **Fallback Mechanism**: If the API call fails or returns no models, the UI falls back to a manually configured list (via `OPENAI_MODELS` environment variable or `models` key in `config.ini`). If neither is set, a hardcoded list of common models is used.
        *   **Advanced Context Management**:
            *   To handle very long conversations without losing context and to stay within model token limits, the application automatically summarizes earlier parts of the chat when the history grows too large.
            *   This summary, along with a configurable number of recent messages, is used as context for the AI, helping maintain coherence over extended interactions.
            *   Uses the `tiktoken` library for accurate token counting to manage context length effectively.
        *   **Chat History Management**: Clear the entire conversation history and its summary within the session.
        *   **Conversation Export**: Download the current chat history as a TXT or JSON file.
        *   Session-based conversation history and summary.
    *   **Command-line Interface (CLI)**:
        *   Simple interactive CLI for sending and receiving messages.
        *   Conversation history maintained for the current session. (Note: The CLI does not currently use the dynamic model selection or advanced context management features available in the Streamlit UI).
*   **Flexible Configuration**: API key, base URL, available models (for UI), and context management parameters can be configured via:
    *   Environment variables (recommended for security).
    *   A `config.ini` file.
*   **Basic Error Handling**: Provides feedback for common issues like missing configuration or API errors.

## Project Structure

```
chatbot_project/
├── config/
│   ├── config.py               # Loads configuration from env vars or INI file
│   ├── config.ini.template     # Template for configuration file
│   └── (config.ini)            # Optional user-created config file (ignored by git)
├── src/
│   ├── __init__.py
│   ├── chatbot.py              # Core Chatbot class for API interaction (token counting, summarization, model fetching)
│   ├── main.py                 # Main script to run the chatbot CLI
│   └── streamlit_app.py        # Script to run the Streamlit web UI
├── tests/
│   ├── __init__.py
│   └── test_chatbot.py         # Unit tests
├── README.md                   # This file
└── requirements.txt            # Python package dependencies (includes tiktoken)
```

*   `src/`: Contains the core Python source code for the chatbot and UI.
*   `config/`: Handles configuration loading and provides a template for settings.
*   `tests/`: Contains unit tests for the project.
*   `requirements.txt`: Lists project dependencies.

## Prerequisites

*   Python 3.x (developed with Python 3.10+)
*   Dependencies listed in `requirements.txt` (includes `requests`, `streamlit`, and `tiktoken`).

## Setup and Installation

1.  **Clone the Repository (if applicable)**:
    If you obtained this project as a Git repository:
    ```bash
    git clone <repository-url>
    cd chatbot_project
    ```
    If you have the files directly, navigate to the `chatbot_project` directory.

2.  **Create a Virtual Environment (Recommended)**:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install Dependencies**:
    Install all required packages using `requirements.txt`:
    ```bash
    pip install -r requirements.txt
    ```

## Configuration

You need to provide an API key and the base URL for the chat API service. This configuration is shared by both the CLI and Streamlit UI. Advanced context management settings are also configurable.

### 1. Environment Variables (Recommended)

This is the most secure method. Set the following environment variables:

*   **Credentials & Models**:
    *   `OPENAI_API_KEY`: Your API key.
    *   `OPENAI_BASE_URL`: The base URL for the API (e.g., `https://api.openai.com/v1`).
    *   `OPENAI_MODELS` (Optional, for Streamlit UI): Comma-separated list of model names, serving as a fallback if API model fetching fails.
*   **Context Management (for Streamlit UI)**:
    *   `CONTEXT_THRESHOLD_PERCENTAGE`: (Float, e.g., `0.75`) Percentage of model's max context to trigger summarization.
    *   `MAX_CONTEXT_SEND_PERCENTAGE`: (Float, e.g., `0.85`) Percentage of model's max context to send to API after processing.
    *   `DEFAULT_SUMMARY_PROMPT`: (String) Prompt template for summarization (must include `{text}`).
    *   `DEFAULT_MODEL_FOR_SUMMARIZATION`: (String) Model name for summarization tasks.
    *   `MAX_RECENT_MESSAGES_AFTER_SUMMARY`: (Integer) Number of recent messages to keep alongside summary.
    *   `ASSUMED_CHAT_MODEL_MAX_TOKENS`: (Integer) Assumed max tokens for the primary chat model if not dynamically known.

Example (Linux/macOS):
```bash
export OPENAI_API_KEY="your_actual_api_key_here"
export OPENAI_BASE_URL="https://api.openai.com/v1"
export OPENAI_MODELS="gpt-3.5-turbo,gpt-4"
export CONTEXT_THRESHOLD_PERCENTAGE="0.7"
export DEFAULT_MODEL_FOR_SUMMARIZATION="gpt-3.5-turbo-instruct" # Example
```

The application prioritizes environment variables.

### 2. `config.ini` File

If environment variables are not set, or for specific settings, the application will look for a `config.ini` file.

1.  **Create `config.ini`**: Copy `config/config.ini.template` to `config/config.ini`.
2.  **Edit `config.ini`**: Open `config/config.ini` and fill in your details.

    **`[Credentials]` Section**:
    ```ini
    api_key = YOUR_API_KEY_HERE
    base_url = YOUR_BASE_URL_HERE
    # models = gpt-3.5-turbo,gpt-4 # Fallback model list for UI
    ```
    *   `models`: Comma-separated list. Primarily a fallback for Streamlit UI model selection (see Features section for priority).

    **`[ContextManagement]` Section (for Streamlit UI)**:
    ```ini
    # context_threshold_percentage = 0.75
    # max_context_send_percentage = 0.85
    # default_summary_prompt = "Summarize the following conversation... {text}"
    # default_model_for_summarization = gpt-3.5-turbo
    # max_recent_messages_after_summary = 5
    # assumed_chat_model_max_tokens = 4096
    ```
    *   `context_threshold_percentage`: (Default: `0.75`) Percentage of the selected model's maximum context length that, if exceeded by the conversation history, triggers summarization.
    *   `max_context_send_percentage`: (Default: `0.85`) Target percentage of the model's maximum context length to utilize for the messages sent to the API (summary + recent history + new prompt).
    *   `default_summary_prompt`: (Default: `"Summarize the following conversation, focusing on key facts, decisions, and the main timeline of events. Condense it as much as possible while retaining critical information for future context: {text}"`) The template used for generating summaries. Must include `{text}`.
    *   `default_model_for_summarization`: (Default: `"gpt-3.5-turbo"`) The language model used for creating summaries.
    *   `max_recent_messages_after_summary`: (Default: `5`) The number of most recent messages to retain alongside the summary when the context is rebuilt.
    *   `assumed_chat_model_max_tokens`: (Default: `4096`) The assumed maximum context tokens for the primary chat model. This is used if the application cannot determine the model's actual context window size at runtime (currently, it's always used as the `Chatbot` class doesn't dynamically fetch this per model).

**Important Security Note**: Avoid committing `config.ini` with real API keys to version control.

## How to Run

Ensure you have completed the Setup and Configuration steps.

### How to Run (Streamlit UI Version)

1.  Navigate to the project root directory (`chatbot_project/`).
2.  Execute: `streamlit run src/streamlit_app.py`
3.  This opens the app in your browser.
4.  **Using the Streamlit UI**:
    *   The main area displays the chat.
    *   Use the **sidebar** for:
        *   **Model Selection**: Choose a model. The list is dynamically populated (API > Manual Config > Default).
        *   **Clear Chat History**: Clears messages and the internal summary.
        *   **Export Conversation**: Download as TXT or JSON.
        *   **Current Summary Tokens**: Shows the token count of the internal summary.
    *   Chat history and its summary are session-based.

### How to Run (CLI Version)

1.  Navigate to the project root directory.
2.  Execute: `python src/main.py`
3.  Interact in the terminal. Type `exit` to quit. (CLI does not use advanced context management).

## Error Handling/Troubleshooting

*   **Configuration Errors**: Check `config.ini` and environment variables.
*   **API Errors**: Verify API key, base URL, and network. Also impacts model fetching and summarization.
*   **Dependencies**: Ensure `pip install -r requirements.txt` was successful. `tiktoken` is crucial for context management.

## Future Enhancements (Optional)

*   Dynamic fetching of `max_tokens` for each model to improve context management accuracy.
*   User-configurable "system message" for the main chat.
*   Advanced API parameters (e.g., temperature for main chat).
*   Streaming responses.

---

This README provides a comprehensive guide to setting up, configuring, and running the chatbot.
```

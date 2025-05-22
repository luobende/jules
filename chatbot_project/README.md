# Configurable OpenAI-Compatible Chatbot

## Overview

This project provides a simple yet configurable chatbot that interacts with OpenAI-compatible chat completion APIs. It offers both a command-line interface (CLI) and an interactive web UI built with Streamlit. It's designed to be easy to set up and use, allowing users to connect to various API providers by configuring the `base_url` and `api_key`. The chatbot supports conversation history, allowing for more contextual interactions in both interfaces.

## Features

*   **OpenAI API Compatibility**: Works with any chat completion API endpoint that follows the OpenAI specification (e.g., OpenAI's official API, locally hosted models with compatible interfaces).
*   **Dual Interfaces**:
    *   **Interactive Web UI (Streamlit)**:
        *   Real-time chat interface.
        *   **Model Selection**: Choose from a list of available language models (configurable, with defaults).
        *   **Chat History Management**: Clear the entire conversation history within the session.
        *   **Conversation Export**: Download the current chat history as a TXT or JSON file.
        *   Session-based conversation history.
    *   **Command-line Interface (CLI)**:
        *   Simple interactive CLI for sending and receiving messages.
        *   Conversation history maintained for the current session.
*   **Flexible Configuration**: API key, base URL, and available models (for UI) can be configured via:
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
│   ├── chatbot.py              # Core Chatbot class for API interaction
│   ├── main.py                 # Main script to run the chatbot CLI
│   └── streamlit_app.py        # Script to run the Streamlit web UI
├── tests/
│   ├── __init__.py
│   └── test_chatbot.py         # Unit tests
├── README.md                   # This file
└── requirements.txt            # Python package dependencies
```

*   `src/`: Contains the core Python source code for the chatbot and UI.
*   `config/`: Handles configuration loading and provides a template for settings.
*   `tests/`: Contains unit tests for the project.
*   `requirements.txt`: Lists project dependencies.

## Prerequisites

*   Python 3.x (developed with Python 3.10+)
*   Dependencies listed in `requirements.txt` (primarily `requests` and `streamlit`).

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

You need to provide an API key and the base URL for the chat API service you intend to use. This configuration is shared by both the CLI and Streamlit UI.

### 1. Environment Variables (Recommended)

This is the most secure method. Set the following environment variables:

*   `OPENAI_API_KEY`: Your API key.
*   `OPENAI_BASE_URL`: The base URL for the API (e.g., `https://api.openai.com/v1`).
*   `OPENAI_MODELS` (Optional): A comma-separated list of model names to populate the model selection dropdown in the Streamlit UI (e.g., `gpt-3.5-turbo,gpt-4,gpt-4-turbo`).

Example (Linux/macOS):
```bash
export OPENAI_API_KEY="your_actual_api_key_here"
export OPENAI_BASE_URL="https://api.openai.com/v1"
export OPENAI_MODELS="gpt-3.5-turbo,gpt-4"
```

The application prioritizes environment variables.

### 2. `config.ini` File

If environment variables are not set, or for specific settings, the application will look for a `config.ini` file.

1.  **Create `config.ini`**:
    Copy `config/config.ini.template` to `config/config.ini`.
    ```bash
    cp config/config.ini.template config/config.ini
    ```

2.  **Edit `config.ini`**:
    Open `config/config.ini` and fill in your details:
    ```ini
    [Credentials]
    api_key = YOUR_API_KEY_HERE
    base_url = YOUR_BASE_URL_HERE
    # Optional: Comma-separated list of models for the Streamlit UI.
    # If commented out or empty, and OPENAI_MODELS env var is not set,
    # a default list (e.g., gpt-3.5-turbo, gpt-4) will be used.
    # models = gpt-3.5-turbo,gpt-4,gpt-4-turbo,another-model
    ```
    *   Replace placeholders for `api_key` and `base_url`.
    *   You can specify a comma-separated list for `models` to customize the dropdown in the Streamlit UI. If this key is absent or empty, and the `OPENAI_MODELS` environment variable is not set, a default list of common models will be used in the UI.

**Important Security Note**: Avoid committing `config.ini` with real API keys to version control.

## How to Run

Ensure you have completed the Setup and Configuration steps.

### How to Run (Streamlit UI Version)

To run the interactive web UI:

1.  Make sure you are in the project root directory (`chatbot_project/`).
2.  Execute the following command in your terminal:
    ```bash
    streamlit run src/streamlit_app.py
    ```
3.  This will typically open the chatbot application in a new tab in your default web browser. If it doesn't open automatically, your terminal will display a local URL (e.g., `http://localhost:8501`) that you can navigate to.
4.  **Using the Streamlit UI**:
    *   The main area displays the chat conversation.
    *   Use the **sidebar** for additional functionalities:
        *   **Choose a Model**: Select your desired language model from the dropdown. This applies to new messages.
        *   **Clear Chat History**: Click this button to remove all messages from the current session's display.
        *   **Export Conversation**: Download the current chat as a `.txt` or `.json` file.
    *   Chat history is maintained for the current browser session.

### How to Run (CLI Version)

To start the command-line chatbot:

1.  Make sure you are in the project root directory (`chatbot_project/`).
2.  Run the `main.py` script:
    ```bash
    python src/main.py
    ```
3.  Interact with the chatbot in your terminal. Type `exit` to quit.

## Basic Usage Example (CLI)

```
You: Hello, what is the capital of France?
Chatbot: The capital of France is Paris.
You: What is a fun fact about it?
Chatbot: A fun fact about Paris is that it's home to the world's largest art museum, the Louvre...
You: exit
Exiting chatbot. Goodbye!
```
The Streamlit UI provides a similar conversational experience within your browser, with added graphical features.

## Error Handling/Troubleshooting

*   **Configuration Errors**: If credentials or models are not found/configured correctly, the applications will indicate this.
*   **API Errors**: Incorrect API keys, base URLs, or network issues can lead to errors, which are generally reported in the UI or console.
*   **Dependencies**: Ensure all packages in `requirements.txt` are installed.

## Future Enhancements (Optional)

*   **System Message Configuration**: Allow setting a "system" message.
*   **Advanced API Parameters**: Support for `temperature`, `max_tokens`, etc.
*   **Streaming Responses**: For more dynamic interaction.
*   **More Robust Testing**: Expand unit and integration tests.
*   **Logging**: Implement more structured logging.

---

This README provides a comprehensive guide to setting up, configuring, and running the chatbot.
```

# Configurable OpenAI-Compatible Chatbot

## Overview

This project provides a simple yet configurable chatbot that interacts with OpenAI-compatible chat completion APIs. It offers both a command-line interface (CLI) and an interactive web UI built with Streamlit. It's designed to be easy to set up and use, allowing users to connect to various API providers by configuring the `base_url` and `api_key`. The chatbot supports conversation history, allowing for more contextual interactions in both interfaces.

## Features

*   **OpenAI API Compatibility**: Works with any chat completion API endpoint that follows the OpenAI specification (e.g., OpenAI's official API, locally hosted models with compatible interfaces).
*   **Dual Interfaces**:
    *   Interactive web UI using Streamlit.
    *   Command-line Interface (CLI).
*   **Flexible Configuration**: API key and base URL can be configured via:
    *   Environment variables (recommended for security).
    *   A `config.ini` file.
*   **Conversation History**: Remembers the context of the current conversation (session-based for Streamlit UI).
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

You need to provide an API key and the base URL for the chat API service you intend to use. This configuration is shared by both the CLI and Streamlit UI. There are two ways to configure these:

### 1. Environment Variables (Recommended)

This is the most secure method, especially in production or shared environments, as it avoids hardcoding credentials in files.

Set the following environment variables in your system or terminal session:

*   `OPENAI_API_KEY`: Your API key.
*   `OPENAI_BASE_URL`: The base URL for the API. For standard OpenAI, this is `https://api.openai.com/v1`.

Example (Linux/macOS):
```bash
export OPENAI_API_KEY="your_actual_api_key_here"
export OPENAI_BASE_URL="https://api.openai.com/v1"
```

Example (Windows PowerShell):
```powershell
$Env:OPENAI_API_KEY="your_actual_api_key_here"
$Env:OPENAI_BASE_URL="https://api.openai.com/v1"
```

The application will prioritize these environment variables if they are set.

### 2. `config.ini` File

If environment variables are not set, the application will look for a `config.ini` file.

1.  **Create `config.ini`**:
    Navigate to the `config/` directory. Copy the template file:
    ```bash
    cp config/config.ini.template config/config.ini
    ```
    (On Windows, use `copy config\config.ini.template config\config.ini`)

2.  **Edit `config.ini`**:
    Open `config/config.ini` with a text editor and fill in your details:
    ```ini
    [Credentials]
    api_key = YOUR_API_KEY_HERE
    base_url = YOUR_BASE_URL_HERE
    ```
    Replace `YOUR_API_KEY_HERE` with your actual API key.
    Replace `YOUR_BASE_URL_HERE` with the correct base URL for your service. For example, for OpenAI's official API, it would be:
    ```ini
    base_url = https://api.openai.com/v1
    ```

**Important Security Note**: If you use the `config.ini` file, ensure it is **not** committed to version control (e.g., Git) if it contains real API keys. The provided `.gitignore` file (if this project is a git repo) should already include `config.ini` to prevent accidental commits.

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
4.  Interact with the chatbot through the web interface. Chat history is maintained for the current session.

### How to Run (CLI Version)

To start the command-line chatbot:

1.  Make sure you are in the project root directory (`chatbot_project/`).
2.  Run the `main.py` script:
    ```bash
    python src/main.py
    ```
3.  You will see a prompt in your terminal:
    ```
    Starting chatbot application...
    You:
    ```
    (Configuration loading messages will also appear here)
4.  Simply type your message and press Enter. The chatbot's response will be displayed. To end the session, type `exit` and press Enter.

## Basic Usage Example (CLI)

```
You: Hello, what is the capital of France?
Chatbot: The capital of France is Paris.
You: What is a fun fact about it?
Chatbot: A fun fact about Paris is that it's home to the world's largest art museum, the Louvre...
You: exit
Exiting chatbot. Goodbye!
```
The Streamlit UI provides a similar conversational experience within your browser.

## Error Handling/Troubleshooting

*   **Configuration Errors**:
    *   If credentials are not found, both the CLI and Streamlit app will indicate this. The Streamlit app will show an error message on the UI, while the CLI will print "CRITICAL" errors and exit. Ensure your configuration via environment variables or `config/config.ini` is correct.
*   **Incorrect API Key (Authentication Errors)**:
    *   The API might return a `401 Unauthorized` error. The CLI will print this (e.g., "Error: API request failed with status code 401..."). The Streamlit UI will show a generic "Sorry, I couldn't get a response" message, but details might be in the console where you ran `streamlit run`. Verify your API key.
*   **Incorrect Base URL or Network Issues**:
    *   You might see `ConnectionRefusedError`, `NameResolutionError`, or API errors like `404 Not Found`. Double-check the `base_url` and your internet connectivity.
*   **API Quota Exceeded**:
    *   The API might return a `429 Too Many Requests` error. Check your API usage limits.
*   **`ModuleNotFoundError`**:
    *   If running from an incorrect directory, you might get import errors. Always run commands (`python src/main.py` or `streamlit run src/streamlit_app.py`) from the project root directory (`chatbot_project/`).
*   **Dependencies Not Installed**:
    *   Ensure you have run `pip install -r requirements.txt`.

## Future Enhancements (Optional)

This is a basic implementation. Potential future enhancements include:

*   **Configurable Model**: Allow users to specify the chat model (e.g., "gpt-4") via configuration, usable by both UIs.
*   **System Message Configuration**: Allow setting a "system" message to guide behavior, accessible in both UIs.
*   **Advanced API Parameters**: Support for `temperature`, `max_tokens`, etc.
*   **Streaming Responses**: Implement for both CLI and Streamlit for better interactivity.
*   **More Robust Testing**: Expand unit and integration tests.
*   **Logging**: Implement more structured logging.

---

This README provides a comprehensive guide to setting up, configuring, and running the chatbot.
```

# Configurable OpenAI-Compatible Chatbot

## Overview

This project provides a simple yet configurable command-line chatbot that interacts with OpenAI-compatible chat completion APIs. It's designed to be easy to set up and use, allowing users to connect to various API providers by configuring the `base_url` and `api_key`. The chatbot supports conversation history, allowing for more contextual interactions.

## Features

*   **OpenAI API Compatibility**: Works with any chat completion API endpoint that follows the OpenAI specification (e.g., OpenAI's official API, locally hosted models with compatible interfaces).
*   **Flexible Configuration**: API key and base URL can be configured via:
    *   Environment variables (recommended for security).
    *   A `config.ini` file.
*   **Conversation History**: Remembers the context of the current conversation.
*   **Basic Error Handling**: Provides feedback for common issues like missing configuration or API errors.
*   **Command-line Interface**: Simple interactive CLI for sending and receiving messages.

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
│   └── main.py                 # Main script to run the chatbot CLI
├── tests/
│   ├── __init__.py
│   └── test_chatbot.py         # Unit tests (currently basic)
└── README.md                   # This file
```

*   `src/`: Contains the core Python source code for the chatbot.
*   `config/`: Handles configuration loading and provides a template for settings.
*   `tests/`: Contains unit tests for the project (currently placeholders, to be expanded).

## Prerequisites

*   Python 3.x (developed with Python 3.10+)
*   The `requests` library

## Setup and Installation

1.  **Clone the Repository (if applicable)**:
    If you obtained this project as a Git repository:
    ```bash
    git clone <repository-url>
    cd chatbot_project
    ```
    If you have the files directly, navigate to the `chatbot_project` directory.

2.  **Install Dependencies**:
    Install the `requests` library using pip:
    ```bash
    pip install requests
    ```
    Or, if you use a virtual environment (recommended):
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    pip install requests
    ```

## Configuration

You need to provide an API key and the base URL for the chat API service you intend to use. There are two ways to configure these:

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

To start the chatbot, run the `main.py` script from the **root directory** of the project (`chatbot_project/`):

```bash
python src/main.py
```

You will see a prompt:

```
Starting chatbot application...
INFO: Checking environment variables for API credentials...
INFO: Not all credentials found in environment variables. Trying to load from '../config/config.ini'...
INFO: API key loaded from '../config/config.ini'.
INFO: Base URL loaded from '../config/config.ini'.
Configuration loaded successfully.
Chatbot initialized with model: gpt-3.5-turbo
Type 'exit' to quit the chat.
You:
```

Simply type your message and press Enter. The chatbot's response will be displayed. To end the session, type `exit` and press Enter.

## Basic Usage Example

```
You: Hello, what is the capital of France?
Chatbot: The capital of France is Paris.
You: What is a fun fact about it?
Chatbot: A fun fact about Paris is that it's home to the world's largest art museum, the Louvre, which houses masterpieces like the Mona Lisa and the Venus de Milo. It would take about 200 days to see every piece of art in the Louvre if you spent just 30 seconds on each one!
You: exit
Exiting chatbot. Goodbye!
```

## Error Handling/Troubleshooting

*   **Missing API Key or Base URL**:
    *   If neither environment variables nor `config.ini` provide valid credentials, `main.py` will print a "CRITICAL" error message and exit. Ensure your configuration is correct.
*   **Incorrect API Key (Authentication Errors)**:
    *   The API might return a `401 Unauthorized` error. This will be printed by the chatbot (e.g., "Error: API request failed with status code 401..."). Verify your API key.
*   **Incorrect Base URL or Network Issues**:
    *   You might see `ConnectionRefusedError`, `NameResolutionError`, or API errors like `404 Not Found`. Double-check the `base_url` and your internet connectivity.
*   **API Quota Exceeded**:
    *   The API might return a `429 Too Many Requests` error. Check your API usage limits with your provider.
*   **`ModuleNotFoundError`**:
    *   If you try to run `python main.py` directly from the `src/` directory, you might encounter import errors. Always run from the project root (`chatbot_project/`) using `python src/main.py`. The `main.py` script attempts to adjust `sys.path` to mitigate this, but running from the root is the standard practice.
*   **`requests` library not found**:
    *   Ensure you have installed it via `pip install requests`.

## Future Enhancements (Optional)

This is a basic implementation. Potential future enhancements include:

*   **Configurable Model**: Allow users to specify the chat model (e.g., "gpt-4", "gpt-3.5-turbo-16k") via configuration.
*   **System Message Configuration**: Allow setting a "system" message to better guide the chatbot's behavior or personality.
*   **Advanced API Parameters**: Support for parameters like `temperature`, `max_tokens`, `top_p`, etc.
*   **Streaming Responses**: Implement support for streaming API responses for a more interactive feel with long replies.
*   **GUI Interface**: Develop a graphical user interface instead of a command-line one.
*   **More Robust Testing**: Expand unit and integration tests.
*   **Logging**: Implement more structured logging instead of just print statements.

---

This README provides a comprehensive guide to setting up, configuring, and running the chatbot.
```

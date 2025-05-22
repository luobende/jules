# chatbot_project/src/chatbot.py

import requests
import json
import sys # For sys.stderr
import os # For os.getenv in __main__

class Chatbot:
    """
    A class to interact with a chat API, such as OpenAI's GPT models.
    """

    def __init__(self, api_key: str, base_url: str):
        """
        Initializes the Chatbot.

        Args:
            api_key (str): The API key for authentication.
            base_url (str): The base URL for the API endpoint.
        """
        self.api_key = api_key
        self.base_url = base_url
        self.model = "gpt-3.5-turbo"  # Default model if no specific model is requested per message

    def send_message(self, message_content: str, conversation_history: list = None, model_name: str = None) -> str | None:
        """
        Sends a message to the chat API and returns the assistant's reply.

        Args:
            message_content (str): The content of the user's message.
            conversation_history (list, optional): A list of previous message objects.
                                                   Each object should be a dictionary with "role" and "content".
                                                   Defaults to None.
            model_name (str, optional): The name of the model to use for this specific request.
                                        If None, uses the chatbot's default model (`self.model`).
                                        Defaults to None.

        Returns:
            str | None: The assistant's reply content, or None if an error occurred.
        """
        if conversation_history is None:
            messages = []
        else:
            messages = list(conversation_history)  # Make a copy to avoid modifying the original

        messages.append({"role": "user", "content": message_content})

        model_to_use = model_name if model_name else self.model
        if not model_to_use: 
            print("Error: No model specified for the API request.", file=sys.stderr)
            return None


        payload = {
            "model": model_to_use,
            "messages": messages,
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        api_url = f"{self.base_url}/chat/completions"

        try:
            # Changed print to sys.stderr for info/debug messages from this class
            print(f"INFO: Sending request to {api_url} with model: {model_to_use}", file=sys.stderr) 
            response = requests.post(api_url, headers=headers, json=payload, timeout=30)

            if response.status_code == 200:
                try:
                    response_data = response.json()
                    if (
                        "choices" in response_data
                        and len(response_data["choices"]) > 0
                        and "message" in response_data["choices"][0]
                        and "content" in response_data["choices"][0]["message"]
                    ):
                        return response_data["choices"][0]["message"]["content"].strip()
                    else:
                        print(f"Error: Unexpected API response format. Full response: {response_data}", file=sys.stderr)
                        return None
                except json.JSONDecodeError:
                    print(f"Error: Could not decode JSON response. Response text: {response.text}", file=sys.stderr)
                    return None
                except KeyError as e:
                    print(f"Error: Missing key in API response: {e}. Full response: {response_data}", file=sys.stderr)
                    return None
            else:
                print(f"Error: API request failed with status code {response.status_code}. Response: {response.text}", file=sys.stderr)
                return None

        except requests.exceptions.Timeout:
            print(f"Error: API request timed out after 30 seconds to {api_url}.", file=sys.stderr)
            return None
        except requests.exceptions.RequestException as e:
            print(f"Error: An exception occurred while making the API request: {e}", file=sys.stderr)
            return None

    def get_available_models(self) -> list[str] | None:
        """
        Fetches the list of available model IDs from the API.

        Returns:
            list[str] | None: A list of model IDs if successful, otherwise None.
                              Returns an empty list if the API returns no models.
        """
        api_url = f"{self.base_url}/models"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json", # Good practice, though not always strictly needed for GET
        }

        try:
            print(f"INFO: Fetching available models from {api_url}", file=sys.stderr)
            response = requests.get(api_url, headers=headers, timeout=30)

            if response.status_code == 200:
                try:
                    response_json = response.json()
                    # Standard OpenAI API returns models in a 'data' list
                    # Each item in 'data' is a dict, model ID is under 'id'
                    model_ids = [
                        item['id'] for item in response_json.get('data', []) if isinstance(item, dict) and 'id' in item
                    ]
                    # Fallback for APIs that might return a simple list of model objects
                    if not model_ids and isinstance(response_json, list):
                         model_ids = [item['id'] for item in response_json if isinstance(item, dict) and 'id' in item]

                    if not model_ids and isinstance(response_json.get('data'), list): # Check if data was list but items were not dicts or no 'id'
                        print(f"Warning: Fetched data from {api_url}, but no model IDs could be extracted. Response structure might be non-standard. Data: {response_json.get('data')}", file=sys.stderr)

                    return model_ids
                except json.JSONDecodeError:
                    print(f"Error: Could not decode JSON response when fetching models. Response text: {response.text}", file=sys.stderr)
                    return None
                except Exception as e: # Catch other potential errors during parsing
                    print(f"Error: Failed to parse models from API response: {e}. Response: {response.text}", file=sys.stderr)
                    return None
            else:
                print(f"Failed to fetch models: API returned status {response.status_code} - {response.text}", file=sys.stderr)
                return None

        except requests.exceptions.Timeout:
            print(f"Error fetching models from API: Request timed out after 30 seconds to {api_url}.", file=sys.stderr)
            return None
        except requests.exceptions.RequestException as e:
            print(f"Error fetching models from API: {e}", file=sys.stderr)
            return None


if __name__ == '__main__':
    print("Testing Chatbot class...")
    # Use environment variables for API key and base URL for testing this script directly
    API_KEY = os.getenv("TEST_OPENAI_API_KEY", "YOUR_API_KEY_HERE") 
    BASE_URL = os.getenv("TEST_OPENAI_BASE_URL", "https://api.openai.com/v1")

    if API_KEY == "YOUR_API_KEY_HERE":
        print("Please set TEST_OPENAI_API_KEY and optionally TEST_OPENAI_BASE_URL environment variables to test live API calls.")
    else:
        bot = Chatbot(api_key=API_KEY, base_url=BASE_URL)

        # Test 1: Fetch available models
        print("\n--- Test 1: Fetching available models ---")
        available_models = bot.get_available_models()
        if available_models is not None:
            print(f"Available models: {available_models}")
            if not available_models:
                 print("API returned an empty list of models or structure was not recognized.")
        else:
            print("Failed to fetch models from the API.")

        # Test 2: Simple message (using default model)
        print("\n--- Test 2: Simple message (default model) ---")
        reply = bot.send_message("Hello, how are you?")
        if reply:
            print(f"Chatbot: {reply}")
        else:
            print("Chatbot: No reply received.")

        # Test 3: Message with history (using default model)
        print("\n--- Test 3: Message with history (default model) ---")
        history = [
            {"role": "user", "content": "What is the capital of France?"},
            {"role": "assistant", "content": "The capital of France is Paris."}
        ]
        reply_with_history = bot.send_message("What is its population?", conversation_history=history)
        if reply_with_history:
            print(f"Chatbot: {reply_with_history}")
        else:
            print("Chatbot: No reply received for message with history.")

        # Test 4: Simple message with a specific model
        # Use a model from the fetched list if available, otherwise fallback or skip
        model_to_test_send = bot.model # Default
        if available_models and "gpt-3.5-turbo" in available_models : # Example, pick one you expect
            model_to_test_send = "gpt-3.5-turbo"
        elif available_models:
            model_to_test_send = available_models[0] # Pick the first one if gpt-3.5-turbo isn't listed

        print(f"\n--- Test 4: Simple message (specific model: {model_to_test_send}) ---")
        reply_specific_model = bot.send_message(f"Tell me a joke, using model {model_to_test_send}.", model_name=model_to_test_send)
        if reply_specific_model:
            print(f"Chatbot ({model_to_test_send}): {reply_specific_model}")
        else:
            print(f"Chatbot ({model_to_test_send}): No reply received.")

        print("\nChatbot class testing with get_available_models complete.")
        print("Ensure 'requests' library is installed (`pip install requests`).")
        print("Actual API interaction depends on a valid API_KEY and network access.")

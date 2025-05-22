# chatbot_project/src/chatbot.py

import requests
import json

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
        if not model_to_use: # Fallback if model_name is empty string and self.model was somehow cleared
            print("Error: No model specified for the API request.")
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
            print(f"INFO: Sending request to {api_url} with model: {model_to_use}") # For debugging
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
                        print(f"Error: Unexpected API response format. Full response: {response_data}")
                        return None
                except json.JSONDecodeError:
                    print(f"Error: Could not decode JSON response. Response text: {response.text}")
                    return None
                except KeyError as e:
                    print(f"Error: Missing key in API response: {e}. Full response: {response_data}")
                    return None
            else:
                print(f"Error: API request failed with status code {response.status_code}. Response: {response.text}")
                return None

        except requests.exceptions.Timeout:
            print(f"Error: API request timed out after 30 seconds to {api_url}.")
            return None
        except requests.exceptions.RequestException as e:
            print(f"Error: An exception occurred while making the API request: {e}")
            return None

if __name__ == '__main__':
    # This is a placeholder for testing and will be removed or updated later.
    print("Testing Chatbot class...")
    API_KEY = os.getenv("TEST_OPENAI_API_KEY", "YOUR_API_KEY_HERE")
    BASE_URL = os.getenv("TEST_OPENAI_BASE_URL", "https://api.openai.com/v1")

    if API_KEY == "YOUR_API_KEY_HERE":
        print("Please replace 'YOUR_API_KEY_HERE' or set TEST_OPENAI_API_KEY env var to test.")
    else:
        bot = Chatbot(api_key=API_KEY, base_url=BASE_URL)

        # Test 1: Simple message (using default model)
        print("\n--- Test 1: Simple message (default model) ---")
        reply = bot.send_message("Hello, how are you?")
        if reply:
            print(f"Chatbot: {reply}")
        else:
            print("Chatbot: No reply received.")

        # Test 2: Message with history (using default model)
        print("\n--- Test 2: Message with history (default model) ---")
        history = [
            {"role": "user", "content": "What is the capital of France?"},
            {"role": "assistant", "content": "The capital of France is Paris."}
        ]
        reply_with_history = bot.send_message("What is its population?", conversation_history=history)
        if reply_with_history:
            print(f"Chatbot: {reply_with_history}")
        else:
            print("Chatbot: No reply received for message with history.")

        # Test 3: Simple message with a specific model (e.g., gpt-4 if available and configured)
        # Note: This test depends on the availability of the specified model.
        # For local testing, you might use a known available model or a dummy one if your API supports it.
        # If the model specified in OPENAI_MODELS is available, use one from there.
        # For now, we'll hardcode one for the test example.
        # This will likely use "gpt-3.5-turbo" if TEST_API_KEY is not a real OpenAI key for gpt-4
        specific_model_to_test = "gpt-3.5-turbo" # or "gpt-4" if you have access
        print(f"\n--- Test 4: Simple message (specific model: {specific_model_to_test}) ---")
        reply_specific_model = bot.send_message(f"Tell me a joke, using model {specific_model_to_test}.", model_name=specific_model_to_test)
        if reply_specific_model:
            print(f"Chatbot ({specific_model_to_test}): {reply_specific_model}")
        else:
            print(f"Chatbot ({specific_model_to_test}): No reply received.")


        print("\nChatbot class modification for model selection per message complete.")
        print("Ensure 'requests' library is installed (`pip install requests`).")
        print("Actual API interaction depends on a valid API_KEY and network access.")

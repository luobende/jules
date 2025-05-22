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
        self.model = "gpt-3.5-turbo"  # Default model

    def send_message(self, message_content: str, conversation_history: list = None) -> str | None:
        """
        Sends a message to the chat API and returns the assistant's reply.

        Args:
            message_content (str): The content of the user's message.
            conversation_history (list, optional): A list of previous message objects.
                                                   Each object should be a dictionary with "role" and "content".
                                                   Defaults to None.

        Returns:
            str | None: The assistant's reply content, or None if an error occurred.
        """
        if conversation_history is None:
            messages = []
        else:
            messages = list(conversation_history)  # Make a copy to avoid modifying the original

        messages.append({"role": "user", "content": message_content})

        payload = {
            "model": self.model,
            "messages": messages,
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        api_url = f"{self.base_url}/chat/completions"

        try:
            response = requests.post(api_url, headers=headers, json=payload, timeout=30) # Added timeout

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
    # For now, it requires you to manually set API_KEY and BASE_URL.
    # In a real scenario, these would come from a config file.
    print("Testing Chatbot class...")
    API_KEY = "YOUR_API_KEY_HERE"  # Replace with a real or dummy key for local testing
    BASE_URL = "https://api.openai.com/v1"  # Replace with the correct base URL

    if API_KEY == "YOUR_API_KEY_HERE":
        print("Please replace 'YOUR_API_KEY_HERE' with an actual API key to test.")
    else:
        bot = Chatbot(api_key=API_KEY, base_url=BASE_URL)

        # Test 1: Simple message
        print("\n--- Test 1: Simple message ---")
        reply = bot.send_message("Hello, how are you?")
        if reply:
            print(f"Chatbot: {reply}")
        else:
            print("Chatbot: No reply received.")

        # Test 2: Message with history
        print("\n--- Test 2: Message with history ---")
        history = [
            {"role": "user", "content": "What is the capital of France?"},
            {"role": "assistant", "content": "The capital of France is Paris."}
        ]
        reply_with_history = bot.send_message("What is its population?", conversation_history=history)
        if reply_with_history:
            print(f"Chatbot: {reply_with_history}")
        else:
            print("Chatbot: No reply received for message with history.")

        # Test 3: Non-existent endpoint (simulating a URL error, though base_url is fixed here)
        # To truly test this, you'd change base_url to something invalid.
        # For now, this will likely just fail if the API key is invalid or quota is exceeded.
        print("\n--- Test 3: Error handling (simulated by potentially invalid key) ---")
        error_bot = Chatbot(api_key="INVALID_KEY_FOR_TESTING", base_url=BASE_URL)
        error_reply = error_bot.send_message("This should fail.")
        if not error_reply:
            print("Chatbot: Correctly handled error (no reply).")
        else:
            print(f"Chatbot: Unexpected reply during error test: {error_reply}")

        print("\n--- Test 4: Changing model (conceptual, as model is hardcoded for now) ---")
        # bot.model = "gpt-4" # Example if model was configurable
        # print(f"Chatbot model set to: {bot.model}")
        # reply_gpt4 = bot.send_message("Explain quantum computing in simple terms.")
        # if reply_gpt4:
        #     print(f"Chatbot (GPT-4 model): {reply_gpt4}")
        # else:
        #     print("Chatbot: No reply received with gpt-4 model.")
        print("Note: Model is currently hardcoded to gpt-3.5-turbo. Model switching test is conceptual.")

    print("\nChatbot class implementation complete and basic test structure added.")
    print("Ensure 'requests' library is installed (`pip install requests`).")
    print("Actual API interaction depends on a valid API_KEY and network access.")

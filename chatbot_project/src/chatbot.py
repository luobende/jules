# chatbot_project/src/chatbot.py

import requests
import json
import sys # For sys.stderr
import os # For os.getenv in __main__
import tiktoken # For token counting

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
        self.model = "gpt-3.5-turbo"  # Default model, can be overridden in send_message

    def _count_tokens(self, text: str, model_name_for_encoding: str = "gpt-3.5-turbo") -> int:
        """Counts tokens, with fallbacks for unknown models."""
        if not text: return 0
        try:
            encoding = tiktoken.encoding_for_model(model_name_for_encoding)
        except KeyError:
            try:
                encoding = tiktoken.get_encoding("cl100k_base")
            except Exception as e:
                print(f"Error: Could not get tiktoken encoding for '{model_name_for_encoding}' or 'cl100k_base': {e}. Using rough estimate len(text)//4.", file=sys.stderr)
                return len(text) // 4 
        try:
            return len(encoding.encode(text))
        except Exception as e:
            print(f"Error: Failed to encode text with tiktoken: {e}. Using rough estimate len(text)//4.", file=sys.stderr)
            return len(text) // 4

    def _build_messages_for_api(
        self,
        summary_text: str | None,
        history_list: list[dict],
        new_prompt_text: str,
        max_tokens: int,
        model_name_for_encoding: str
    ) -> list[dict]:
        """
        Constructs the list of messages for the API call, ensuring it fits within max_tokens.
        The summary is treated as a system message. Recent history is prioritized.
        """
        messages_for_api = []
        current_tokens = 0

        # Add summary as system message if present
        if summary_text:
            summary_message = {"role": "system", "content": summary_text}
            summary_tokens = self._count_tokens(summary_text, model_name_for_encoding)
            if summary_tokens < max_tokens: # Only add if summary itself isn't too large
                messages_for_api.append(summary_message)
                current_tokens += summary_tokens
            else:
                print(f"Warning: Summary itself ({summary_tokens} tokens) exceeds max_tokens ({max_tokens}). Sending without summary.", file=sys.stderr)
                # Potentially, we could try to truncate the summary here if it's critical
                # For now, we just omit it if it's too large on its own.

        # Add the new user prompt
        # We need to account for its tokens first as it's the most important
        new_prompt_message = {"role": "user", "content": new_prompt_text}
        new_prompt_tokens = self._count_tokens(new_prompt_text, model_name_for_encoding)

        # Iterate through history from newest to oldest, adding messages if they fit
        temp_history_to_add = []
        remaining_tokens_for_history = max_tokens - current_tokens - new_prompt_tokens
        
        if remaining_tokens_for_history < 0: # Not even space for the new prompt
            print(f"Warning: New prompt ({new_prompt_tokens} tokens) alone (plus summary {current_tokens} tokens) might exceed max_tokens ({max_tokens}). Attempting to send prompt anyway.", file=sys.stderr)
            # If just the prompt and summary are too big, we might have an issue.
            # However, the API might still handle it, or we might need a more aggressive strategy.
            # For now, we'll let it try with at least the prompt if summary was added.
            # If summary was omitted due to its size, this check becomes more critical for the prompt.
            if new_prompt_tokens > max_tokens : # Absolute check if prompt itself is too big
                 print(f"Error: New prompt ({new_prompt_tokens} tokens) exceeds max_tokens ({max_tokens}). Cannot send.", file=sys.stderr)
                 # In this scenario, we can't even send the prompt. This is an issue for the caller to handle (e.g. by disallowing such long prompts)
                 # For now, this method would return a list that's too large, leading to API error or truncation by API.
                 # A robust solution might be to truncate new_prompt_text here, or signal error.
                 # For now, let's assume the calling logic (or user) prevents prompts that are individually too large.
                 pass # Let it proceed, API will likely error out.

        for message in reversed(history_list):
            message_text = message.get("content", "")
            message_tokens = self._count_tokens(message_text, model_name_for_encoding)
            
            if current_tokens + message_tokens + new_prompt_tokens <= max_tokens:
                temp_history_to_add.append(message)
                current_tokens += message_tokens
            else:
                # Not enough space for this message, stop adding older history
                break
        
        messages_for_api.extend(reversed(temp_history_to_add)) # Add in correct chronological order
        messages_for_api.append(new_prompt_message) # Finally, add the new user prompt

        # Final check (mostly for the new_prompt if it was very large)
        final_tokens = sum(self._count_tokens(m["content"], model_name_for_encoding) for m in messages_for_api)
        if final_tokens > max_tokens:
             print(f"Warning: Final constructed messages ({final_tokens} tokens) still exceed max_tokens ({max_tokens}). API might truncate or error.", file=sys.stderr)

        return messages_for_api


    def summarize_conversation(self, text_to_summarize: str, 
                               summary_prompt_template: str = "Please summarize the following text concisely: {text}", 
                               model_for_summarization: str = "gpt-3.5-turbo",
                               max_tokens_summary: int = 150, # Default from prompt, was 150 in code
                               temperature: float = 0.5) -> str | None:
        if "{text}" not in summary_prompt_template:
            print("Error: summary_prompt_template must contain '{text}' placeholder.", file=sys.stderr)
            return None
        prompt = summary_prompt_template.format(text=text_to_summarize)
        payload = { "model": model_for_summarization, "messages": [{"role": "user", "content": prompt}],
                    "temperature": temperature, "max_tokens": max_tokens_summary }
        headers = { "Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json" }
        api_url = f"{self.base_url}/chat/completions"
        try:
            print(f"INFO: Sending summarization request to {api_url} with model: {model_for_summarization}", file=sys.stderr)
            response = requests.post(api_url, headers=headers, json=payload, timeout=60)
            if response.status_code == 200:
                response_data = response.json()
                if ("choices" in response_data and len(response_data["choices"]) > 0 and
                    "message" in response_data["choices"][0] and "content" in response_data["choices"][0]["message"]):
                    return response_data["choices"][0]["message"]["content"].strip()
                else:
                    print(f"Error: Unexpected API response format for summarization. Full response: {response_data}", file=sys.stderr)
            else:
                print(f"Error: Summarization API request failed with status code {response.status_code}. Response: {response.text}", file=sys.stderr)
        except requests.exceptions.Timeout:
            print(f"Error: Summarization API request timed out after 60 seconds to {api_url}.", file=sys.stderr)
        except requests.exceptions.RequestException as e:
            print(f"Error: An exception occurred while making the summarization API request: {e}", file=sys.stderr)
        return None

    def send_message(
        self,
        new_user_prompt: str,
        full_conversation_history: list[dict],
        current_summary: str | None, # Can be None
        model_config: dict, 
        context_management_config: dict
    ) -> tuple[str | None, str | None, list[dict] | None]:
        """
        Sends a message to the chat API, managing context and summarization, and returns the reply.
        """
        ai_response_content = None
        updated_summary = current_summary # By default, summary doesn't change
        messages_sent_to_api = None

        model_name = model_config.get('name', self.model) # Fallback to self.model
        max_tokens_for_model = model_config.get('max_tokens', 4096) # Fallback to a common default

        # --- a. Token Estimation (for deciding on summarization) ---
        # Combine summary, full history, and new prompt for initial estimation
        temp_context_for_estimation = []
        if current_summary:
            temp_context_for_estimation.append({"role": "system", "content": current_summary}) # Tentative role
        temp_context_for_estimation.extend(full_conversation_history)
        temp_context_for_estimation.append({"role": "user", "content": new_user_prompt})
        
        total_estimated_tokens = sum(self._count_tokens(msg.get("content", ""), model_name) for msg in temp_context_for_estimation)
        
        # --- b. Summarization Trigger ---
        threshold_percentage = context_management_config.get('threshold_percentage', 0.75)
        threshold_for_summarization = max_tokens_for_model * threshold_percentage
        
        summary_to_use_for_api = current_summary
        history_part_for_api = list(full_conversation_history) # Make a mutable copy

        if total_estimated_tokens > threshold_for_summarization:
            print(f"INFO: Estimated tokens ({total_estimated_tokens}) exceed threshold ({threshold_for_summarization}). Attempting summarization.", file=sys.stderr)
            
            text_to_summarize_parts = []
            if current_summary:
                text_to_summarize_parts.append(f"Current summary to extend/integrate:\n{current_summary}")

            # Summarize all but the most recent N messages, prepended by current summary (if any)
            max_recent_after_summary = context_management_config.get('max_recent_after_summary', 5)
            num_messages_to_summarize = len(full_conversation_history) - max_recent_after_summary
            
            if num_messages_to_summarize > 0:
                history_to_include_in_summary = full_conversation_history[:num_messages_to_summarize]
                for msg in history_to_include_in_summary:
                    text_to_summarize_parts.append(f"{msg['role'].capitalize()}: {msg['content']}")
            elif not current_summary : # No old history to summarize and no current summary means nothing to summarize
                 print("INFO: Token count high, but not enough old messages to summarize and no existing summary. Proceeding without new summarization.", file=sys.stderr)


            if text_to_summarize_parts: # Only summarize if there's content
                text_to_summarize_str = "\n\n".join(text_to_summarize_parts)
                
                new_summary_candidate = self.summarize_conversation(
                    text_to_summarize=text_to_summarize_str,
                    summary_prompt_template=context_management_config.get('summary_prompt_template', "Summarize: {text}"),
                    model_for_summarization=context_management_config.get('model_for_summarization', self.model),
                    max_tokens_summary=context_management_config.get('max_tokens_for_summary', 250), # Added a default for this
                    temperature=context_management_config.get('temperature_for_summary', 0.5) # Added a default
                )

                if new_summary_candidate:
                    print(f"INFO: Summarization successful. New summary generated.", file=sys.stderr)
                    updated_summary = new_summary_candidate # This is the new state for summary
                    summary_to_use_for_api = new_summary_candidate
                    # Keep only the last N messages from history
                    if max_recent_after_summary > 0 and len(full_conversation_history) >= max_recent_after_summary:
                         history_part_for_api = full_conversation_history[-max_recent_after_summary:]
                    elif len(full_conversation_history) < max_recent_after_summary: # Keep all if fewer than N
                         history_part_for_api = full_conversation_history
                    else: # max_recent_after_summary is 0 or negative
                         history_part_for_api = []
                else:
                    print(f"WARNING: Summarization failed. Using previous summary/full history for context.", file=sys.stderr)
                    # summary_to_use_for_api remains current_summary
                    # history_part_for_api remains full_conversation_history (will be truncated)
            else:
                print("INFO: No content identified for summarization, proceeding with current context.", file=sys.stderr)

        # --- c. Context Assembly and Final Truncation for API Call ---
        send_percentage = context_management_config.get('send_percentage', 0.85)
        max_tokens_to_send_to_api = int(max_tokens_for_model * send_percentage)

        messages_sent_to_api = self._build_messages_for_api(
            summary_text=summary_to_use_for_api,
            history_list=history_part_for_api,
            new_prompt_text=new_user_prompt,
            max_tokens=max_tokens_to_send_to_api,
            model_name_for_encoding=model_name
        )
        
        if not messages_sent_to_api or not any(m['role'] == 'user' for m in messages_sent_to_api):
            print("Error: No messages to send after context assembly, or new user prompt was excluded. Aborting.", file=sys.stderr)
            return None, updated_summary, None


        # --- d. API Call ---
        payload = {
            "model": model_name,
            "messages": messages_sent_to_api,
            # Add other API params like temperature, max_tokens (for response) if needed from model_config
        }
        headers = { "Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json" }
        api_url = f"{self.base_url}/chat/completions"

        try:
            print(f"INFO: Sending final request to {api_url} with model: {model_name}. Effective messages count: {len(messages_sent_to_api)}", file=sys.stderr)
            # For debugging, can print messages_sent_to_api if small enough or token counts
            # total_tokens_sent = sum(self._count_tokens(m["content"], model_name) for m in messages_sent_to_api)
            # print(f"DEBUG: Total tokens being sent: {total_tokens_sent} / {max_tokens_to_send_to_api}", file=sys.stderr)

            response = requests.post(api_url, headers=headers, json=payload, timeout=30)

            if response.status_code == 200:
                response_data = response.json()
                if ("choices" in response_data and len(response_data["choices"]) > 0 and
                    "message" in response_data["choices"][0] and "content" in response_data["choices"][0]["message"]):
                    ai_response_content = response_data["choices"][0]["message"]["content"].strip()
                else:
                    print(f"Error: Unexpected API response format (send_message). Full response: {response_data}", file=sys.stderr)
            else:
                print(f"Error: API request failed (send_message) with status code {response.status_code}. Response: {response.text}", file=sys.stderr)
        
        except requests.exceptions.Timeout:
            print(f"Error: API request timed out (send_message) after 30 seconds to {api_url}.", file=sys.stderr)
        except requests.exceptions.RequestException as e:
            print(f"Error: An exception occurred (send_message) while making the API request: {e}", file=sys.stderr)
        except Exception as e: # Catch any other unexpected errors during API call phase
            print(f"Error: Unexpected error during API call: {e}", file=sys.stderr)


        # --- e. Return Values ---
        # messages_sent_to_api already includes the new_user_prompt.
        # For effective_history_for_api, we might want to exclude the system prompt if the app manages it separately.
        # However, the prompt asks for "actual list of messages (summary + recent) sent to the API".
        # So, messages_sent_to_api seems correct.
        return ai_response_content, updated_summary, messages_sent_to_api


    def get_available_models(self) -> list[str] | None:
        api_url = f"{self.base_url}/models"
        headers = { "Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json", }
        try:
            print(f"INFO: Fetching available models from {api_url}", file=sys.stderr)
            response = requests.get(api_url, headers=headers, timeout=30)
            if response.status_code == 200:
                response_json = response.json()
                model_ids = [ item['id'] for item in response_json.get('data', []) if isinstance(item, dict) and 'id' in item ]
                if not model_ids and isinstance(response_json, list):
                     model_ids = [item['id'] for item in response_json if isinstance(item, dict) and 'id' in item]
                return model_ids
            else:
                print(f"Failed to fetch models: API returned status {response.status_code} - {response.text}", file=sys.stderr)
        except Exception as e:
            print(f"Error fetching models from API: {e}", file=sys.stderr)
        return None


if __name__ == '__main__':
    print("Testing Chatbot class with new send_message logic...")
    API_KEY = os.getenv("TEST_OPENAI_API_KEY")
    BASE_URL = os.getenv("TEST_OPENAI_BASE_URL", "https://api.openai.com/v1")

    if not API_KEY:
        print("Please set TEST_OPENAI_API_KEY and optionally TEST_OPENAI_BASE_URL environment variables to test live API calls.")
    else:
        bot = Chatbot(api_key=API_KEY, base_url=BASE_URL)

        # --- Basic Test for _build_messages_for_api ---
        print("\n--- Test: _build_messages_for_api ---")
        dummy_summary = "This is a background summary."
        dummy_history = [
            {"role": "user", "content": "Old question 1"},
            {"role": "assistant", "content": "Old answer 1"},
            {"role": "user", "content": "Old question 2"},
            {"role": "assistant", "content": "Old answer 2"},
        ]
        dummy_prompt = "New question about everything."
        # Assuming gpt-3.5-turbo has ~4096 tokens. Let's test with a smaller max_tokens for build.
        # Tokens for summary: ~8, prompt: ~6. History items ~4-5 tokens each.
        # Total for above: ~8 + 18 + 6 = 32
        built_messages = bot._build_messages_for_api(dummy_summary, dummy_history, dummy_prompt, 30, "gpt-3.5-turbo")
        print(f"Built messages (limit 30 tokens): {json.dumps(built_messages, indent=2)}")
        # Expected: summary, Old Q2, Old A2, New Q. (Old Q1/A1 likely truncated)
        # Let's verify token count for this specific case
        actual_tokens = sum(bot._count_tokens(m["content"], "gpt-3.5-turbo") for m in built_messages)
        print(f"Token count for built messages: {actual_tokens}")


        # --- Test for send_message (conceptual, requires live API & careful setup) ---
        print("\n--- Test: send_message with context management (conceptual) ---")
        
        sample_history = [
            {"role": "user", "content": "What was the first topic we discussed?"},
            {"role": "assistant", "content": "We first discussed renewable energy, specifically solar power."},
            {"role": "user", "content": "And after that?"},
            {"role": "assistant", "content": "Then we talked about the advantages and disadvantages of solar power."},
        ]
        # Add more messages to make it long
        for i in range(5):
            sample_history.append({"role": "user", "content": f"Tell me more about topic {i+1}."})
            sample_history.append({"role": "assistant", "content": f"Details about topic {i+1} focusing on aspect A and B."})

        model_cfg = {'name': 'gpt-3.5-turbo', 'max_tokens': 4096} # Example
        context_cfg = {
            'threshold_percentage': 0.1, # Low threshold to force summarization for testing
            'send_percentage': 0.85,
            'summary_prompt_template': "Summarize this conversation clearly and concisely: {text}",
            'model_for_summarization': 'gpt-3.5-turbo',
            'max_recent_after_summary': 2,
            'max_tokens_for_summary': 200, # For the summarize_conversation call
            'temperature_for_summary': 0.3
        }
        
        current_sum = None # Start with no summary

        print(f"\nRound 1: Initial message, no summary yet.")
        response1, current_sum, history1 = bot.send_message("My first real question is about AI ethics.", sample_history, current_sum, model_cfg, context_cfg)
        if response1:
            print(f"AI (1): {response1}")
            print(f"Updated Summary (1): {current_sum}")
            # print(f"Effective History (1): {history1}")
        else:
            print("AI (1): Failed to get response.")

        # Simulate another turn
        if response1: # Only if first call was successful
            sample_history.append({"role": "user", "content": "My first real question is about AI ethics."})
            sample_history.append({"role": "assistant", "content": response1})
            
            print(f"\nRound 2: Follow-up, potentially using summary from round 1.")
            response2, current_sum, history2 = bot.send_message("What are the main concerns?", sample_history, current_sum, model_cfg, context_cfg)
            if response2:
                print(f"AI (2): {response2}")
                print(f"Updated Summary (2): {current_sum}")
            else:
                print("AI (2): Failed to get response.")
        
        print("\nNote: Live API calls for send_message with summarization are complex to validate without inspecting intermediate states and token counts precisely. The test above is conceptual.")
        print("Ensure 'tiktoken' is installed: `pip install tiktoken`")

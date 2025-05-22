# chatbot_project/tests/test_chatbot.py

import unittest
from unittest.mock import patch, Mock, mock_open
import os
import sys
import json
import configparser # For TestConfigLoading

# Adjust sys.path to allow imports from src and config
# This is similar to what's done in main.py
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.chatbot import Chatbot
from config.config import load_config
import requests # For requests.exceptions

class TestChatbot(unittest.TestCase):

    def setUp(self):
        self.api_key = "test_api_key"
        self.base_url = "https://api.example.com/v1"
        self.chatbot = Chatbot(api_key=self.api_key, base_url=self.base_url)
        self.test_message = "Hello, chatbot!"
        self.api_url = f"{self.base_url}/chat/completions"

    @patch('src.chatbot.requests.post')
    def test_send_message_success(self, mock_post):
        mock_response = Mock()
        mock_response.status_code = 200
        expected_reply = "This is a test response."
        mock_response.json.return_value = {
            "choices": [{"message": {"content": expected_reply}}]
        }
        mock_post.return_value = mock_response

        reply = self.chatbot.send_message(self.test_message)

        mock_post.assert_called_once_with(
            self.api_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": self.chatbot.model,
                "messages": [{"role": "user", "content": self.test_message}],
            },
            timeout=30
        )
        self.assertEqual(reply, expected_reply)

    @patch('src.chatbot.requests.post')
    def test_send_message_with_history(self, mock_post):
        mock_response = Mock()
        mock_response.status_code = 200
        expected_reply = "Response considering history."
        mock_response.json.return_value = {
            "choices": [{"message": {"content": expected_reply}}]
        }
        mock_post.return_value = mock_response

        conversation_history = [
            {"role": "user", "content": "Previous message"},
            {"role": "assistant", "content": "Previous reply"}
        ]
        current_message = "New message"
        reply = self.chatbot.send_message(current_message, conversation_history=conversation_history)

        expected_messages_payload = conversation_history + [{"role": "user", "content": current_message}]
        mock_post.assert_called_once_with(
            self.api_url,
            headers=unittest.mock.ANY, # Headers checked in another test
            json={
                "model": self.chatbot.model,
                "messages": expected_messages_payload,
            },
            timeout=30
        )
        self.assertEqual(reply, expected_reply)

    @patch('src.chatbot.requests.post')
    def test_send_message_api_error(self, mock_post):
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_post.return_value = mock_response

        reply = self.chatbot.send_message(self.test_message)
        self.assertIsNone(reply)

    @patch('src.chatbot.requests.post')
    def test_send_message_request_exception(self, mock_post):
        mock_post.side_effect = requests.exceptions.RequestException("Network error")

        reply = self.chatbot.send_message(self.test_message)
        self.assertIsNone(reply)

    @patch('src.chatbot.requests.post')
    def test_send_message_timeout_exception(self, mock_post):
        mock_post.side_effect = requests.exceptions.Timeout("Request timed out")

        reply = self.chatbot.send_message(self.test_message)
        self.assertIsNone(reply)

    @patch('src.chatbot.requests.post')
    def test_send_message_json_decode_error(self, mock_post):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = json.JSONDecodeError("Error", "doc", 0)
        mock_response.text = "Invalid JSON" # For the print statement in chatbot.py
        mock_post.return_value = mock_response

        reply = self.chatbot.send_message(self.test_message)
        self.assertIsNone(reply)

    @patch('src.chatbot.requests.post')
    def test_send_message_unexpected_response_format_no_choices(self, mock_post):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"error": "No choices field"}
        mock_post.return_value = mock_response

        reply = self.chatbot.send_message(self.test_message)
        self.assertIsNone(reply)

    @patch('src.chatbot.requests.post')
    def test_send_message_unexpected_response_format_empty_choices(self, mock_post):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"choices": []}
        mock_post.return_value = mock_response

        reply = self.chatbot.send_message(self.test_message)
        self.assertIsNone(reply)

    @patch('src.chatbot.requests.post')
    def test_send_message_unexpected_response_format_no_message(self, mock_post):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"choices": [{"something_else": "data"}]}
        mock_post.return_value = mock_response

        reply = self.chatbot.send_message(self.test_message)
        self.assertIsNone(reply)

    @patch('src.chatbot.requests.post')
    def test_send_message_unexpected_response_format_no_content(self, mock_post):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"choices": [{"message": {"no_content_here": "data"}}]}
        mock_post.return_value = mock_response

        reply = self.chatbot.send_message(self.test_message)
        self.assertIsNone(reply)


class TestConfigLoading(unittest.TestCase):
    
    def setUp(self):
        self.test_config_file_path = "test_config.ini"
        # Clear relevant env vars before each test
        self.original_env = {}
        self.env_vars_to_clear = ['OPENAI_API_KEY', 'OPENAI_BASE_URL']
        for var in self.env_vars_to_clear:
            if var in os.environ:
                self.original_env[var] = os.environ[var]
                del os.environ[var]

    def tearDown(self):
        if os.path.exists(self.test_config_file_path):
            os.remove(self.test_config_file_path)
        # Restore original environment variables
        for var, val in self.original_env.items():
            os.environ[var] = val

    @patch.dict(os.environ, {'OPENAI_API_KEY': 'env_key', 'OPENAI_BASE_URL': 'env_url'})
    def test_load_from_env_vars(self):
        api_key, base_url = load_config(self.test_config_file_path)
        self.assertEqual(api_key, 'env_key')
        self.assertEqual(base_url, 'env_url')

    def test_load_from_ini_file(self):
        config_content = """
[Credentials]
api_key = file_key
base_url = file_url
"""
        with open(self.test_config_file_path, 'w') as f:
            f.write(config_content)
        
        api_key, base_url = load_config(self.test_config_file_path)
        self.assertEqual(api_key, 'file_key')
        self.assertEqual(base_url, 'file_url')

    @patch.dict(os.environ, {'OPENAI_API_KEY': 'env_key_priority', 'OPENAI_BASE_URL': 'env_url_priority'})
    def test_load_env_vars_priority(self):
        config_content = """
[Credentials]
api_key = file_key
base_url = file_url
"""
        with open(self.test_config_file_path, 'w') as f:
            f.write(config_content)
            
        api_key, base_url = load_config(self.test_config_file_path)
        self.assertEqual(api_key, 'env_key_priority')
        self.assertEqual(base_url, 'env_url_priority')

    def test_load_config_file_not_found(self):
        # Ensure file does not exist
        if os.path.exists(self.test_config_file_path):
            os.remove(self.test_config_file_path)
        
        # Suppress warnings from load_config for this test
        with patch('builtins.print'):
            api_key, base_url = load_config("non_existent_config.ini")
        self.assertIsNone(api_key)
        self.assertIsNone(base_url)

    def test_load_config_missing_section(self):
        config_content = """
[OtherSection]
api_key = file_key
"""
        with open(self.test_config_file_path, 'w') as f:
            f.write(config_content)

        with patch('builtins.print'): # Suppress warnings
            api_key, base_url = load_config(self.test_config_file_path)
        self.assertIsNone(api_key) # Assuming api_key is only looked for under [Credentials]
        self.assertIsNone(base_url)

    def test_load_config_missing_option_api_key(self):
        config_content = """
[Credentials]
base_url = file_url
"""
        with open(self.test_config_file_path, 'w') as f:
            f.write(config_content)
        
        with patch('builtins.print'): # Suppress warnings
            api_key, base_url = load_config(self.test_config_file_path)
        self.assertIsNone(api_key)
        self.assertEqual(base_url, 'file_url')

    def test_load_config_missing_option_base_url(self):
        config_content = """
[Credentials]
api_key = file_key
"""
        with open(self.test_config_file_path, 'w') as f:
            f.write(config_content)

        with patch('builtins.print'): # Suppress warnings
            api_key, base_url = load_config(self.test_config_file_path)
        self.assertEqual(api_key, 'file_key')
        self.assertIsNone(base_url)

    def test_load_config_empty_file(self):
        with open(self.test_config_file_path, 'w') as f:
            f.write("") # Empty file
        
        with patch('builtins.print'): # Suppress warnings
            api_key, base_url = load_config(self.test_config_file_path)
        self.assertIsNone(api_key)
        self.assertIsNone(base_url)

    def test_load_config_placeholder_values(self):
        config_content = """
[Credentials]
api_key = YOUR_API_KEY_HERE
base_url = YOUR_BASE_URL_HERE
"""
        with open(self.test_config_file_path, 'w') as f:
            f.write(config_content)
        
        with patch('builtins.print'): # Suppress warnings
            api_key, base_url = load_config(self.test_config_file_path)
        self.assertIsNone(api_key) # Placeholders should be treated as if not set
        self.assertIsNone(base_url)


if __name__ == '__main__':
    # This allows running the tests directly from this file:
    # python chatbot_project/tests/test_chatbot.py
    # However, standard practice is `python -m unittest discover tests` from project root
    unittest.main()

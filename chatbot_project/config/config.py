# chatbot_project/config/config.py

import configparser
import os
import sys # For printing to stderr

def load_config(config_file_path: str = 'config.ini') -> tuple[
    str | None, str | None, list[str], # Credentials and Models
    float, float, str, str, int, int # Context Management
]:
    """
    Loads API key, base URL, models list, and context management parameters.

    Priority for loading:
    1. Environment variables.
    2. Configuration file (e.g., config.ini).
    3. Hardcoded defaults.

    Args:
        config_file_path (str): The path to the configuration file.
                                Defaults to 'config.ini'.

    Returns:
        tuple: Contains:
            - api_key (str | None)
            - base_url (str | None)
            - models_list (list[str])
            - context_threshold_percentage (float)
            - max_context_send_percentage (float)
            - default_summary_prompt (str)
            - default_model_for_summarization (str)
            - max_recent_messages_after_summary (int)
            - assumed_chat_model_max_tokens (int)
    """
    # --- Default values ---
    api_key = None
    base_url = None
    models_list = []

    # Context Management Defaults
    context_threshold_percentage = 0.75
    max_context_send_percentage = 0.85
    default_summary_prompt = "Summarize the following conversation, focusing on key facts, decisions, and the main timeline of events. Condense it as much as possible while retaining critical information for future context: {text}"
    default_model_for_summarization = "gpt-3.5-turbo"
    max_recent_messages_after_summary = 5
    assumed_chat_model_max_tokens = 4096

    config = configparser.ConfigParser()

    # --- Helper for env var loading ---
    def get_env_var(env_name, current_value, type_converter=None):
        env_value = os.getenv(env_name)
        if env_value is not None:
            print(f"INFO: Found '{env_name}' in environment variables.", file=sys.stderr)
            if type_converter:
                try:
                    return type_converter(env_value)
                except ValueError:
                    print(f"WARNING: Could not convert env var {env_name}='{env_value}' to required type. Using default/INI value.", file=sys.stderr)
                    return current_value # Fallback to current (default or previous)
            return env_value
        return current_value

    # --- Load Credentials and Models from Environment Variables ---
    print("INFO: Checking environment variables for API credentials, models, and context settings...", file=sys.stderr)
    api_key = get_env_var('OPENAI_API_KEY', api_key)
    base_url = get_env_var('OPENAI_BASE_URL', base_url)
    models_env_str = get_env_var('OPENAI_MODELS', None)
    if models_env_str:
        models_list = [model.strip() for model in models_env_str.split(',') if model.strip()]
        if models_list:
            print(f"INFO: Loaded models from env: {models_list}", file=sys.stderr)

    # --- Load Context Management from Environment Variables ---
    context_threshold_percentage = get_env_var('CONTEXT_THRESHOLD_PERCENTAGE', context_threshold_percentage, float)
    max_context_send_percentage = get_env_var('MAX_CONTEXT_SEND_PERCENTAGE', max_context_send_percentage, float)
    default_summary_prompt = get_env_var('DEFAULT_SUMMARY_PROMPT', default_summary_prompt)
    default_model_for_summarization = get_env_var('DEFAULT_MODEL_FOR_SUMMARIZATION', default_model_for_summarization)
    max_recent_messages_after_summary = get_env_var('MAX_RECENT_MESSAGES_AFTER_SUMMARY', max_recent_messages_after_summary, int)
    assumed_chat_model_max_tokens = get_env_var('ASSUMED_CHAT_MODEL_MAX_TOKENS', assumed_chat_model_max_tokens, int)

    # --- Load from INI file if not fully set by environment variables or defaults are still active ---
    try:
        # Adjust path to be relative to this script's directory if a simple filename is given
        if not os.path.isabs(config_file_path) and not os.path.dirname(config_file_path):
             script_dir = os.path.dirname(__file__)
             # Handle case where script_dir might be empty (e.g. running from root with `python config/config.py`)
             if not script_dir: script_dir = "." 
             # Check if config_file_path is 'config.ini' and we are in 'config' dir, then it's just 'config.ini'
             # Otherwise, if it's 'config.ini' and we are likely in project root, it's 'config/config.ini'
             if os.path.basename(config_file_path) == 'config.ini' and os.path.basename(script_dir) == 'config':
                 path_to_try = os.path.join(script_dir, os.path.basename(config_file_path)) # e.g. ./config.ini from config/
             else: # Default case if called from project root or other locations
                 path_to_try = os.path.join(script_dir, "..", "config", os.path.basename(config_file_path)) # e.g. config/config.ini
                 # More robust: try to find config.ini relative to where 'config.py' is or in a 'config' subdirectory
                 if not os.path.exists(path_to_try):
                     path_to_try = os.path.join(script_dir, os.path.basename(config_file_path)) # Try in current script dir
                 if not os.path.exists(path_to_try) and os.path.basename(script_dir) != 'config': # If not in script dir, try one level up then into config
                     path_to_try = os.path.join(os.path.dirname(script_dir), "config", os.path.basename(config_file_path))


             # Fallback for direct execution from project root: `python config/config.py`
             # In this case, config_file_path='config.ini' is intended to be `config/config.ini`
             # However, the logic above might make it `config/../config/config.ini`.
             # A simpler approach for the default 'config.ini':
             if config_file_path == 'config.ini':
                 potential_paths = [
                     os.path.join(os.path.dirname(__file__), '..', 'config', 'config.ini'), # from src/
                     os.path.join(os.path.dirname(__file__), 'config.ini'),                # from config/
                     'config/config.ini'                                                  # from project root
                 ]
                 actual_config_path = None
                 for p in potential_paths:
                     if os.path.exists(p):
                         actual_config_path = p
                         break
                 if actual_config_path:
                     config_file_path = actual_config_path
                 else: # Default to trying to find it in a 'config' subdirectory from current working directory if all else fails
                     config_file_path = os.path.join(os.getcwd(), 'config', 'config.ini') if not os.path.exists(config_file_path) else config_file_path


        if not os.path.exists(config_file_path):
            print(f"WARNING: Configuration file '{config_file_path}' not found. Using defaults or environment variables if set.", file=sys.stderr)
        else:
            print(f"INFO: Reading configuration from '{config_file_path}'", file=sys.stderr)
            config.read(config_file_path)

            # Credentials Section
            if 'Credentials' in config:
                if api_key is None: api_key = config.get('Credentials', 'api_key', fallback=None)
                if base_url is None: base_url = config.get('Credentials', 'base_url', fallback=None)
                if not models_list: # Only load from INI if not set by env
                    models_ini_str = config.get('Credentials', 'models', fallback='')
                    if models_ini_str:
                        models_list = [model.strip() for model in models_ini_str.split(',') if model.strip()]
                        if models_list: print(f"INFO: Loaded models from INI: {models_list}", file=sys.stderr)
                
                # Handle placeholder values from INI for api_key and base_url
                if api_key == "YOUR_API_KEY_HERE":
                    print("WARNING: API key in INI is a placeholder. Please replace it.", file=sys.stderr)
                    api_key = None
                if base_url == "YOUR_BASE_URL_HERE":
                    print("WARNING: Base URL in INI is a placeholder. Please replace it.", file=sys.stderr)
                    base_url = None
            
            # ContextManagement Section (load only if not set by env, i.e., still at default)
            if 'ContextManagement' in config:
                if context_threshold_percentage == 0.75: # Default check
                    context_threshold_percentage = config.getfloat('ContextManagement', 'context_threshold_percentage', fallback=context_threshold_percentage)
                if max_context_send_percentage == 0.85: # Default check
                    max_context_send_percentage = config.getfloat('ContextManagement', 'max_context_send_percentage', fallback=max_context_send_percentage)
                if default_summary_prompt == "Summarize the following conversation, focusing on key facts, decisions, and the main timeline of events. Condense it as much as possible while retaining critical information for future context: {text}": # Default check
                    default_summary_prompt = config.get('ContextManagement', 'default_summary_prompt', fallback=default_summary_prompt)
                if default_model_for_summarization == "gpt-3.5-turbo": # Default check
                    default_model_for_summarization = config.get('ContextManagement', 'default_model_for_summarization', fallback=default_model_for_summarization)
                if max_recent_messages_after_summary == 5: # Default check
                    max_recent_messages_after_summary = config.getint('ContextManagement', 'max_recent_messages_after_summary', fallback=max_recent_messages_after_summary)
                if assumed_chat_model_max_tokens == 4096: # Default check
                    assumed_chat_model_max_tokens = config.getint('ContextManagement', 'assumed_chat_model_max_tokens', fallback=assumed_chat_model_max_tokens)

    except FileNotFoundError: # Should be caught by os.path.exists, but as a safeguard
        print(f"WARNING: Configuration file '{config_file_path}' not found. Using defaults or environment variables.", file=sys.stderr)
    except Exception as e:
        print(f"ERROR: Could not parse configuration file '{config_file_path}': {e}. Using defaults or environment variables.", file=sys.stderr)

    # Final checks for critical values
    if not api_key:
        print("CRITICAL: API key not found. Please set OPENAI_API_KEY or add to config file.", file=sys.stderr)
    if not base_url:
        print("CRITICAL: Base URL not found. Please set OPENAI_BASE_URL or add to config file.", file=sys.stderr)
    if not models_list:
        print("INFO: No models configured. UI may use a default list or fetch from API if capable.", file=sys.stderr)

    return (
        api_key, base_url, models_list,
        context_threshold_percentage, max_context_send_percentage,
        default_summary_prompt, default_model_for_summarization,
        max_recent_messages_after_summary, assumed_chat_model_max_tokens
    )

if __name__ == '__main__':
    print("--- Testing load_config directly (config.py) ---")
    
    # Create a dummy config.ini for testing
    dummy_config_path = 'dummy_config_for_test.ini'
    with open(dummy_config_path, 'w') as f:
        f.write("[Credentials]\n")
        f.write("api_key = TEST_KEY_FROM_FILE\n")
        f.write("base_url = https://api.example.com/v1/from_file\n")
        f.write("models = gpt-3.5-turbo-file, gpt-4-file\n\n")
        f.write("[ContextManagement]\n")
        f.write("context_threshold_percentage = 0.70\n")
        f.write("max_context_send_percentage = 0.80\n")
        f.write("default_summary_prompt = Custom summary prompt: {text}\n")
        f.write("default_model_for_summarization = gpt-4-file-summary\n")
        f.write("max_recent_messages_after_summary = 3\n")
        f.write("assumed_chat_model_max_tokens = 8000\n")

    print(f"\n1. Test loading from file '{dummy_config_path}':")
    (api_k, base_u, models_l, ctx_thresh, max_ctx_send, sum_prompt, sum_model, max_recent, assumed_tokens) = load_config(dummy_config_path)
    print(f"  API Key: {api_k}")
    print(f"  Base URL: {base_u}")
    print(f"  Models List: {models_l}")
    print(f"  Context Threshold %: {ctx_thresh}")
    print(f"  Max Context Send %: {max_ctx_send}")
    print(f"  Default Summary Prompt: '{sum_prompt}'")
    print(f"  Default Model for Summarization: {sum_model}")
    print(f"  Max Recent Messages After Summary: {max_recent}")
    print(f"  Assumed Chat Model Max Tokens: {assumed_tokens}")

    print("\n2. Test loading with environment variables (should override file):")
    os.environ['OPENAI_API_KEY'] = 'ENV_KEY'
    os.environ['OPENAI_BASE_URL'] = 'ENV_URL'
    os.environ['OPENAI_MODELS'] = 'env-model1,env-model2'
    os.environ['CONTEXT_THRESHOLD_PERCENTAGE'] = '0.65'
    os.environ['MAX_CONTEXT_SEND_PERCENTAGE'] = '0.75'
    os.environ['DEFAULT_SUMMARY_PROMPT'] = 'Env summary prompt: {text}'
    os.environ['DEFAULT_MODEL_FOR_SUMMARIZATION'] = 'env-summary-model'
    os.environ['MAX_RECENT_MESSAGES_AFTER_SUMMARY'] = '2'
    os.environ['ASSUMED_CHAT_MODEL_MAX_TOKENS'] = '16000'

    (api_k_e, base_u_e, models_l_e, ctx_thresh_e, max_ctx_send_e, sum_prompt_e, sum_model_e, max_recent_e, assumed_tokens_e) = load_config(dummy_config_path)
    print(f"  API Key (Env): {api_k_e}")
    print(f"  Base URL (Env): {base_u_e}")
    print(f"  Models List (Env): {models_l_e}")
    print(f"  Context Threshold % (Env): {ctx_thresh_e}")
    print(f"  Max Context Send % (Env): {max_ctx_send_e}")
    print(f"  Default Summary Prompt (Env): '{sum_prompt_e}'")
    print(f"  Default Model for Summarization (Env): {sum_model_e}")
    print(f"  Max Recent Messages After Summary (Env): {max_recent_e}")
    print(f"  Assumed Chat Model Max Tokens (Env): {assumed_tokens_e}")

    # Clean up environment variables
    del os.environ['OPENAI_API_KEY']
    del os.environ['OPENAI_BASE_URL']
    del os.environ['OPENAI_MODELS']
    del os.environ['CONTEXT_THRESHOLD_PERCENTAGE']
    del os.environ['MAX_CONTEXT_SEND_PERCENTAGE']
    del os.environ['DEFAULT_SUMMARY_PROMPT']
    del os.environ['DEFAULT_MODEL_FOR_SUMMARIZATION']
    del os.environ['MAX_RECENT_MESSAGES_AFTER_SUMMARY']
    del os.environ['ASSUMED_CHAT_MODEL_MAX_TOKENS']

    print("\n3. Test loading with no INI file (should use defaults):")
    # Ensure no dummy file exists for this test
    if os.path.exists(dummy_config_path): os.remove(dummy_config_path)
    if os.path.exists('config.ini'): # Also remove standard config.ini if it exists for a clean default test
        print("Temporarily moving existing config.ini for default test")
        os.rename('config.ini', 'config.ini.temp_for_test')
        
    (api_k_d, base_u_d, models_l_d, ctx_thresh_d, max_ctx_send_d, sum_prompt_d, sum_model_d, max_recent_d, assumed_tokens_d) = load_config("non_existent_config.ini")
    print(f"  API Key (Default): {api_k_d}") # Expected None
    print(f"  Base URL (Default): {base_u_d}") # Expected None
    print(f"  Models List (Default): {models_l_d}") # Expected []
    print(f"  Context Threshold % (Default): {ctx_thresh_d}")
    print(f"  Max Context Send % (Default): {max_ctx_send_d}")
    print(f"  Default Summary Prompt (Default): '{sum_prompt_d}'")
    print(f"  Default Model for Summarization (Default): {sum_model_d}")
    print(f"  Max Recent Messages After Summary (Default): {max_recent_d}")
    print(f"  Assumed Chat Model Max Tokens (Default): {assumed_tokens_d}")

    if os.path.exists('config.ini.temp_for_test'):
        os.rename('config.ini.temp_for_test', 'config.ini')

    # Clean up dummy file
    if os.path.exists(dummy_config_path):
        os.remove(dummy_config_path)

    print("\n--- load_config testing complete ---")

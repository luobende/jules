# chatbot_project/config/config.py

import configparser
import os

def load_config(config_file_path: str = 'config.ini') -> tuple[str | None, str | None, list[str]]:
    """
    Loads API key, base URL, and an optional list of models for the chatbot.

    Priority for loading:
    1. Environment variables (OPENAI_API_KEY, OPENAI_BASE_URL, OPENAI_MODELS).
    2. Configuration file (e.g., config.ini).

    Args:
        config_file_path (str): The path to the configuration file.
                                Defaults to 'config.ini'.

    Returns:
        tuple[str | None, str | None, list[str]]: 
            A tuple containing (api_key, base_url, models_list).
            api_key and base_url can be None if not found.
            models_list will be an empty list if not configured or found.
    """
    api_key = None
    base_url = None
    models_list = []

    # 1. Check environment variables first
    print("INFO: Checking environment variables for API credentials and models...")
    api_key_env = os.getenv('OPENAI_API_KEY')
    base_url_env = os.getenv('OPENAI_BASE_URL')
    models_env = os.getenv('OPENAI_MODELS')

    if api_key_env:
        print("INFO: API key found in environment variable OPENAI_API_KEY.")
        api_key = api_key_env
    if base_url_env:
        print("INFO: Base URL found in environment variable OPENAI_BASE_URL.")
        base_url = base_url_env
    if models_env:
        print("INFO: Models list found in environment variable OPENAI_MODELS.")
        models_list = [model.strip() for model in models_env.split(',') if model.strip()]
        if models_list:
             print(f"INFO: Loaded models from env: {models_list}")


    # If not all found in environment variables (api_key, base_url) or models_list is empty,
    # try to load from config file.
    # Models list from env takes precedence if present.
    should_try_config_file = False
    if not api_key or not base_url:
        should_try_config_file = True
        print(f"INFO: API key or Base URL not fully found in environment variables. Trying to load from '{config_file_path}'...")
    
    if not models_list: # If models were not loaded from env, try from config
        should_try_config_file = True
        print(f"INFO: Models list not found or empty in environment variables. Trying to load from '{config_file_path}'...")


    if should_try_config_file:
        config = configparser.ConfigParser()
        try:
            # Path adjustment logic (simplified for clarity, assuming config_file_path is correctly relative or absolute)
            if not os.path.exists(config_file_path):
                # Attempt to find it relative to common execution points (e.g., project root or src/)
                # This part is a heuristic and might need adjustment based on actual run locations.
                alt_path_from_src = os.path.join(os.path.dirname(__file__), '..', config_file_path) # e.g. ../config/config.ini from src/streamlit_app.py
                alt_path_in_config_dir = os.path.join(os.path.dirname(__file__), os.path.basename(config_file_path)) # e.g. config/config.ini from root

                if os.path.exists(alt_path_from_src):
                    config_file_path = alt_path_from_src
                    print(f"INFO: Adjusted config path to: {config_file_path}")
                elif os.path.exists(alt_path_in_config_dir) and config_file_path != alt_path_in_config_dir: # if called from project root
                    config_file_path = alt_path_in_config_dir
                    print(f"INFO: Adjusted config path to: {config_file_path}")
                elif not os.path.exists(config_file_path): # if still not found after trying alts
                     raise FileNotFoundError(f"Configuration file '{config_file_path}' not found in typical locations.")


            read_files = config.read(config_file_path)
            if not read_files:
                 raise FileNotFoundError(f"Configuration file '{config_file_path}' found but could not be read or is empty.")

            if 'Credentials' in config:
                if not api_key and 'api_key' in config['Credentials']:
                    api_key_file = config['Credentials']['api_key']
                    if api_key_file and api_key_file != "YOUR_API_KEY_HERE":
                        print(f"INFO: API key loaded from '{config_file_path}'.")
                        api_key = api_key_file
                    elif api_key_file == "YOUR_API_KEY_HERE":
                        print(f"WARNING: API key in '{config_file_path}' is a placeholder.")
                    else:
                        print(f"WARNING: API key in '{config_file_path}' is empty.")

                if not base_url and 'base_url' in config['Credentials']:
                    base_url_file = config['Credentials']['base_url']
                    if base_url_file and base_url_file != "YOUR_BASE_URL_HERE":
                        print(f"INFO: Base URL loaded from '{config_file_path}'.")
                        base_url = base_url_file
                    elif base_url_file == "YOUR_BASE_URL_HERE":
                        print(f"WARNING: Base URL in '{config_file_path}' is a placeholder.")
                    else:
                         print(f"WARNING: Base URL in '{config_file_path}' is empty.")
                
                # Load models only if not already loaded from environment
                if not models_list and 'models' in config['Credentials']:
                    models_file_str = config['Credentials']['models']
                    if models_file_str:
                        models_list_file = [model.strip() for model in models_file_str.split(',') if model.strip()]
                        if models_list_file:
                            print(f"INFO: Models list loaded from '{config_file_path}': {models_list_file}")
                            models_list = models_list_file
                        else:
                            print(f"WARNING: 'models' key in '{config_file_path}' is empty or contains only whitespace/commas.")
                    else:
                        print(f"WARNING: 'models' key in '{config_file_path}' is empty.")

            else: # No [Credentials] section
                if not api_key or not base_url or not models_list: # Only warn if we actually needed something
                    print(f"WARNING: Section [Credentials] not found in '{config_file_path}'.")

        except FileNotFoundError:
            if not api_key or not base_url or not models_list:
                print(f"WARNING: Configuration file '{config_file_path}' not found.")
        except (configparser.NoSectionError, configparser.NoOptionError) as e:
            if not api_key or not base_url or not models_list:
                print(f"ERROR: Error reading configuration file '{config_file_path}': {e}")
        except configparser.Error as e:
            if not api_key or not base_url or not models_list:
                print(f"ERROR: Could not parse configuration file '{config_file_path}': {e}")

    # Final checks and warnings
    if not api_key:
        print("CRITICAL: API key not found. Please set OPENAI_API_KEY or add to config file.")
    if not base_url:
        print("CRITICAL: Base URL not found. Please set OPENAI_BASE_URL or add to config file.")
    if not models_list: # This means neither env var nor config file provided models
        print("INFO: No models configured via OPENAI_MODELS or config file. UI may use a default list.")

    return api_key, base_url, models_list

if __name__ == '__main__':
    print("--- Testing load_config directly (config.py) ---")
    
    # Create a dummy config.ini for testing
    dummy_config_path = 'dummy_config.ini'
    with open(dummy_config_path, 'w') as f:
        f.write("[Credentials]\n")
        f.write("api_key = TEST_KEY_FROM_FILE\n")
        f.write("base_url = https://api.example.com/v1/from_file\n")
        f.write("models = gpt-3.5-turbo-file, gpt-4-file\n")

    print(f"\n1. Test loading from file '{dummy_config_path}':")
    key, url, models = load_config(dummy_config_path)
    print(f"Loaded API Key: {key}")
    print(f"Loaded Base URL: {url}")
    print(f"Loaded Models: {models}")

    print("\n2. Test loading with environment variables (should override file):")
    os.environ['OPENAI_API_KEY'] = 'TEST_KEY_FROM_ENV'
    os.environ['OPENAI_BASE_URL'] = 'https://api.example.com/v1/from_env'
    os.environ['OPENAI_MODELS'] = 'gpt-env-model1, gpt-env-model2, gpt-env-model3'
    key_env, url_env, models_env = load_config(dummy_config_path)
    print(f"Loaded API Key (from env): {key_env}")
    print(f"Loaded Base URL (from env): {url_env}")
    print(f"Loaded Models (from env): {models_env}")
    
    print("\n3. Test loading with only API_KEY from env (base_url and models from file):")
    del os.environ['OPENAI_BASE_URL']
    del os.environ['OPENAI_MODELS']
    key_env_only, url_file_only, models_file_only = load_config(dummy_config_path)
    print(f"Loaded API Key (from env): {key_env_only}")
    print(f"Loaded Base URL (from file): {url_file_only}")
    print(f"Loaded Models (from file): {models_file_only}")

    # Clean up environment variables and dummy file
    del os.environ['OPENAI_API_KEY']
    if os.path.exists(dummy_config_path):
        os.remove(dummy_config_path)

    print("\n--- load_config testing complete ---")

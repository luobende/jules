# chatbot_project/config/config.py

import configparser
import os

def load_config(config_file_path: str = 'config.ini') -> tuple[str | None, str | None]:
    """
    Loads API key and base URL for the chatbot.

    Priority for loading:
    1. Environment variables (OPENAI_API_KEY, OPENAI_BASE_URL).
    2. Configuration file (e.g., config.ini).

    Args:
        config_file_path (str): The path to the configuration file.
                                Defaults to 'config.ini'. Assumed to be relative
                                to the project root if called from scripts in root,
                                or adjusted path if called from elsewhere (e.g. src/main.py).

    Returns:
        tuple[str | None, str | None]: A tuple containing (api_key, base_url).
                                       Values can be None if not found.
    """
    api_key = None
    base_url = None

    # 1. Check environment variables first
    print("INFO: Checking environment variables for API credentials...")
    api_key_env = os.getenv('OPENAI_API_KEY')
    base_url_env = os.getenv('OPENAI_BASE_URL')

    if api_key_env:
        print("INFO: API key found in environment variable OPENAI_API_KEY.")
        api_key = api_key_env
    if base_url_env:
        print("INFO: Base URL found in environment variable OPENAI_BASE_URL.")
        base_url = base_url_env

    # If not all found in environment variables, try to load from config file
    if not api_key or not base_url:
        print(f"INFO: Not all credentials found in environment variables. Trying to load from '{config_file_path}'...")
        config = configparser.ConfigParser()
        try:
            if not os.path.exists(config_file_path):
                # This case is primarily for when the default path is used and the file is missing.
                # If a specific path is provided and it doesn't exist, FileNotFoundError will be raised by read().
                if config_file_path == 'config.ini' and not os.path.exists('../config/config.ini') and not os.path.exists('config/config.ini'):
                     print(f"WARNING: Configuration file '{config_file_path}' not found in common locations relative to execution.")
                     # Try to infer common locations if called from src or root
                     potential_paths = [config_file_path, f"../{config_file_path}", f"config/{os.path.basename(config_file_path)}"]
                     found_path = None
                     for p_path in potential_paths:
                         if os.path.exists(p_path):
                             config_file_path = p_path
                             found_path = True
                             break
                     if not found_path:
                         print(f"WARNING: Configuration file '{config_file_path}' not found.")

            if not os.path.exists(config_file_path): # Re-check after potential path adjustment
                 raise FileNotFoundError(f"Configuration file '{config_file_path}' not found.")


            read_files = config.read(config_file_path)
            if not read_files: # Check if config.read actually read any files
                 raise FileNotFoundError(f"Configuration file '{config_file_path}' found but could not be read or is empty.")


            if 'Credentials' in config:
                if not api_key and 'api_key' in config['Credentials']:
                    api_key_file = config['Credentials']['api_key']
                    if api_key_file and api_key_file != "YOUR_API_KEY_HERE":
                        print(f"INFO: API key loaded from '{config_file_path}'.")
                        api_key = api_key_file
                    elif api_key_file == "YOUR_API_KEY_HERE":
                        print(f"WARNING: API key in '{config_file_path}' is a placeholder. Please replace it.")
                    else:
                        print(f"WARNING: API key in '{config_file_path}' is empty.")


                if not base_url and 'base_url' in config['Credentials']:
                    base_url_file = config['Credentials']['base_url']
                    if base_url_file and base_url_file != "YOUR_BASE_URL_HERE":
                        print(f"INFO: Base URL loaded from '{config_file_path}'.")
                        base_url = base_url_file
                    elif base_url_file == "YOUR_BASE_URL_HERE":
                        print(f"WARNING: Base URL in '{config_file_path}' is a placeholder. Please replace it.")
                    else:
                         print(f"WARNING: Base URL in '{config_file_path}' is empty.")

            else:
                print(f"WARNING: Section [Credentials] not found in '{config_file_path}'.")

        except FileNotFoundError:
            # This is expected if the file doesn't exist and env vars are also not set.
            # Only print a warning if we haven't already found the credentials in env vars.
            if not api_key or not base_url:
                print(f"WARNING: Configuration file '{config_file_path}' not found.")
        except (configparser.NoSectionError, configparser.NoOptionError) as e:
            # This means the file exists but is malformed or missing expected keys.
            if not api_key or not base_url:
                print(f"ERROR: Error reading configuration file '{config_file_path}': {e}")
        except configparser.Error as e: # Catch any other configparser errors
            if not api_key or not base_url:
                print(f"ERROR: Could not parse configuration file '{config_file_path}': {e}")


    # Final checks and warnings
    if not api_key:
        print("CRITICAL: API key not found. Please set the OPENAI_API_KEY environment variable or add it to the configuration file.")
    if not base_url:
        print("CRITICAL: Base URL not found. Please set the OPENAI_BASE_URL environment variable or add it to the configuration file.")

    return api_key, base_url

if __name__ == '__main__':
    # Example of how to use:
    # This part is for testing the function directly and will not run when imported.
    print("--- Testing load_config directly (config.py) ---")
    # Test with default path (assuming config.ini might be in parent or current dir)
    # Create a dummy config.ini for testing if it doesn't exist
    if not os.path.exists('config.ini') and not os.path.exists('../config/config.ini'):
        print("Creating a dummy 'config.ini' for testing load_config...")
        with open('config.ini', 'w') as f:
            f.write("[Credentials]\n")
            f.write("api_key = TEST_KEY_FROM_FILE\n")
            f.write("base_url = https://api.example.com/v1/from_file\n")
        config_path_to_test = 'config.ini'
    elif os.path.exists('../config/config.ini'):
        config_path_to_test = '../config/config.ini'
        print("INFO: Found config.ini in parent directory for testing.")
    elif os.path.exists('config/config.ini'):
        config_path_to_test = 'config/config.ini'
        print("INFO: Found config.ini in config/ directory for testing.")
    else:
        config_path_to_test = 'config.ini' # Fallback to current dir
        print("INFO: Using 'config.ini' from current directory for testing (if it exists).")


    print(f"\nAttempting to load configuration using path: '{config_path_to_test}'")
    key, url = load_config(config_path_to_test)
    print(f"Loaded API Key: {key}")
    print(f"Loaded Base URL: {url}")

    print("\n--- Testing with environment variables (config.py) ---")
    os.environ['OPENAI_API_KEY'] = 'TEST_KEY_FROM_ENV'
    os.environ['OPENAI_BASE_URL'] = 'https://api.example.com/v1/from_env'
    key_env, url_env = load_config(config_path_to_test) # Config file should be ignored now
    print(f"Loaded API Key (from env): {key_env}")
    print(f"Loaded Base URL (from env): {url_env}")
    del os.environ['OPENAI_API_KEY']
    del os.environ['OPENAI_BASE_URL']

    if os.path.exists('config.ini') and "TEST_KEY_FROM_FILE" in open('config.ini').read():
        print("\nRemoving dummy 'config.ini' created for testing.")
        os.remove('config.ini')

    print("--- load_config testing complete ---")

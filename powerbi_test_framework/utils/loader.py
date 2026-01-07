
import json

# Global placeholders
MONDAY_API_KEY = None
MONDAY_API_URL = None
MONDAY_FILE_URL = None
BOARD_NAME = None
GROUP_NAME = None
REPORT_PATH = None
ENVIRONMENT = None

def load(env: str):
    """Loads config values globally based on environment name."""
    global MONDAY_API_KEY, MONDAY_API_URL, MONDAY_FILE_URL, BOARD_NAME, GROUP_NAME, REPORT_PATH, ENVIRONMENT

    with open("powerbi_test_framework/utils/config.json", "r") as f:
        data = json.load(f)

    if env not in data:
        raise ValueError(f"❌ '{env}' not found in config.json. Available: {list(data.keys())}")

    env_data = data[env]

    MONDAY_API_KEY = env_data.get("MONDAY_API_KEY")
    MONDAY_API_URL = env_data.get("MONDAY_API_URL")
    MONDAY_FILE_URL = env_data.get("MONDAY_FILE_URL")
    BOARD_NAME = env_data.get("BOARD_NAME")
    GROUP_NAME = env_data.get("GROUP_NAME")
    REPORT_PATH = env_data.get("REPORT_PATH")
    ENVIRONMENT = env

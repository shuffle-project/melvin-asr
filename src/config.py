"""config file that reads all config from .env or CMD environment for app"""
import os
from dotenv import dotenv_values

def read_config() -> dict:
    """Read the config from .env or environment variables, returns dict with config"""
    dotenv_config = dotenv_values()

    def get_config(key, required=False, default=None):
        """Function to check and get configuration"""
        # Try to get value from .env, otherwise from environment variable, otherwise default
        value = dotenv_config.get(key, os.getenv(key, default))
        if required and value is None:
            raise ValueError(
                f"Configuration error: '{key}' is not set in .env, as an environment variable or as a default value"
            )
        return value

    # All config variables
    return {
        "PORT": int(get_config("PORT", default="1234")),
        "WEBSOCKET_PORT": int(get_config("WEBSOCKET_PORT", default="1235")),
        "ENVIRONMENT": get_config("ENVIRONMENT", default="development"),
        "HOST": get_config("HOST", default="localhost"),
        "MODEL": get_config("MODEL", required=True),
        "API_KEY": get_config("API_KEY", required=True),
        "DEBUG": get_config("DEBUG", default=False),
        "WHISPER_MODELS": get_config("WHISPER_MODELS", required=True),
        "AUDIO_FILE_PATH": get_config("AUDIO_FILE_PATH", required=True),
        "STATUS_PATH": get_config("STATUS_PATH", required=True),
        "AUDIO_FILE_FORMAT": get_config("AUDIO_FILE_FORMAT", required=True),
    }

try:
    CONFIG = read_config()
except ValueError as e:
    print(f"Error: {e}")
    CONFIG = None

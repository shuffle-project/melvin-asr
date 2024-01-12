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
                f"Configuration error: '{key}' is not set in .env" +
                " as an environment variable or as a default value"
            )
        return value

    # All config variables
    return {
        "PORT": int(get_config("PORT", default="1234")),
        "WEBSOCKET_PORT": int(get_config("WEBSOCKET_PORT", default="1235")),
        "ENVIRONMENT": get_config("ENVIRONMENT", default="development"),
        "HOST": get_config("HOST", default="localhost"),
        "MODEL_PATH": get_config("MODEL_PATH", required=True),
        "MODEL_CONFIG_YAML_PATH": get_config("MODEL_CONFIG_YAML_PATH", required=True),
        "UNLAOD_REST_MODELS_SCHEDULE": get_config("UNLAOD_REST_MODELS_SCHEDULE", required=True),
        "STREAM_MODEL": get_config("STREAM_MODEL", required=True),
        "STREAM_MODEL_DEVICE": get_config("STREAM_MODEL_DEVICE", required=True),
        "STREAM_MODEL_COMPUTE_TYPE": get_config("STREAM_MODEL_COMPUTE_TYPE", required=True),
        "API_KEY": get_config("API_KEY", required=True),
        "DEBUG": get_config("DEBUG", default=False),
        "AUDIO_FILE_PATH": get_config("AUDIO_FILE_PATH", required=True),
        "STATUS_PATH": get_config("STATUS_PATH", required=True),
        "AUDIO_FILE_FORMAT": get_config("AUDIO_FILE_FORMAT", required=True),
        "MAX_OLD_STATUS_FILES": get_config("MAX_OLD_STATUS_FILES", required=True),
        "CLEAN_UP_SCHEDULE": get_config("CLEAN_UP_SCHEDULE", required=True),
    }


try:
    CONFIG = read_config()
except ValueError as e:
    print(f"Error: {e}")
    CONFIG = None

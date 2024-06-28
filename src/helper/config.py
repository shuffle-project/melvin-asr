"""config file that reads all config from .env or CMD environment for app"""
import os
import yaml


def read_config(config_yml_path: str) -> dict:
    """Read the config from .env or environment variables, returns dict with config"""

    config = {}
    with open(config_yml_path, "r", encoding="utf-8") as data:
        config = yaml.safe_load(data)

    def get_config(key, default=None):
        """Function to check and get configuration"""

        # Get the value from the config file, if it is not there, get it from the environment variables
        # allow environment variables to override the config file for easy deployment
        value = config.get(key, os.getenv(key, default))
        if value is None:
            raise ValueError(
                f"Configuration error: '{key}' is not set in .env"
                + " as an environment variable or as a default value"
            )
        return value

    return {
        # Essential Configuration, these are required in config.yml
        "debug": get_config("debug"),
        "api_keys": get_config("api_keys"),
        "rest_runner": get_config("rest_runner"),
        "websocket_stream": get_config("websocket_stream"),
        # Networking Configuration
        #   Port that the REST API will listen on
        "rest_port": int(get_config("rest_port", default="8393")),
        #   Port that the Websocket will listen on
        "websocket_port": int(get_config("websocket_port", default="8394")),
        #   Host name of the application
        "host": get_config("host", default="localhost"),
        #
        # File System Configuration
        #   Path to the status file folder
        "status_file_path": get_config("status_file_path", default="/data/status/"),
        #   Path to the model folder
        "model_path": get_config("model_path", default="/models/"),
        #   Path to the audio file folder
        "audio_file_path": get_config("audio_file_path", default="/data/audio_files/"),
        #   Path to the audio file folder
        "export_file_path": get_config("audio_file_path", default="/data/export/"),
        #   Audio file format to use
        "audio_file_format": get_config("audio_file_format", default=".wav"),
        #
        # Cleanup Configuration
        #   Hours that status and audio files are kept
        "keep_data_for_hours": get_config("keep_data_for_hours", default=72),
        #   How often to clean up files in data (only runs if no transcriptions are in progress)
        "cleanup_schedule_in_minutes": get_config(
            "cleanup_schedule_in_minutes", default=10
        ),
    }


if os.path.exists(os.getcwd() + "/config.local.yml"):
    CONFIG = read_config(os.getcwd() + "/config.local.yml")
elif os.path.exists(os.getcwd() + "/config.yml"):
    CONFIG = read_config(os.getcwd() + "/config.yml")
else:
    raise RuntimeWarning("No config file found")

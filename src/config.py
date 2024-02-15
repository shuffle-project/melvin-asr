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

        value = config.get(key, os.getenv(key, default))
        if value is None:
            raise ValueError(
                f"Configuration error: '{key}' is not set in .env"
                + " as an environment variable or as a default value"
            )
        return value

    return {
        # Essential Configuration, these are required in config.yml
        "debug" : get_config("debug"),
        "api_keys": get_config("api_keys"),
        "rest_runner": get_config("rest_runner"),
        "stream_runner": get_config("stream_runner"),

        # Networking Configuration
        # Port that the REST API will listen on
        "rest_port": int(get_config("rest_port", default="8393")),
        # Port that the Websocket will listen on
        "websocket_port": int(get_config("websocket_port", default="8394")),
        # Host name of the application
        "host": get_config("host", default="localhost"),
        # File System Configuration
        "status_file_path": get_config("status_file_path", default="/data/status/"),
        "model_path": get_config("model_path", default="/models/"),
        "audio_file_path": get_config("audio_file_path", default="/data/audio_files/"),
        "audio_file_format": get_config("audio_file_format", default=".wav"),
        #
        # Domain Configuration
        #   Time the rest models stays in RAM until beeing unloaded when unused 
        "rest_models_in_ram_in_seconds": get_config("rest_models_in_ram_in_seconds", default=20),
        #
        # Cleanup Configuration
        #   Number of audio files to keep in the audio files folder, before the endpoint refuses to accept new files
        "audio_files_to_store": get_config("audio_files_to_store", default=100),
        #   Number of files to keep in the status folder
        "status_files_to_store": get_config("status_files_to_store", default=100),
        #   How often to clean up finished or error status files in minutes (only runs if no transcriptions are in progress)
        "cleanup_schedule_in_minutes": get_config("cleanup_schedule_in_minutes", default=5),
    }


try:
    CONFIG = read_config(os.getcwd() + "/config.yml")
except ValueError as e:
    print(f"Error: {e}")
    CONFIG = None

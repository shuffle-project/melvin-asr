"""config file that reads all config from .env or CMD environment for app"""

import os
from typing import List, Literal

import yaml
from faster_whisper.tokenizer import _LANGUAGE_CODES
from pydantic import BaseModel

WhisperModels = Literal[
    "tiny", "small", "medium", "large", "large-v3", "large-v3-turbo"
]
ComputeTypes = Literal["int8", "float16", "int8_float16"]
LanguageCode = Literal[*list(_LANGUAGE_CODES)]


class RestRunnerConfigResponse(BaseModel):
    device: str
    transcription_enabled: bool
    models: List[WhisperModels]
    compute_type: ComputeTypes
    device_index: int
    num_workers: int
    cpu_threads: int
    translation_enabled: bool
    translation_model: str
    translation_device: str


class WebsocketStreamDeviceConfigResponse(BaseModel):
    active: bool
    model: WhisperModels
    device_index: int
    worker_seats: int


class WebsocketStreamConfigResponse(BaseModel):
    cpu: WebsocketStreamDeviceConfigResponse
    cuda: WebsocketStreamDeviceConfigResponse


class TranscriptionDefaultConfigResponse(BaseModel):
    vad_filter: bool
    condition_on_previous_text: bool


class ConfigResponse(BaseModel):
    # Essential Configuration, these are required in config.yml
    log_level: str
    rest_runner: List[RestRunnerConfigResponse]
    rest_models: List[WhisperModels]
    websocket_stream: WebsocketStreamConfigResponse
    rest_port: int
    websocket_port: int
    host: str
    status_file_path: str
    model_path: str
    audio_file_path: str
    export_file_path: str
    audio_file_format: str
    keep_data_for_hours: int
    cleanup_schedule_in_minutes: int
    transcription_default: TranscriptionDefaultConfigResponse
    supported_language_codes: List[LanguageCode]


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

    def get_extracted_field_from_config(key, nested_key):
        """Function to extract one field from an array of config options"""
        value = get_config(key)
        res = []
        for nested_val in value:
            if nested_key not in nested_val:
                raise ValueError(
                    f"Configuration error: '{nested_key}' could not be extracted from value from '{key}'"
                )
            res += nested_val[nested_key]
        return list(set(res))

    return {
        # Essential Configuration, these are required in config.yml
        "log_level": get_config("log_level").upper(),
        "api_keys": get_config("api_keys"),
        "rest_runner": get_config("rest_runner"),
        "rest_models": get_extracted_field_from_config("rest_runner", "models"),
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
        "status_file_path": get_config("status_file_path", default="data/status"),
        #   Path to the model folder
        "model_path": get_config("model_path", default="models"),
        #   Path to the audio file folder
        "audio_file_path": get_config("audio_file_path", default="data/audio_files"),
        #   Path to the audio file folder
        "export_file_path": get_config("audio_file_path", default="data/export"),
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
        # Transcription default Configuration
        "transcription_default": get_config("transcription_default"),
        "supported_language_codes": list(_LANGUAGE_CODES),
    }


if os.path.exists(os.path.join(os.getcwd(), "config.local.yml")):
    CONFIG = read_config(os.path.join(os.getcwd(), "config.local.yml"))
elif os.path.exists(os.path.join(os.getcwd(), "config.yml")):
    CONFIG = read_config(os.path.join(os.getcwd(), "config.yml"))
else:
    raise RuntimeWarning("No config file found")

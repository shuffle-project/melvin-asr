"""Config file for the whispercpp_runner"""
# similar lines in 2 files do not matter
# pylint: disable=R0801

import json
import os

# load shared config.json
sharedConfigPath = os.getcwd() + "/infrastructure/shared/config.json"
with open(sharedConfigPath, encoding="utf-8") as json_data:
    data = json.load(json_data)
WHISPER_MODELS = data["models"]

"""Log level"""
LOGGER_DEBUG = False

"""dir we store audio files in"""
AUDIO_FILE_PATH = "/data/audio_files/"

"""dir we store transcripts in"""
TRANSCRIPT_PATH = "/data/transcripts/"

"""dir we store status information in"""
STATUS_PATH = "/data/status/"

"""format of audio files"""
AUDIO_FILE_FORMAT = ".wav"

"""fallback model (must be included in WHISPER_MODELS)"""
FALLBACK_MODEL = "small"

"""path to the whisper.cpp models"""
MODEL_PATH_FROM_ROOT = "/infrastructure/models/"

"""path to the whisper.cpp executable"""
WHISPER_CPP_PATH = "/whispercpp_runner/whisper.cpp/main"

"""max number of done status files to keep"""
MAX_DONE_FILES = 1

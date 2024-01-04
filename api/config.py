"""config file for api"""
# similar lines in 2 files do not matter
# pylint: disable=R0801

import json
import os

# load shared config.json
sharedConfigPath = os.getcwd() + "/infrastrucure/shared/config.json"
with open(sharedConfigPath, encoding="utf-8") as json_data:
    data = json.load(json_data)
WHISPER_MODELS = data["models"]

"""dir we store audio files in"""
AUDIO_FILE_PATH = "/data/audio_files/"

"""dir we store transcripts in"""
TRANSCRIPT_PATH = "/data/transcripts/"

"""dir we store status information in"""
STATUS_PATH = "/data/status"

"""format of audio files"""
AUDIO_FILE_FORMAT = ".wav"

# similar lines in 2 files do not matter
# pylint: disable=R0801

"""dir we store audio files in"""
AUDIO_FILE_PATH = "/data/audio_files/"

"""dir we store transcripts in"""
TRANSCRIPT_PATH = "/data/transcripts/"

"""dir we store settings in"""
SETTING_PATH = "/data/settings/"

"""format of audio files"""
AUDIO_FILE_FORMAT = ".wav"

"""models we can use"""
WHISPER_MODELS = ["small", "medium", "large-v1"]

"""fallback model"""
FALLBACK_MODEL = "small"

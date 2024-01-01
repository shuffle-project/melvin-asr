# similar lines in 2 files do not matter
# pylint: disable=R0801

"""Log level"""
LOGGER_DEBUG = True

"""dir we store audio files in"""
AUDIO_FILE_PATH = "/data/audio_files/"

"""dir we store transcripts in"""
TRANSCRIPT_PATH = "/data/transcripts/"

"""dir we store status information in"""
STATUS_PATH = "/data/status"

"""format of audio files"""
AUDIO_FILE_FORMAT = ".wav"

"""models we can use"""
WHISPER_MODELS = ["small", "tiny", "medium"]

"""fallback model (must be included in WHISPER_MODELS)"""
FALLBACK_MODEL = "small"

"""path to the whisper.cpp models"""
MODEL_PATH_FROM_ROOT = "/whispercpp_runner/whisper.cpp/models/"

"""path to the whisper.cpp executable"""
WHISPER_CPP_PATH = "/whispercpp_runner/whisper.cpp/main"

"""max number of done status files to keep"""
MAX_DONE_FILES = 1

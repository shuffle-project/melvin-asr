""" This module contains the handler for the transcription process. """
import time
import os
from datetime import datetime
from whispercpp_binding.transcribe_to_json import transcript_to_json

AUDIO_FILE_PATH = "/data/audio_files/"
AUDIO_FILE_FORMAT = ".wav"

WHISPER_MODELS = ["small", "medium", "large-v1"]
FALLBACK_MODEL = "small"


class Runner:
    """
    This class handles the transcription process by running whisper continuously.
    """

    def __init__(self, ident: int, model: str):
        self.ident = ident
        if model in WHISPER_MODELS:
            print("RUNNER: Model is valid, running " + model + ".")
            self.model = model
        else:
            print("RUNNER: Model is not valid, fallback to " + FALLBACK_MODEL + ".")
            self.model = FALLBACK_MODEL

    def startup(self) -> None:
        """continuously checks for new transcriptions to process"""
        while True:
            next_file_name = self.get_oldest_audio_file()
            if next_file_name == "None":
                print("No files to process.")
                time.sleep(3)
                continue
            print("Processing file: " + next_file_name)
            self.run_whisper(next_file_name)
            os.remove(os.getcwd() + AUDIO_FILE_PATH + next_file_name)

    def get_oldest_audio_file(
        self, directory=AUDIO_FILE_PATH, audio_format=AUDIO_FILE_FORMAT
    ) -> str:
        """Gets the oldest .wav file from the audio_files directory."""
        full_dir = os.getcwd() + directory
        oldest_filename: str = ""
        oldest_age_days = -1

        files = os.listdir(full_dir)

        wav_files = [file for file in files if file.endswith(audio_format)]
        if len(wav_files) == 0:
            return "None"

        for filename in wav_files:
            file_path = os.path.join(full_dir, filename)
            # Get the last modified time and convert it to a datetime object
            modification_time = os.path.getmtime(file_path)
            file_age_days = (
                datetime.now() - datetime.fromtimestamp(modification_time)
            ).days
            if oldest_age_days == -1 or file_age_days > oldest_age_days:
                oldest_age_days = file_age_days
                oldest_filename = filename

        return oldest_filename

    def run_whisper(self, audio_file_name: str) -> None:
        """Runs whisper"""

        print("Running whisper on file: " + audio_file_name)

        transcript_to_json(
            main_path="/whisper.cpp/main",
            model_path="/whisper.cpp/models/ggml-small.bin",
            audio_file_path=AUDIO_FILE_PATH + audio_file_name,
            output_file="/data/transcripts/" + audio_file_name,
            debug=False,
        )

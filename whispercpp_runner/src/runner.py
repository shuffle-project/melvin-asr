""" This module contains the handler for the transcription process. """
import os
import time
from runner_config import (
    AUDIO_FILE_PATH,
    AUDIO_FILE_FORMAT,
    MODEL_PATH_FROM_ROOT,
    WHISPER_CPP_PATH,
    WHISPER_MODELS,
    FALLBACK_MODEL,
    TRANSCRIPT_PATH,
)
from src.data_handler import DataHandler
from src.helper.file_handler import FileHandler
from src.helper.logger import Logger, Color
from src.transcriber import Transcriber


class Runner:
    """
    This class handles the transcription process by running whisper continuously.
    """

    def __init__(self, model: str, runner_type: str):
        """Constructor of the Runner class."""
        self.log = Logger("Runner", True, Color.OKCYAN)
        self.data_handler = DataHandler()
        self.file_handler = FileHandler()
        self.runner_type = runner_type

        if model in WHISPER_MODELS:
            self.log.print_log("Model is valid, running " + model + ".")
            self.model = model
        else:
            self.log.print_error(
                "Model is not valid, fallback to " + FALLBACK_MODEL + "."
            )
            self.model = FALLBACK_MODEL

    # pylint: disable=W0718
    def run(self) -> None:
        """continuously checks for new transcriptions to process"""
        c = 0
        while True:
            c += 1
            transcription_id = self.data_handler.get_oldest_status_file_in_query(self.runner_type)
            if transcription_id == "None":
                time.sleep(0.1)
                if c > 100000:
                    self.data_handler.delete_oldest_done_status_files()
                    self.log.print_log("Deleted old done files.")
                    c = 0
                continue

            self.log.print_log("Processing file: " + transcription_id)
            try:
                self.run_whisper(transcription_id)
            except RuntimeError as e:
                self.log.print_error("Error running whisper: " + str(e))
                self.data_handler.update_status_file("error", transcription_id, str(e))
                continue

    def run_whisper(self, transcription_id: str) -> None:
        """Runs whisper"""

        self.data_handler.update_status_file("in_progress", transcription_id)

        audio_file_name = f"{transcription_id}{AUDIO_FILE_FORMAT}"

        settings = self.data_handler.get_status_file_settings(transcription_id)
        if settings is None:
            settings = {"language": "auto"}

        self.log.print_log("Running whisper on file: " + audio_file_name)
        start_time = time.time()
        Transcriber(
            WHISPER_CPP_PATH,
            MODEL_PATH_FROM_ROOT + f"ggml-{self.model}.bin",
            AUDIO_FILE_PATH + audio_file_name,
            TRANSCRIPT_PATH + audio_file_name,
            settings,
            False,
        ).transcribe()
        end_time = time.time()  # Get the current time after execution
        self.log.print_log(
            f"Time taken by transcribe_to_json: {end_time - start_time} seconds"
        )
        self.file_handler.delete(os.getcwd() + AUDIO_FILE_PATH + audio_file_name)
        self.data_handler.merge_transcript_to_status(transcription_id)

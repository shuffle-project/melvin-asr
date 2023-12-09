""" This module contains the handler for the transcription process. """
import os
from runner_config import (
    AUDIO_FILE_PATH,
    AUDIO_FILE_FORMAT,
    MODEL_PATH_FROM_ROOT,
    WHISPER_CPP_PATH,
    WHISPER_MODELS,
    FALLBACK_MODEL,
)
from binding.transcribe_to_json import transcribe_to_json
from src.data_handler import DataHandler
from src.helper.logger import Logger, Color


class Runner:
    """
    This class handles the transcription process by running whisper continuously.
    """

    def __init__(self, model: str):
        """Constructor of the Runner class."""
        self.log = Logger("Runner", Color.OKCYAN)
        self.data_handler = DataHandler()
        if model in WHISPER_MODELS:
            self.log.print_log("Model is valid, running " + model + ".")
            self.model = model
        else:
            self.log.print_error("Model is not valid, fallback to " + FALLBACK_MODEL + ".")
            self.model = FALLBACK_MODEL

    # pylint: disable=W0718
    def run(self) -> None:
        """continuously checks for new transcriptions to process"""
        while True:
            transcription_id = self.data_handler.get_oldest_status_file_in_query()
            if transcription_id == "None":
                # print("No files to process.")
                self.data_handler.delete_oldest_done_status_files()
                continue
            self.log.print_log("Processing file: " + transcription_id)
            try:
                self.run_whisper(transcription_id)
            except RuntimeError as e:
                self.log.print_error("Error running whisper: " + str(e))
                self.data_handler.update_status_file("error", str(e))
                continue

            os.remove(
                os.getcwd() + AUDIO_FILE_PATH + transcription_id + AUDIO_FILE_FORMAT
            )
            self.data_handler.merge_transcript_to_status(transcription_id)

    def run_whisper(self, transcription_id: str) -> None:
        """Runs whisper"""

        self.data_handler.update_status_file("in_progress", transcription_id)

        audio_file_name = f"{transcription_id}{AUDIO_FILE_FORMAT}"

        self.log.print_log("Running whisper on file: " + audio_file_name)

        transcribe_to_json(
            main_path=WHISPER_CPP_PATH,
            model_path=MODEL_PATH_FROM_ROOT + f"ggml-{self.model}.bin",
            audio_file_path=AUDIO_FILE_PATH + audio_file_name,
            output_file="/data/transcripts/" + audio_file_name,
            debug=False,
        )

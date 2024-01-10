""" This module contains the handler for the transcription process. """
import json
import time
from src.helper.transcription import TranscriptionStatusValue
from src.config import CONFIG
from src.helper.data_handler import DataHandler
from src.helper.logger import Logger, Color
from src.transcription.transcriber import Transcriber


class Runner:
    """
    This class handles the transcription process by running whisper continuously.
    """

    def __init__(self, identifier: int = 0):
        """Constructor of the Runner class."""
        self.identifier = identifier
        self.log = Logger(f"Runner{identifier}", True, Color.BRIGHT_CYAN)
        self.data_handler = DataHandler()
        self.transcriber = Transcriber(json.loads(CONFIG["AVAILABLE_MODELS"]))

    def run(self) -> None:
        """continuously checks for new transcriptions to process"""
        self.log.print_log("started")
        c = 0
        while True:
            c += 1
            transcription_id = self.data_handler.get_oldest_status_file_in_query()
            if transcription_id == "None":
                time.sleep(0.1)

                # clean up job
                schedule = int(CONFIG["CLEAN_UP_SCHEDULE"]) * 10 * 60  # in minutes
                if c > schedule:
                    self.data_handler.clean_up_status_files(
                        int(CONFIG["MAX_OLD_STATUS_FILES"])
                    )
                    self.log.print_log("Status files cleaned up.")
                    c = 0

                continue

            self.log.print_log("Processing file: " + transcription_id)
            try:
                self.transcribe(transcription_id)

            except RuntimeError as e:
                self.log.print_error("Error running whisper: " + str(e))
                self.data_handler.update_status_file(
                    TranscriptionStatusValue.ERROR.value, transcription_id, str(e)
                )
                continue

    def transcribe(self, transcription_id) -> None:
        """Transcribes the audio file with the given transcription_id."""
        # get data
        audio_file_path = self.data_handler.get_audio_file_path_by_id(transcription_id)
        settings = self.data_handler.get_status_file_settings(transcription_id)
        if settings is None or settings.get("model") is None:
            self.log.print_log("No model selected, using small as default.")
            model = CONFIG["DEFAULT_REST_MODEL"]
        else:
            model = settings["model"]

        # transcribe and update data
        transcript_data = self.transcriber.transcribe_audio_file(
            audio_file_path, model, settings
        )
        self.data_handler.merge_transcript_to_status(transcription_id, transcript_data)
        self.data_handler.delete_audio_file(transcription_id)
        self.data_handler.update_status_file(
            TranscriptionStatusValue.FINISHED.value, transcription_id
        )

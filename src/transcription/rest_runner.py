""" This module contains the handler for the transcription process. """
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

    def __init__(
        self, model_name: str, identifier: str, device: str, compute_type: str
    ):
        """Constructor of the Runner class."""
        self.identifier = identifier
        self.transcriber = Transcriber(model_name, device, compute_type)

        self.log = Logger(f"Runner{identifier}", True, Color.BRIGHT_CYAN)
        self.data_handler = DataHandler()

    def run(self) -> None:
        """continuously checks for new transcriptions to process"""
        self.log.print_log("started")

        cu = 0  # counter for unload model
        cc = 0  # counter for clean up
        while True:
            cu += 1
            cc += 1
            transcription_id = self.data_handler.get_oldest_status_file_in_query()

            # if no transcription is available, wait
            if transcription_id == "None":
                time.sleep(0.1)
                # unload model if not used for a while
                schedule = int(CONFIG["UNLAOD_REST_MODELS_SCHEDULE"]) * 10  # in seconds
                if cu > schedule:
                    self.transcriber.unload_model()
                    cu = 0

                # clean up job
                schedule = int(CONFIG["CLEAN_UP_SCHEDULE"]) * 10 * 60  # in minutes
                if cc > schedule:
                    self.data_handler.clean_up_status_files(
                        int(CONFIG["MAX_OLD_STATUS_FILES"])
                    )
                    self.log.print_log("Status files cleaned up.")
                    cc = 0

                continue

            # if transcription is available, process it
            self.log.print_log("Processing file: " + transcription_id)
            try:
                self.data_handler.update_status_file(
                    TranscriptionStatusValue.IN_PROGRESS.value, transcription_id
                )
                self.transcribe(transcription_id)
                cu = 0

            # need to catch all exceptions here
            # pylint: disable=W0718
            except Exception as e:
                self.log.print_error(
                    f"Runner Exception of type {type(e).__name__}: {str(e)}"
                )
                self.data_handler.update_status_file(
                    TranscriptionStatusValue.ERROR.value, transcription_id, str(e)
                )
                continue

    def transcribe(self, transcription_id) -> None:
        """Transcribes the audio file with the given transcription_id."""
        # get data
        audio_file_path = self.data_handler.get_audio_file_path_by_id(transcription_id)
        settings = self.data_handler.get_status_file_settings(transcription_id)

        # transcribe and update data
        transcript_data = self.transcriber.transcribe_audio_file(
            audio_file_path, settings
        )
        self.data_handler.merge_transcript_to_status(transcription_id, transcript_data)
        self.data_handler.delete_audio_file(transcription_id)
        self.data_handler.update_status_file(
            TranscriptionStatusValue.FINISHED.value, transcription_id
        )

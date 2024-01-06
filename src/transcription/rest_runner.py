""" This module contains the handler for the transcription process. """
import time
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
        self.transcriber = Transcriber()

    # pylint: disable=W0718
    def run(self) -> None:
        """continuously checks for new transcriptions to process"""
        self.log.print_log("started")
        c = 0
        while True:
            c += 1
            transcription_id = self.data_handler.get_oldest_status_file_in_query()
            if transcription_id == "None":
                time.sleep(0.1)
                if c > 60000:
                    self.data_handler.delete_oldest_done_status_files()
                    self.log.print_log("Deleted old done files.")
                    c = 0
                continue

            self.log.print_log("Processing file: " + transcription_id)
            try:
                audio_file_path = self.data_handler.get_audio_file_path_by_id(transcription_id)
                transcript_data = self.transcriber.transcribe_audio_file(audio_file_path)
                self.data_handler.merge_transcript_to_status(transcription_id, transcript_data)
                self.data_handler.delete_audio_file(transcription_id)
                self.data_handler.update_status_file("done", transcription_id)

            except RuntimeError as e:
                self.log.print_error("Error running whisper: " + str(e))
                self.data_handler.update_status_file("error", transcription_id, str(e))
                continue

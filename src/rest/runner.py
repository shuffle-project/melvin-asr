"""This module contains the handler for the transcription process."""

import os
import random
import time
from datetime import datetime

from src.helper import logger
from src.helper.config import CONFIG
from src.helper.data_handler import DataHandler
from src.helper.types.transcription_status import TranscriptionStatus
from src.rest.rest_transcriber import Transcriber


class Runner:
    """
    This class handles the transcription process by running whisper continuously.
    """

    def __init__(self, config: dict, identifier: int):
        """Constructor of the Runner class."""
        self.identifier = identifier
        self.transcriber = Transcriber(config)

        self.log = logger.get_logger_with_id(__name__, identifier)
        self.data_handler = DataHandler()

    def run(self) -> None:
        """continuously checks for new transcriptions to process"""
        self.log.info("started")

        cc = 0  # counter for clean up
        while True:
            cc += 1
            transcription_id = self.get_oldest_status_file_in_query()

            if transcription_id == "None":
                time.sleep(0.1)

                schedule = int(CONFIG["cleanup_schedule_in_minutes"]) * 10 * 60
                if cc > schedule:
                    self.data_handler.clean_up_audio_and_status_files()
                    self.log.info("Status files cleaned up.")
                    cc = 0

                continue

            self.log.debug("Processing file: " + transcription_id)
            try:
                self.data_handler.update_status_file(
                    TranscriptionStatus.IN_PROGRESS.value, transcription_id
                )
                self.transcribe(transcription_id)

            except Exception as e:
                self.log.error(f"Runner Exception of type {type(e).__name__}: {str(e)}")
                self.data_handler.update_status_file(
                    TranscriptionStatus.ERROR.value, transcription_id, str(e)
                )
                continue

    def transcribe(self, transcription_id) -> None:
        """Transcribes the audio file with the given transcription_id."""
        audio_file_path = self.data_handler.get_audio_file_path_by_id(transcription_id)
        status_file = self.data_handler.get_status_file_by_id(transcription_id)
        settings = self.data_handler.get_status_file_settings(transcription_id)

        task = status_file["task"]

        response = None
        if task == "transcribe":
            response = self.transcriber.transcribe_audio_file(audio_file_path, settings)
        elif task == "align":
            response = self.transcriber.align_audio_file(
                audio_file_path, status_file["text"], status_file["language"]
            )

        self.data_handler.delete_audio_file(transcription_id)
        if response["success"] is False or (response["data"]["segments"] is None):
            self.data_handler.update_status_file(
                TranscriptionStatus.ERROR.value,
                transcription_id,
                response["data"],
            )
            return
        self.data_handler.merge_transcript_to_status(transcription_id, response["data"])

    def get_oldest_status_file_in_query(
        self,
        race_condition_sleep_ms: int = 5000,
        data_handler: DataHandler = DataHandler(),
    ) -> str:
        """Gets the oldest transcription in query."""
        oldest_start_time = None
        oldest_transcription_id: str = None

        files = os.listdir(data_handler.status_path)
        if len(files) == 0:
            return "None"

        # wait to avoid race conditions between runners
        time.sleep(random.randint(0, race_condition_sleep_ms) / 1000.0)

        for filename in os.listdir(data_handler.status_path):
            try:
                if filename.endswith(".json"):
                    data = data_handler.file_handler.read_json(
                        os.path.join(data_handler.status_path, filename)
                    )
                    current_status = data.get("status")
                    start_time = data.get("start_time")
                    model = data.get("model")

                    if start_time is None or current_status is None:
                        continue

                    if current_status != TranscriptionStatus.IN_QUERY.value:
                        continue

                    if model != self.transcriber.model_name and model is not None:
                        continue

                    current_datetime = datetime.fromisoformat(start_time)
                    if (
                        oldest_start_time is None
                        or current_datetime < oldest_start_time
                    ):
                        oldest_start_time = current_datetime
                        oldest_transcription_id = data.get("transcription_id")

            except Exception as e:
                self.log.error(
                    f"Caught Exception of type {type(e).__name__}"
                    + f"while getting oldest status file: {str(e)}"
                )
                transcription_id = filename.split(".")[0]
                data_handler.delete_status_file(transcription_id)
                data_handler.delete_audio_file(transcription_id)
                continue

        if oldest_transcription_id:
            return oldest_transcription_id
        return "None"

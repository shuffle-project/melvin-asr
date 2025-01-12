"""This module contains the handler for the transcription process."""

import os
import random
import time
from datetime import datetime, timezone
from typing import Tuple

from src.helper import logger
from src.helper.align_translation_segments import align_segments
from src.helper.config import CONFIG
from src.helper.data_handler import DataHandler
from src.helper.translate import translate_text
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

        start_time = time.time()
        schedule = int(CONFIG["cleanup_schedule_in_minutes"]) * 60
        while True:
            now = time.time()
            if now > start_time + schedule:
                self.data_handler.clean_up_audio_and_status_files()
                self.log.info("Status files cleaned up.")
                start_time = now

            task_id, task = self.get_oldest_status_file_in_query()

            if task_id == "None":
                time.sleep(10)
                continue

            self.log.debug("Processing file: " + task_id)
            try:
                self.data_handler.update_status_file(
                    TranscriptionStatus.IN_PROGRESS.value, task_id
                )
                if task == "transcribe" or task == "align":
                    self.transcribe(task_id)
                if task == "translate":
                    self.translate(task_id)

            except Exception as e:
                self.log.error(f"Runner Exception of type {type(e).__name__}: {str(e)}")
                self.data_handler.update_status_file(
                    TranscriptionStatus.ERROR.value, task_id, str(e)
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

    def translate(self, task_id) -> None:
        """Translates the audio file with the given transcription_id."""
        transcription = self.data_handler.get_status_file_by_id(task_id)

        # TODO: Move the following in the runner handler
        transcription["start_time"] = (
            datetime.now(timezone.utc).replace(microsecond=0).isoformat()
        )
        translated_text = translate_text(
            transcription["transcript"]["text"],
            transcription["language"],
            transcription["target_language"],
        )

        transcription["transcript"] = align_segments(
            transcription["transcript"], translated_text
        )

        # This is here to see the difference in segmented tranlation level
        # for segment in transcription["transcript"]["segments"]:
        #     segment["text"] = translate_text(
        #         segment["text"], transcription["language"], target_language
        #     )

        transcription["language"] = transcription["target_language"]
        transcription["end_time"] = (
            datetime.now(timezone.utc).replace(microsecond=0).isoformat()
        )
        transcription["status"] = TranscriptionStatus.FINISHED.value

        self.data_handler.write_status_file(task_id, transcription)

    def get_oldest_status_file_in_query(
        self,
        race_condition_sleep: float = 5.0,
        data_handler: DataHandler = DataHandler(),
    ) -> Tuple[str, str]:
        """Gets the oldest transcription in query."""
        oldest_start_time = None
        oldest_transcription_id: str = None

        files = os.listdir(data_handler.status_path)
        if len(files) == 0:
            return ("None", "None")

        # wait to avoid race conditions between runners
        time.sleep(random.uniform(0, race_condition_sleep))

        for filename in os.listdir(data_handler.status_path):
            try:
                if filename.endswith(".json"):
                    data = data_handler.file_handler.read_json(
                        os.path.join(data_handler.status_path, filename)
                    )
                    current_status = data.get("status")
                    start_time = data.get("start_time")
                    model = data.get("model")
                    task = data.get("task")

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

        return (
            (oldest_transcription_id, task)
            if oldest_transcription_id
            else ("None", task)
        )

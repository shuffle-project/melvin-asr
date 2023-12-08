"""types of the transcription object"""
import json
import os
import uuid
from datetime import datetime
from enum import Enum

from config import STATUS_PATH


class TranscriptionStatusValue(Enum):
    """status values of a transcription"""

    IN_QUERY = "in_query"
    IN_PROGRESS = "in_progress"
    FINISHED = "finished"
    ERROR = "error"


class TranscriptionNotFoundError(Exception):
    """
    Exception raised when a transcription is not found.
    """

    def __str__(self):
        return f"Transcription not found: {super().__str__()}"


class Transcription:
    """
    Class representing a transcription.
    """
    def __init__(self, transcription_id: uuid.UUID):
        """
        Constructor of the Transcription class.
        :param transcription_id: The id of the transcription.
        """
        self.transcription_id: str = str(transcription_id)
        self.status: TranscriptionStatusValue = TranscriptionStatusValue.IN_QUERY
        self.start_time: str = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        self.error_message = None
        self.settings = None

    def save_to_file(self):
        """
        Saves the transcription to a file.
        """
        status_dir = os.getcwd() + STATUS_PATH
        if not os.path.exists(status_dir):
            os.makedirs(status_dir)

        file_path = os.path.join(status_dir, f"{self.transcription_id}.json")

        data = {
            "transcription_id": self.transcription_id,
            "status": self.status.value,
            "start_time": self.start_time
        }

        if self.settings is not None:
            data["settings"] = self.settings

        if self.error_message is not None:
            data["error_message"] = self.error_message

        with open(file_path, 'w', encoding="utf-8") as file:
            json.dump(data, file)

    def get_status(self):
        """
        Returns the status file of the transcription.
        """
        file_path = os.path.join(STATUS_PATH, f"{self.transcription_id}.json")

        if os.path.exists(file_path):
            with open(file_path, 'r', encoding="utf-8") as file:
                return json.load(file)
        else:
            return None

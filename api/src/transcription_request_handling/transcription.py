"""types of the transcription object"""
import os
import uuid
from enum import Enum
from datetime import datetime


class TranscriptionStatusValue(Enum):
    """status values of a transcription"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    FINISHED = "finished"
    ERROR = "error"


TRANSCRIPTIONS_DIR = "/data/transcripts"


class TranscriptionNotFoundError(Exception):
    """
    Exception raised when a transcription is not found.
    """


class Transcription:
    """
    Class of the objects that enable transcription handling
    - transcription_id (str): The unique id for the transcription. (ENUM TranscriptionStatusValue)
    - status (str): The status of the transcription.
    - start_time (str): The start time of the transcription (formatted as "YYYY-MM-DDTHH:mm:ssZ").
    - end_time (str): The end time of the transcription (formatted as "YYYY-MM-DDTHH:mm:ssZ").
    - transcript (str): The transcription text (optional).
    - error_message (str): Any error message in case of failure (optional).
    """

    def __init__(self):
        self.transcription_id: str = str(uuid.uuid4())
        self.status: TranscriptionStatusValue = TranscriptionStatusValue.IN_PROGRESS
        self.start_time: str = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        self.end_time: str = ""
        self.transcript = ""
        self.error_message = ""

    def print_object(self):
        """returns the object as JSON"""
        return {
            "transcription_id": self.transcription_id,
            "status": self.status.value,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "transcript": self.transcript,
            "error_message": self.error_message,
        }

    def update_status(self):
        """updates the status of the transcription if there is a transcription"""
        files = os.listdir(os.getcwd() + TRANSCRIPTIONS_DIR)
        print("update_status", files)
        if (self.transcription_id + ".wav.json") in files:
            self.status = TranscriptionStatusValue.FINISHED
            self.end_time = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        return
    
    


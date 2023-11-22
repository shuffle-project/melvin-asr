"""types of the transcription object"""
import os
import uuid
from enum import Enum
from datetime import datetime
from CONFIG import AUDIO_FILE_PATH, TRANSCRIPT_PATH
from src.helper.parse_json_file import parse_json_file



class TranscriptionStatusValue(Enum):
    """status values of a transcription"""
    INPROGRESS = "in_progress"
    FINISHED = "finished"
    ERROR = "error"

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

    def __init__(self, transcription_id: str = uuid.uuid4()):
        self.transcription_id: str = str(transcription_id)
        self.status: TranscriptionStatusValue = TranscriptionStatusValue.INPROGRESS
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

    def update_status(self) -> None:
        """updates the status of the transcription if there is a transcription"""
        files = os.listdir(os.getcwd() + TRANSCRIPT_PATH)
        if (self.transcription_id + ".wav.json") in files:
            try:
                self.transcript = parse_json_file(os.getcwd() + TRANSCRIPT_PATH + "/" + self.transcription_id + ".wav.json")
            # Need to catch all Exceptions
            # pylint: disable=W0718
            except Exception as e:
                print("ERROR reading transcript for id {self.transcription_id}:" + e)
                # if there is now .wav file and no transcript, then we have an error
            self.status = TranscriptionStatusValue.FINISHED
            self.end_time = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        return

def search_undefined_transcripts(transcription_id) -> Transcription:
    """Searches in Transcripts_dir for uninstanciated transcripts and return new object"""
    transcription_files = os.listdir(os.getcwd() + TRANSCRIPT_PATH)
    audio_files = os.listdir(os.getcwd() + AUDIO_FILE_PATH)
    if (transcription_id + ".wav.json") in transcription_files:
        new_transcription = Transcription(transcription_id)
        new_transcription.update_status()
        return new_transcription
    if (transcription_id + ".wav") in audio_files:
        new_transcription = Transcription(transcription_id)
        return new_transcription
    raise TranscriptionNotFoundError(f"Transcription with id {transcription_id} not found")

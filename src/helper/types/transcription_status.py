"""types of the transcription object"""
from enum import Enum


class TranscriptionStatus(Enum):
    """status values of a transcription"""

    IN_QUERY = "in_query"
    IN_PROGRESS = "in_progress"
    FINISHED = "finished"
    ERROR = "error"

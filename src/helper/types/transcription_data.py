from typing import Dict, List

from typing_extensions import TypedDict


class Word(TypedDict):
    text: str
    start: float
    end: float
    probability: float


class Segment(TypedDict):
    text: str
    start: float
    end: float
    words: List[Word]


class Transcript(TypedDict):
    text: str
    segments: List[Segment]


class TranscriptionData(TypedDict):
    transcription_id: str
    status: str
    start_time: str
    settings: Dict[str, object]
    model: str
    task: str
    language: str
    transcript: Transcript

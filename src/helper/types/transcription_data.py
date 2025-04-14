from typing import Dict, List, Literal, Optional

from pydantic import BaseModel
from typing_extensions import TypedDict

from src.helper.config import WhisperModels
from src.helper.types.transcription_status import TranscriptionStatus

Tasks = Literal["transcribe", "align", "force-align"]


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


class WebsocketTranscriptResponse(BaseModel):
    result: List[Word]
    text: str


class TranscriptionListResponse(BaseModel):
    transcription_id: str
    status: TranscriptionStatus


class TranscriptionTranscriptResponse(BaseModel):
    text: str
    segments: List[Segment]


class TranscriptionFullResponse(BaseModel):
    transcription_id: str
    status: TranscriptionStatus
    start_time: str
    settings: dict
    model: WhisperModels
    task: Tasks
    text: str
    language: str
    transcript: TranscriptionTranscriptResponse


class TranscriptionPostResponse(BaseModel):
    transcription_id: str
    status: TranscriptionStatus
    start_time: str
    settings: dict
    model: WhisperModels
    task: Tasks
    text: str
    language: str


class TranslationPostData(BaseModel):
    language: str
    target_language: str
    method: Optional[str] = None
    transcript: Transcript
    transcription_id: Optional[str] = None
    task: Optional[Tasks] = None
    status: Optional[TranscriptionStatus] = None
    start_time: Optional[str] = None


class TranslationResponse(TypedDict):
    transcription_id: str
    language: str
    start_time: str
    end_time: str
    status: TranscriptionStatus
    transcript: Transcript

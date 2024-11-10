from pydantic import BaseModel


class TranscriptionData(BaseModel):
    transcription_id: str
    status: str
    start_time: str
    settings: dict | None = None
    model: str | None = None
    task: str
    text: str | None = None
    language: str | None = None

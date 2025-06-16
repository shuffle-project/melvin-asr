from datetime import datetime
from enum import Enum
from typing import Annotated, Literal, Optional, Union
from uuid import UUID

from pydantic import BaseModel, Field

from .transcript import Transcript


class JobStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

class JobType(str, Enum):
    TRANSCRIPTION = "transcription"
    TRANSLATION = "translation"
    ALIGNMENT = "alignment"

class TranslationAlignmentMethod(str, Enum):
    SEGMENT_LEVEL = "segment_level"
    WORD_LEVEL = "word_level"

class BaseJob(BaseModel):
    id: UUID
    job_type: JobType
    status: JobStatus
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

# Transcription

class TranscriptionRequest(BaseModel):
    audio_filename: str = Field(..., description="Filename of a previously uploaded audio file")
    language: Optional[str] = Field(None, description="Language code for the audio")
    vad_filter: Optional[bool] = Field(None, description="Enable VAD filter")
    condition_on_previous_text: Optional[bool] = Field(None, description="Condition on previous text")
    batched_inference: Optional[bool] = Field(None, description="Enable batched inference")
    initial_prompt: Optional[str] = Field(None, description="Initial prompt for transcription")

class TranscriptionJob(BaseJob):
    job_type: Literal[JobType.TRANSCRIPTION] = JobType.TRANSCRIPTION
    settings: TranscriptionRequest

# Translation

class TranslationRequest(BaseModel):
    source_language: str = Field(..., description="Language code of the source transcript")
    target_language: str = Field(..., description="Language code for translated transcript")
    transcript: Transcript = Field(..., description="Transcript object containing the text to be translated")
    alignment_method: TranslationAlignmentMethod = Field(TranslationAlignmentMethod.WORD_LEVEL, description="Method for aligning translated text with original transcript")

class TranslationJob(BaseJob):
    job_type: Literal[JobType.TRANSLATION] = JobType.TRANSLATION
    settings: TranslationRequest

# Alignment

class AlignmentMethod(str, Enum):
    BY_AUDIO = "by_audio"
    BY_TRANSCRIPT = "by_transcript"
    BY_TIME = "by_time"

class AlignmentBaseRequest(BaseModel):
    method: AlignmentMethod = Field(..., description="Method for alignment")
    transcript: Transcript = Field(..., description="Transcript object containing the text to be aligned")

class AlignmentByAudioRequest(AlignmentBaseRequest):
    method: Literal[AlignmentMethod.BY_AUDIO] = AlignmentMethod.BY_AUDIO
    language: str = Field(..., description="Language code for the audio")
    audio_filename: str = Field(..., description="Filename of a previously uploaded audio file")

class AlignmentByTranscriptRequest(AlignmentBaseRequest):
    method: Literal[AlignmentMethod.BY_TRANSCRIPT] = AlignmentMethod.BY_TRANSCRIPT
    transcript_with_timings: Transcript = Field(..., description="Transcript object containing the text with timings")

class AlignmentByTimeRequest(AlignmentBaseRequest):
    method: Literal[AlignmentMethod.BY_TIME] = AlignmentMethod.BY_TIME
    start: float = Field(..., description="Start time for alignment")
    end: float = Field(..., description="End time for alignment")
    
AlignmentRequest = Annotated[
    Union[AlignmentByAudioRequest, AlignmentByTranscriptRequest, AlignmentByTimeRequest],
    Field(discriminator="method")
]

class AlignmentJob(BaseJob):
    job_type: Literal[JobType.ALIGNMENT] = JobType.ALIGNMENT
    settings: AlignmentRequest

# Job

Job = Annotated[
    Union[TranscriptionJob, TranslationJob, AlignmentJob],
    Field(discriminator="job_type")
]

class JobResult(BaseModel):
    transcript: Transcript
    raw_result: Optional[dict] = None
import uuid
from datetime import datetime
from typing import Annotated, List

from core.job_handler import JobHandler
from core.processing import seamlessm4t, whisper
from core.upload_handler import upload_handler
from dependencies import (require_alignment_enabled, require_api_key,
                          require_transcription_enabled,
                          require_translation_enabled)
from fastapi import APIRouter, Depends, HTTPException, Path
from fastapi.params import Param
from models.job import (AlignmentJob, BaseJob, Job, JobResult, JobStatus,
                        JobType, TranscriptionJob, TranscriptionRequest,
                        TranslationJob, TranslationRequest)

router = APIRouter()

job_handler = JobHandler()

@router.get("/", response_model=List[BaseJob], dependencies=[Depends(require_api_key)])
async def get_jobs():
    jobs = job_handler.list_jobs()
    return [job.model_dump(exclude={'settings'}) for job in jobs]

@router.post("/transcription", response_model=TranscriptionJob, dependencies=[Depends(require_api_key), Depends(require_transcription_enabled)])
async def create_transcription(
    request: TranscriptionRequest
):
    if request.language and not whisper.is_language_supported(request.language):
        raise HTTPException(status_code=400, detail={
            "error": "Unsupported language {request.language}",
            "supported_languages": whisper.get_supported_languages()
        })

    if not upload_handler.file_exists(request.audio_filename):
        raise HTTPException(status_code=400, detail="Upload file not found")

    job = TranscriptionJob(
        id=uuid.uuid4(),
        status=JobStatus.PENDING,
        created_at=datetime.now(),
        settings=request.model_dump(exclude_unset=True)
    )
    return job_handler.create_job(job)

@router.post("/translation", response_model=TranslationJob, dependencies=[Depends(require_api_key), Depends(require_translation_enabled)])
async def create_translation(
    request: TranslationRequest
):
    if not seamlessm4t.is_language_supported(request.source_language):
        raise HTTPException(status_code=400, detail={
            "error": f"Unsupported target language {request.source_language}",
            "supported_languages": whisper.get_supported_languages()
        })
    
    if not seamlessm4t.is_language_supported(request.target_language):
        raise HTTPException(status_code=400, detail={
            "error": f"Unsupported target language {request.target_language}",
            "supported_languages": whisper.get_supported_languages()
        })
    
    job = TranslationJob(
        id=uuid.uuid4(),
        status=JobStatus.PENDING,
        created_at=datetime.now(),
        settings=request.model_dump(exclude_unset=True)
    )
    return job_handler.create_job(job)

@router.post("/alignment", response_model=AlignmentJob, dependencies=[Depends(require_api_key), Depends(require_alignment_enabled)])
async def create_transcription():
    job = AlignmentJob(
        id=uuid.uuid4(),
        status=JobStatus.PENDING,
        created_at=datetime.now(),
    )
    return job_handler.create_job(job)

@router.get("/{job_id}", response_model=Job, dependencies=[Depends(require_api_key)])
async def get_job_by_id(
    job_id = Annotated[uuid.UUID, Path()]
):
    job = job_handler.get_job(job_id)
    return job

@router.get("/{job_id}/result", response_model=JobResult, dependencies=[Depends(require_api_key)])
async def get_job_result(
    job_id = Annotated[uuid.UUID, Path()]
):
    job = job_handler.get_job(job_id)
    if job.status != JobStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Job is not completed yet")
    result = job_handler.get_job_result(job_id)
    return result
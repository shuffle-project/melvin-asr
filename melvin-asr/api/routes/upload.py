

import uuid
from io import BytesIO

from core.upload_handler import upload_handler
from dependencies import require_api_key, require_transcription_enabled
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from models.upload import UploadResponse
from pydub import AudioSegment

router = APIRouter()

@router.post("/", response_model=UploadResponse, dependencies=[Depends(require_api_key), Depends(require_transcription_enabled)])
async def create_transcription(
    audio_file: UploadFile = File(...)
):
    try:
        file_content = await audio_file.read()
        audio = AudioSegment.from_file(BytesIO(file_content))
        return upload_handler.create_audio_file(audio)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid or unsupported audio file")
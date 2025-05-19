

from core.config import config
from core.logger import get_logger
from fastapi import HTTPException, Security
from fastapi.security import APIKeyHeader

logger = get_logger(__name__)

api_key_header = APIKeyHeader(name="Authorization", auto_error=False)
async def require_api_key(api_key: str = Security(api_key_header)):
    if api_key not in config.api_keys:
        logger.warning(f"Unauthorized API key attempt: {api_key}")
        raise HTTPException(status_code=401, detail="Unauthorized")
    return api_key

transcription_enabled = any(c.transcription_enabled for c in config.batch_workers)
def require_transcription_enabled():
    if not transcription_enabled:
        raise HTTPException(status_code=400, detail="Transcription is not enabled on this server.")
    
def require_alignment_enabled():
    if not transcription_enabled:
        raise HTTPException(status_code=400, detail="Alignment is not enabled on this server.")
    
translation_enabled = any(c.translation_enabled for c in config.batch_workers)
def require_translation_enabled():
    if not translation_enabled:
        raise HTTPException(status_code=400, detail="Translation is not enabled on this server.")
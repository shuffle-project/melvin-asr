
from core.config import config
from dependencies import require_api_key
from fastapi import APIRouter, Depends
from models.settings import Settings

router = APIRouter()


@router.get("", response_model=Settings, response_model_exclude={"api_keys"}, dependencies=[Depends(require_api_key)])
async def get_settings():
    settings = Settings.model_validate_json(config.model_dump_json())
    return settings
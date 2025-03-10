import json
import logging
import time
import uuid
from datetime import datetime, timezone
from random import choice

from fastapi import (
    Body,
    Depends,
    FastAPI,
    File,
    Form,
    HTTPException,
    Security,
    UploadFile,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi.security.api_key import APIKeyHeader
from pydub import AudioSegment
from starlette.status import HTTP_401_UNAUTHORIZED

from src.helper.config import CONFIG
from src.helper.data_handler import DataHandler
from src.helper.SM4T_translate import check_language_supported_guard
from src.helper.time_it import time_it
from src.helper.types.transcription_data import TranscriptionData
from src.helper.types.transcription_status import TranscriptionStatus

LOGGER = logging.getLogger(__name__)
DATA_HANDLER = DataHandler()


config = CONFIG

app = FastAPI()
# Enable CORS for all domains
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
api_key_header = APIKeyHeader(name="Authorization", auto_error=False)


def custom_openapi():
    """Modify the openapi definition to include our auth schema"""
    if not app.openapi_schema:
        openapi_schema = app.openapi()
        openapi_schema["components"]["securitySchemes"] = {
            "APIKeyHeader": {
                "type": "apiKey",
                "in": "header",
                "name": "Authorization",
                "description": "API Key needed to access this endpoint.",
            }
        }
        openapi_schema["security"] = [{"APIKeyHeader": []}]
        app.openapi_schema = openapi_schema
    return app.openapi_schema


async def require_api_key(api_key: str = Security(api_key_header)):
    """Dependency to require an API key for a route."""
    config = CONFIG
    if api_key not in config["api_keys"]:
        LOGGER.warning(f"Unauthorized API key attempt: {api_key}")
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    return api_key


def require_translation_enabled():
    """Dependency to require translation to be enabled."""
    if not any(
        runner_config.get("translation_enabled", False)
        for runner_config in CONFIG["rest_runner"]
    ):
        raise HTTPException(
            status_code=400, detail="Translation is not enabled on this server."
        )


def require_transcription_enabled():
    """Dependency to require translation to be enabled."""
    if not any(
        runner_config.get("transcription_enabled", False)
        for runner_config in CONFIG["rest_runner"]
    ):
        raise HTTPException(
            status_code=400, detail="Transcription is not enabled on this server."
        )


@time_it
@app.get("/", response_class=JSONResponse, dependencies=[Depends(require_api_key)])
async def show_config():
    """Returns the config of this service, excluding API keys."""
    config_info = config.copy()
    config_info.pop("api_keys", None)
    return JSONResponse(content=config_info, status_code=200)


@app.get(
    "/health", response_class=PlainTextResponse, dependencies=[Depends(require_api_key)]
)
async def health_check():
    """Return health status."""
    return "OK"


@time_it
@app.get("/transcriptions", dependencies=[Depends(require_api_key)])
async def get_transcriptions():
    """Get all transcriptions and their statuses."""
    transcriptions = []
    for file_name in DATA_HANDLER.get_all_status_filenames():
        try:
            file_name = file_name[:-5]  # remove .json
            data = DATA_HANDLER.get_status_file_by_id(file_name)
            transcriptions.append(
                {
                    "transcription_id": data["transcription_id"],
                    "status": data["status"],
                }
            )
        except Exception as e:
            LOGGER.error(f"Error while reading status file {file_name}: {e}")
            DATA_HANDLER.delete_status_file(file_name)
    return JSONResponse(content=transcriptions, status_code=200)


@time_it
@app.get("/transcriptions/{transcription_id}", dependencies=[Depends(require_api_key)])
async def get_transcriptions_id(transcription_id: str):
    """Get the status of a transcription by ID."""
    file = DATA_HANDLER.get_status_file_by_id(transcription_id)
    if file:
        return JSONResponse(content=file, status_code=200)
    raise HTTPException(status_code=404, detail="Transcription ID not found")


@time_it
@app.post(
    "/transcriptions",
    dependencies=[Depends(require_api_key), Depends(require_transcription_enabled)],
    responses={
        418: {"description": "Requested Model is not supported"}
    }
)
async def post_transcription(
    file: UploadFile = File(...),
    language: str | None = Form("en"),
    settings: str | None = Form("{}"),
    # Random selection of available models.
    # This should prevent requests without specified model from 'clogging' the runner of one specific model
    model: str | None = Form(choice(config["rest_models"])),
    task: str = Form("transcribe"),
    text: str | None = Form(""),
):
    """Transcribe an audio file."""
    if language and language not in config["supported_language_codes"]:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported language code: {language}",
        )

    if model and model not in config["rest_models"]:
        raise HTTPException(
            status_code=418,
            detail=f'Requested Model not available. Requested: {model} Configured Models: {", ".join(config["rest_models"])}. A teapot cannot brew coffee.',
        )

    transcription_id = str(uuid.uuid4())
    try:
        audio = AudioSegment.from_file(file.file)
        result = DATA_HANDLER.save_audio_file(audio, transcription_id)
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["message"])
    except Exception as e:
        LOGGER.error(f"Audio processing error: {e}")
        raise HTTPException(status_code=500, detail="Something went wrong")

    time.sleep(0.1)  # TODO: Remove this line...

    if task.endswith("align") and (not text or not language):
        missing_field = "text" if not text else "language"
        raise HTTPException(
            status_code=400,
            detail=f"property {missing_field} is required for task align",
        )

    settings_dict = json.loads(settings) if settings else None
    data = TranscriptionData(
        transcription_id=transcription_id,
        status=TranscriptionStatus.IN_QUERY.value,
        start_time=datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        settings=settings_dict,
        model=model,
        task=task,
        text=text,
        language=language,
    )

    DATA_HANDLER.write_status_file(transcription_id, data)
    return JSONResponse(content=data, status_code=200)


@time_it
@app.get(
    "/export/transcript/{transcription_id}", dependencies=[Depends(require_api_key)]
)
async def get_stream_transcript_export(transcription_id: str):
    """Get the transcription JSON for a specific ID."""
    file = DATA_HANDLER.get_export_json_by_id(transcription_id)
    if file:
        return JSONResponse(content=file, status_code=200)
    raise HTTPException(status_code=404, detail="Transcription ID not found")


@time_it
@app.get("/export/audio/{transcription_id}", dependencies=[Depends(require_api_key)])
async def get_stream_audio_export(transcription_id: str):
    """Get the audio WAV file for a specific transcription ID."""
    file = DATA_HANDLER.get_audio_file_by_id(transcription_id)

    if file is None:
        raise HTTPException(status_code=404, detail="File not found")

    return PlainTextResponse(
        content=file,
        headers={
            "Content-Type": "audio/wav",
            "Content-Disposition": f"attachment; filename={transcription_id}.wav",
        },
    )


@time_it
@app.post(
    "/translate/{target_language}",
    dependencies=[Depends(require_api_key), Depends(require_translation_enabled)],
)
async def translate(
    target_language: str,
    transcription: TranscriptionData = Body(...),
):
    """Translate text to a target language."""

    # Raise Bad Request if Language is not supported
    check_language_supported_guard(target_language)
    check_language_supported_guard(transcription["language"])

    if not transcription["transcript"]["text"]:
        raise HTTPException(
            status_code=400,
            detail="No text provided in the transcription data to translate.",
        )
    transcription_id = str(uuid.uuid4())
    transcription["transcription_id"] = transcription_id
    transcription["task"] = "translate"
    transcription["target_language"] = target_language
    transcription["status"] = TranscriptionStatus.IN_QUERY.value
    DATA_HANDLER.write_status_file(transcription_id, transcription)

    return JSONResponse(content={"id": transcription_id}, status_code=200)


# This could be merged with other requests, but that also requires fixing the demo so it will stay here for now
@time_it
@app.get(
    "/translate/{transcription_id}",
    dependencies=[Depends(require_api_key), Depends(require_translation_enabled)],
)
async def get_translated(transcription_id: str):
    """Get the translated file for a specific ID."""
    file = DATA_HANDLER.get_status_file_by_id(transcription_id)

    if file:
        if file["status"] != TranscriptionStatus.FINISHED.value:
            filtered_file = {
                key: value for key, value in file.items() if key != "transcript"
            }
            return JSONResponse(content=filtered_file, status_code=200)
        return JSONResponse(content=file, status_code=200)
    raise HTTPException(status_code=404, detail="Transcription ID not found")

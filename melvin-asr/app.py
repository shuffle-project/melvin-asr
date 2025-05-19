from contextlib import asynccontextmanager

from api.routes import health, jobs, settings, upload
from core.job_handler import JobHandler
from core.logger import get_logger
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

logger = get_logger(__name__)

job_handler = JobHandler()

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        logger.info("ASR API is starting up.")
        job_handler.initialise()

        yield
        logger.info("ASR API is shutting down.")
    except Exception as e:
        logger.error(f"Error during lifespan: {e}")

app = FastAPI(lifespan=lifespan)

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="Melvin ASR API",
        version="2.0.0",
        routes=app.routes,
    )
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

app.openapi = custom_openapi

app.include_router(settings.router, prefix="/settings")
app.include_router(health.router, prefix="/health")
app.include_router(upload.router, prefix="/upload")
app.include_router(jobs.router, prefix="/jobs")
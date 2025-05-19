from typing import List

from core.config import AppConfig, BatchWorkerConfig
from core.processing.seamlessm4t import \
    get_supported_languages as get_seamlessm4t_supported_languages
from core.processing.whisper import \
    get_supported_languages as get_whisper_supported_languages
from pydantic import BaseModel


class Settings(BaseModel):
    def __init__(self, config: AppConfig):
        self.config = config

    def transcription_languages(self) -> List[str]:
        for worker in self.config.batch_workers:
            if isinstance(worker, BatchWorkerConfig) and worker.transcription_enabled:
                return get_whisper_supported_languages()
        return []
            
    def translation_languages(self) -> List[str]:
        for worker in self.config.batch_workers:
            if isinstance(worker, BatchWorkerConfig) and worker.translation_enabled:
                return get_seamlessm4t_supported_languages()
        return []
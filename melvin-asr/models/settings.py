from core.config import AppConfig
from core.processing.seamlessm4t import \
    get_supported_languages as get_seamlessm4t_supported_languages
from core.processing.whisper import \
    get_supported_languages as get_whisper_supported_languages
from pydantic import computed_field


class Settings(AppConfig):
    @computed_field(return_type=list[str])
    @property
    def transcription_languages(self) -> list[str]:
        for worker in self.batch_workers:
            if worker.transcription_enabled:
                return get_whisper_supported_languages()
        return []
            
    @computed_field(return_type=list[str])
    @property
    def translation_languages(self) -> list[str]:
        for worker in self.batch_workers:
            if worker.translation_enabled:
                return get_seamlessm4t_supported_languages()
        return []
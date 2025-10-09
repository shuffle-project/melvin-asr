from typing import Annotated, List, Literal, Optional, Union

import yaml
from core import paths
from pydantic import BaseModel, Field


class TranscriptionModelSettings(BaseModel):
    vad_filter: bool = True
    condition_on_previous_text: bool = False

class BaseBatchWorker(BaseModel):
    cpu_threads: int
    num_workers: int = 1
    device_index: int = 0
    transcription_enabled: bool
    transcription_model: Optional[str]
    transcription_model_settings: Optional[TranscriptionModelSettings]
    translation_enabled: bool
    translation_model: Optional[str]

class CPUBatchWorker(BaseBatchWorker):
    device: Literal["cpu"]
    compute_type: Literal["int8"]

    def get_device(self):
        return "cpu"

class GPUBatchWorker(BaseBatchWorker):
    device: Literal["cuda"]
    compute_type: Literal["float16", "int8_float16"]

    def get_device(self):
        return f"cuda:{self.device_index}" if self.device_index != None else "cuda"

BatchWorkerConfig = Annotated[
    Union[CPUBatchWorker, GPUBatchWorker], 
    Field(discriminator="device")
]

class AppConfig(BaseModel):
    host: str = "127.0.0.1"
    port: int = 8000
    api_keys: list[str] = []
    log_level: Literal["info", "warn", "error"] = "info"

    batch_workers: List[BatchWorkerConfig] = []


def load_config() -> AppConfig:
    config_path = paths.config_path
    if config_path.exists():
        with config_path.open("r") as f:
            raw = yaml.safe_load(f)
            return AppConfig(**raw)
    return AppConfig()

config = load_config()

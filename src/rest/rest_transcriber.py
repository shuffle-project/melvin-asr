"""Module to handle the transcription process"""

import logging
from dataclasses import asdict

from src.helper.forced_alignment import align_ground_truth
from faster_whisper import WhisperModel, BatchedInferencePipeline

from src.helper.model_handler import ModelHandler
from src.helper.segment_info_parser import parse_segment_list
from src.helper.time_it import time_it
from src.helper.transcription_settings import TranscriptionSettings

from src.helper.util import disable_tqdm
import stable_whisper

LOGGER = logging.getLogger(__name__)

class Transcriber:
    """Class to handle the transcription process"""

    def __init__(self, config: dict):
        # Parsing Config
        # possible config options:
        #   device: cpu
        #   model: tiny
        #   compute_type: int8
        #   device_index: 0
        #   num_workers: 1
        #   cpu_threads: 4
        #   transcription_mode: default

        self.device = config.get("device", "cpu")

        self.supported_models = config.get("models",["tiny"])

        assert len(self.supported_models) > 0

        self.compute_type = config.get("compute_type", "int8")

        self.device_index = config.get("device_index",0)

        self.num_workers = config.get("num_workers", 1)

        self.cpu_threads = config.get("cpu_threads", 4)

        self.transcription_mode = config.get("transcription_mode", "default")

        # Avoiding Compute Type mismatch
        if (
            (self.device == "cpu" and self.compute_type == "int8")
            or (self.device == "cuda" and self.compute_type == "float16")
            or (self.device == "cuda" and self.compute_type == "int8_float16")
        ):
            pass
        else:
            LOGGER.error(
                "Invalid or Unmatching device or compute_type: "
                + f"{self.device} {self.compute_type}, Fallback to CPU int8"
            )
            self.device = "cpu"
            self.compute_type = "int8"

        self.model: WhisperModel = None
        ModelHandler().setup_model(self.supported_models[-1])
        self.loaded_model_name = None
        self.load_model(self.supported_models[-1])

    def supports_model(self, requested_model: str) -> bool:
        return requested_model in self.supported_models

    def get_preferred_model(self) -> str:
        return self.supported_models[-1]

    def load_model(self, model) -> bool:
        """loads the model if not loaded"""

        if self.loaded_model_name == model:
            return True

        ModelHandler().setup_model(model)

        self.model = stable_whisper.load_faster_whisper(
            ModelHandler().get_model_path(model),
            local_files_only=True,
            device=self.device,
            compute_type=self.compute_type,
            device_index=self.device_index,
            num_workers=self.num_workers,
            cpu_threads=self.cpu_threads,
        )

        self.loaded_model_name = model

        return True

    @time_it
    def transcribe_audio_file(
        self, audio_file_path: str, model:str, settings: dict = None
    ) -> dict:
        """Function to run the transcription process"""
        LOGGER.debug(f"Transcribing with model {model}")
        assert self.supports_model(model)
        self.load_model(model)
        try:
            LOGGER.info("Transcribing file: " + str(audio_file_path))
            return {
                "success": True,
                "data": self.transcribe_with_settings(
                    audio_file_path, self.model, settings
                ),
            }
        except Exception as e:
            LOGGER.error("Error during transcription: " + str(e))
            return {"success": False, "data": str(e)}

    def transcribe_with_settings(
        self, audio, model: WhisperModel, settings: dict
    ) -> dict:
        """Function to transcribe with settings"""
        settings = TranscriptionSettings().get_and_update_settings(settings)

        segments = []

        if self.transcription_mode == "default":
            res = model.transcribe(audio, **settings)
            segments = [s.to_dict() for s in res.segments]

        elif self.transcription_mode == "batched":
            batched_model = BatchedInferencePipeline(model=model)
            segments, _ = batched_model.transcribe(audio, batch_size=16, **settings)
            segments = [asdict(s) for s in segments]

        # TODO: Maybe aligning the result can give us the same quality of results that transcribe_stable would have given us. This can be validated with rest benchmarks
        data = parse_segment_list(segments)
        return data

    @time_it
    def force_align_audio_file(self, audio_file_path: str, text: str, model: str, language: str) -> dict:
        """Function to run the alignment process"""
        assert self.supports_model(model)
        self.load_model(model)
        try:
            LOGGER.info("Align transcript for file: " + str(audio_file_path))
            result = align_ground_truth(self.model, text, audio_file_path)
            data = parse_segment_list({"segments": result}
                                      )

            return {
                "success": True,
                "data": data,
            }
        except Exception as e:
            LOGGER.error("Error during alignment: " + str(e))
            return {"success": False, "data": str(e)}


    @time_it
    def align_audio_file(self, audio_file_path: str, text: str, model: str, language: str) -> dict:
        """Function to run the alignment process"""

        assert self.supports_model(model)
        self.load_model(model)
        try:
            LOGGER.info("Align transcript for file: " + str(audio_file_path))
            with disable_tqdm():
                result: stable_whisper.WhisperResult = self.model.align(
                    audio=audio_file_path,
                    text=text,
                    language=language, 
                    verbose=None,
                )
                data = parse_segment_list(result.segments_to_dicts())

                return {
                    "success": True,
                    "data": data,
                }
        except Exception as e:
            LOGGER.error("Error during alignment: " + str(e))
            return {"success": False, "data": str(e)}

"""Module to handle the transcription process"""

import logging

import stable_whisper
from faster_whisper import WhisperModel, BatchedInferencePipeline

from src.helper.model_handler import ModelHandler
from src.helper.segment_info_parser import parse_stable_whisper_result
from src.helper.time_it import time_it
from src.helper.transcription_settings import TranscriptionSettings

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

        if "device" in config:
            self.device = config["device"]
        else:
            self.device = "cpu"

        if "model" in config:
            self.model_name = config["model"]
        else:
            self.model_name = "tiny"

        if "compute_type" in config:
            self.compute_type = config["compute_type"]
        else:
            self.compute_type = "int8"

        if "device_index" in config:
            self.device_index = config["device_index"]
        else:
            self.device_index = 0

        if "num_workers" in config:
            self.num_workers = config["num_workers"]
        else:
            self.num_workers = 1

        if "cpu_threads" in config:
            self.cpu_threads = config["cpu_threads"]
        else:
            self.cpu_threads = 4

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
        ModelHandler().setup_model(self.model_name)

    def load_model(self) -> bool:
        """loads the model if not loaded"""
        if self.model is not None:
            return True
        self.model = stable_whisper.load_faster_whisper(
            ModelHandler().get_model_path(self.model_name),
            local_files_only=True,
            device=self.device,
            compute_type=self.compute_type,
            device_index=self.device_index,
            num_workers=self.num_workers,
            cpu_threads=self.cpu_threads,
        )

    @time_it
    def transcribe_audio_file(
        self, audio_file_path: str, settings: dict = None
    ) -> dict:
        """Function to run the transcription process"""
        self.load_model()
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
        # cannot use transcribe_stable because it performs illegal actions on segment
        # issue likely resides here:
        # https://github.com/jianfch/stable-ts/blob/9fe1bf511862dccb669ff27f5fae9ae206b91a10/stable_whisper/whisper_word_level/faster_whisper.py#L204

        batched_model = BatchedInferencePipeline(model=model)
        segments, _ = batched_model.transcribe(audio, batch_size=16, **settings)

        #result = model.transcribe(audio, **settings)
        result = {"segments": segments}
        # TODO: Maybe alignint the result can give us the same quality of results that transcribe_stable would have given us. This can be validated with rest benchmarks
        data = parse_stable_whisper_result(result)
        return data

    @time_it
    def align_audio_file(self, audio_file_path: str, text: str, language: str) -> dict:
        """Function to run the alignment process"""
        self.load_model()
        try:
            LOGGER.info("Align transcript for file: " + str(audio_file_path))
            result = self.model.align(audio_file_path, text, language)
            data = parse_stable_whisper_result(result)

            return {
                "success": True,
                "data": data,
            }
        except Exception as e:
            LOGGER.error("Error during alignment: " + str(e))
            return {"success": False, "data": str(e)}

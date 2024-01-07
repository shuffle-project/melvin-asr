""" Module to handle the transcription process """
import os
import time
from faster_whisper import WhisperModel
from faster_whisper.transcribe import TranscriptionInfo
import numpy as np
from src.helper.system_monitor import SystemMonitor
from src.config import CONFIG
from src.helper.logger import Logger, Color

LOGGER = Logger("Transcriber", True, Color.MAGENTA)


def time_it(func):
    """
    Decorator function to measure and print the execution time of a function.
    """

    def wrapper(*args, **kwargs):
        log = LOGGER
        start_time = time.time()  # Record the start time
        result = func(*args, **kwargs)  # Execute the function
        end_time = time.time()  # Record the end time
        elapsed_time = end_time - start_time  # Calculate elapsed time
        log.print_log(
            f"Function {func.__name__} took {elapsed_time:.4f} seconds to execute."
        )
        return result

    return wrapper


class Transcriber:
    """Class to handle the transcription process"""

    def __init__(self, models_to_load: [str]):
        self.log = LOGGER
        self.system_monitor = SystemMonitor()
        self.models: [{"name": str, "model": WhisperModel}] = self.load_models(
            models_to_load
        )
        self.log.print_log(f"Models ready for Transcriber: {self.models}")

    def load_models(
        self, models_to_load: [str]
    ) -> [{"name": str, "model": WhisperModel}]:
        """Function to load the models"""
        loaded_models: [{"name": str, "model": WhisperModel}] = []
        self.log.print_log(f"RAM usage before loading models: {self.system_monitor.return_ram_usage()}")
        for model_name in models_to_load:
            model_path = self.get_model_path(model_name)
            model = WhisperModel(model_path, local_files_only=True, device="cpu", compute_type="int8")
            loaded_models.append({"name": model_name, "model": model})
        self.log.print_log(f"RAM usage after loading models: {self.system_monitor.return_ram_usage()}")
        return loaded_models

    def get_model_path(self, model_name: str) -> str:
        """Function to get the model path"""
        model_path = os.getcwd() + CONFIG["MODEL_PATH"] + model_name
        return model_path

    def get_model(self, model_name: str) -> WhisperModel:
        """Function to get a model"""
        for model in self.models:
            if model["name"] == model_name:
                return model["model"]
        return None

    def parse_transcription_info_to_dict(self, info: TranscriptionInfo) -> dict:
        """Function to convert the transcription info to a dictionary"""
        # TUPEL attributes:
        #
        # language: str
        # language_probability: float
        # duration: float
        # duration_after_vad: float
        # all_language_probs: Optional[List[Tuple[str, float]]]
        # transcription_options: TranscriptionOptions
        # vad_options: VadOptions

        info_dict = {
            "language": info.language,
            "language_probability": info.language_probability,
            "duration": info.duration,
            "duration_after_vad": info.duration_after_vad,
            # "all_language_probs": info.all_language_probs,
            "transcription_options": info.transcription_options,
            "vad_options": info.vad_options,
        }
        return info_dict

    def make_segments_and_info_to_dict(
        self, segments: tuple, info: TranscriptionInfo
    ) -> dict:
        """Function to convert the segments and info to a dictionary"""
        segments_list = list(segments)

        combined_dict = {
            "segments": segments_list,
            "info": self.parse_transcription_info_to_dict(info),
        }
        return combined_dict

    @time_it
    def transcribe_audio_audio_segment(self, audio_segment, model_name) -> dict:
        """Function to run the transcription process"""
        model = self.get_model(model_name)
        if model is None:
            self.log.print_error("Model not found")
            return None
        try:
            self.log.print_log("Transcribing audio segment")
            # Faster Whisper Call
            audio_data_bytes = (
                np.frombuffer(audio_segment.raw_data, np.int16)
                .flatten()
                .astype(np.float32)
                / 32768.0
            )
            segments, info = model.transcribe(
                audio_data_bytes, beam_size=5, word_timestamps=True
            )
            data_dict = self.make_segments_and_info_to_dict(segments, info)
            return data_dict
        # need to catch all exceptions here because the whisper call is not
        # pylint: disable=W0718
        except Exception as e:
            self.log.print_error("Error during transcription: " + str(e))
            return None

    @time_it
    def transcribe_audio_file(self, audio_file_path: str, model_name: str) -> dict:
        """Function to run the transcription process"""
        model = self.get_model(model_name)
        if model is None:
            self.log.print_error("Model not found")
            return None
        try:
            self.log.print_log("Transcribing file: " + str(audio_file_path))
            # Faster Whisper Call
            segments, info = model.transcribe(
                audio_file_path, beam_size=5, word_timestamps=True
            )
            data_dict = self.make_segments_and_info_to_dict(segments, info)
            return data_dict
            # need to catch all exceptions here because the whisper call is not
            # pylint: disable=W0718
        except Exception as e:
            self.log.print_error("Error during transcription: " + str(e))
            return None

""" Module to handle the transcription process """
import os
import time
from faster_whisper import WhisperModel
from faster_whisper.transcribe import TranscriptionInfo
import numpy as np
from src.config import CONFIG
from src.helper.logger import Logger, Color
from src.transcription.transcription_settings import TranscriptionSettings

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

    def __init__(self, model_name, device, compute_type):
        self.log = LOGGER
        self.model_name = model_name
        self.device = device
        self.compute_type = compute_type
        self.model: WhisperModel = None

    def load_model(self) -> bool:
        """loads the model if not loaded"""
        if self.model is not None:
            return True
        model_path = self.get_model_path(self.model_name)
        try:
            # compute_type for CPU is only int8, for CUDA ist float16 or int8_float16
            # pylint: disable=R0916
            if (
                (self.device == "cpu" and self.compute_type == "int8")
                or (self.device == "cuda" and self.compute_type == "float16")
                or (self.device == "cuda" and self.compute_type == "int8_float16")
            ):
                self.model = WhisperModel(
                    model_path,
                    local_files_only=True,
                    device=self.device,
                    compute_type=self.compute_type,
                )
            else:
                self.log.print_error(
                    "Invalid or Unmatching device or compute_type: "
                    + f"{self.device} {self.compute_type}, Fallback to CPU int8"
                )
                self.model = WhisperModel(
                    model_path, local_files_only=True, device="cpu", compute_type="int8"
                )
            return True
        # need to catch all exceptions here
        # pylint: disable=W0718
        except Exception as e:
            self.log.print_error("Error loading model: " + str(e))
            return False

    def unload_model(self) -> bool:
        """unloads the model if loaded"""
        if self.model is not None:
            self.model = None
        return True

    def get_model_path(self, model_name: str) -> str:
        """Function to get the model path"""
        model_path = os.getcwd() + CONFIG["MODEL_PATH"] + model_name
        return model_path

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
    def transcribe_audio_audio_segment(
        self, audio_segment, settings: dict = None
    ) -> dict:
        """Function to run the transcription process"""
        self.load_model()
        try:
            self.log.print_log("Transcribing audio segment")
            audio_data_bytes = (
                np.frombuffer(audio_segment.raw_data, np.int16)
                .flatten()
                .astype(np.float32)
                / 32768.0
            )
            return {
                "success": True,
                "data": self.transcribe_with_settings(
                    audio_data_bytes, self.model, settings
                ),
            }
        # need to catch all exceptions here because the whisper call is not
        # pylint: disable=W0718
        except Exception as e:
            self.log.print_error("Error during transcription: " + str(e))
            return {
                "success": False,
                "data": str(e)
            }

    @time_it
    def transcribe_audio_file(
        self, audio_file_path: str, settings: dict = None
    ) -> dict:
        """Function to run the transcription process"""
        self.load_model()
        try:
            self.log.print_log("Transcribing file: " + str(audio_file_path))
            return {
                "success": True,
                "data": self.transcribe_with_settings(
                    audio_file_path, self.model, settings
                ),
            }

            # need to catch all exceptions here because the whisper call is not
            # pylint: disable=W0718
        except Exception as e:
            self.log.print_error("Error during transcription: " + str(e))
            return {
                "success": False,
                "data": str(e)
            }

    def transcribe_with_settings(
        self, audio, model: WhisperModel, settings: dict
    ) -> dict:
        """Function to transcribe with settings"""
        settings = TranscriptionSettings().get_and_update_settings(settings)
        segments, info = model.transcribe(audio, **settings)
        return self.make_segments_and_info_to_dict(segments, info)

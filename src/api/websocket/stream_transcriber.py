""" Module to handle the transcription process """
import io
import os
import time
import wave
from faster_whisper import WhisperModel
from src.config import CONFIG
from src.helper.logger import Logger, Color
from src.transcription.segment_info_parser import parse_segments_and_info_to_dict
from src.transcription.transcription_settings import TranscriptionSettings

LOGGER = Logger("Transcriber", True, Color.MAGENTA)


# def time_it(func):
#     """
#     Decorator function to measure and print the execution time of a function.
#     """
#
#     def wrapper(*args, **kwargs):
#         log = LOGGER
#         start_time = time.time()  # Record the start time
#         result = func(*args, **kwargs)  # Execute the function
#         end_time = time.time()  # Record the end time
#         elapsed_time = end_time - start_time  # Calculate elapsed time
#         log.print_log(
#             f"Function {func.__name__} took {elapsed_time:.4f} seconds to execute."
#         )
#         return result
#
#     return wrapper


# class StreamTranscriber:
#     """Class to handle the transcription process"""
#
#     def __init__(self, model_name, device, compute_type):
#         self.log = LOGGER
#         self.model_name = model_name
#         self.device = device
#         self.compute_type = compute_type
#         self.cpu_threads = 4
#         self.num_workers = 1
#         self.threads
#         self.model: WhisperModel = None
#
#     def load_model(self) -> bool:
#         """loads the model if not loaded"""
#         if self.model is not None:
#             return True
#         model_path = self.get_model_path(self.model_name)
#         try:
#             # compute_type for CPU is only int8, for CUDA ist float16 or int8_float16
#             if (
#                     (self.device == "cpu" and self.compute_type == "int8")
#                     or (self.device == "cuda" and self.compute_type == "float16")
#                     or (self.device == "cuda" and self.compute_type == "int8_float16")
#             ):
#                 self.model = WhisperModel(
#                     model_path,
#                     local_files_only=True,
#                     device=self.device,
#                     compute_type=self.compute_type,
#                 )
#             else:
#                 self.log.print_error(
#                     "Invalid or Unmatching device or compute_type: "
#                     + f"{self.device} {self.compute_type}, Fallback to CPU int8"
#                 )
#                 self.model = WhisperModel(
#                     model_path, local_files_only=True, device="cpu", compute_type="int8"
#                 )
#             return True
#         except Exception as e:
#             self.log.print_error("Error loading model: " + str(e))
#             return False
#
#     def unload_model(self) -> bool:
#         """unloads the model if loaded"""
#         if self.model is not None:
#             self.model = None
#         return True
#
#     def get_model_path(self, model_name: str) -> str:
#         """Function to get the model path"""
#         model_path = os.getcwd() + CONFIG["model_path"] + model_name
#         return model_path
#
#     @time_it
#     def transcribe_audio_chunk(
#             self,
#             audio_chunk,
#             settings: dict = None,
#             sample_rate=16000,
#             num_channels=1,
#             sampwidth=2,
#     ) -> dict:  # returns a tuple with a dict or None
#         """Function to run the transcription process"""
#         self.load_model()
#         try:
#             self.log.print_log("Transcribing audio chunk of length: " + str(len(audio_chunk)))
#             result = "ERROR"
#             with io.BytesIO() as wav_io:
#                 with wave.open(wav_io, "wb") as wav_file:
#                     wav_file.setnchannels(num_channels)
#                     wav_file.setsampwidth(sampwidth)
#                     wav_file.setframerate(sample_rate)
#                     wav_file.writeframes(audio_chunk)
#                 wav_io.seek(0)
#                 result = self.transcribe_with_settings(wav_io, self.model, settings)
#             return result
#         except Exception as e:
#             self.log.print_error("Error during transcription: " + str(e))
#             return None
#
#     @time_it
#     def transcribe_audio_file(
#             self, audio_file_path: str, settings: dict = None
#     ) -> dict:
#         """Function to run the transcription process"""
#         self.load_model()
#         try:
#             self.log.print_log("Transcribing file: " + str(audio_file_path))
#             return {
#                 "success": True,
#                 "data": self.transcribe_with_settings(
#                     audio_file_path, self.model, settings
#                 ),
#             }
#         except Exception as e:
#             self.log.print_error("Error during transcription: " + str(e))
#             return {"success": False, "data": str(e)}
#
#     def transcribe_with_settings(
#             self, audio, model: WhisperModel, settings: dict
#     ) -> dict:
#         """Function to transcribe with settings"""
#         settings = TranscriptionSettings().get_and_update_settings(settings)
#         segments, info = model.transcribe(audio, **settings)
#         return parse_segments_and_info_to_dict(segments, info)


class Transcriber:
    def __init__(self, num_workers: int, model_name, device, compute_type):
        self.num_workers = num_workers
        self.availableWorkers = num_workers
        self.model_name = model_name
        self.device = device
        self.compute_type = compute_type

        self.model: WhisperModel or None = None

    @staticmethod
    def get_model_path(self, model_name: str) -> str:
        """Function to get the model path"""
        model_path = os.getcwd() + CONFIG["model_path"] + model_name
        return model_path

    def load_model(self) -> bool:
        """loads the model if not loaded"""
        if self.model is not None:
            return True
        model_path = self.get_model_path(self.model_name)
        try:
            # compute_type for CPU is only int8, for CUDA ist float16 or int8_float16
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
        except Exception as e:
            self.log.print_error("Error loading model: " + str(e))
            return False

    def _transcribe(self,
                    audio_chunk,
                    settings: dict = None,
                    sample_rate=16000,
                    num_channels=1,
                    sampwidth=2,
                    ) -> dict:

        """Function to run the transcription process"""
        try:
            self.log.print_log("Transcribing audio chunk of length: " + str(len(audio_chunk)))
            result = "ERROR"
            with io.BytesIO() as wav_io:
                with wave.open(wav_io, "wb") as wav_file:
                    wav_file.setnchannels(num_channels)
                    wav_file.setsampwidth(sampwidth)
                    wav_file.setframerate(sample_rate)
                    wav_file.writeframes(audio_chunk)
                wav_io.seek(0)
                result = self.transcribe_with_settings(wav_io, self.model, settings)
            return result
        except Exception as e:
            self.log.print_error("Error during transcription: " + str(e))
            return None

    @staticmethod
    def transcribe_with_settings(
            audio, model: WhisperModel, settings: dict
    ) -> dict:
        """Function to transcribe with settings"""
        settings = TranscriptionSettings().get_and_update_settings(settings)
        segments, info = model.transcribe(audio, **settings)
        return parse_segments_and_info_to_dict(segments, info)

    def get_worker(self):
        if self._worker_available():
            self.availableWorkers = self.availableWorkers - 1
            return self._transcribe
        else:
            return None

    def return_worker(self):
        self.availableWorkers = self.availableWorkers + 1
        pass

    def _worker_available(self) -> bool:
        pass

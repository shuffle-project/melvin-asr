""" Module to handle the transcription process """
import io
import os
import wave
from typing import Callable, Union

from faster_whisper import WhisperModel

from src.helper.config import CONFIG
from src.helper.logger import Logger, Color
from src.transcription.segment_info_parser import parse_segments_and_info_to_dict
from src.transcription.transcription_settings import TranscriptionSettings

LOGGER = Logger("Transcriber", True, Color.MAGENTA)


class Transcriber:
    def __init__(self, model_name: str, device: str, device_index: list, compute_type: str, cpu_threads: int,
                 num_workers: int, ):
        """
        This class converts audio to text. You should use it by initializing a Transcriber once and then ask to get
        a transcribe worker method via getWorker(). If there is a free worker available, you will get the transcribe
        method and can call it as often as you want. If you're done with all transcription tasks,
        hand back your worker resource by calling return_worker().

        Args:
            model_name: Which Whisper model to use.
            device: Which device to use. cuda or CPU.
            device_index: Which device IDs to use. E.g. for 3 GPUs = [0,1,2]
            compute_type: Quantization of the Whisper model
            cpu_threads: Number of threads to use when running on CPU (4 by default)
            num_workers: Having multiple workers enables true parallelism when running the model
        """

        self._log = LOGGER
        self._model_name = model_name
        self._device = device
        self._device_index = device_index
        self._compute_type = compute_type
        self._cpu_threads = cpu_threads
        self._num_workers = num_workers
        self._model: WhisperModel or None = None

        self._availableWorkers = num_workers

        if self._load_model():
            self._log.print_log("Successfully initialized WhisperModel")

    @classmethod
    def for_gpu(cls, model_name: str, device_index: list):
        return cls(model_name=model_name, device="cuda", device_index=device_index, compute_type="float16",
                   cpu_threads=0,
                   num_workers=1)

    @classmethod
    def for_cpu(cls, model_name: str, cpu_threads, num_workers):
        return cls(model_name=model_name, device="cpu", device_index=[1], compute_type="int8", cpu_threads=cpu_threads,
                   num_workers=num_workers)

    @staticmethod
    def _get_model_path(model_name: str) -> str:
        """Function to get the model path"""
        model_path = os.getcwd() + CONFIG["model_path"] + model_name
        return model_path

    def _load_model(self) -> bool:
        """loads the model if not loaded"""
        if self._model is not None:
            return True
        model_path = self._get_model_path(self._model_name)
        try:
            # compute_type for CPU is only int8, for CUDA ist float16 or int8_float16
            if (
                    (self._device == "cpu" and self._compute_type == "int8")
                    or (self._device == "cuda" and self._compute_type == "float16")
                    or (self._device == "cuda" and self._compute_type == "int8_float16")
            ):
                self._model = WhisperModel(
                    model_path,
                    local_files_only=True,
                    device=self._device,
                    device_index=self._device_index,
                    compute_type=self._compute_type,
                    cpu_threads=self._cpu_threads,
                    num_workers=self._num_workers,
                )
            else:
                self._log.print_error(
                    "Invalid or unmatching device or compute_type: "
                    + f"{self._device} {self._compute_type}, Fallback to CPU int8"
                )
                self._model = WhisperModel(
                    model_path, local_files_only=True, device="cpu", compute_type="int8"
                )
            return True
        except Exception as e:
            self._log.print_error("Error loading model: " + str(e))
            return False

    def _transcribe(self,
                    audio_chunk,
                    settings: dict = None,
                    sample_rate=16000,
                    num_channels=1,
                    sampwidth=2,
                    ) -> dict or None:

        """Function to run the transcription process"""
        try:
            self._log.print_log("Transcribing audio chunk of length: " + str(len(audio_chunk)))
            result = "ERROR"
            with io.BytesIO() as wav_io:
                with wave.open(wav_io, "wb") as wav_file:
                    wav_file.setnchannels(num_channels)
                    wav_file.setsampwidth(sampwidth)
                    wav_file.setframerate(sample_rate)
                    wav_file.writeframes(audio_chunk)
                wav_io.seek(0)
                result = self._transcribe_with_settings(wav_io, self._model, settings)
            return result
        except Exception as e:
            self._log.print_error("Error during transcription: " + str(e))
            return None

    @staticmethod
    def _transcribe_with_settings(
            audio, model: WhisperModel, settings: dict
    ) -> dict:
        """Function to transcribe with settings"""
        settings = TranscriptionSettings().get_and_update_settings(settings)
        segments, info = model.transcribe(audio, **settings)
        return parse_segments_and_info_to_dict(segments, info)

    def get_worker(self) -> Union[None or Callable]:
        """
        Function to get the transcribe method, if workers are available
        Returns: callable transcribe method or None

        """
        if self._worker_available():
            self._availableWorkers = self._availableWorkers - 1
            return self._transcribe
        else:
            return None

    def return_worker(self):
        """
        Call this only to signalize that you are freeing a worker resource and won't call the transcribe method again.
        Returns:

        """
        self._availableWorkers = self._availableWorkers + 1
        pass

    def _worker_available(self) -> bool:
        if self._availableWorkers > 0:
            return True
        return False

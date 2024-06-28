""" Module to handle the transcription process """
import io
import wave
from typing import Callable

from faster_whisper import WhisperModel

from src.helper.logger import Logger, Color
from src.helper.model_handler import ModelHandler
from src.helper.segment_info_parser import parse_segments_and_info_to_dict
from src.helper.transcription_settings import TranscriptionSettings

LOGGER = Logger("Stream Transcriber", True, Color.CYAN)


class Transcriber:
    def __init__(
        self,
        worker_seats: int,
        model_name: str,
        device: str,
        compute_type: str,
        device_index: list,
        cpu_threads: int,
        num_workers: int,
    ):
        """
        This class converts audio to text. You should use it by initializing a Transcriber once and then ask to get
        a transcribe worker method via getWorker(). If there is a free worker available, you will get the transcribe
        method and can call it as often as you want. If you're done with all transcription tasks,
        hand back your worker resource by calling return_worker().

        Args:
            worker_seats: Number of workers available
            model_name: Which Whisper model to use.
            device: Which device to use. cuda or CPU.
            device_index: Which device IDs to use. E.g. for 3 GPUs = [0,1,2]
            compute_type: Quantization of the Whisper model
            cpu_threads: Number of threads to use when running on CPU (4 by default)
            num_workers: Having multiple workers enables true parallelism when running the model
        """

        self._log = LOGGER
        self._worker_seats = worker_seats
        self._model_name = model_name
        self._device = device
        self._device_index = device_index
        self._compute_type = compute_type
        self._cpu_threads = cpu_threads
        self._num_workers = num_workers
        self._model: WhisperModel = self._load_model()

        self._availableWorkers = worker_seats

    @classmethod
    def for_gpu(cls, worker_seats: int, model_name: str, device_index: list):
        return cls(
            worker_seats=worker_seats,
            model_name=model_name,
            device="cuda",
            compute_type="float16",
            device_index=device_index,
            cpu_threads=4,
            num_workers=1,
        )

    @classmethod
    def for_cpu(cls, worker_seats: int, model_name: str, cpu_threads, num_workers):
        return cls(
            worker_seats=worker_seats,
            model_name=model_name,
            device="cpu",
            device_index=0,
            compute_type="int8",
            cpu_threads=cpu_threads,
            num_workers=num_workers,
        )

    def _load_model(self) -> None:
        """loads the model if not loaded"""
        ModelHandler().setup_model(self._model_name)
        return WhisperModel(
            ModelHandler().get_model_path(self._model_name),
            local_files_only=True,
            device=self._device,
            device_index=self._device_index,
            compute_type=self._compute_type,
            cpu_threads=self._cpu_threads,
            num_workers=self._num_workers,
        )

    def _transcribe(
        self,
        audio_chunk: bytes,
        settings: dict,
        quit: bool = False,
    ) -> dict:
        """Function to run the transcription process"""
        sample_rate = 16000
        num_channels = 1
        sampwidth = 2

        if quit:
            self.return_worker()

        self._log.print_log(
            "Transcribing audio chunk of length: " + str(len(audio_chunk))
        )
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

    @staticmethod
    def _transcribe_with_settings(audio, model: WhisperModel, settings: dict) -> dict:
        """Function to transcribe with settings"""
        settings = TranscriptionSettings().get_and_update_settings(settings)
        segments, info = model.transcribe(audio, **settings)
        return parse_segments_and_info_to_dict(segments, info)

    def get_worker(self) -> Callable:
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

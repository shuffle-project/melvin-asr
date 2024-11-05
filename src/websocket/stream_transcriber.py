"""Module to handle the transcription process"""

import io
import wave

from faster_whisper import WhisperModel
from faster_whisper.utils import logging

from src.helper.model_handler import ModelHandler
from src.helper.segment_info_parser import parse_segments_and_info_to_dict
from src.helper.transcription_settings import TranscriptionSettings

LOGGER = logging.getLogger(__name__)


class Transcriber:
    def __init__(
        self,
        model_name: str,
        device: str,
        compute_type: str,
        device_index: list,
        cpu_threads: int,
        num_workers: int,
    ):
        """
        This class converts audio to text. You should use it by initializing a Transcriber once and then pass it to all streams that you want to transcribe at.

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
        self._model: WhisperModel = self._load_model()

    @classmethod
    def for_gpu(cls, model_name: str, device_index: list):
        return cls(
            model_name=model_name,
            device="cuda",
            compute_type="float16",
            device_index=device_index,
            cpu_threads=4,
            num_workers=1,
        )

    @classmethod
    def for_cpu(cls, model_name: str, cpu_threads, num_workers):
        return cls(
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
        prompt: str = "",
    ) -> dict:
        """Function to run the transcription process"""
        sample_rate = 16000
        num_channels = 1
        sampwidth = 2

        result = "ERROR"
        with io.BytesIO() as wav_io:
            with wave.open(wav_io, "wb") as wav_file:
                wav_file.setnchannels(num_channels)
                wav_file.setsampwidth(sampwidth)
                wav_file.setframerate(sample_rate)
                wav_file.writeframes(audio_chunk)
            wav_io.seek(0)
            settings = TranscriptionSettings().get_and_update_settings(
                {"initial_prompt": prompt}
            )
            segments, info = self._model.transcribe(wav_io, **settings)
            result = parse_segments_and_info_to_dict(segments, info)
        return result

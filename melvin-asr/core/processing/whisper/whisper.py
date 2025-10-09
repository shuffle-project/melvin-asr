import os
from typing import List

import stable_whisper
from core.config import BatchWorkerConfig
from core.logger import get_logger
from core.paths import models_path
from core.tqdm import disable_tqdm
from core.upload_handler import upload_handler
from faster_whisper import available_models, download_model
from models.job import AlignmentByAudioRequest, JobResult, TranscriptionRequest
from models.transcript import Segment, Transcript, Word

from .languages import is_language_supported

logger = get_logger(__name__)
class Whisper:
    def __init__(self, config: BatchWorkerConfig):
        self.config = config

    def initialize(self):
        model_name = self.config.transcription_model
        if model_name not in available_models():
            raise ValueError(f"Model {model_name} is not available.")
        
        local_model_path = os.path.join(models_path, model_name)
        if not os.path.exists(local_model_path):
            try:
                logger.info(f"Downloading model {model_name} to {local_model_path}")
                download_model(model_name, output_dir=local_model_path)
            except Exception as e:
                logger.error(f"Error downloading model {model_name}: {e}")
                raise
        
        try:
            logger.info(f"Loading model {model_name}")
            
            self.model = stable_whisper.load_faster_whisper(
                local_model_path,
                device=self.config.get_device(),
                compute_type=self.config.compute_type,
                cpu_threads=self.config.cpu_threads,
                num_workers=self.config.num_workers,
            )
        except:
            logger.error(f"Error loading model {model_name}")
            raise

    def transcribe(self, settings: TranscriptionRequest) -> JobResult:
        # TODO: transcription settings
        # TODO: mode default and batched

        try:
            audio_filepath = upload_handler.get_file_path(settings.audio_filename)
            with disable_tqdm():
                result: stable_whisper.result.WhisperResult = self.model.transcribe(audio_filepath, language=settings.language)
            
            raw_result = result.to_dict()
            transcript = self.result_to_transcript(raw_result)
            return JobResult(
                transcript=transcript,
                raw_result=raw_result
            )
        except Exception as e:
            logger.error(f"Error transcribing audio: {e}")
            raise

    def align_transcript_to_audio(self, settings: AlignmentByAudioRequest) -> JobResult:
        try:
            audio_filepath = upload_handler.get_file_path(settings.audio_filename)
            with disable_tqdm():
                result: stable_whisper.WhisperResult = self.model.align(audio=audio_filepath, text=settings.transcript.text, language=settings.language, verbose=False)
            
            raw_result = result.to_dict()
            transcript = self.result_to_transcript(raw_result)
            return JobResult(
                transcript=transcript,
                raw_result=raw_result
            )
        except Exception as e:
            logger.error(f"Error aligning transcript to audio: {e}")
            raise

    def result_to_transcript(self, result: dict) -> Transcript:
        segments: List[Segment] = []
        for segment in result["segments"]:
            words: List[Word] = [Word(
                text = x["word"],
                start = x["start"],
                end = x["end"],
                probability = x["probability"],
            ) for x in segment["words"]]
            
            segments.append(Segment(
                text = segment["text"],
                start = segment["start"],
                end = segment["end"],
                words = words
            ))

        return Transcript(
            text = result["text"],
            segments = segments
        )


import os

import torch
from core.config import BatchWorkerConfig
from core.logger import get_logger
from core.paths import models_path
from core.processing.alignment import alignment
from core.tqdm import disable_tqdm
from models.job import JobResult, TranslationRequest
from models.transcript import Segment, Transcript, Word
from transformers import SeamlessM4TTokenizer, SeamlessM4Tv2ForTextToText

from .languages import map_language_code

logger = get_logger(__name__)

available_models = ["facebook/seamless-m4t-v2-large"]
class SeamlessM4T:
    def __init__(self, config: BatchWorkerConfig):
        self.config = config
        self.device = config.get_device()

    def initialize(self):
        model_name = self.config.translation_model
        if model_name not in available_models:
            raise ValueError(f"Model {model_name} is not available.")
        
        model_download_directory = f"models--{model_name}".replace('/', '--')
        local_model_path = os.path.join(models_path, model_download_directory)
        if not os.path.exists(local_model_path):
            logger.info(f"Model {model_name} is not downloaded yet")

        try:
            with disable_tqdm():
                self.tokenizer: SeamlessM4TTokenizer = SeamlessM4TTokenizer.from_pretrained(model_name, cache_dir=models_path)
                self.model: SeamlessM4Tv2ForTextToText = SeamlessM4Tv2ForTextToText.from_pretrained(model_name, cache_dir=models_path)
            
                logger.info(f"Loading model {model_name}")
                self.model.to(self.config.get_device())
        except:
            logger.error(f"Error loading model {model_name}")
            raise

    # TODO: Extend this to support multiple languages and sentence ending characters
    def get_translation_chunks(self, text: str) -> list[str]:
        words = text.split()
        sentence = ""
        sentences: list[str] = []
        for word in words:
            if sentence == "":
                sentence += word
                continue

            is_end = word.endswith(".")
            if len(sentence + word) > 256:
                sentences.append(sentence)
                sentence = word
            elif len(sentence + word) > 64 and is_end:
                sentence += " "+word
                sentences.append(sentence)
                sentence = ""
            else:
                sentence += " " + word

        if sentence != "":
            sentences.append(sentence)

        return sentences
    
    def interpolate_timestamps(self, words: list[str], start: float, end: float) -> list[Word]:
        aligned_words: list[Word] = []

        N = len(words)
        if N == 0:
            return []
        
        duration = (end - start) / N
        for i, word in enumerate(words):
            word_start = start + i * duration
            word_end = start + (i + 1) * duration
            aligned_words.append(
                Word(
                    text=word,
                    start=word_start,
                    end=word_end
                )
            )

        return aligned_words
    
    def translate(self, settings: TranslationRequest) -> JobResult:
        try:
            source_language = map_language_code(settings.source_language)
            target_language = map_language_code(settings.target_language)

            translated_segments: list[str] = []
            for segment in settings.transcript.segments:
                segmented_text: list[str] = self.get_translation_chunks(segment.text)
                
                translated_chunks: list[str] = []
                for chunk in segmented_text:
                    inputs = self.tokenizer(chunk,return_tensors="pt",src_lang=source_language,).to(self.device)

                    with torch.no_grad():
                        outputs = self.model.generate(**inputs, tgt_lang=target_language)

                    translated_chunk: list[str] = self.tokenizer.batch_decode(outputs, skip_special_tokens=True)
                    for segment in translated_chunk:
                        translated_chunks.append(segment)

                translated_text = " ".join(translated_chunks)
                translated_segments.append(translated_text)

            
            transcript = Transcript(text=" ".join(translated_segments), segments=[])
            for i, segment in enumerate(settings.transcript.segments):
                aligned_words = self.interpolate_timestamps(translated_segments[i].split(), segment.start, segment.end)
                transcript.segments.append(
                    Segment(
                        text=translated_segments[i],
                        start=segment.start,
                        end=segment.end,
                        words=aligned_words,
                    )
                )

            return JobResult(transcript=transcript)

        except Exception as e:
            logger.error(f"Error translating text: {e}")
            raise e
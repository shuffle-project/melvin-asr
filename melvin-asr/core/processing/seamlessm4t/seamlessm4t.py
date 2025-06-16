

import os
from typing import List

import torch
from core.config import BatchWorkerConfig
from core.logger import get_logger
from core.paths import models_path
from core.processing.alignment import alignment
from core.tqdm import disable_tqdm
from models.job import (JobResult, TranslationAlignmentMethod,
                        TranslationRequest)
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
    def get_translation_chunks(self, words: List[Word]) -> List[List[Word]]:
        sentence_words: List[Word] = [] 
        chunks: List[List[Word]] = []
        for word in words:
            sentence = " ".join([w.text.strip() for w in sentence_words])
            if len(sentence_words) == 0:
                sentence_words.append(word)
                continue

            is_end = word.text.endswith(".")
            new_sentence = sentence + " " + word.text
            if len(new_sentence) > 256:
                chunks.append(sentence_words)
                sentence_words = [word]
            elif len(new_sentence) > 64 and is_end:
                sentence_words.append(word)
                chunks.append(sentence_words)
                sentence_words = []
            else:
                sentence_words.append(word)

        if len(sentence_words) > 0:
            chunks.append(sentence_words)

        return chunks
    
    def interpolate_timestamps(self, words: List[str], start: float, end: float) -> List[Word]:
        aligned_words: List[Word] = []

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

            translated_segments: List[Segment] = []
            for segment in settings.transcript.segments:
                word_chunks = self.get_translation_chunks(segment.words)
                
                translated_and_aligned_words: List[Word] = []
                for chunk in word_chunks:
                    text = " ".join([word.text for word in chunk])
                    inputs = self.tokenizer(text, return_tensors="pt", src_lang=source_language,).to(self.device)

                    with torch.no_grad():
                        outputs = self.model.generate(**inputs, tgt_lang=target_language)

                    translated_texts: List[str] = self.tokenizer.batch_decode(outputs, skip_special_tokens=True)
                    translated_words: List[str] = []
                    for translated_text in translated_texts:
                        translated_words.extend([word.strip() for word in translated_text.split() if word.strip()])

                    timestamps = [word.start for word in chunk if word.start is not None] + [word.end for word in chunk if word.end is not None]
                    start = min(timestamps) or segment.start
                    end = max(timestamps) or segment.end

                    words = self.interpolate_timestamps(translated_words, start, end)
                    translated_and_aligned_words.extend(words)

                translated_segments.append(
                    Segment(
                        text=" ".join([word.text for word in translated_and_aligned_words]),
                        start=segment.start,
                        end=segment.end,
                        words=translated_and_aligned_words,
                    )
                )

            translated_text = " ".join([segment.text for segment in translated_segments])
            translated_transcript = Transcript(text=translated_text, segments=translated_segments)

            if settings.alignment_method == TranslationAlignmentMethod.SEGMENT_LEVEL:
                for segment in translated_transcript.segments:
                    segment.words = self.interpolate_timestamps(
                        [word.text for word in segment.words],
                        segment.start,
                        segment.end
                    )
            elif settings.alignment_method == TranslationAlignmentMethod.WORD_LEVEL:
                # This is already handled when translating chunks with seamlessm4t
                pass

            return JobResult(transcript=translated_transcript)

        except Exception as e:
            logger.error(f"Error translating text: {e}")
            raise e
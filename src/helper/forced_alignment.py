from dataclasses import dataclass
import logging
import os
from typing import List
import numpy as np

from faster_whisper import WhisperModel
from faster_whisper.audio import decode_audio, pad_or_trim
from faster_whisper.tokenizer import Tokenizer
from faster_whisper.transcribe import Segment, Word

import nltk
from src.helper.config import CONFIG

LOGGER = logging.getLogger(__name__)

# Small model -> we can download it wherever
nltk.download("punkt_tab", download_dir=os.path.join(os.getcwd(), CONFIG["model_path"], "punkt_tab"))
nltk.data.path.append(os.path.join(os.getcwd(), CONFIG["model_path"], "punkt_tab"))

TERMINATING_CHARACTERS = [".",",","!","?"]

@dataclass(frozen=True, slots=True)
class Alignment:
    words: list[str]
    word_start_times: list[float]
    word_end_times: list[float]
    sentence_duration: float


def align_sentence(tokenizer, model: WhisperModel, sentence: str, audio, cutoff_time=0.0) -> Alignment:

    features = model.feature_extractor(audio)

    content_frames = features.shape[-1]

    text_tokens = [*tokenizer.encode(sentence), tokenizer.eot]
    token_start_times = np.full(len(text_tokens), np.inf)
    token_end_times = np.full(len(text_tokens), 0.0)
    seen_tokens = 0

    for seek in range(
        0, content_frames, model.feature_extractor.nb_max_frames
    ):
        segment_size = min(
            model.feature_extractor.nb_max_frames,
            content_frames - seek,
        )
        segment = features[:, seek: seek + segment_size]
        segment = pad_or_trim(segment, model.feature_extractor.nb_max_frames)

        encoder_output = model.encode(segment)

        result = model.model.align(
            encoder_output,
            tokenizer.sot_sequence,
            [text_tokens[seen_tokens:]],
            segment_size,
        )[0]

        token_indices = np.array([pair[0] for pair in result.alignments])
        time_indices = np.array([pair[1] for pair in result.alignments])

        # Update token_start_times for newly aligned tokens
        new_seen_tokens = seen_tokens
        seen_time = seek * model.feature_extractor.time_per_frame
        for i, (local_token, local_time) in enumerate(zip(token_indices, time_indices)):
            token = seen_tokens + local_token
            new_seen_tokens = max(seen_tokens, token)
            if token < len(token_start_times):
                time = local_time / model.tokens_per_second + seen_time
                token_start_times[token] = min(token_start_times[token], time)

                # Set the end time as the next token's start time (if exists)
                if i + 1 < len(time_indices):
                    next_time = time_indices[i + 1] / model.tokens_per_second + seen_time
                else:
                    next_time = time + (1 / model.tokens_per_second)  # Approximate small gap

                token_end_times[token] = max(token_end_times[token], next_time)

        seen_tokens = new_seen_tokens
        if seen_tokens == len(text_tokens):
            break

    np.maximum.accumulate(token_end_times, out=token_end_times)
    np.minimum.accumulate(token_start_times[::-1], out=token_start_times[::-1])

    words, word_tokens = tokenizer.split_to_word_tokens(text_tokens)
    word_boundaries = np.cumsum([len(t) for t in word_tokens])

    sentence_duration = len(audio) / model.feature_extractor.sampling_rate
    word_start_times = [
    min(token_start_times[boundary - len(t)], sentence_duration)
        for boundary, t in zip(word_boundaries, word_tokens)
    ]

    word_end_times = [
        min(token_end_times[boundary - 1], sentence_duration)
        for boundary in word_boundaries
    ]

    assert len(word_start_times) == len(word_end_times)

    for i in range(len(word_start_times)):
        word_start_times[i] += cutoff_time
        word_end_times[i] += cutoff_time

    return Alignment(words, word_start_times, word_end_times, sentence_duration)

def get_segments_from_alignment(alignment: Alignment, raw_text: str) -> Segment:
    words = []
    for i in range(len(alignment.words)):
        stripped = alignment.words[i].strip()

        if len(stripped) == 0:
            continue

        if stripped in TERMINATING_CHARACTERS:
            # This swallows leading terminating characters
            # This may or may not be a problem...idc and idk
            if len(words) > 0:
                # Append to previous word
                words[-1].word += stripped
                # Take the end
                words[-1].end = max(words[-1].end, alignment.word_end_times[i])
            continue
        words.append(
            Word(
                start=alignment.word_start_times[i],
                end=alignment.word_start_times[i],
                word=stripped,
                probability=0.99,
            )
        )
        if len(words) == 0:
            continue

    return Segment(
        # Id gets tossed anyway
        id=len(raw_text),
        words=words,
        end=alignment.word_end_times[-1],
        start=alignment.word_start_times[0],
        text=raw_text,
        seek=0,
        tokens=[],
        avg_logprob=0.0,
        compression_ratio=0.0,
        no_speech_prob=0.0,
        temperature=0.0
    )


def align_ground_truth(model: WhisperModel, ground_truth: str, audio_path: str) -> List[Segment]:
    tokenizer = Tokenizer(model.hf_tokenizer, True, "transcribe", "en")

    sentences = nltk.sent_tokenize(ground_truth)
    cutoff_time = 0.0
    segments = []

    audio = decode_audio(
        audio_path,
        sampling_rate=model.feature_extractor.sampling_rate,
    )

    LOGGER.debug(f"Starting alignment for ground truth with {len(sentences)} segments.")

    while len(sentences) > 0:
        sentence = sentences.pop(0)
        res = align_sentence(tokenizer, model, sentence, audio, cutoff_time)
        # No words found
        # This should (tm) never happen
        if len(res.word_end_times) == 0:
            continue
        # Trim audio
        audio = audio[int(
            (res.word_end_times[-1] - cutoff_time) * 16_000
        ):]
        cutoff_time = res.word_end_times[-1]
        if (segment := get_segments_from_alignment(alignment=res, raw_text=sentence)) is not None:
            segments.append(segment)
    return segments

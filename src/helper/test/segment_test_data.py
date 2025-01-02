# Sample data for usage in tests

from faster_whisper.transcribe import (
    Segment,
    TranscriptionInfo,
    TranscriptionOptions,
    Word,
    VadOptions,
)

TRANSCRIPTION_OPTIONS_SAMPLE = TranscriptionOptions(
    beam_size=5,
    best_of=3,
    patience=1.5,
    length_penalty=1.0,
    repetition_penalty=1.2,
    no_repeat_ngram_size=3,
    log_prob_threshold=-1.0,
    no_speech_threshold=0.5,
    compression_ratio_threshold=2.4,
    condition_on_previous_text=True,
    prompt_reset_on_temperature=0.7,
    temperatures=[0.7, 0.9, 1.2],
    initial_prompt="Welcome to the transcription system.",
    prefix=None,
    suppress_blank=False,
    suppress_tokens=[-1, 0, 1],
    without_timestamps=True,
    max_initial_timestamp=1.0,
    word_timestamps=False,
    prepend_punctuations=".,?!",
    append_punctuations=".,?!",
    multilingual=True,
    max_new_tokens=200,
    clip_timestamps="end",
    hallucination_silence_threshold=None,
    hotwords="keyword1, keyword2",
)

TRANSCRIPTION_OPTIONS_SAMPLE_EXPECTED_DICT = {
    "beam_size": 5,
    "best_of": 3,
    "patience": 1.5,
    "length_penalty": 1.0,
    "repetition_penalty": 1.2,
    "no_repeat_ngram_size": 3,
    "log_prob_threshold": -1.0,
    "no_speech_threshold": 0.5,
    "compression_ratio_threshold": 2.4,
    "condition_on_previous_text": True,
    "prompt_reset_on_temperature": 0.7,
    "temperatures": [0.7, 0.9, 1.2],
    "initial_prompt": "Welcome to the transcription system.",
    "prefix": None,
    "suppress_blank": False,
    "suppress_tokens": [-1, 0, 1],
    "without_timestamps": True,
    "max_initial_timestamp": 1.0,
    "word_timestamps": False,
    "prepend_punctuations": ".,?!",
    "append_punctuations": ".,?!",
    "multilingual": True,
    "max_new_tokens": 200,
    "clip_timestamps": "end",
    "hallucination_silence_threshold": None,
    "hotwords": "keyword1, keyword2",
}

VAD_OPTIONS_SAMPLE: VadOptions = VadOptions()

# These values are hardcoded within the data class
VAD_OPTIONS_SAMPLE_EXPECTED_DICT = {
    "threshold": 0.5,
    "neg_threshold": None,
    "min_speech_duration_ms": 0,
    "max_speech_duration_s": float("inf"),
    "min_silence_duration_ms": 2000,
    "speech_pad_ms": 400,
}

# Mock data for testing
TRANSCRIPTION_INFO_SAMPLE = TranscriptionInfo(
    language="en",
    language_probability=0.99,
    duration=123.45,
    duration_after_vad=120.45,
    all_language_probs=None,
    transcription_options=TRANSCRIPTION_OPTIONS_SAMPLE,
    vad_options=VAD_OPTIONS_SAMPLE,
)

TRANSCRIPTION_INFO_SAMPLE_EXPECTED_DICT = {
    "language": "en",
    "language_probability": 0.99,
    "duration": 123.45,
    "duration_after_vad": 120.45,
    # "all_language_probs": None,
    "transcription_options": TRANSCRIPTION_OPTIONS_SAMPLE_EXPECTED_DICT,
    "vad_options": VAD_OPTIONS_SAMPLE_EXPECTED_DICT,
}


SEGMENTS_SAMPLE = (
    Segment(
        id=1,
        seek=0,
        start=0.0,
        end=10.0,
        text="Hello world",
        tokens=[0, 1, 2, 3],
        avg_logprob=-0.1,
        compression_ratio=1.2,
        no_speech_prob=0.01,
        words=[
            Word(0.0, 1.0, "Hello", 0.9),
            Word(1.0, 2.0, "world", 0.95),
        ],
        temperature=0.5,
    ),
    Segment(
        id=2,
        seek=1,
        start=10.0,
        end=20.0,
        text="This is a test",
        tokens=[4, 5, 6, 7],
        avg_logprob=-0.2,
        compression_ratio=1.3,
        no_speech_prob=0.02,
        words=[
            Word(10.0, 11.0, "This", 0.9),
            Word(11.0, 12.0, "is", 0.85),
            Word(12.0, 13.0, "a", 0.8),
            Word(13.0, 14.0, "test", 0.75),
        ],
        temperature=0.6,
    ),
)

SEGMENTS_SAMPLE_EXPECTED_LIST = [
    {
        "id": 1,
        "seek": 0,
        "start": 0.0,
        "end": 10.0,
        "text": "Hello world",
        "tokens": [0, 1, 2, 3],
        "temperature": 0.5,
        "avg_logprob": -0.1,
        "compression_ratio": 1.2,
        "no_speech_prob": 0.01,
        "words": [
            {"start": 0.0, "end": 1.0, "word": "Hello", "probability": 0.9},
            {"start": 1.0, "end": 2.0, "word": "world", "probability": 0.95},
        ],
    },
    {
        "id": 2,
        "seek": 1,
        "start": 10.0,
        "end": 20.0,
        "text": "This is a test",
        "tokens": [4, 5, 6, 7],
        "temperature": 0.6,
        "avg_logprob": -0.2,
        "compression_ratio": 1.3,
        "no_speech_prob": 0.02,
        "words": [
            {"start": 10.0, "end": 11.0, "word": "This", "probability": 0.9},
            {"start": 11.0, "end": 12.0, "word": "is", "probability": 0.85},
            {"start": 12.0, "end": 13.0, "word": "a", "probability": 0.8},
            {"start": 13.0, "end": 14.0, "word": "test", "probability": 0.75},
        ],
    },
]

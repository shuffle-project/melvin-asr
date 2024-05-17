import unittest
from src.transcription.segment_info_parser_streaming import (
    parse_segments_and_info_to_dict, 
    parse_transcription_info_to_dict, 
    parse_segment_words_to_dict, 
    parse_transcription_segments_to_dict
)

from dataclasses import dataclass, field
from typing import List, Tuple, Optional

@dataclass
class TranscriptionOptions:
    beam_size: int
    best_of: int
    patience: float
    length_penalty: float
    repetition_penalty: float
    no_repeat_ngram_size: int
    log_prob_threshold: float
    no_speech_threshold: float
    compression_ratio_threshold: float
    condition_on_previous_text: bool
    prompt_reset_on_temperature: float
    temperatures: List[float]
    initial_prompt: Optional[str]
    prefix: Optional[str]
    suppress_blank: bool
    suppress_tokens: List[int]
    without_timestamps: bool
    max_initial_timestamp: float
    word_timestamps: bool
    prepend_punctuations: str
    append_punctuations: str
    max_new_tokens: Optional[int]
    clip_timestamps: str
    hallucination_silence_threshold: Optional[float]

@dataclass
class TranscriptionInfo:
    language: str
    language_probability: float
    duration: float
    duration_after_vad: float
    all_language_probs: List[Tuple[str, float]]
    transcription_options: TranscriptionOptions
    vad_options: Optional[object]  # Replace with actual type if known

class TestSegmentInfoParserStreaming(unittest.TestCase):

    def test_parse_segments_and_info_to_dict(self):
        segments = [("segment1", 0.5, 1.0), ("segment2", 1.5, 2.0)]
        info = {"transcription_id": "12345", "duration": 3.0}
        expected_result = {
            "segments": [
                {"segment": "segment1", "start_time": 0.5, "end_time": 1.0},
                {"segment": "segment2", "start_time": 1.5, "end_time": 2.0}
            ],
            "transcription_id": "12345",
            "duration": 3.0
        }
        result = parse_segments_and_info_to_dict(segments, info)
        self.assertEqual(result, expected_result)

    def test_parse_transcription_info_to_dict(self):
        info = {"transcription_id": "12345", "duration": 3.0}
        expected_result = {
            "transcription_id": "12345",
            "duration": 3.0
        }
        result = parse_transcription_info_to_dict(info)
        self.assertEqual(result, expected_result)
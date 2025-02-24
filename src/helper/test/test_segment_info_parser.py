"""This File contains tests for the parser functions."""

import pytest
from faster_whisper.transcribe import (
    TranscriptionInfo,
    Word,
)

from src.helper.segment_info_parser import (
    parse_segment_words_to_dict,
    parse_segments_and_info_to_dict,
    parse_transcription_info_to_dict,
    parse_transcription_segments_to_dict,
)

from src.helper.test.segment_test_data import (
    SEGMENTS_SAMPLE,
    SEGMENTS_SAMPLE_EXPECTED_LIST,
    TRANSCRIPTION_INFO_SAMPLE,
    TRANSCRIPTION_INFO_SAMPLE_EXPECTED_DICT,
)


def test_parse_transcription_info_to_dict():
    """Tests the parse_transcription_info_to_dict function."""
    assert (
        parse_transcription_info_to_dict(TRANSCRIPTION_INFO_SAMPLE)
        == TRANSCRIPTION_INFO_SAMPLE_EXPECTED_DICT
    )


def test_parse_segment_words_to_dict():
    """Tests the parse_segment_words_to_dict function."""
    words_array = [
        Word(0.0, 1.0, "Hello", 0.9),
        Word(1.0, 2.0, "world", 0.95),
    ]
    expected_word_dict = [
        {"start": 0.0, "end": 1.0, "word": "Hello", "probability": 0.9},
        {"start": 1.0, "end": 2.0, "word": "world", "probability": 0.95},
    ]

    assert parse_segment_words_to_dict(words_array) == expected_word_dict


def test_parse_transcription_segments_to_dict():
    """Tests the parse_transcription_segments_to_dict function."""

    assert (
        parse_transcription_segments_to_dict(SEGMENTS_SAMPLE)
        == SEGMENTS_SAMPLE_EXPECTED_LIST
    )


def test_parse_segments_and_info_to_dict():
    """Tests the parse_segments_and_info_to_dict function."""
    expected_combined_dict = {
        "segments": SEGMENTS_SAMPLE_EXPECTED_LIST,
        "info": TRANSCRIPTION_INFO_SAMPLE_EXPECTED_DICT,
    }

    assert (
        parse_segments_and_info_to_dict(SEGMENTS_SAMPLE, TRANSCRIPTION_INFO_SAMPLE)
        == expected_combined_dict
    )


def test_parse_segment_words_to_dict_none():
    """Tests the parse_segment_words_to_dict function with None as input."""
    words_array = None
    expected_word_dict = []
    assert parse_segment_words_to_dict(words_array) == expected_word_dict


def test_parse_segment_words_to_dict_not_string():
    """Tests the parse_segment_words_to_dict function with non-string word."""
    words_array = [
        Word(0.0, 1.0, None, 0.9),
        Word(1.0, 2.0, 123, 0.95),
        Word(2.0, 3.0, "test", 0.97),
    ]
    expected_word_dict = [
        {"start": 2.0, "end": 3.0, "word": "test", "probability": 0.97},
    ]
    assert parse_segment_words_to_dict(words_array) == expected_word_dict


def test_parse_transcription_info_to_dict_with_empty_options():
    """Tests the parse_transcription_info_to_dict function with empty lists for options."""
    mock_info = TranscriptionInfo(
        language="fr",
        language_probability=0.90,
        duration=100.0,
        duration_after_vad=95.0,
        all_language_probs=None,
        transcription_options=None,
        vad_options=None,
    )

    expected_info_dict = {
        "language": "fr",
        "language_probability": 0.90,
        "duration": 100.0,
        "duration_after_vad": 95.0,
        "transcription_options": None,
        "vad_options": None,
    }

    assert parse_transcription_info_to_dict(mock_info) == expected_info_dict


if __name__ == "__main__":
    pytest.main()

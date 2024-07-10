"""This File contains tests for the parser functions."""
import pytest

from src.helper.segment_info_parser import (
    parse_segments_and_info_to_dict,
    parse_transcription_info_to_dict,
    parse_segment_words_to_dict,
    parse_transcription_segments_to_dict,
)

# Mock data for testing
mock_info = type(
    "MockInfo",
    (object,),
    {
        "language": "en",
        "language_probability": 0.99,
        "duration": 123.45,
        "duration_after_vad": 120.45,
        "transcription_options": {"option1": "value1"},
        "vad_options": {"option1": "value1"},
    },
)()

mock_segments = (
    [
        1,
        0,
        0.0,
        10.0,
        "Hello world",
        [0, 1, 2, 3],
        0.5,
        -0.1,
        1.2,
        0.01,
        [
            [0.0, 1.0, "Hello", 0.9],
            [1.0, 2.0, "world", 0.95],
        ],
    ],
    [
        2,
        1,
        10.0,
        20.0,
        "This is a test",
        [4, 5, 6, 7],
        0.6,
        -0.2,
        1.3,
        0.02,
        [
            [10.0, 11.0, "This", 0.9],
            [11.0, 12.0, "is", 0.85],
            [12.0, 13.0, "a", 0.8],
            [13.0, 14.0, "test", 0.75],
        ],
    ],
)


def test_parse_transcription_info_to_dict():
    """Tests the parse_transcription_info_to_dict function."""
    expected_info_dict = {
        "language": "en",
        "language_probability": 0.99,
        "duration": 123.45,
        "duration_after_vad": 120.45,
        "transcription_options": {"option1": "value1"},
        "vad_options": {"option1": "value1"},
    }

    assert parse_transcription_info_to_dict(mock_info) == expected_info_dict


def test_parse_segment_words_to_dict():
    """Tests the parse_segment_words_to_dict function."""
    words_array = [
        [0.0, 1.0, "Hello", 0.9],
        [1.0, 2.0, "world", 0.95],
    ]
    expected_word_dict = [
        {"start": 0.0, "end": 1.0, "word": "Hello", "probability": 0.9},
        {"start": 1.0, "end": 2.0, "word": "world", "probability": 0.95},
    ]

    assert parse_segment_words_to_dict(words_array) == expected_word_dict


def test_parse_transcription_segments_to_dict():
    """Tests the parse_transcription_segments_to_dict function."""
    segments = [
        [
            1,
            0,
            0.0,
            10.0,
            "Hello world",
            [0, 1, 2, 3],
            0.5,
            -0.1,
            1.2,
            0.01,
            [
                [0.0, 1.0, "Hello", 0.9],
                [1.0, 2.0, "world", 0.95],
            ],
        ],
        [
            2,
            1,
            10.0,
            20.0,
            "This is a test",
            [4, 5, 6, 7],
            0.6,
            -0.2,
            1.3,
            0.02,
            [
                [10.0, 11.0, "This", 0.9],
                [11.0, 12.0, "is", 0.85],
                [12.0, 13.0, "a", 0.8],
                [13.0, 14.0, "test", 0.75],
            ],
        ],
    ]

    expected_segments_dict = [
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

    assert parse_transcription_segments_to_dict(segments) == expected_segments_dict


def test_parse_segments_and_info_to_dict():
    """Tests the parse_segments_and_info_to_dict function."""
    expected_combined_dict = {
        "segments": [
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
        ],
        "info": {
            "language": "en",
            "language_probability": 0.99,
            "duration": 123.45,
            "duration_after_vad": 120.45,
            "transcription_options": {"option1": "value1"},
            "vad_options": {"option1": "value1"},
        },
    }

    assert (
        parse_segments_and_info_to_dict(mock_segments, mock_info)
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
        [0.0, 1.0, None, 0.9],
        [1.0, 2.0, 123, 0.95],
        [2.0, 3.0, "test", 0.97],
    ]
    expected_word_dict = [
        {"start": 2.0, "end": 3.0, "word": "test", "probability": 0.97},
    ]
    assert parse_segment_words_to_dict(words_array) == expected_word_dict

# Mock class for testing parsing from a class
class MockInfo:
    def __init__(self, language, language_probability, duration, duration_after_vad, transcription_options, vad_options):
        self.language = language
        self.language_probability = language_probability
        self.duration = duration
        self.duration_after_vad = duration_after_vad
        self.transcription_options = transcription_options
        self.vad_options = vad_options

def test_parse_transcription_info_to_dict_with_infinity_and_nan():
    """Tests the parse_transcription_info_to_dict function with infinity and NaN values in options."""
    mock_info = MockInfo(
        language="en",
        language_probability=0.99,
        duration=123.45,
        duration_after_vad=120.45,
        transcription_options=[0.5, float('inf'), float('-inf'), float('nan')],
        vad_options=[0.5, 250, float('inf'), 2000, 1024, 400, float('nan')]
    )

    expected_info_dict = {
        "language": "en",
        "language_probability": 0.99,
        "duration": 123.45,
        "duration_after_vad": 120.45,
        "transcription_options": [0.5, "Infinity", "-Infinity", "NaN"],
        "vad_options": [0.5, 250, "Infinity", 2000, 1024, 400, "NaN"]
    }

    assert parse_transcription_info_to_dict(mock_info) == expected_info_dict

def test_parse_transcription_info_to_dict_without_special_values():
    """Tests the parse_transcription_info_to_dict function without any special values."""
    mock_info = MockInfo(
        language="en",
        language_probability=0.95,
        duration=150.0,
        duration_after_vad=145.0,
        transcription_options=[0.5, 1.0, 2.0],
        vad_options=[0.5, 250, 300, 2000, 1024, 400]
    )

    expected_info_dict = {
        "language": "en",
        "language_probability": 0.95,
        "duration": 150.0,
        "duration_after_vad": 145.0,
        "transcription_options": [0.5, 1.0, 2.0],
        "vad_options": [0.5, 250, 300, 2000, 1024, 400]
    }

    assert parse_transcription_info_to_dict(mock_info) == expected_info_dict

def test_parse_transcription_info_to_dict_with_empty_options():
    """Tests the parse_transcription_info_to_dict function with empty lists for options."""
    mock_info = MockInfo(
        language="fr",
        language_probability=0.90,
        duration=100.0,
        duration_after_vad=95.0,
        transcription_options=[],
        vad_options=[]
    )

    expected_info_dict = {
        "language": "fr",
        "language_probability": 0.90,
        "duration": 100.0,
        "duration_after_vad": 95.0,
        "transcription_options": [],
        "vad_options": []
    }

    assert parse_transcription_info_to_dict(mock_info) == expected_info_dict

def test_parse_transcription_info_to_dict_with_non_list_options():
    """Tests the parse_transcription_info_to_dict function with non-list options."""
    mock_info = MockInfo(
        language="es",
        language_probability=0.88,
        duration=110.0,
        duration_after_vad=105.0,
        transcription_options="not_a_list",
        vad_options="not_a_list"
    )

    expected_info_dict = {
        "language": "es",
        "language_probability": 0.88,
        "duration": 110.0,
        "duration_after_vad": 105.0,
        "transcription_options": "not_a_list",
        "vad_options": "not_a_list"
    }

    assert parse_transcription_info_to_dict(mock_info) == expected_info_dict

if __name__ == "__main__":
    pytest.main()

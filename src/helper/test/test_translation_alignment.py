from logging import log

import pytest
from fastapi import HTTPException

from src.helper.align_translation_segments import Transcript, align_segments


def test_align_segments_basic():
    original_transcript = Transcript(
        text="Hello world",
        segments=[
            {
                "text": "Hello world",
                "start": 0.0,
                "end": 2.0,
                "words": [
                    {"text": "Hello", "start": 0.0, "end": 1.0, "probability": 0.9},
                    {"text": "world", "start": 1.0, "end": 2.0, "probability": 0.95},
                ],
            }
        ],
    )

    translated_text = "Hallo Welt"
    result = align_segments(original_transcript, translated_text)

    assert result["text"] == translated_text
    assert result["segments"][0]["words"][0]["text"] == "Hallo"
    assert result["segments"][0]["words"][1]["text"] == "Welt"


def test_align_segments_empty_translation():
    original_transcript = Transcript(
        text="Hello world",
        segments=[
            {
                "text": "Hello world",
                "start": 0.0,
                "end": 2.0,
                "words": [
                    {"text": "Hello", "start": 0.0, "end": 1.0, "probability": 0.9},
                    {"text": "world", "start": 1.0, "end": 2.0, "probability": 0.95},
                ],
            }
        ],
    )

    with pytest.raises(HTTPException) as exc_info:
        align_segments(original_transcript, "")
    assert exc_info.value.status_code == 400
    assert (
        "Alignment not possible without translation or transcript"
        in exc_info.value.detail
    )


def test_align_segments_empty_transcript():
    original_transcript = Transcript(text="", segments=[])
    with pytest.raises(HTTPException) as exc_info:
        align_segments(original_transcript, "Hallo Welt")
    assert exc_info.value.status_code == 400
    assert (
        "Alignment not possible without translation or transcript"
        in exc_info.value.detail
    )


def test_align_segments_mismatched_length():
    start = 0.0
    end = 6.0
    original_transcript = Transcript(
        text="Hello world this is a test",
        segments=[
            {
                "text": "Hello world this is a test",
                "start": start,
                "end": end,
                "words": [
                    {"text": "Hello", "start": start, "end": 1.0, "probability": 0.9},
                    {"text": "world", "start": 1.0, "end": 2.0, "probability": 0.95},
                    {"text": "this", "start": 2.0, "end": 3.0, "probability": 0.8},
                    {"text": "is", "start": 3.0, "end": 4.0, "probability": 0.85},
                    {"text": "a", "start": 4.0, "end": 5.0, "probability": 0.9},
                    {"text": "test", "start": 5.0, "end": end, "probability": 0.95},
                ],
            }
        ],
    )

    translated_text = "Hallo Welt Test"
    result = align_segments(original_transcript, translated_text)

    assert result["text"] == translated_text
    assert result["segments"][0]["words"][0]["text"] == "Hallo"
    assert result["segments"][0]["words"][1]["text"] == "Welt"
    assert result["segments"][0]["words"][2]["text"] == "Test"

    assert result["segments"][0]["words"][0]["start"] == start
    assert result["segments"][0]["words"][1]["start"] >= start + end / 3
    assert result["segments"][0]["words"][1]["end"] <= end - end / 3
    assert result["segments"][0]["words"][2]["end"] == end


if __name__ == "__main__":
    pytest.main()

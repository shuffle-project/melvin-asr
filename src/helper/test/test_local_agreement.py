from typing import List
from faster_whisper.transcribe import Word
import pytest

from src.helper.local_agreement import LocalAgreement

EXAMPLE_SENTENCE = ["This", "is", "a", "test", "sentence", "for", "local", "agreement"]
EXAMPLE_MULTIPLE_SENTENCES = ["This", "is", "a", "test.", "This", "is", "sadly", "unfinished"]

def test_creation():
    testable = LocalAgreement()
    assert testable.get_confirmed_length() == 0
    assert testable.contains_has_sentence_end() is False

def test_merge():
    partial1: List[Word] = [
        Word(1.0 * i, 1.0 * (i + 1) - 0.1, EXAMPLE_SENTENCE[i], 0.9) for i in range(2)
    ] + [Word(1.0 * 2, 1.0 * (3) - 0.1, "Error", 0.1)]
    partial2: List[Word] = [
        Word(1.0 * i, 1.0 * (i + 1) - 0.1, EXAMPLE_SENTENCE[i], 0.9) for i in range(4)
    ]
    partial3: List[Word] = [
        Word(1.0 * i, 1.0 * (i + 1) - 0.1, EXAMPLE_SENTENCE[i], 0.9)
        for i in range(len(EXAMPLE_SENTENCE))
    ]

    testable = LocalAgreement()
    testable.merge(partial1)
    assert len(testable.get_confirmed_text()) == 0
    testable.merge(partial2)
    # should stop here because it is not sure if the next word is Error or not
    assert testable.get_confirmed_text() == "This is"
    testable.merge(partial3)
    # Now it should be clear the Error was...well an error?
    assert testable.get_confirmed_text() == "This is a test"
    assert testable.contains_has_sentence_end() is False

def test_merge_with_sentence_end():
    partial1: List[Word] = [
        Word(1.0 * i, 1.0 * (i + 1) - 0.1, EXAMPLE_MULTIPLE_SENTENCES[i], 0.9) for i in range(2)
    ] + [Word(1.0 * 2, 1.0 * (3) - 0.1, "Error", 0.1)]
    partial2: List[Word] = [
        Word(1.0 * i, 1.0 * (i + 1) - 0.1, EXAMPLE_MULTIPLE_SENTENCES[i], 0.9) for i in range(4)
    ]
    partial3: List[Word] = [
        Word(1.0 * i, 1.0 * (i + 1) - 0.1, EXAMPLE_MULTIPLE_SENTENCES[i], 0.9)
        for i in range(len(EXAMPLE_MULTIPLE_SENTENCES))
    ]

    testable = LocalAgreement()
    testable.merge(partial1)
    assert len(testable.get_confirmed_text()) == 0
    assert testable.contains_has_sentence_end() is False
    testable.merge(partial2)

    testable.merge(partial3)
    assert testable.get_confirmed_text() == "This is a test."
    assert testable.contains_has_sentence_end() is True

def test_clear():
    partial: List[Word] = [
        Word(1.0 * i, 1.0 * (i + 1) - 0.1, EXAMPLE_SENTENCE[i], 0.9)
        for i in range(len(EXAMPLE_SENTENCE))
    ]

    testable = LocalAgreement()
    assert len(testable.get_confirmed_text()) == 0
    testable.merge(partial)
    testable.merge(partial)
    assert (
        testable.get_confirmed_text() == "This is a test sentence for local agreement"
    )
    testable.clear()
    assert len(testable.get_confirmed_text()) == 0

def test_flush_total():
    testable = LocalAgreement()

    testable.confirmed = [
        Word(1.0 * i, 1.0 * (i + 1) - 0.1, EXAMPLE_SENTENCE[i], 0.9)
        for i in range(len(EXAMPLE_SENTENCE))
    ]

    assert testable.get_confirmed_length() == len(EXAMPLE_SENTENCE)
    assert testable.contains_has_sentence_end() is False

    assert testable.flush_confirmed() == [
        Word(1.0 * i, 1.0 * (i + 1) - 0.1, EXAMPLE_SENTENCE[i], 0.9)
        for i in range(len(EXAMPLE_SENTENCE))
    ]

    assert testable.get_confirmed_text() == ""
    assert testable.get_confirmed_length() == 0


def test_flush_partial_by_index():
    testable = LocalAgreement()

    testable.confirmed = [
        Word(1.0 * i, 1.0 * (i + 1) - 0.1, EXAMPLE_SENTENCE[i], 0.9)
        for i in range(len(EXAMPLE_SENTENCE))
    ]

    assert testable.get_confirmed_length() == len(EXAMPLE_SENTENCE)
    assert testable.contains_has_sentence_end() is False

    assert testable.flush_confirmed(3) == [
        Word(1.0 * i, 1.0 * (i + 1) - 0.1, EXAMPLE_SENTENCE[i], 0.9) for i in range(3)
    ]

    assert testable.get_confirmed_length() == len(EXAMPLE_SENTENCE) - 3
    assert testable.get_confirmed_text() == "test sentence for local agreement"

def test_flush_partial_by_sentence_end():
    testable = LocalAgreement()

    testable.confirmed = [
        Word(1.0 * i, 1.0 * (i + 1) - 0.1, EXAMPLE_MULTIPLE_SENTENCES[i], 0.9)
        for i in range(len(EXAMPLE_MULTIPLE_SENTENCES))
    ]

    assert testable.get_confirmed_length() == len(EXAMPLE_MULTIPLE_SENTENCES)
    assert testable.contains_has_sentence_end() is False

    assert testable.flush_at_sentence_end() == [
        Word(1.0 * i, 1.0 * (i + 1) - 0.1, EXAMPLE_MULTIPLE_SENTENCES[i], 0.9) for i in range(4)
    ]

    assert testable.get_confirmed_text() == "This is sadly unfinished"


if __name__ == "__main__":
    pytest.main()

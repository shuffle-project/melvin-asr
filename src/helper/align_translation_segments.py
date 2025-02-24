import json
import logging
import os
from typing import List

from fastapi import HTTPException
from typing_extensions import TypedDict


class Word(TypedDict):
    text: str
    start: float
    end: float
    probability: float


class Segment(TypedDict):
    text: str
    start: float
    end: float
    words: List[Word]


class Transcript(TypedDict):
    text: str
    segments: List[Segment]


LOGGER = logging.getLogger(__name__)


def align_segments(original_transcript: Transcript, translated_text: str) -> Transcript:
    """
    Perform a proportional distribution alignment of `translated_text` onto the
    words in `original_transcript`.

    Returns a *new* Transcript with the same structure, but each Word's `text`
    replaced by the aligned translated tokens (joined by spaces).

    If an original word has no overlap with any translated token, its text becomes "".
    If multiple translated tokens map to the same original word, they are combined.
    """

    # Gather *all* original words into a flat list (tracking where they came from).
    flat_words = []
    for segment_index, seg in enumerate(original_transcript["segments"]):
        for word_index, w in enumerate(seg["words"]):
            flat_words.append((segment_index, word_index, w))

    if not flat_words or not translated_text.strip():
        raise HTTPException(
            status_code=400,
            detail="Alignment not possible without translation or transcript",
        )

    translated_tokens = translated_text.split()

    N = len(flat_words)
    M = len(translated_tokens)

    # We'll store, for each original word i, a list of translated tokens assigned.
    aligned_tokens_per_word = [[] for _ in range(N)]

    # Walk through original words (i) and translated tokens (j) in parallel.
    i = 0  # index for original words
    j = 0  # index for translated tokens

    # A function to get the fraction range of i-th original word => [i/N, (i+1)/N)
    def original_range(i):
        return (i / N, (i + 1) / N)

    # A function to get the fraction range of j-th translated token => [j/M, (j+1)/M)
    def translated_range(j):
        return (j / M, (j + 1) / M)

    while i < N and j < M:
        i_start, i_end = original_range(i)
        j_start, j_end = translated_range(j)

        # Overlap is the intersection of [i_start, i_end) and [j_start, j_end)
        overlap_start = max(i_start, j_start)
        overlap_end = min(i_end, j_end)
        overlap = overlap_end - overlap_start

        if overlap > 0:
            aligned_tokens_per_word[i].append(translated_tokens[j])
            j += 1

        # Whichever fraction ends first, we advance that pointer
        if i_end <= j_end:
            i += 1
        if i_end >= j_end and overlap <= 0:
            j += 1

    new_transcript = Transcript(text=translated_text, segments=[])

    # Initialize new segments
    for seg in original_transcript["segments"]:
        new_segment = Segment(text="", start=seg["start"], end=seg["end"], words=[])
        new_transcript["segments"].append(new_segment)

    # Fill words
    for idx, (segment_index, word_index, old_word) in enumerate(flat_words):
        new_word_text = " ".join(aligned_tokens_per_word[idx])
        new_word = Word(
            text=new_word_text,
            start=old_word["start"],
            end=old_word["end"],
            probability=old_word["probability"],
        )
        new_transcript["segments"][segment_index]["words"].append(new_word)

    # Fix segment texts
    for seg in new_transcript["segments"]:
        seg["text"] = " ".join(word["text"] for word in seg["words"] if word["text"])

    return new_transcript


def load_status_file(file_path: str) -> dict:
    with open(file_path, "r") as file:
        return json.load(file)


# THIS IS FOR TESTING
if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Construct the relative path to the JSON file
    status_file_path = os.path.join(
        script_dir, "../../data/status/ce0cf48e-6610-4996-9790-fbb77ed77e9b.json"
    )

    # Load the status file
    status_data = load_status_file(status_file_path)

    result = align_segments(
        status_data["transcript"],
        "Deshalb, liebe Mitbürgerinnen und Mitbürger, fragen Sie nicht, was Ihr Land für Sie tun kann, sondern was Sie für Ihr Land tun können.",
    )

    print(json.dumps(result, indent=4, ensure_ascii=False))

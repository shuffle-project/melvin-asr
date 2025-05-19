from core.logger import get_logger
from models.transcript import Segment, Transcript, Word

logger = get_logger(__name__)

def align_by_time(start: float, end: float, text: str) -> Transcript:
    fake_transcript = Transcript(
        text="A Z",
        segments=[
            Segment(
                text="A Z",
                start=start,
                end=end,
                words=[
                    Word(text="A", start=start, end=start, probability=1.0),
                    Word(text="Z", start=end, end=end, probability=1.0),
                ],
            )
        ],
    )

    return align_by_transcript(fake_transcript, text)

def align_by_transcript(transcript_with_timings: Transcript, transcript: Transcript) -> Transcript:
    """
    Perform a proportional distribution alignment of `translated_text` onto the
    words in `original_transcript`.

    Returns a *new* Transcript with the same structure, but each Word's `text`
    replaced by the aligned translated words (joined by spaces).

    If an original word has no overlap with any translated word, its text becomes "".
    If multiple translated words map to the same original word, they are combined.
    """

    try:
        # Gather *all* original words into a flat list (tracking where they came from).
        flat_words: list[tuple[int, int, Word]] = []
        for segment_index, seg in enumerate(transcript_with_timings.segments):
            for word_index, w in enumerate(seg.words):
                flat_words.append((segment_index, word_index, w))

        translated_words = text.split()

        N = len(flat_words)
        M = len(translated_words)

        # We'll store, for each original word i, a list of translated words assigned.
        aligned_words_per_word = [[] for _ in range(N)]

        # Walk through original words (i) and translated words (j) in parallel.
        i = 0  # index for original words
        j = 0  # index for translated words

        # A function to get the fraction range of i-th original word => [i/N, (i+1)/N)
        def original_range(i):
            return (i / N, (i + 1) / N)

        # A function to get the fraction range of j-th translated word => [j/M, (j+1)/M)
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
                aligned_words_per_word[i].append(translated_words[j])
                j += 1

            # Whichever fraction ends first, we advance that pointer
            if i_end <= j_end:
                i += 1
            if i_end >= j_end and overlap <= 0:
                j += 1

        new_transcript = Transcript(text=text, segments=[])

        # Initialize new segments
        for seg in transcript_with_timings.segments:
            new_segment = Segment(text="", start=seg.start, end=seg.end, words=[])
            new_transcript.segments.append(new_segment)

        # Fill words
        pending_start_time = None
        for idx, (segment_index, word_index, old_word) in enumerate(flat_words):
            new_word_text = " ".join(aligned_words_per_word[idx])

            # If first word is empty, store its start time for the next word
            if (
                not new_word_text
                and len(new_transcript.segments[segment_index].words) == 0
            ):
                pending_start_time = old_word.start
                continue

            # if word exists prior, replace prior end with this end
            if not new_word_text and word_index > 0:
                new_transcript.segments[segment_index].words[-1].end = old_word.end
                continue

            new_word = Word(
                text=new_word_text,
                start=pending_start_time if pending_start_time else old_word.start,
                end=old_word.end,
                probability=old_word.probability,
            )
            pending_start_time = None  # Reset after applying
            new_transcript.segments[segment_index].words.append(new_word)

        # Update segment texts
        for seg in new_transcript.segments:
            seg.text = " ".join(word.text for word in seg.words if word.text)

        # Squash segments in place (back to front)
        i = len(new_transcript.segments) - 1  # Start from the end
        while i > 0:
            if not new_transcript.segments[i].text:
                new_transcript.segments[i - 1].end = new_transcript.segments[i].end
                del new_transcript.segments[i]
            i -= 1
        
        return new_transcript
    except Exception as e:
        print(e)
        logger.info(f"Error in align_by_transcript: {e}")
        raise
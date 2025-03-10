from dataclasses import dataclass
import numpy as np
import time

from faster_whisper import WhisperModel
from faster_whisper.audio import decode_audio, pad_or_trim
from faster_whisper.tokenizer import Tokenizer
from faster_whisper.transcribe import Segment, Word

import nltk
import ssl

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

nltk.download("punkt_tab")

transcription = 'And so, my fellow Americans: ask not what your country can do for you — ask what you can do for your country.'
file_path = './example.wav'

TERMINATING_CHARACTERS = [".",",","!","?"]

class ForcedAlignment:
    def __init__(self):
        self.whisper = WhisperModel("large-v3-turbo")
        self.tokenizer = Tokenizer(self.whisper.hf_tokenizer, True, "transcribe", "en")

    def align_sentence(self, sentence, audio_path, cutoff_time=0.0):
        @dataclass(frozen=True, slots=True)
        class Alignment:
            words: list[str]
            word_start_times: list[float]
            word_end_times: list[float]
            sentence_duration: float

        print(f"Aligning '{sentence[:25]}...' with {audio_path}")

        audio = decode_audio(
            audio_path,
            sampling_rate=self.whisper.feature_extractor.sampling_rate,
        )

        audio = audio[int(cutoff_time * 16_000):]

        features = self.whisper.feature_extractor(audio)

        content_frames = features.shape[-1]

        text_tokens = [*self.tokenizer.encode(sentence), self.tokenizer.eot]
        token_start_times = np.full(len(text_tokens), np.inf)
        token_end_times = np.full(len(text_tokens), 0.0)
        seen_tokens = 0

        for seek in range(
                0, content_frames, self.whisper.feature_extractor.nb_max_frames
        ):
            segment_size = min(
                self.whisper.feature_extractor.nb_max_frames,
                content_frames - seek,
            )
            segment = features[:, seek: seek + segment_size]
            segment = pad_or_trim(segment, self.whisper.feature_extractor.nb_max_frames)

            encoder_output = self.whisper.encode(segment)

            print(f"{self.whisper}")

            result = self.whisper.model.align(
                encoder_output,
                self.tokenizer.sot_sequence,
                [text_tokens[seen_tokens:]],
                segment_size,
            )[0]

            token_indices = np.array([pair[0] for pair in result.alignments])
            time_indices = np.array([pair[1] for pair in result.alignments])

            # Update token_start_times for newly aligned tokens
            new_seen_tokens = seen_tokens
            seen_time = seek * self.whisper.feature_extractor.time_per_frame
            for i, (local_token, local_time) in enumerate(zip(token_indices, time_indices)):
                token = seen_tokens + local_token
                new_seen_tokens = max(seen_tokens, token)
                if token < len(token_start_times):
                    time = local_time / self.whisper.tokens_per_second + seen_time
                    token_start_times[token] = min(token_start_times[token], time)

                    # Set the end time as the next token's start time (if exists)
                    if i + 1 < len(time_indices):
                        next_time = time_indices[i + 1] / self.whisper.tokens_per_second + seen_time
                    else:
                        next_time = time + (1 / self.whisper.tokens_per_second)  # Approximate small gap

                    token_end_times[token] = max(token_end_times[token], next_time)

            seen_tokens = new_seen_tokens
            if seen_tokens == len(text_tokens):
                break

        np.maximum.accumulate(token_end_times, out=token_end_times)
        np.minimum.accumulate(token_start_times[::-1], out=token_start_times[::-1])

        words, word_tokens = self.tokenizer.split_to_word_tokens(text_tokens)
        word_boundaries = np.cumsum([len(t) for t in word_tokens])

        sentence_duration = len(audio) / self.whisper.feature_extractor.sampling_rate
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

    def run(self):
        sentences = nltk.sent_tokenize(transcription)
        start_time = time.time()
        cutoff_time = 0.0
        segments = []
        while len(sentences) > 0:
            print(f"{len(sentences)} left...")
            sentence = sentences.pop(0)
            res = self.align_sentence(sentence, file_path, cutoff_time)
            cutoff_time = res.word_end_times[-1]
            words = []
            for i in range(len(res.words)):
                stripped = res.words[i].strip()
                if len(stripped) == 0:
                    continue

                if stripped in TERMINATING_CHARACTERS:
                    if len(words) > 0:
                        # Append to previous word
                        words[-1].word += stripped
                        # Take the end
                        words[-1].end = max(words[-1].end, res.word_end_times[i])
                    continue
                words.append(
                    Word(
                        start=res.word_start_times[i],
                        end=res.word_start_times[i],
                        word=stripped,
                        probability=0.99,
                    )
                )
            if len(words) == 0:
                continue

            segments.append(Segment(
                id=len(sentences),
                words=words,
                end=res.word_end_times[-1],
                start=res.word_start_times[0],
                text=sentence,
                seek=0,
                tokens=[],
                avg_logprob=0.0,
                compression_ratio=0.0,
                no_speech_prob=0.0,
                temperature=0.0
            ))
            print(segments[-1])
        end_time = time.time()
        print("Time taken:", (end_time - start_time))
        return segments

if __name__ == "__main__":
    aligner = ForcedAlignment()
    aligner.run()

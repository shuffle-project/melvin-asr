from dataclasses import dataclass
import numpy as np

from faster_whisper import download_model, WhisperModel
from faster_whisper.audio import decode_audio, pad_or_trim
from faster_whisper.tokenizer import Tokenizer

transcription = 'And so, my fellow Americans: ask not what your country can do for you — ask what you can do for your country.'
file_path = './example.wav'

class ForcedAlignment:
    def __init__(self):
        self.whisper = WhisperModel("large-v3-turbo")
        self.tokenizer = Tokenizer(self.whisper.hf_tokenizer, True, "transcribe", "en")

    def align_sentence(self, sentence, audio_path):
        @dataclass(frozen=True, slots=True)
        class Alignment:
            words: list[str]
            word_start_times: list[float]
            sentence_duration: float

        print(f"Aligning '{sentence[:50]}...' with {audio_path}")

        audio = decode_audio(
            audio_path,
            sampling_rate=self.whisper.feature_extractor.sampling_rate,
        )
        features = self.whisper.feature_extractor(audio)

        content_frames = features.shape[-1]

        text_tokens = [*self.tokenizer.encode(sentence), self.tokenizer.eot]
        token_start_times = np.full(len(text_tokens), np.inf)
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
            for local_token, local_time in zip(token_indices, time_indices):
                token = seen_tokens + local_token
                new_seen_tokens = max(seen_tokens, token)
                if token < len(token_start_times):
                    time = local_time / self.whisper.tokens_per_second + seen_time
                    token_start_times[token] = min(token_start_times[token], time)

            seen_tokens = new_seen_tokens
            if seen_tokens == len(text_tokens):
                break

        np.minimum.accumulate(token_start_times[::-1], out=token_start_times[::-1])

        # words, word_tokens = self.tokenizer.split_tokens_on_unicode(text_tokens)
        words, word_tokens = self.tokenizer.split_to_word_tokens(text_tokens)
        word_boundaries = np.cumsum([len(t) for t in word_tokens])

        sentence_duration = len(audio) / self.whisper.feature_extractor.sampling_rate
        word_start_times = [
            min(token_start_times[boundary - len(t)], sentence_duration)
            for boundary, t in zip(word_boundaries, word_tokens)
        ]

        print("words", words)
        print("word_start_times", word_start_times)
        print("sentence_duration", sentence_duration)

        return Alignment(words, word_start_times, sentence_duration)

    def run(self):
        self.align_sentence(transcription,file_path)

if __name__ == "__main__":
    aligner = ForcedAlignment()
    aligner.run()
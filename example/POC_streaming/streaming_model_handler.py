import io
import wave

from faster_whisper import WhisperModel

from segment_info_parser_streaming import parse_segments_and_info_to_dict


class StreamingModelHandler:
    def __init__(self):

        self.model = WhisperModel("tiny", device="cpu", compute_type="int8")

        self.sample_rate = 16000
        self.num_channels = 1
        self.sampwidth = 2

    async def transcribe_bytes(self, audio_chunk: bytes):
        """Function to transcribe a chunk of audio"""
        result = "transcription error"
        with io.BytesIO() as wav_io:
            with wave.open(wav_io, "wb") as wav_file:
                wav_file.setnchannels(self.num_channels)
                wav_file.setsampwidth(self.sampwidth)
                wav_file.setframerate(self.sample_rate)
                wav_file.writeframes(audio_chunk)
            wav_io.seek(0)
            segments, info = self.model.transcribe(
                wav_io,
                word_timestamps=True,
                vad_filter=True,
            )
            result = parse_segments_and_info_to_dict(segments, info)
        return result

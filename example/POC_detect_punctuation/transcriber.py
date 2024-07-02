import io
import wave

from faster_whisper import WhisperModel

from segment_info_parser_streaming import parse_segments_and_info_to_dict


class Transcriber:
    def __init__(self):

        self.model = WhisperModel("tiny", device="cpu", compute_type="int8")

        self.sample_rate = 16000
        self.num_channels = 1
        self.sampwidth = 2

    def transcribe_audio_audio_chunk(self, audio_chunk: bytes, settings: dict):
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
                **settings
            )
            result = parse_segments_and_info_to_dict(segments, info)
        return result

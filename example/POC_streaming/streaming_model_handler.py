import io
import wave

from faster_whisper import WhisperModel

from segment_info_parser_streaming import parse_segments_and_info_to_dict

class StreamingModelHandler:
    def __init__(self, model_number: int):
        self.model_number = model_number
        self.models = []
        for _ in range(model_number):
            self.add_model()

        self.sample_rate = 16000
        self.num_channels = 1
        self.sampwidth = 2

    def add_model(self):
        model = WhisperModel("tiny", device="cpu", compute_type="int8")
        is_busy = False
        self.models.append({"model": model, "is_busy": is_busy})

    def find_free_model(self) -> WhisperModel:
        print(self.models)
        for model in self.models:
            if not model["is_busy"]:
                model["is_busy"] = True
                return model
        return None

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
            free_model = self.find_free_model()
            if free_model:
                segments, info = free_model["model"].transcribe(wav_io, word_timestamps=True)
                result = parse_segments_and_info_to_dict(segments, info)
            else :
                result = "All models are busy"
            free_model["is_busy"] = False
        return result
""" Module to handle the transcription process """
from faster_whisper import WhisperModel
from faster_whisper.transcribe import TranscriptionInfo
import numpy as np
from src.helper.logger import Logger, Color


class Transcriber:
    """Class to handle the transcription process"""

    def __init__(self, model_path: str = "./models/tiny"):
        self.log = Logger("Transcriber", True, Color.MAGENTA)
        self.model = WhisperModel(model_path, device="cpu", compute_type="int8")

    def parse_transcription_info_to_dict(self, info: TranscriptionInfo) -> dict:
        """Function to convert the transcription info to a dictionary"""
        # TUPEL attributes:
        #
        # language: str
        # language_probability: float
        # duration: float
        # duration_after_vad: float
        # all_language_probs: Optional[List[Tuple[str, float]]]
        # transcription_options: TranscriptionOptions
        # vad_options: VadOptions

        info_dict = {
            "language": info.language,
            "language_probability": info.language_probability,
            "duration": info.duration,
            "duration_after_vad": info.duration_after_vad,
            # "all_language_probs": info.all_language_probs,
            "transcription_options": info.transcription_options,
            "vad_options": info.vad_options,
        }
        return info_dict

    def make_segments_and_info_to_dict(
        self, segments: tuple, info: TranscriptionInfo
    ) -> dict:
        """Function to convert the segments and info to a dictionary"""
        segments_list = list(segments)

        combined_dict = {
            "segments": segments_list,
            "info": self.parse_transcription_info_to_dict(info),
        }
        return combined_dict

    def transcribe_audio_audio_segment(self, audio_segment) -> dict:
        """Function to run the transcription process"""
        try:
            self.log.print_log("Transcribing audio segment: " + str(audio_segment))
            # Faster Whisper Call
            audio_data_bytes = np.frombuffer(audio_segment.raw_data, np.int16).flatten().astype(np.float32) / 32768.0
            segments, info = self.model.transcribe(
                audio_data_bytes, beam_size=5, word_timestamps=True
            )
            data_dict = self.make_segments_and_info_to_dict(segments, info)
            self.log.print_log("Transcription complete.")
            return data_dict
        # need to catch all exceptions here because the whisper call is not
        # pylint: disable=W0718
        except Exception as e:
            self.log.print_error("Error during transcription: " + str(e))
            return None


    def transcribe_audio_file(self, audio_file_path: str) -> dict:
        """Function to run the transcription process"""
        try:
            self.log.print_log("Transcribing file: " + str(audio_file_path))
            # Faster Whisper Call
            segments, info = self.model.transcribe(
                audio_file_path, beam_size=5, word_timestamps=True
            )
            data_dict = self.make_segments_and_info_to_dict(segments, info)
            self.log.print_log("Transcription complete.")
            return data_dict
            # need to catch all exceptions here because the whisper call is not
            # pylint: disable=W0718
        except Exception as e:
            self.log.print_error("Error during transcription: " + str(e))
            return None

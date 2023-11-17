""" This module contains the handler for the transcription process. """
import sys
import time
from src.transcription_request_handling.transcription_model import Transcription


# def main() -> None:
#     """Loop to handle request queue"""
#     results = transcript_to_json(
#         main_path="/whisper.cpp/main",
#         model_path="/whisper.cpp/models/ggml-small.bin",
#         audio_file_path="/whisper.cpp/samples/jfk.wav",
#         output_file="/data/main",
#         debug=True,
#     )
#     print(results)


# main()


TRANSCRIPTION_RUNNER = 1


class Handler:
    """
    TBD
    """

    def __init__(self, runner_amount=TRANSCRIPTION_RUNNER):
        self.runner_amount = runner_amount

    def startup(self):
        """continuously checks for new transcriptions to process"""
        while True:
            print("Checking for new transcriptions...")
            time.sleep(5)


"""
This module contains the Startup functions for the file transcriber.
"""
from src.helper.logger import Logger
from src.transcription.rest_runner import Runner

log = Logger("run_transcription", True)


def run_file_transcriber():
    """Starts the file transcriber."""
    runner = Runner(1)
    runner.run()

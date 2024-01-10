"""
This module contains the Startup functions for the file transcriber.
"""
from src.config import CONFIG
from src.helper.logger import Color, Logger
from src.transcription.rest_runner import Runner

def run_file_transcriber():
    """Starts the file transcriber."""
    log = Logger("run_file_transcriber", True, Color.UNDERLINE)
    log.print_log("Starting file transcription runner..")
    runner = Runner(CONFIG["REST_MODEL"], 1)
    runner.run()

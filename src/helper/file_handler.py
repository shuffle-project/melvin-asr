"""This module contains a JSON FileHandler to simplify reading and writing JSON files."""

import json
import logging
import os
from typing import List, Tuple

from fastapi import UploadFile
from pydub import AudioSegment
from pydub.exceptions import CouldntDecodeError

LOGGER = logging.getLogger(__name__)

# 5 hours in seconds
MAX_AUDIO_LENGTH = 5 * 60 * 60

class FileHandler:
    """This class handles the reading and writing of JSON files."""

    @staticmethod
    def load_into_valid_audiosegment(file: UploadFile) -> Tuple[(AudioSegment | None), List[str]]:
        errors: List[str] = []
        audio: AudioSegment | None = None
        # If this is none we will just assume it is okay...
        # There should (tm) be no way for this to be none
        if file.filename is not None:
            if not file.filename.endswith('.wav'):
                return (None, ["Uploaded audio file should be of type wav"])
        try:
            # Load audio using pydub
            loaded_audio = AudioSegment.from_file(file.file, format="wav")

            # Check sample rate
            if loaded_audio.frame_rate != 16000:
                errors.append("Invalid sample rate. Must be 16 kHz.")

            if loaded_audio.duration_seconds > MAX_AUDIO_LENGTH:
                errors.append(f"Maximum allowed audio length exceeded. Max audio length is at {MAX_AUDIO_LENGTH} seconds.")

            audio = loaded_audio
        except CouldntDecodeError:
            errors.append("Could not decode file using ffmpeg. This is an indicator that the uploaded file is corrupted.")
        except Exception as e:
            raise e
        return (audio, errors)

    def read_json(self, file_path):
        """Reads a JSON file and returns the data."""
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                data = json.load(file)
            return data
        except Exception as e:
            LOGGER.error("Error reading JSON file: " + str(e))
            return None

    def write_json(self, file_path, data) -> bool:
        """Writes a JSON file."""
        try:
            with open(file_path, "w", encoding="utf-8") as file:
                json.dump(data, file)
            return True
        except Exception as e:
            LOGGER.error("Error writing JSON file: " + str(e))
            return False

    def create(self, file_path, data) -> bool:
        """Creates a JSON file."""
        try:
            with open(file_path, "x", encoding="utf-8") as file:
                json.dump(data, file)
            return True
        except Exception as e:
            LOGGER.error("Error creating JSON file: " + str(e))
            return False

    def delete(self, file_path) -> bool:
        """Deletes a file."""
        try:
            os.remove(file_path)
            return True
        except Exception as e:
            LOGGER.error("Error deleting file: " + str(e))
            return False

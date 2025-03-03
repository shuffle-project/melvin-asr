"""cleanup_data.fixture.py"""

import os

import pytest

from src.helper.data_handler import DataHandler

DATA_HANDLER = DataHandler()


@pytest.fixture(autouse=True)
def cleanup_data():
    """deletes all .json in the status folder and all .wav in the audio folder"""
    yield
    for file in os.listdir(DATA_HANDLER.status_path):
        if file.endswith(".json"):
            os.remove(os.path.join(DATA_HANDLER.status_path, file))
    for file in os.listdir(DATA_HANDLER.audio_file_path):
        if file.endswith(".wav"):
            os.remove(os.path.join(DATA_HANDLER.audio_file_path, file))

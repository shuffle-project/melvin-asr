"""This File contains tests for the Runner class."""
# ignore unused-import because of pytest fixtures
# ruff: noqa: F811
# ruff: noqa: F401
import os
from src.config import CONFIG
from src.transcription.transcriber import Transcriber

TRANSCRIBER = Transcriber("tiny", "cpu", "int8")


def test_get_model_path():
    """Tests the get_model_path function."""

    CONFIG["model_path"] = "/models1/"

    assert TRANSCRIBER.get_model_path("tiny") == os.getcwd() + "/models1/tiny"
    assert TRANSCRIBER.get_model_path("medium") == os.getcwd() + "/models1/medium"
    assert TRANSCRIBER.get_model_path("large") == os.getcwd() + "/models1/large"

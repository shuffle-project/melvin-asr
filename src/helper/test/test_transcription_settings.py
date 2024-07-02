"""This File contains tests for the Runner class."""
# ignore unused-import because of pytest fixtures
# ruff: noqa: F811
# ruff: noqa: F401
import os
from src.helper.config import CONFIG
from src.helper.transcription_settings import TranscriptionSettings

TranscriptionSettingsInstance = TranscriptionSettings()

TranscriptionSettingsInstance.default_settings = {
    "language": "en",
    "task": "transcribe",
}


def test_get_and_update_settings_entirely():
    """Tests the get_and_update_settings function."""
    settings = {
        "language": "de",
        "task": "transcribe",
    }
    result = TranscriptionSettingsInstance.get_and_update_settings(settings)
    assert result == settings


def test_get_and_update_settings_partially():
    """Tests the get_and_update_settings function."""
    settings = {
        "language": "de",
    }
    result = TranscriptionSettingsInstance.get_and_update_settings(settings)
    assert result == {
        "language": "de",
        "task": "transcribe",
    }

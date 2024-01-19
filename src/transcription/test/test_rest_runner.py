"""This File contains tests for the Runner class."""
import os
import pytest
from src.helper.data_handler import DataHandler
from src.helper.types.transcription_status import TranscriptionStatus
from src.transcription.rest_runner import Runner

# pylint: disable=redefined-outer-name
# pylint: disable=unused-argument

EXAMPLE_STATUS_FILE_PATH = "/src/transcription/test/files/data/status/"
EXAMPLE_AUDIO_FILE_PATH = "/src/transcription/test/files/data/audio_files/"

RUNNER = Runner("tiny", "1", "cpu", "int8")
DATA_HANDLER = DataHandler(EXAMPLE_STATUS_FILE_PATH, EXAMPLE_AUDIO_FILE_PATH)


@pytest.fixture
def setup_code():
    """Fixture to setup the test environment."""
    yield
    for filename in os.listdir(os.getcwd() + EXAMPLE_STATUS_FILE_PATH):
        # remove .json from all names, if theay are .json
        if filename.endswith(".json"):
            filename = filename[:-5]
            DATA_HANDLER.delete_status_file(filename)


def test_get_oldest_status_file_in_query_fail(setup_code):
    """Tests getting the oldest status file in query returns None if no status file is available."""
    # by default there is no status file in the test folder having a start_time which is required
    assert RUNNER.get_oldest_status_file_in_query(1, DATA_HANDLER) == "None"


def test_get_oldest_status_file_in_query_success(setup_code):
    """Tests getting the oldest status file in query returns the transcription_id."""
    # prepare write.json file
    data = {
        "transcription_id": "write",
        "status": TranscriptionStatus.IN_QUERY.value,
        "start_time": "2021-05-01T00:00:00Z",
    }
    DATA_HANDLER.write_status_file("write", data)
    # check status file
    assert RUNNER.get_oldest_status_file_in_query(1, DATA_HANDLER) == "write"


def test_get_oldest_status_file_in_query_oldest_first(setup_code):
    """Tests getting the oldest status file in query when 2 are available."""
    # prepare write.json file
    data = {
        "transcription_id": "writeNew",
        "status": TranscriptionStatus.IN_QUERY.value,
        "start_time": "2021-05-01T00:00:00Z",
    }
    DATA_HANDLER.write_status_file("writeNew", data)
    data = {
        "transcription_id": "writeOld",
        "status": TranscriptionStatus.IN_QUERY.value,
        "start_time": "2021-04-01T00:00:00Z",
    }
    DATA_HANDLER.write_status_file("writeOld", data)
    # check status file
    assert RUNNER.get_oldest_status_file_in_query(1, DATA_HANDLER) == "writeOld"

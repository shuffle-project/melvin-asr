"""This File contains tests for the Runner class."""
# pylint: disable=redefined-outer-name
# pylint: disable=unused-argument
# pylint: disable=unused-import
from src.test_base.cleanup_data_fixture import cleanup_data
from src.helper.data_handler import DataHandler
from src.helper.types.transcription_status import TranscriptionStatus
from src.transcription.rest_runner import Runner

RUNNER = Runner("tiny", "1", "cpu", "int8")
DATA_HANDLER = DataHandler()


def test_get_oldest_status_file_in_query_fail():
    """Tests getting the oldest status file in query returns None if no status file is available."""
    # by default there is no status file in the test folder having a start_time which is required
    assert RUNNER.get_oldest_status_file_in_query(1, DATA_HANDLER) == "None"


def test_get_oldest_status_file_in_query_success(cleanup_data):
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


def test_get_oldest_status_file_in_query_oldest_first(cleanup_data):
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

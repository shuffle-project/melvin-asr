"""This File contains tests for the DataHandler class."""
import datetime
import os
import shutil
from src.helper.data_handler import DataHandler
from src.helper.transcription import TranscriptionStatusValue

EXAMPLE_STATUS_FILE_PATH = "/src/helper/test/files/data/status/"
EXAMPLE_AUDIO_FILE_PATH = "/src/helper/test/files/data/audio_files/"

EXAMPLE_TRANSCRIPTION_ID = "example"

DATA_HANDLER = DataHandler(EXAMPLE_STATUS_FILE_PATH, EXAMPLE_AUDIO_FILE_PATH)


def test_get_status_file_by_id_success():
    """Tests getting a existing status file by id."""
    data = DATA_HANDLER.get_status_file_by_id("example")
    assert data == {"test": "test"}


def test_get_status_file_by_id_fail():
    """Tests getting a non existing status file by id."""
    data = DATA_HANDLER.get_status_file_by_id("non_existing")
    assert data is None


def test_get_all_status_filenames():
    """Tests getting all status filenames."""
    filenames = DATA_HANDLER.get_all_status_filenames()
    # check if filenames are correct
    assert ("example.json" in filenames) is True
    assert ("write.json" in filenames) is True


def test_write_status_file():
    """Tests writing a status file."""
    time = datetime.datetime.now()
    data = {"time": str(time)}
    DATA_HANDLER.write_status_file("write", data)
    assert DATA_HANDLER.get_status_file_by_id("write") == data


def test_get_audio_file_path_by_id():
    """Tests getting a audio file path by id."""
    path = DATA_HANDLER.get_audio_file_path_by_id("example")
    assert ("/src/helper/test/files/data/audio_files/example.wav" in path) is True


def test_get_audio_file_path_by_id_fail():
    """Tests getting a non existing audio file path by id."""
    path = DATA_HANDLER.get_audio_file_path_by_id("non_existing")
    assert path is None


def test_update_status_file_success():
    """Tests updating a status file."""
    # prepare write.json file
    data = {"status": TranscriptionStatusValue.IN_PROGRESS.value}
    DATA_HANDLER.write_status_file("write", data)
    # update status file
    DATA_HANDLER.update_status_file(TranscriptionStatusValue.FINISHED.value, "write")
    # check status file
    end_time = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    check_data = {
        "status": TranscriptionStatusValue.FINISHED.value,
        "end_time": end_time,
    }
    assert DATA_HANDLER.get_status_file_by_id("write") == check_data


def test_update_status_file_fail():
    """Tests updating a non existing status file."""
    DATA_HANDLER.update_status_file(
        TranscriptionStatusValue.FINISHED.value, "non_existing"
    )
    assert DATA_HANDLER.get_status_file_by_id("non_existing") is None


def test_update_status_file_with_error_message():
    """Tests updating a status file with an error message."""
    # prepare write.json file
    data = {"status": TranscriptionStatusValue.IN_PROGRESS.value}
    DATA_HANDLER.write_status_file("write", data)
    # update status file
    DATA_HANDLER.update_status_file(
        TranscriptionStatusValue.ERROR.value, "write", "error"
    )
    # check status file
    check_data = {
        "status": TranscriptionStatusValue.ERROR.value,
        "error_message": "error",
    }
    assert DATA_HANDLER.get_status_file_by_id("write") == check_data


def test_merge_transcript_to_status_success():
    """Tests merging a transcript to a status file."""
    # prepare write.json file
    data = {"status": TranscriptionStatusValue.IN_PROGRESS.value}
    DATA_HANDLER.write_status_file("write", data)
    # merge transcript to status file
    transcript_data = {"transcript": "test"}
    DATA_HANDLER.merge_transcript_to_status("write", transcript_data)
    # check status file
    end_time = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    check_data = {
        "status": TranscriptionStatusValue.FINISHED.value,
        "transcript": {"transcript": "test"},
        "end_time": end_time,
    }
    assert DATA_HANDLER.get_status_file_by_id("write") == check_data


def test_merge_transcript_to_status_fail():
    """Tests merging a transcript to a non existing status file."""
    assert DATA_HANDLER.merge_transcript_to_status("non_existing", {}) is False


def test_get_oldest_status_file_in_query_fail():
    """Tests getting the oldest status file in query."""
    # by default there is no status file in the test folder having a start_time which is required
    assert DATA_HANDLER.get_oldest_status_file_in_query(1) == "None"


def test_get_oldest_status_file_in_query_success():
    """Tests getting the oldest status file in query."""
    # prepare write.json file
    data = {
        "transcription_id": "write",
        "status": TranscriptionStatusValue.IN_QUERY.value,
        "start_time": "2021-05-01T00:00:00Z",
    }
    DATA_HANDLER.write_status_file("write", data)
    # check status file
    assert DATA_HANDLER.get_oldest_status_file_in_query(1) == "write"


def test_delete_audio_file_success():
    """Tests deleting an audio file."""
    # copy example.wav to example_delete.wav
    source_path = os.getcwd() + EXAMPLE_AUDIO_FILE_PATH + "example.wav"
    destination_path = os.getcwd() + EXAMPLE_AUDIO_FILE_PATH + "example-delete.wav"
    shutil.copy(source_path, destination_path)

    # delete example-delete.wav
    DATA_HANDLER.delete_audio_file("example-delete")
    assert os.path.isfile(destination_path) is False

def test_delete_audio_file_fail():
    """Tests deleting a non existing audio file."""
    DATA_HANDLER.delete_audio_file("non_existing")
    assert True

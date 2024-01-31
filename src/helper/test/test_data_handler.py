"""This File contains tests for the DataHandler class."""
# ignore unused-import because of pytest fixtures
# ruff: noqa: F811
# ruff: noqa: F401
import datetime
import os
from pydub import AudioSegment
from src.test_base.cleanup_data_fixture import cleanup_data
from src.helper.data_handler import DataHandler
from src.helper.types.transcription_status import TranscriptionStatus

EXAMPLE_TRANSCRIPTION_ID = "example"
EXAMPLE_AUDIO_FILE_PATH = os.getcwd() + "/src/test_base/example.wav"

DATA_HANDLER = DataHandler()


def test_get_status_file_by_id_success(cleanup_data):
    """Tests getting a existing status file by id."""
    DATA_HANDLER.write_status_file("example", {"test": "test"})
    data = DATA_HANDLER.get_status_file_by_id("example")
    assert data == {"test": "test"}


def test_get_status_file_by_id_fail():
    """Tests getting a non existing status file by id."""
    data = DATA_HANDLER.get_status_file_by_id("non_existing")
    assert data is None


def test_get_all_status_filenames(cleanup_data):
    """Tests getting all status filenames."""
    DATA_HANDLER.write_status_file("example1", {"test": "test"})
    DATA_HANDLER.write_status_file("example2", {"test": "test"})
    filenames = DATA_HANDLER.get_all_status_filenames()
    # check if filenames are correct
    assert ("example1.json" in filenames) is True
    assert ("example2.json" in filenames) is True


def test_write_status_file(cleanup_data):
    """Tests writing a status file."""
    time = datetime.datetime.now()
    data = {"time": str(time)}
    DATA_HANDLER.write_status_file("write", data)
    assert DATA_HANDLER.get_status_file_by_id("write") == data


def test_write_status_file_does_not_exist(cleanup_data):
    """Tests writing a status file."""
    time = datetime.datetime.now()
    data = {"time": str(time)}
    DATA_HANDLER.write_status_file("write1", data)
    assert DATA_HANDLER.get_status_file_by_id("write1") == data
    DATA_HANDLER.delete_status_file("write1")


def test_delete_status_file_success(cleanup_data):
    """Tests deleting a status file."""
    DATA_HANDLER.write_status_file("write", {})
    res = DATA_HANDLER.delete_status_file("write")
    assert res is True
    assert DATA_HANDLER.get_status_file_by_id("write") is None


def test_delete_status_file_fail():
    """Tests deleting a non existing status file."""
    res = DATA_HANDLER.delete_status_file("non_existing")
    assert res is False


def test_get_audio_file_path_by_id(cleanup_data):
    """Tests getting a audio file path by id."""
    # copy example.wav to example-save.wav
    example_audio_data = AudioSegment.from_wav(EXAMPLE_AUDIO_FILE_PATH)
    # save example-save.wav
    res = DATA_HANDLER.save_audio_file(example_audio_data, "example")
    assert res == {"success": True, "message": "Conversion successful."}
    path = DATA_HANDLER.get_audio_file_path_by_id("example")
    assert (DATA_HANDLER.audio_file_path in path) is True


def test_get_audio_file_path_by_id_fail():
    """Tests getting a non existing audio file path by id."""
    path = DATA_HANDLER.get_audio_file_path_by_id("non_existing")
    assert path is None


def test_update_status_file_success(cleanup_data):
    """Tests updating a status file."""
    # prepare write.json file
    data = {"status": TranscriptionStatus.IN_PROGRESS.value}
    DATA_HANDLER.write_status_file("write", data)
    # update status file
    DATA_HANDLER.update_status_file(TranscriptionStatus.FINISHED.value, "write")
    # check status file
    end_time = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    check_data = {
        "status": TranscriptionStatus.FINISHED.value,
        "end_time": end_time,
    }
    assert DATA_HANDLER.get_status_file_by_id("write") == check_data


def test_update_status_file_fail():
    """Tests updating a non existing status file."""
    DATA_HANDLER.update_status_file(TranscriptionStatus.FINISHED.value, "non_existing")
    assert DATA_HANDLER.get_status_file_by_id("non_existing") is None


def test_update_status_file_with_error_message(cleanup_data):
    """Tests updating a status file with an error message."""
    # prepare write.json file
    data = {"status": TranscriptionStatus.IN_PROGRESS.value}
    DATA_HANDLER.write_status_file("write", data)
    # update status file
    DATA_HANDLER.update_status_file(TranscriptionStatus.ERROR.value, "write", "error")
    # check status file
    check_data = {
        "status": TranscriptionStatus.ERROR.value,
        "error_message": "error",
    }
    assert DATA_HANDLER.get_status_file_by_id("write") == check_data


def test_merge_transcript_to_status_success(cleanup_data):
    """Tests merging a transcript to a status file."""
    # prepare write.json file
    data = {"status": TranscriptionStatus.IN_PROGRESS.value}
    DATA_HANDLER.write_status_file("write", data)
    # merge transcript to status file
    transcript_data = {"transcript": "test"}
    DATA_HANDLER.merge_transcript_to_status("write", transcript_data)
    # check status file
    end_time = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    check_data = {
        "status": TranscriptionStatus.FINISHED.value,
        "transcript": {"transcript": "test"},
        "end_time": end_time,
    }
    assert DATA_HANDLER.get_status_file_by_id("write") == check_data


def test_merge_transcript_to_status_fail():
    """Tests merging a transcript to a non existing status file."""
    assert DATA_HANDLER.merge_transcript_to_status("non_existing", {}) is False


def test_save_audio_file_success(cleanup_data):
    """Tests saving an audio file."""
    # copy example.wav to example-save.wav
    example_audio_data = AudioSegment.from_wav(EXAMPLE_AUDIO_FILE_PATH)
    # save example-save.wav
    res = DATA_HANDLER.save_audio_file(example_audio_data, "example-save")
    assert res == {"success": True, "message": "Conversion successful."}
    # cleanup
    DATA_HANDLER.delete_audio_file("example-save")


def test_save_audio_file_fail():
    """Tests saving an audio file."""
    res = DATA_HANDLER.save_audio_file("/non_existing/path", "example-save")
    assert res == {
        "success": False,
        "message": "Audio File creation failed for: 'str' object has no attribute 'set_frame_rate'",
    }


def test_delete_audio_file_success():
    """Tests deleting an audio file."""
    example_audio_data = AudioSegment.from_wav(EXAMPLE_AUDIO_FILE_PATH)
    res = DATA_HANDLER.save_audio_file(example_audio_data, "example-delete")

    # delete example-delete.wav
    res = DATA_HANDLER.delete_audio_file("example-delete")
    assert res is True
    assert os.path.isfile(DATA_HANDLER.audio_file_path + "example-delete.wav") is False


def test_delete_audio_file_fail():
    """Tests deleting a non existing audio file."""
    res = DATA_HANDLER.delete_audio_file("non_existing")
    assert res is False


def test_get_number_of_audio_files():
    """Tests getting the number of audio files."""
    assert DATA_HANDLER.get_number_of_audio_files() == 0
    example_audio_data = AudioSegment.from_wav(EXAMPLE_AUDIO_FILE_PATH)
    DATA_HANDLER.save_audio_file(example_audio_data, "example-file")
    assert DATA_HANDLER.get_number_of_audio_files() == 1
    DATA_HANDLER.delete_audio_file("example-file")
    assert DATA_HANDLER.get_number_of_audio_files() == 0

"""This File contains tests for the DataHandler class."""

# ignore unused-import because of pytest fixtures
# ruff: noqa: F811
# ruff: noqa: F401
import datetime
import json
import os

from pydub import AudioSegment

from src.helper.config import CONFIG
from src.helper.data_handler import DataHandler
from src.helper.test_base.cleanup_data_fixture import cleanup_data
from src.helper.types.transcription_status import TranscriptionStatus

EXAMPLE_TRANSCRIPTION_ID = "example"
EXAMPLE_AUDIO_FILE_PATH = os.getcwd() + "/src/helper/test_base/example.wav"

DATA_HANDLER = DataHandler()


def test_get_status_file_by_id_success(cleanup_data: None):
    """Tests getting a existing status file by id."""
    DATA_HANDLER.write_status_file("example", {"test": "test"})
    data = DATA_HANDLER.get_status_file_by_id("example")
    assert data == {"test": "test"}


def test_get_status_file_by_id_fail():
    """Tests getting a non existing status file by id."""
    data = DATA_HANDLER.get_status_file_by_id("non_existing")
    assert data is None


def test_get_all_status_filenames(cleanup_data: None):
    """Tests getting all status filenames."""
    DATA_HANDLER.write_status_file("example1", {"test": "test"})
    DATA_HANDLER.write_status_file("example2", {"test": "test"})
    filenames = DATA_HANDLER.get_all_status_filenames()
    # check if filenames are correct
    assert ("example1.json" in filenames) is True
    assert ("example2.json" in filenames) is True


def test_write_status_file(cleanup_data: None):
    """Tests writing a status file."""
    time = datetime.datetime.now(datetime.timezone.utc)
    data = {"time": str(time)}
    DATA_HANDLER.write_status_file("write", data)
    assert DATA_HANDLER.get_status_file_by_id("write") == data


def test_write_status_file_does_not_exist(cleanup_data: None):
    """Tests writing a status file."""
    time = datetime.datetime.now(datetime.timezone.utc)
    data = {"time": str(time)}
    DATA_HANDLER.write_status_file("write1", data)
    assert DATA_HANDLER.get_status_file_by_id("write1") == data
    DATA_HANDLER.delete_status_file("write1")


def test_delete_status_file_success(cleanup_data: None):
    """Tests deleting a status file."""
    DATA_HANDLER.write_status_file("write", {})
    res = DATA_HANDLER.delete_status_file("write")
    assert res is True
    assert DATA_HANDLER.get_status_file_by_id("write") is None


def test_delete_status_file_fail():
    """Tests deleting a non existing status file."""
    res = DATA_HANDLER.delete_status_file("non_existing")
    assert res is False


def test_get_audio_file_path_by_id(cleanup_data: None):
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


def test_update_status_file_success(cleanup_data: None):
    """Tests updating a status file."""
    # prepare write.json file
    data = {"status": TranscriptionStatus.IN_PROGRESS.value}
    DATA_HANDLER.write_status_file("write", data)
    # update status file
    DATA_HANDLER.update_status_file(TranscriptionStatus.FINISHED.value, "write")

    assert (
        DATA_HANDLER.get_status_file_by_id("write")["status"]
        == TranscriptionStatus.FINISHED.value
    )


def test_update_status_file_fail():
    """Tests updating a non existing status file."""
    DATA_HANDLER.update_status_file(TranscriptionStatus.FINISHED.value, "non_existing")
    assert DATA_HANDLER.get_status_file_by_id("non_existing") is None


def test_update_status_file_with_error_message(cleanup_data: None):
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


def test_merge_transcript_to_status_success(cleanup_data: None):
    """Tests merging a transcript to a status file."""
    # prepare write.json file
    data = {"status": TranscriptionStatus.IN_PROGRESS.value}
    DATA_HANDLER.write_status_file("write", data)
    # merge transcript to status file
    transcript_data = {"transcript": "test"}
    DATA_HANDLER.merge_transcript_to_status("write", transcript_data)
    # check status file
    check_data = {
        "status": TranscriptionStatus.FINISHED.value,
        "transcript": {"transcript": "test"},
    }
    actual_data = DATA_HANDLER.get_status_file_by_id("write")
    assert actual_data["status"] == check_data["status"]
    assert (
        actual_data["transcript"]["transcript"]
        == check_data["transcript"]["transcript"]
    )


def test_merge_transcript_to_status_fail():
    """Tests merging a transcript to a non existing status file."""
    assert DATA_HANDLER.merge_transcript_to_status("non_existing", {}) is False


def test_save_audio_file_success(cleanup_data: None):
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


def test_get_number_of_audio_files(cleanup_data: None):
    """Tests getting the number of audio files."""
    assert DATA_HANDLER.get_number_of_audio_files() == 0
    example_audio_data = AudioSegment.from_wav(EXAMPLE_AUDIO_FILE_PATH)
    DATA_HANDLER.save_audio_file(example_audio_data, "example-file")
    assert DATA_HANDLER.get_number_of_audio_files() == 1
    DATA_HANDLER.delete_audio_file("example-file")
    assert DATA_HANDLER.get_number_of_audio_files() == 0


def test_clean_up_audio_and_status_files(cleanup_data: None):
    """Tests cleaning up audio and status files."""
    DATA_HANDLER.write_status_file("example", {"test": "test"})
    example_audio_data = AudioSegment.from_wav(EXAMPLE_AUDIO_FILE_PATH)
    DATA_HANDLER.save_audio_file(example_audio_data, "example")

    assert DATA_HANDLER.get_number_of_audio_files() == 1
    assert DATA_HANDLER.get_status_file_by_id("example") is not None

    DATA_HANDLER.clean_up_audio_and_status_files(0)
    assert DATA_HANDLER.get_number_of_audio_files() == 0
    assert DATA_HANDLER.get_status_file_by_id("example") is None


def test_clean_up_audio_and_status_files_do_keep(cleanup_data: None):
    """Tests cleaning up audio and status files."""
    DATA_HANDLER.write_status_file("example", {"test": "test"})
    example_audio_data = AudioSegment.from_wav(EXAMPLE_AUDIO_FILE_PATH)
    DATA_HANDLER.save_audio_file(example_audio_data, "example")

    assert DATA_HANDLER.get_number_of_audio_files() == 1
    assert DATA_HANDLER.get_status_file_by_id("example") is not None

    DATA_HANDLER.clean_up_audio_and_status_files(1)
    assert DATA_HANDLER.get_number_of_audio_files() == 1
    assert DATA_HANDLER.get_status_file_by_id("example") is not None


def test_export_wav_file_success(cleanup_data: None):
    """Tests exporting a WAV file."""
    example_audio_data = AudioSegment.from_wav(EXAMPLE_AUDIO_FILE_PATH)
    resampled_audio = example_audio_data.set_frame_rate(16000).set_channels(1)

    # Get the raw data of the resampled audio
    audio_chunk = resampled_audio.raw_data

    export_path = DATA_HANDLER.export_wav_file(audio_chunk, "example-export")
    assert os.path.isfile(export_path) is True
    assert export_path.endswith(".wav")

    # Verify the exported file can be loaded and has the correct properties
    exported_audio = AudioSegment.from_wav(export_path)
    assert exported_audio.frame_rate == 16000
    assert exported_audio.channels == 1

    # Cleanup
    os.remove(export_path)


def test_export_dict_to_json_file_success(cleanup_data: None):
    """Tests exporting a dictionary to a JSON file."""
    data = {
        "result": [
            {"conf": 0.428089, "start": 5.642375, "end": 6.582375, "word": "Okay,"},
            {"conf": 0.711699, "start": 7.202375, "end": 7.642375, "word": "let's"},
            {"conf": 0.984197, "start": 7.642375, "end": 7.882375, "word": "try"},
            {"conf": 0.997035, "start": 7.882375, "end": 8.522375, "word": "again"},
            {"conf": 0.279302, "start": 8.522375, "end": 9.422375, "word": "20,"},
            {"conf": 0.864112, "start": 9.762375, "end": 9.762375, "word": "so"},
            {"conf": 0.057683, "start": 9.762375, "end": 9.962375, "word": "der"},
            {"conf": 0.382845, "start": 9.962375, "end": 10.282375, "word": "relativ"},
            {"conf": 0.429512, "start": 10.282375, "end": 10.522375, "word": "schrei"},
            {"conf": 0.78254, "start": 10.522375, "end": 10.862375, "word": "vorbei"},
            {"conf": 0.943829, "start": 10.862375, "end": 11.202375, "word": "sein."},
        ],
        "text": " Okay, let's try again 20, so der relativ schrei vorbei sein.",
    }
    export_path = DATA_HANDLER.export_dict_to_json_file(data, "example-export")
    assert os.path.isfile(export_path) is True
    assert export_path.endswith(".json")

    # Verify the content of the exported file
    with open(export_path, "r") as json_file:
        content = json.load(json_file)
    assert content == data

    # Cleanup
    os.remove(export_path)


def test_cleanup_interrupted_jobs():
    """
    Tests cleaning up on instance start

    This test specifically ignores the impact on the status file directory to not delete existing files
    """

    base_amount = len(os.listdir(DATA_HANDLER.status_path))

    DATA_HANDLER.write_status_file("example_irrecoverable", {"status": "in_progress"})
    DATA_HANDLER.write_status_file("example_fine", {"status": "error"})
    file_path = os.path.join(DATA_HANDLER.status_path, "invalid_json")
    with open(file_path, "w", encoding="utf-8") as file:
        file.write("no json")

    assert DATA_HANDLER.get_status_file_by_id("example_irrecoverable") is not None
    assert DATA_HANDLER.get_status_file_by_id("example_fine") is not None
    assert len(os.listdir(DATA_HANDLER.status_path)) == base_amount + 3

    DATA_HANDLER.cleanup_interrupted_jobs()
    assert DATA_HANDLER.get_status_file_by_id("example_irrecoverable") is None
    assert DATA_HANDLER.get_status_file_by_id("example_fine") is not None
    # 2 Files should be cleaned up
    assert len(os.listdir(DATA_HANDLER.status_path)) == base_amount + 1

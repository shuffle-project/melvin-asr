"""This File contains tests for the FileHandler class."""

import datetime
import os
from src.helper.file_handler import FileHandler

EXAMPLE_READ_FILE_PATH = os.path.join(os.getcwd() + "/src/helper/test/files/read.json")
EXAMPLE_WRITE_FILE_PATH = os.path.join(
    os.getcwd() + "/src/helper/test/files/write.json"
)
EXAMPLE_CREATE_TO_DELETE_FILE_PATH = os.path.join(
    os.getcwd() + "/src/helper/test/files/delete.json"
)
FILE_HANDLER = FileHandler()


def test_read_json_success():
    """Tests reading a JSON file that exists."""
    data = FILE_HANDLER.read_json(EXAMPLE_READ_FILE_PATH)
    assert data == {"test": "test"}


def test_read_json_fail():
    """Tests reading a JSON file that does not exist."""
    data = FILE_HANDLER.read_json("does/not/exist.json")
    assert data is None


def test_write_json_success():
    """Tests writing a JSON file by writing the current time."""
    time = datetime.datetime.now()
    data = {"time": str(time)}
    success = FILE_HANDLER.write_json(EXAMPLE_WRITE_FILE_PATH, data)
    assert success is True
    assert FILE_HANDLER.read_json(EXAMPLE_WRITE_FILE_PATH) == data


def test_write_json_fail():
    """Tests writing a non existing JSON file by writing the current time."""
    time = datetime.datetime.now()
    data = {"time": str(time)}
    success = FILE_HANDLER.write_json("does/not/exist.json", data)
    assert success is False


def test_create_delete_file():
    """Tests deleting a file."""
    # create a file first
    data = {"test": "test"}
    FILE_HANDLER.create(EXAMPLE_CREATE_TO_DELETE_FILE_PATH, data)
    assert FILE_HANDLER.read_json(EXAMPLE_CREATE_TO_DELETE_FILE_PATH) == data
    # delete the file
    success = FILE_HANDLER.delete(EXAMPLE_CREATE_TO_DELETE_FILE_PATH)
    assert success is True
    # check if the file still exists
    assert FILE_HANDLER.read_json(EXAMPLE_CREATE_TO_DELETE_FILE_PATH) is None

# this needs to be the last step, because the write file needs to be resetet
def test_reset():
    """restores the write.json file to its original state."""
    data = {"test": "test"}
    success = FILE_HANDLER.write_json(EXAMPLE_WRITE_FILE_PATH, data)
    assert success is True
    assert FILE_HANDLER.read_json(EXAMPLE_WRITE_FILE_PATH) == data
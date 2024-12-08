"""This File contains tests for the FileHandler class."""

# ignore unused-import because of pytest fixtures
# ruff: noqa: F811
# ruff: noqa: F401
import datetime
import json
import os

import pytest

from src.helper.file_handler import FileHandler

FILE_HANDLER = FileHandler()
TEST_FILE_PATH = os.getcwd() + "/src/helper/test/test.json"
TEST_FILE_DATA = {"test": "test"}


@pytest.fixture(autouse=True)
def setup_and_teardown_file():
    """Creates a test file and deletes it after the test."""
    with open(TEST_FILE_PATH, "w", encoding="utf-8") as f:
        json.dump(TEST_FILE_DATA, f)
    yield
    if os.path.exists(TEST_FILE_PATH):
        os.remove(TEST_FILE_PATH)


def test_read_json_success(setup_and_teardown_file):
    """Tests reading a JSON file that exists."""
    data = FILE_HANDLER.read_json(TEST_FILE_PATH)
    assert data == TEST_FILE_DATA


def test_read_json_fail():
    """Tests reading a JSON file that does not exist."""
    data = FILE_HANDLER.read_json("does/not/exist.json")
    assert data is None


def test_write_json_success(setup_and_teardown_file):
    """Tests writing a JSON file by writing the current time."""
    time = datetime.datetime.now(datetime.timezone.utc)
    data = {"time": str(time)}
    success = FILE_HANDLER.write_json(TEST_FILE_PATH, data)
    assert success is True
    assert FILE_HANDLER.read_json(TEST_FILE_PATH) == data


def test_write_json_fail():
    """Tests writing a non existing JSON file by writing the current time."""
    time = datetime.datetime.now(datetime.timezone.utc)
    data = {"time": str(time)}
    success = FILE_HANDLER.write_json("does/not/exist.json", data)
    assert success is False


def test_delete_file():
    """Tests deleting a file."""
    data = {"test": "test"}
    FILE_HANDLER.create(TEST_FILE_PATH, data)
    assert FILE_HANDLER.read_json(TEST_FILE_PATH) == data
    success = FILE_HANDLER.delete(TEST_FILE_PATH)
    assert success is True
    assert FILE_HANDLER.read_json(TEST_FILE_PATH) is None

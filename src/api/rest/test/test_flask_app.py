"""This File contains tests for the Flask_app endpoints."""
# pylint: disable=redefined-outer-name
# pylint: disable=unused-argument
# pylint: disable=unused-import
import os
import pytest
from src.test_base.cleanup_data_fixture import cleanup_data
from src.api.rest.flask_app import create_app
from src.helper.data_handler import DataHandler

EXAMPLE_AUDIO_FILE_PATH = os.getcwd() + "/src/test_base/example.wav"
EXAMPLE_AUTH_KEY = "example"

DATA_HANDLER = DataHandler()


@pytest.fixture
def rest_client():
    """Create a Flask test client"""
    app = create_app(EXAMPLE_AUTH_KEY)
    with app.test_client() as client:
        yield client


def test_health_check(rest_client):
    """Test the health check endpoint"""
    response = rest_client.get("/health")
    assert response.status_code == 200
    assert response.data == b"OK"


def test_welcome(rest_client):
    """Test the welcome endpoint"""
    response = rest_client.get("/")
    assert response.status_code == 200
    assert (
        "Welcome to the Transcription API!" in response.data.decode("utf-8")
    ) is True


def test_post_transcription(rest_client, cleanup_data):
    """Test the post transcription endpoint"""
    # post with a audio file in the body
    with open(EXAMPLE_AUDIO_FILE_PATH, "rb") as audio_file:
        response = rest_client.post(
            "/transcriptions",
            headers={"key": EXAMPLE_AUTH_KEY},
            data={"file": audio_file},
            content_type="multipart/form-data",
        )

    response_dict = response.get_json()

    # check if the response is correct
    assert response.status_code == 200
    assert response_dict["settings"] is None
    assert response_dict["status"] == "in_query"
    assert response_dict["transcription_id"] is not None
    assert ("start_time" in response_dict) is True

    # check if the audio file and status file exist
    assert (
        DATA_HANDLER.get_audio_file_path_by_id(response_dict["transcription_id"])
        is not None
    )
    status_file = DATA_HANDLER.get_status_file_by_id(response_dict["transcription_id"])
    assert status_file is not None
    assert status_file["status"] == "in_query"
    assert status_file["settings"] is None
    assert status_file["status"] == "in_query"
    assert status_file["transcription_id"] is not None
    assert ("start_time" in status_file) is True


def test_post_transcription_without_file(rest_client, cleanup_data):
    """Test the post transcription endpoint without a file"""
    response = rest_client.post("/transcriptions", headers={"key": EXAMPLE_AUTH_KEY})
    assert response.status_code == 400
    # parse the response to a string to compare it with the expected string
    assert response.data.decode("utf-8") == "No file posted"


def test_post_transcription_with_wrong_file(rest_client, cleanup_data):
    """Test the post transcription endpoint without a file"""
    with open(EXAMPLE_AUDIO_FILE_PATH, "rb") as audio_file:
        response = rest_client.post(
            "/transcriptions",
            headers={"key": EXAMPLE_AUTH_KEY},
            data={"file1": audio_file},
            content_type="multipart/form-data",
        )
    assert response.status_code == 400
    # parse the response to a string to compare it with the expected string
    assert response.data.decode("utf-8") == "No file posted"


def test_get_transcriptions_id(rest_client, cleanup_data):
    """Test the get transcription id endpoint"""
    with open(EXAMPLE_AUDIO_FILE_PATH, "rb") as audio_file:
        response_post = rest_client.post(
            "/transcriptions",
            headers={"key": EXAMPLE_AUTH_KEY},
            data={"file": audio_file},
            content_type="multipart/form-data",
        )
    response_dict_post = response_post.get_json()
    transcription_id = response_dict_post["transcription_id"]
    response = rest_client.get(
        f"/transcriptions/{transcription_id}", headers={"key": EXAMPLE_AUTH_KEY}
    )
    response_dict = response.get_json()
    assert response.status_code == 200
    assert response_dict["settings"] is None
    assert response_dict["status"] == "in_query"
    assert response_dict["transcription_id"] is not None
    assert ("start_time" in response_dict) is True
    assert response_dict == response_dict_post


def test_get_transcriptions_id_not_found(rest_client, cleanup_data):
    """Test the get transcription id endpoint with a not existing id"""
    response = rest_client.get(
        "/transcriptions/123456789", headers={"key": EXAMPLE_AUTH_KEY}
    )
    assert response.status_code == 404
    assert response.data.decode("utf-8") == "Transcription ID not found"


def test_get_transcriptions_without_files(rest_client):
    """Test the get transcriptions endpoint without files"""
    response = rest_client.get("/transcriptions", headers={"key": EXAMPLE_AUTH_KEY})
    assert response.status_code == 200
    assert response.get_json() == []


def test_get_transcriptions_with_files(rest_client, cleanup_data):
    """Test the get transcription id endpoint with files"""
    # write file
    with open(EXAMPLE_AUDIO_FILE_PATH, "rb") as audio_file:
        response_post = rest_client.post(
            "/transcriptions",
            headers={"key": EXAMPLE_AUTH_KEY},
            data={"file": audio_file},
            content_type="multipart/form-data",
        )
    response_dict_post = response_post.get_json()
    transcription_id = response_dict_post["transcription_id"]
    # read file
    response_get = rest_client.get(
        f"/transcriptions/{transcription_id}",
        headers={"key": EXAMPLE_AUTH_KEY},
    )
    assert response_get.status_code == 200
    response_dict_get = response_get.get_json()
    assert "transcription_id" in response_dict_get
    assert response_dict_get["transcription_id"] == transcription_id


def test_invalid_auth_key(rest_client):
    """Test the get transcriptions endpoint with an invalid auth key"""
    response = rest_client.get("/transcriptions", headers={"key": "INVALID_KEY"})
    assert response.status_code == 401
    assert "Unauthorized" in response.data.decode("utf-8")

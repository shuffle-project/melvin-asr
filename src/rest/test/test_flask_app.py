"""This File contains tests for the Flask_app endpoints."""
# ignore unused-import because of pytest fixtures
# ruff: noqa: F811
# ruff: noqa: F401
import json
import os

import pytest

from src.helper.config import CONFIG
from src.helper.data_handler import DataHandler
from src.helper.test_base.cleanup_data_fixture import cleanup_data
from src.rest.app import create_app

EXAMPLE_AUDIO_FILE_PATH = os.getcwd() + "/src/helper/test_base/example.wav"
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
    response = rest_client.get(
        "/health", headers={"Authorization": EXAMPLE_AUTH_KEY})
    assert response.status_code == 200
    assert response.data == b"OK"


def test_show_config(rest_client):
    """Test the show config endpoint"""
    response = rest_client.get(
        "/", headers={"Authorization": EXAMPLE_AUTH_KEY})
    config_info = CONFIG.copy()
    config_info.pop("api_keys")
    assert response.status_code == 200
    assert response.data.decode("utf-8") == json.dumps(config_info, indent=4)
    assert response.headers["Content-Type"] == "application/json"
    # make sure indent is right
    assert response.data.decode("utf-8") != json.dumps(config_info, indent=2)


def test_show_config_without_api_keys(rest_client):
    """Make sure the show config endpoint does not show api keys"""
    response = rest_client.get(
        "/", headers={"Authorization": EXAMPLE_AUTH_KEY})
    assert response.status_code == 200
    assert "api_keys" not in response.data.decode("utf-8")
    assert response.data.decode("utf-8") != json.dumps(CONFIG, indent=4)


def test_show_config_unauthorized(rest_client):
    """Test the show config endpoint with an invalid auth key"""
    response = rest_client.get("/", headers={"Authorization": "INVALID_KEY"})
    assert response.status_code == 401
    assert "Unauthorized" in response.data.decode("utf-8")


def test_post_transcription(rest_client, cleanup_data):
    """Test the post transcription endpoint"""
    # post with a audio file in the body
    with open(EXAMPLE_AUDIO_FILE_PATH, "rb") as audio_file:
        response = rest_client.post(
            "/transcriptions",
            headers={"Authorization": EXAMPLE_AUTH_KEY},
            data={"file": audio_file},
            content_type="multipart/form-data",
        )

    response_dict = response.get_json()

    assert response.headers["Content-Type"] == "application/json"
    assert response.status_code == 200
    assert response_dict["settings"] is None
    assert response_dict["status"] == "in_query"
    assert response_dict["transcription_id"] is not None
    assert ("start_time" in response_dict) is True
    assert (
        DATA_HANDLER.get_audio_file_path_by_id(
            response_dict["transcription_id"])
        is not None
    )
    status_file = DATA_HANDLER.get_status_file_by_id(
        response_dict["transcription_id"])
    assert status_file is not None
    assert status_file["status"] == "in_query"
    assert status_file["settings"] is None
    assert status_file["status"] == "in_query"
    assert status_file["transcription_id"] is not None
    assert ("start_time" in status_file) is True


def test_post_transcription_without_file(rest_client, cleanup_data):
    """Test the post transcription endpoint without a file"""
    response = rest_client.post(
        "/transcriptions", headers={"Authorization": EXAMPLE_AUTH_KEY})
    assert response.status_code == 400
    assert response.data.decode("utf-8") == "No file posted"


def test_post_transcription_with_wrong_file(rest_client, cleanup_data):
    """Test the post transcription endpoint without a file"""
    with open(EXAMPLE_AUDIO_FILE_PATH, "rb") as audio_file:
        response = rest_client.post(
            "/transcriptions",
            headers={"Authorization": EXAMPLE_AUTH_KEY},
            data={"file1": audio_file},
            content_type="multipart/form-data",
        )
    assert response.status_code == 400
    assert response.data.decode("utf-8") == "No file posted"


def test_get_transcriptions_id(rest_client, cleanup_data):
    """Test the get transcription id endpoint"""
    with open(EXAMPLE_AUDIO_FILE_PATH, "rb") as audio_file:
        response_post = rest_client.post(
            "/transcriptions",
            headers={"Authorization": EXAMPLE_AUTH_KEY},
            data={"file": audio_file},
            content_type="multipart/form-data",
        )
    response_dict_post = response_post.get_json()
    transcription_id = response_dict_post["transcription_id"]
    response = rest_client.get(
        f"/transcriptions/{transcription_id}", headers={"Authorization": EXAMPLE_AUTH_KEY}
    )
    response_dict = response.get_json()
    assert response.headers["Content-Type"] == "application/json"
    assert response.status_code == 200
    assert response_dict["settings"] is None
    assert response_dict["model"] is None
    assert response_dict["status"] == "in_query"
    assert response_dict["transcription_id"] is not None
    assert ("start_time" in response_dict) is True
    assert response_dict == response_dict_post


def test_get_transcriptions_id_not_found(rest_client, cleanup_data):
    """Test the get transcription id endpoint with a not existing id"""
    response = rest_client.get(
        "/transcriptions/123456789", headers={"Authorization": EXAMPLE_AUTH_KEY}
    )
    assert response.status_code == 404
    assert response.data.decode("utf-8") == "Transcription ID not found"


def test_get_transcriptions_without_files(rest_client):
    """Test the get transcriptions endpoint without files"""
    response = rest_client.get(
        "/transcriptions", headers={"Authorization": EXAMPLE_AUTH_KEY})
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/json"
    assert response.get_json() == []


def test_get_transcriptions_with_files(rest_client, cleanup_data):
    """Test the get transcription id endpoint with files"""
    with open(EXAMPLE_AUDIO_FILE_PATH, "rb") as audio_file:
        response_post = rest_client.post(
            "/transcriptions",
            headers={"Authorization": EXAMPLE_AUTH_KEY},
            data={"file": audio_file},
            content_type="multipart/form-data",
        )
    response_dict_post = response_post.get_json()
    transcription_id = response_dict_post["transcription_id"]
    response_get = rest_client.get(
        f"/transcriptions/{transcription_id}",
        headers={"Authorization": EXAMPLE_AUTH_KEY},
    )
    assert response_get.headers["Content-Type"] == "application/json"
    assert response_get.status_code == 200
    response_dict_get = response_get.get_json()
    assert "transcription_id" in response_dict_get
    assert response_dict_get["transcription_id"] == transcription_id


def test_invalid_auth_key(rest_client):
    """Test the get transcriptions endpoint with an invalid auth key"""
    response = rest_client.get(
        "/transcriptions", headers={"Authorization": "INVALID_KEY"})
    assert response.status_code == 401
    assert "Unauthorized" in response.data.decode("utf-8")


def test_post_transcription_with_settings_model(rest_client, cleanup_data):
    """
    Test the get transcription id endpoint
    with settings and model in data
    """
    with open(EXAMPLE_AUDIO_FILE_PATH, "rb") as audio_file:
        response_post = rest_client.post(
            "/transcriptions",
            headers={"Authorization": EXAMPLE_AUTH_KEY},
            data={"settings": '{"test": "test"}',
                  "model": "tiny", "file": audio_file},
            content_type="multipart/form-data",
        )
    response_dict_post = response_post.get_json()
    transcription_id = response_dict_post["transcription_id"]
    response = rest_client.get(
        f"/transcriptions/{transcription_id}", headers={"Authorization": EXAMPLE_AUTH_KEY}
    )
    response_dict = response.get_json()
    assert response.headers["Content-Type"] == "application/json"
    assert response.status_code == 200
    assert response_dict["settings"] == {"test": "test"}
    assert response_dict["model"] == "tiny"
    assert response_dict["status"] == "in_query"
    assert response_dict["transcription_id"] is not None
    assert ("start_time" in response_dict) is True
    assert response_dict == response_dict_post


def test_post_transc_with_tomany_audio_files_stored_not_including_model(
    rest_client, cleanup_data
):
    """
    Test the post transcription endpoint
    with to many audio files stored in the queue
    It should still allow to post a transcription without a model specified
    """
    with open(EXAMPLE_AUDIO_FILE_PATH, "rb") as audio_file:
        response = rest_client.post(
            "/transcriptions",
            headers={"Authorization": EXAMPLE_AUTH_KEY},
            data={"file": audio_file},
            content_type="multipart/form-data",
        )
    assert response.status_code == 200
    with open(EXAMPLE_AUDIO_FILE_PATH, "rb") as audio_file:
        response = rest_client.post(
            "/transcriptions",
            headers={"Authorization": EXAMPLE_AUTH_KEY},
            data={"file": audio_file},
            content_type="multipart/form-data",
        )
    response_dict = response.get_json()
    assert response.headers["Content-Type"] == "application/json"
    assert response.status_code == 200
    assert response_dict["status"] == "in_query"
    assert response_dict["transcription_id"] is not None

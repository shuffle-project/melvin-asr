"""This File contains tests for the Rest_app endpoints."""
# ignore unused-import because of pytest fixtures
# ruff: noqa: F811
# ruff: noqa: F401
import os

import pytest
from fastapi.testclient import TestClient  # Import TestClient from FastAPI

from src.helper.config import CONFIG
from src.helper.data_handler import DataHandler
from src.rest.app import app

EXAMPLE_AUDIO_FILE_PATH = os.path.join(
    os.getcwd(), "src", "helper", "test_base", "example.wav")
EXAMPLE_AUTH_KEY = CONFIG["api_keys"][0]
DATA_HANDLER = DataHandler()


@pytest.fixture
def rest_client():
    """Create a FastAPI test client using TestClient"""
    client = TestClient(app)
    yield client


@pytest.fixture(autouse=True)
def clear_transcriptions_before_test(rest_client):
    """Ensure all transcriptions are cleared before each test"""
    DATA_HANDLER.clean_up_audio_and_status_files()


@pytest.fixture
def transcription_id(rest_client):
    """Fixture for posting a transcription and retrieving its ID"""
    with open(EXAMPLE_AUDIO_FILE_PATH, "rb") as audio_file:
        response = rest_client.post(
            "/transcriptions",
            headers={"Authorization": EXAMPLE_AUTH_KEY},
            files={"file": audio_file},
        )
    response_dict = response.json()
    return response_dict["transcription_id"]


def test_health_check(rest_client):
    """Test the health check endpoint"""
    response = rest_client.get(
        "/health", headers={"Authorization": EXAMPLE_AUTH_KEY})
    assert response.status_code == 200


def test_show_config(rest_client):
    """Test the show config endpoint"""
    response = rest_client.get(
        "/", headers={"Authorization": EXAMPLE_AUTH_KEY})
    config_info = CONFIG.copy()
    config_info.pop("api_keys", None)  # Exclude api_keys
    assert response.status_code == 200
    assert response.json() == config_info


def test_show_config_unauthorized(rest_client):
    """Test the show config endpoint with an invalid auth key"""
    response = rest_client.get("/", headers={"Authorization": "INVALID_KEY"})
    assert response.status_code == 401
    assert "Unauthorized" in response.json().get("detail", "")


def test_post_transcription(rest_client):
    """Test the post transcription endpoint"""
    with open(EXAMPLE_AUDIO_FILE_PATH, "rb") as audio_file:
        response = rest_client.post(
            "/transcriptions",
            headers={"Authorization": EXAMPLE_AUTH_KEY},
            files={"file": audio_file},
        )
    response_dict = response.json()
    assert response.status_code == 200
    assert response_dict["status"] == "in_query"
    assert "transcription_id" in response_dict
    assert DATA_HANDLER.get_audio_file_path_by_id(
        response_dict["transcription_id"]) is not None
    assert DATA_HANDLER.get_status_file_by_id(
        response_dict["transcription_id"]) is not None


def test_post_transcription_without_file(rest_client):
    """Test the post transcription endpoint without a file"""
    response = rest_client.post(
        "/transcriptions", headers={"Authorization": EXAMPLE_AUTH_KEY})
    assert response.status_code == 422


def test_post_transcription_with_wrong_file(rest_client):
    """Test the post transcription endpoint with an incorrect file key"""
    with open(EXAMPLE_AUDIO_FILE_PATH, "rb") as audio_file:
        response = rest_client.post(
            "/transcriptions",
            headers={"Authorization": EXAMPLE_AUTH_KEY},
            files={"file1": audio_file},
        )
    assert response.status_code == 422


def test_get_transcriptions_id(rest_client, transcription_id):
    """Test the get transcription by ID endpoint"""
    response = rest_client.get(
        f"/transcriptions/{transcription_id}", headers={"Authorization": EXAMPLE_AUTH_KEY}
    )
    response_dict = response.json()
    assert response.status_code == 200
    assert response_dict["status"] == "in_query"
    assert response_dict["transcription_id"] == transcription_id


def test_get_transcriptions_id_not_found(rest_client):
    """Test the get transcription ID endpoint with a non-existent ID"""
    response = rest_client.get(
        "/transcriptions/123456789", headers={"Authorization": EXAMPLE_AUTH_KEY})
    assert response.status_code == 404
    assert response.json().get("detail") == "Transcription ID not found"


def test_get_transcriptions_without_files(rest_client):
    """Test the get transcriptions endpoint without any transcriptions"""

    response = rest_client.get(
        "/transcriptions", headers={"Authorization": EXAMPLE_AUTH_KEY})
    assert response.status_code == 200
    assert response.json() == []


def test_post_transcription_with_settings_model(rest_client):
    """Test the post transcription endpoint with settings and model"""
    with open(EXAMPLE_AUDIO_FILE_PATH, "rb") as audio_file:
        response = rest_client.post(
            "/transcriptions",
            headers={"Authorization": EXAMPLE_AUTH_KEY},
            data={"settings": '{"test": "test"}', "model": "tiny"},
            files={"file": audio_file},
        )
    response_dict = response.json()
    transcription_id = response_dict["transcription_id"]
    response = rest_client.get(
        f"/transcriptions/{transcription_id}", headers={"Authorization": EXAMPLE_AUTH_KEY})
    response_dict = response.json()
    assert response.status_code == 200
    assert response_dict["settings"] == {"test": "test"}
    assert response_dict["model"] == "tiny"
    assert response_dict["status"] == "in_query"
    assert response_dict["transcription_id"] == transcription_id


# def test_invalid_auth_key(rest_client):
#     """Test the get transcriptions endpoint with an invalid auth key"""
#     response = rest_client.get(
#         "/transcriptions", headers={"Authorization": "INVALID_KEY"})
#     assert response.status_code == 401
#     assert "Unauthorized" in response.json().get("detail", "")

#     def test_post_transcription_with_settings_model(rest_client, cleanup_data):
#     """
#     Test the get transcription id endpoint
#     with settings and model in data
#     """
#     with open(EXAMPLE_AUDIO_FILE_PATH, "rb") as audio_file:
#         response_post = rest_client.post(
#             "/transcriptions",
#             headers={"Authorization": EXAMPLE_AUTH_KEY},
#             data={"settings": '{"test": "test"}',
#                   "model": "tiny", "file": audio_file},
#             content_type="multipart/form-data",
#         )
#     response_dict_post = response_post.get_json()
#     transcription_id = response_dict_post["transcription_id"]
#     response = rest_client.get(
#         f"/transcriptions/{transcription_id}", headers={"Authorization": EXAMPLE_AUTH_KEY}
#     )
#     response_dict = response.get_json()
#     assert response.headers["Content-Type"] == "application/json"
#     assert response.status_code == 200
#     assert response_dict["settings"] == {"test": "test"}
#     assert response_dict["model"] == "tiny"
#     assert response_dict["status"] == "in_query"
#     assert response_dict["transcription_id"] is not None
#     assert ("start_time" in response_dict) is True
#     assert response_dict == response_dict_post


# def test_post_transc_with_tomany_audio_files_stored_not_including_model(
#     rest_client, cleanup_data
# ):
#     """
#     Test the post transcription endpoint
#     with to many audio files stored in the queue
#     It should still allow to post a transcription without a model specified
#     """
#     with open(EXAMPLE_AUDIO_FILE_PATH, "rb") as audio_file:
#         response = rest_client.post(
#             "/transcriptions",
#             headers={"Authorization": EXAMPLE_AUTH_KEY},
#             data={"file": audio_file},
#             content_type="multipart/form-data",
#         )
#     assert response.status_code == 200
#     with open(EXAMPLE_AUDIO_FILE_PATH, "rb") as audio_file:
#         response = rest_client.post(
#             "/transcriptions",
#             headers={"Authorization": EXAMPLE_AUTH_KEY},
#             data={"file": audio_file},
#             content_type="multipart/form-data",
#         )
#     response_dict = response.get_json()
#     assert response.headers["Content-Type"] == "application/json"
#     assert response.status_code == 200
#     assert response_dict["status"] == "in_query"
#     assert response_dict["transcription_id"] is not None

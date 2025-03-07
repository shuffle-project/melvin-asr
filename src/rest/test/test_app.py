"""This File contains tests for the Rest_app endpoints."""

# ignore unused-import because of pytest fixtures
# ruff: noqa: F811
# ruff: noqa: F401
import json
import os

import pytest
from fastapi.testclient import TestClient  # Import TestClient from FastAPI

from src.helper.config import CONFIG
from src.helper.data_handler import DataHandler
from src.helper.test_base.cleanup_data_fixture import cleanup_data  # is required
from src.rest.app import app

EXAMPLE_AUDIO_FILE_PATH = os.path.join(
    os.getcwd(), "src", "helper", "test_base", "example.wav"
)
EXAMPLE_AUTH_KEY = CONFIG["api_keys"][0]
DATA_HANDLER = DataHandler()

EXAMPLE_TRANSCRIPT_PATH = os.path.join(
    os.getcwd(), "src", "helper", "test_base", "example.json"
)

EXAMPLE_TRANSCRIPT = json.load(open(EXAMPLE_TRANSCRIPT_PATH, "r"))


@pytest.fixture
def rest_client():
    """Create a FastAPI test client using TestClient"""
    client = TestClient(app)
    yield client


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
    response = rest_client.get("/health", headers={"Authorization": EXAMPLE_AUTH_KEY})
    assert response.status_code == 200


def test_show_config(rest_client):
    """Test the show config endpoint"""
    response = rest_client.get("/", headers={"Authorization": EXAMPLE_AUTH_KEY})
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
    assert (
        DATA_HANDLER.get_audio_file_path_by_id(response_dict["transcription_id"])
        is not None
    )
    assert (
        DATA_HANDLER.get_status_file_by_id(response_dict["transcription_id"])
        is not None
    )


def test_post_transcription_without_file(rest_client):
    """Test the post transcription endpoint without a file"""
    response = rest_client.post(
        "/transcriptions", headers={"Authorization": EXAMPLE_AUTH_KEY}
    )
    assert response.status_code == 422

def test_post_transcription_with_unconfigured_model(rest_client):
    """Test the post transcription endpoint with a model that has no configured runner"""
    with open(EXAMPLE_AUDIO_FILE_PATH, "rb") as audio_file:
        response = rest_client.post(
            "/transcriptions",
            headers={"Authorization": EXAMPLE_AUTH_KEY},
            files={"file": audio_file},
            data={"model": "mini-big-123-v5-alpha"},
        )
    assert response.status_code == 418


def test_post_transcription_with_wrong_file(rest_client):
    """Test the post transcription endpoint with an incorrect file key"""
    with open(EXAMPLE_AUDIO_FILE_PATH, "rb") as audio_file:
        response = rest_client.post(
            "/transcriptions",
            headers={"Authorization": EXAMPLE_AUTH_KEY},
            files={"file1": audio_file},
        )
    assert response.status_code == 422

def test_post_transcription_align(rest_client):
    """Test the post transcription endpoint"""
    with open(EXAMPLE_AUDIO_FILE_PATH, "rb") as audio_file:
        response = rest_client.post(
            "/transcriptions",
            headers={"Authorization": EXAMPLE_AUTH_KEY},
            files={"file": audio_file},
            data={"task":"align", "text":"And so, my fellow Americans: ask not what your country can do for you — ask what you can do for your country.'"}
        )
    response_dict = response.json()
    assert response.status_code == 200
    assert response_dict["status"] == "in_query"
    assert "transcription_id" in response_dict
    assert (
        DATA_HANDLER.get_audio_file_path_by_id(response_dict["transcription_id"])
        is not None
    )
    assert (
        DATA_HANDLER.get_status_file_by_id(response_dict["transcription_id"])
        is not None
    )

def test_post_transcription_align_no_text(rest_client):
    """Test the post transcription endpoint"""
    with open(EXAMPLE_AUDIO_FILE_PATH, "rb") as audio_file:
        response = rest_client.post(
            "/transcriptions",
            headers={"Authorization": EXAMPLE_AUTH_KEY},
            files={"file": audio_file},
            data={"task":"align"}
        )
    assert response.status_code == 400

def test_get_transcriptions_id(rest_client, transcription_id):
    """Test the get transcription by ID endpoint"""
    response = rest_client.get(
        f"/transcriptions/{transcription_id}",
        headers={"Authorization": EXAMPLE_AUTH_KEY},
    )
    response_dict = response.json()
    assert response.status_code == 200
    assert response_dict["status"] == "in_query"
    assert response_dict["transcription_id"] == transcription_id


def test_get_transcriptions_id_not_found(rest_client):
    """Test the get transcription ID endpoint with a non-existent ID"""
    response = rest_client.get(
        "/transcriptions/123456789", headers={"Authorization": EXAMPLE_AUTH_KEY}
    )
    assert response.status_code == 404
    assert response.json().get("detail") == "Transcription ID not found"


def test_get_transcriptions_without_files(rest_client):
    """Test the get transcriptions endpoint without any transcriptions"""
    response = rest_client.get(
        "/transcriptions", headers={"Authorization": EXAMPLE_AUTH_KEY}
    )
    assert response.status_code == 200
    assert response.json() == []


def test_post_transcription_with_settings_model(rest_client):
    """Test the post transcription endpoint with settings and model"""
    configured_model = CONFIG["rest_models"][0]
    with open(EXAMPLE_AUDIO_FILE_PATH, "rb") as audio_file:
        response = rest_client.post(
            "/transcriptions",
            headers={"Authorization": EXAMPLE_AUTH_KEY},
            data={"settings": '{"test": "test"}', "model": configured_model},
            files={"file": audio_file},
        )
    assert response.status_code == 200
    response_dict = response.json()
    transcription_id = response_dict["transcription_id"]
    response = rest_client.get(
        f"/transcriptions/{transcription_id}",
        headers={"Authorization": EXAMPLE_AUTH_KEY},
    )
    response_dict = response.json()
    assert response_dict["settings"] == {"test": "test"}
    assert response_dict["model"] == configured_model
    assert response_dict["status"] == "in_query"
    assert response_dict["transcription_id"] == transcription_id


def test_invalid_auth_key(rest_client):
    """Test the get transcriptions endpoint with an invalid auth key"""
    response = rest_client.get(
        "/transcriptions", headers={"Authorization": "INVALID_KEY"}
    )
    assert response.status_code == 401
    assert "Unauthorized" in response.json().get("detail", "")


def test_post_transc_with_too_many_audio_files_stored_not_including_model(rest_client):
    """
    Test the post transcription endpoint
    with too many audio files stored in the queue
    It should still allow to post a transcription without a model specified
    """
    with open(EXAMPLE_AUDIO_FILE_PATH, "rb") as audio_file:
        response = rest_client.post(
            "/transcriptions",
            headers={"Authorization": EXAMPLE_AUTH_KEY},
            files={"file": audio_file},
        )
    assert response.status_code == 200
    with open(EXAMPLE_AUDIO_FILE_PATH, "rb") as audio_file:
        response = rest_client.post(
            "/transcriptions",
            headers={"Authorization": EXAMPLE_AUTH_KEY},
            files={"file": audio_file},
        )
    response_dict = response.json()
    assert response.headers["Content-Type"] == "application/json"
    assert response.status_code == 200
    assert response_dict["status"] == "in_query"
    assert response_dict["transcription_id"] is not None


def test_translation_with_wrong_language(rest_client):
    """Test the translation endpoint with a wrong language"""
    response = rest_client.post(
        "/translate/falsch",
        headers={"Authorization": EXAMPLE_AUTH_KEY},
        json=EXAMPLE_TRANSCRIPT,
    )
    assert response.status_code == 400


def test_working_translation(rest_client):
    """Test the translation endpoint with a working translation"""
    response = rest_client.post(
        "/translate/de",
        headers={"Authorization": EXAMPLE_AUTH_KEY},
        json=EXAMPLE_TRANSCRIPT,
    )
    assert response.status_code == 200
    assert response.json()["id"] is not None


# TODO: (after SM4T implementation)
# def test_fail_translate_with_invalid_original_language(rest_client):
#     """Test the translation endpoint with a working translation"""
#     response = rest_client.post(
#         "/translate/de",
#         headers={"Authorization ": EXAMPLE_AUTH_KEY},
#         json=EXAMPLE_TRANSCRIPT,
#     )
#     assert True
#     # assert response.status_code == 200

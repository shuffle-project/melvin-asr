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
EXAMPLE_RESAMPLED_AUDIO_FILE_PATH = os.path.join(
    os.getcwd(), "src", "helper", "test_base", "example_resampled.wav"
)
EXAMPLE_JSON_FILE_PATH = os.path.join(
    os.getcwd(), "src", "helper", "test_base", "example.json"
)
EXAMPLE_AUTH_KEY = CONFIG["api_keys"][0]
DATA_HANDLER = DataHandler()

EXAMPLE_TRANSCRIPT_PATH = os.path.join(
    os.getcwd(), "src", "helper", "test_base", "example_translation.json"
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


def check_post_transcription_response(response):
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


def check_transcription_with_model(rest_client, model: str):
    with open(EXAMPLE_AUDIO_FILE_PATH, "rb") as audio_file:
        response = rest_client.post(
            "/transcriptions",
            headers={"Authorization": EXAMPLE_AUTH_KEY},
            files={"file": audio_file},
            data={"model": model},
        )
    check_post_transcription_response(response)

    assert response.json()["model"] == model


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
    check_post_transcription_response(response)


def test_post_transcription_with_different_supported_models(rest_client):
    """Test the post transcription endpoint with different models -> does model loading work"""
    check_transcription_with_model(rest_client, CONFIG["rest_runner"][0]["models"][0])
    check_transcription_with_model(rest_client, CONFIG["rest_runner"][0]["models"][1])


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


def test_post_transcription_with_wrong_file_type(rest_client):
    """Test the post transcription endpoint"""
    with open(EXAMPLE_JSON_FILE_PATH, "rb") as audio_file:
        response = rest_client.post(
            "/transcriptions",
            headers={"Authorization": EXAMPLE_AUTH_KEY},
            files={"file": audio_file},
        )
        assert response.status_code == 400


def test_post_transcription_with_wrong_file_type_but_valid_name(rest_client):
    """Test the post transcription endpoint"""
    with open(EXAMPLE_JSON_FILE_PATH, "rb") as audio_file:
        response = rest_client.post(
            "/transcriptions",
            headers={"Authorization": EXAMPLE_AUTH_KEY},
            files={"file": ("sample.wav", audio_file)},
        )
        assert response.status_code == 400


def test_post_transcription_with_wrong_sample_rate_file(rest_client):
    """Test the post transcription endpoint"""
    with open(EXAMPLE_RESAMPLED_AUDIO_FILE_PATH, "rb") as audio_file:
        response = rest_client.post(
            "/transcriptions",
            headers={"Authorization": EXAMPLE_AUTH_KEY},
            files={"file": audio_file},
        )
        assert response.status_code == 400


def test_post_transcription_align(rest_client):
    with open(EXAMPLE_AUDIO_FILE_PATH, "rb") as audio_file:
        response = rest_client.post(
            "/transcriptions",
            headers={"Authorization": EXAMPLE_AUTH_KEY},
            files={"file": audio_file},
            data={
                "task": "align",
                "text": "And so, my fellow Americans: ask not what your country can do for you — ask what you can do for your country.'",
            },
        )
    check_post_transcription_response(response)


def test_post_transcription_forced_align(rest_client):
    with open(EXAMPLE_AUDIO_FILE_PATH, "rb") as audio_file:
        response = rest_client.post(
            "/transcriptions",
            headers={"Authorization": EXAMPLE_AUTH_KEY},
            files={"file": audio_file},
            data={
                "task": "force-align",
                "text": "And so, my fellow Americans: ask not what your country can do for you — ask what you can do for your country.'",
            },
        )
    check_post_transcription_response(response)


def test_post_transcription_align_no_text(rest_client):
    """Test the post transcription endpoint"""
    with open(EXAMPLE_AUDIO_FILE_PATH, "rb") as audio_file:
        response = rest_client.post(
            "/transcriptions",
            headers={"Authorization": EXAMPLE_AUTH_KEY},
            files={"file": audio_file},
            data={"task": "align"},
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


def test_translation_with_unsupported_target_language(rest_client):
    """Test the translation endpoint with a wrong language"""
    invalid_payload = EXAMPLE_TRANSCRIPT.copy()
    invalid_payload["target_language"] = "wrong"
    response = rest_client.post(
        "/translate",
        headers={"Authorization": EXAMPLE_AUTH_KEY},
        json=invalid_payload,
    )
    assert response.status_code == 400


def test_working_translation(rest_client):
    """Test the translation endpoint with a working translation"""
    response = rest_client.post(
        "/translate",
        headers={"Authorization": EXAMPLE_AUTH_KEY},
        json=EXAMPLE_TRANSCRIPT,
    )
    assert response.status_code == 200
    assert response.json()["id"] is not None


def test_fail_translate_with_nsupported_original_language(rest_client):
    """Test the translation endpoint with a working translation"""
    invalid_payload = EXAMPLE_TRANSCRIPT.copy()
    invalid_payload["language"] = "wrong"

    response = rest_client.post(
        "/translate",
        headers={"Authorization": EXAMPLE_AUTH_KEY},
        json=invalid_payload,
    )
    assert response.status_code == 400


def test_using_faulty_translations_method(rest_client):
    """Test the translation endpoint with a working translation"""
    invalid_payload = EXAMPLE_TRANSCRIPT.copy()
    invalid_payload["method"] = "default"

    response = rest_client.post(
        "/translate",
        headers={"Authorization": EXAMPLE_AUTH_KEY},
        json=invalid_payload,
    )
    assert response.status_code == 200
    assert response.json()["id"] is not None


def test_using_no_translations_method(rest_client):
    """Test the translation endpoint with a working translation"""
    invalid_payload = EXAMPLE_TRANSCRIPT.copy()
    del invalid_payload["method"]

    response = rest_client.post(
        "/translate",
        headers={"Authorization": EXAMPLE_AUTH_KEY},
        json=invalid_payload,
    )
    assert response.status_code == 200
    assert response.json()["id"] is not None

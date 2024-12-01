import os
import wave
from unittest.mock import Mock, patch

import pytest
from fastapi.testclient import TestClient

from src.websocket.websockets_server import WebSocketServer, app

MOCK_CONFIG = {
    "websocket_stream": {
        "cuda": {
            "active": False,
            "model": "tiny",
            "device_index": 0,
            "worker_seats": 1,
        },
        "cpu": {"active": True, "model": "tiny", "cpu_threads": 1, "worker_seats": 1},
    }
}

EXAMPLE_WAV_FILE = "src/websocket/test/example.wav"

# Test Initialization


def test_websocket_server_initialization():
    server = WebSocketServer(config=MOCK_CONFIG)
    assert server.gpu_config == MOCK_CONFIG["websocket_stream"]["cuda"]
    assert server.cpu_config == MOCK_CONFIG["websocket_stream"]["cpu"]


@patch("src.websocket.stream_transcriber.Transcriber.for_cpu", return_value=Mock())
def test_websocket_server_transcribers(mock_for_cpu):
    server = WebSocketServer(config=MOCK_CONFIG)
    mock_for_cpu.assert_called_once_with(
        model_name="tiny", cpu_threads=1, num_workers=1
    )
    assert server.cpu_transcriber is not None


@pytest.mark.asyncio
async def test_start_stream_and_response_to_text():
    client = TestClient(app)

    with client.websocket_connect("/") as websocket:
        websocket.send_text("Hello")
        response = websocket.receive_text()
        assert response == "control message unknown"


@pytest.mark.asyncio
async def test_send_eof_and_expect_connection_close():
    client = TestClient(app)

    with client.websocket_connect("/") as websocket:
        websocket.send_text("eof")

        try:
            response = websocket.receive_text(timeout=8)
            assert isinstance(response, str)
        except Exception:
            pytest.fail("No response received, expected connection closure.")

        # Check if response file exists in the export directory
        export_dir = "./data/export"
        response_file = os.path.join(export_dir, f"{response}.json")
        assert os.path.isfile(response_file)


@pytest.mark.asyncio
async def test_start_stream_and_response_to_audio_bytes():
    client = TestClient(app)

    # Helper to read WAV file
    def read_wav_file(file_path):
        with wave.open(file_path, "rb") as wav_file:
            return wav_file.readframes(wav_file.getnframes())

    audio_data = read_wav_file(EXAMPLE_WAV_FILE)

    with client.websocket_connect("/") as websocket:
        websocket.send_bytes(audio_data)

        messages = []
        while True:
            try:
                message = websocket.receive_text(timeout=15)
                messages.append(message)
            except Exception:
                break  # Exit on timeout or connection close

        assert len(messages) > 0, "No messages received"
        for message in messages:
            assert isinstance(message, str)
            assert "partial" in message or "result" in message

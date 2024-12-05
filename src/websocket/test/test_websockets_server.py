import asyncio
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
            await asyncio.sleep(5)
            response = websocket.receive_text()
            print(f"Message received, connection is still open: {response}")
            # TODO: how to test the connection is then closed?
            # Ends with a string response, else it would be a json response
            # TODO: can come an empty string? Should be properly validated what comes back?
            response = websocket.receive_text()
            assert isinstance(response, str)
        except Exception as e:
            print(f"Exception: {e}")
            raise
        except RuntimeError as e:
            if "disconnect message" not in str(e):
                raise


# @pytest.mark.asyncio
# async def test_start_stream_and_response_to_audio_bytes():
#     client = TestClient(app)

#     def read_wav_file(file_path):
#         with wave.open(file_path, "rb") as wav_file:
#             return wav_file.readframes(wav_file.getnframes())

#     audio_data = read_wav_file(EXAMPLE_WAV_FILE)
#     with client.websocket_connect("/") as websocket:
#         websocket.send_bytes(audio_data)
#         messages = []
#         while True:
#             try:
#                 message = websocket.receive_json()
#                 print(f"Message received: {message}", flush=True)
#                 messages.append(message)
#             except RuntimeError as e:
#                 if "disconnect message" in str(e):
#                     break
#                 raise
#             except Exception as e:
#                 print(f"Exception: {e}")
#                 raise
#         websocket.close()
#         raise AssertionError(messages)
#         assert len(messages) > 0, "No messages received"

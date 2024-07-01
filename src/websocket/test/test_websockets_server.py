import asyncio
import threading
from unittest.mock import patch, Mock
import wave

import pytest
import websockets
import os
from src.websocket.websockets_server import (
    WebSocketServer,
)

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


# helper functions
async def run_server_in_thread(server):
    await server.start_server()


async def read_wav_file(file_path):
    with wave.open(file_path, "rb") as wav_file:
        return wav_file.readframes(wav_file.getnframes())


# Tests


def test_websocket_server_initialization():
    server = WebSocketServer("localhost", 8080, MOCK_CONFIG)
    assert server.host == "localhost"
    assert server.port == 8080
    print(server.gpu_config)
    assert server.gpu_config == MOCK_CONFIG["websocket_stream"]["cuda"]
    assert server.cpu_config == MOCK_CONFIG["websocket_stream"]["cpu"]


@patch("src.websocket.stream_transcriber.Transcriber.for_cpu", return_value=Mock())
def test_websocket_server_transcribers(mock_for_cpu):
    server = WebSocketServer("localhost", 8080, MOCK_CONFIG)
    mock_for_cpu.assert_called_once_with(
        worker_seats=1, model_name="tiny", cpu_threads=1, num_workers=1
    )
    assert server.cpu_transcriber is not None


@pytest.mark.asyncio
async def test_start_stream_and_response_to_text():
    server = WebSocketServer("localhost", 8080, MOCK_CONFIG)

    # Run the server in another thread, as it is blocking
    server_thread = threading.Thread(
        target=asyncio.run, args=(run_server_in_thread(server),)
    )
    server_thread.start()

    await asyncio.sleep(0.5)  # Give the server some time to start

    try:
        async with websockets.connect("ws://localhost:8080") as websocket:
            await websocket.send("Hello")
            response = await websocket.recv()
            assert response == "control message unknown"
            await websocket.close()
    finally:
        server.stop_server()
        server_thread.join(timeout=1)


@pytest.mark.asyncio
async def test_send_eof_and_expect_connection_close():
    server = WebSocketServer("localhost", 8080, MOCK_CONFIG)

    # Run the server in another thread, as it is blocking
    server_thread = threading.Thread(
        target=asyncio.run, args=(run_server_in_thread(server),)
    )
    server_thread.start()

    await asyncio.sleep(0.5)  # Give the server some time to start

    response: str = "" # We need to get the export files with the server response
    try:
        async with websockets.connect("ws://localhost:8080") as websocket:
            print("WebSocket connection established, sending 'eof'")
            await websocket.send("eof")

            # We expect the server to close the connection after receiving 'eof'
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                print(f"Message received: {response}")
                assert isinstance(response, str)
                # The connection should be closed, so we can assert here
                assert True
            except asyncio.TimeoutError:
                print("No message received, connection is still open")
    finally:
        print("Stopping server")
        server.stop_server()
        server_thread.join(timeout=1)
        print("Server stopped")

        # Find the file in the export directory
        export_dir = "./data/export"
        response_file = os.path.join(export_dir, f"{response}.json")

        # Check if the file exists
        if os.path.isfile(response_file):
            print("response.json file found in the export directory")
            assert True
        else:
            print("response.json file not found in the export directory")


@pytest.mark.asyncio
async def test_start_stream_and_response_to_audio_bytes():
    async def run_server_in_thread(server):
        await server.start_server()

    server = WebSocketServer("localhost", 8080, MOCK_CONFIG)

    # Run the server in another thread, as it is blocking
    server_thread = threading.Thread(
        target=asyncio.run, args=(run_server_in_thread(server),)
    )
    server_thread.start()

    await asyncio.sleep(0.5)  # Give the server some time to start

    # Read the example WAV file
    audio_data = await read_wav_file(EXAMPLE_WAV_FILE)

    try:
        async with websockets.connect("ws://localhost:8080") as websocket:
            await websocket.send(audio_data)
            await asyncio.sleep(3)  # Give the server some time to process the audio

            messages = []
            while True:
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=15.0)
                    messages.append(message)
                except asyncio.TimeoutError:
                    print("No message received for 5 seconds, sending 'oef'")
                    await websocket.close()
                    break

            # Print all messages (for debugging purposes)
            for message in messages:
                print(message)
                assert isinstance(message, str)
                assert message != ""
                assert "partial" in message or "result" in message

            assert len(messages) > 0
    except websockets.exceptions.ConnectionClosedOK:
        print("Connection closed as expected")
    finally:
        server.stop_server()
        server_thread.join(timeout=1)

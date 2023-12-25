"""Test the WebSocket server."""
import asyncio
import os
import multiprocessing
import time
import pytest
import websockets
from websocket.websockets_app import WebSocketServer

# Constants for testing
SERVER_HOST = "localhost"
SERVER_PORT = 1235
current_dir = os.path.dirname(os.path.abspath(__file__))
jfk_wav_path = os.path.join(current_dir, 'jfk.wav')

def run_server():
    """Function to run the WebSocket server."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    ws_server = WebSocketServer(port=SERVER_PORT, host=SERVER_HOST)
    loop.run_until_complete(ws_server.start_server())
    loop.run_forever()

@pytest.fixture(scope='session', autouse=True)
def server():
    """Fixture to start the WebSocket server."""
    # Start the server in a separate process
    print("Websocket starting server")
    server_process = multiprocessing.Process(target=run_server)
    server_process.start()
    print("Websocket server started")

    # Wait for the server to start
    time.sleep(1)  # Adjust as needed

    yield

    # Stop the server process
    server_process.terminate()
    server_process.join()

@pytest.mark.asyncio
async def test_send_audio_data():
    """Test sending audio data to the WebSocket server."""
    # Read the audio data from jfk.wav
    with open(jfk_wav_path, 'rb') as file:
        test_audio_data = file.read()

    print("connecting to server")
    # Connect to the WebSocket server and send test data
    async with websockets.connect(f"ws://{SERVER_HOST}:{SERVER_PORT}") as websocket:
        await websocket.send(test_audio_data)
        response = await websocket.recv()
        print("RESPONSE: " + response)
        assert response == "Transcription timed out"

# Implement other tests as needed

import time
from unittest.mock import Mock, patch

from fastapi.testclient import TestClient
from pydub import AudioSegment

from src.websocket.websockets_server import WebSocketServer, app

TEST_TIMEOUT_SECONDS = 120

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

# Mock values because we dont want to test the transcription model
TRANSCRIPTION_MOCK = {
    "segments": [
        {
            "id": 1,
            "seek": 266,
            "start": 0.3,
            "end": 2.96,
            "text": "This Is A Test !",
            "tokens": [50364, 2438, 11, 291, 519, 11262, 307],
            "temperature": 0,
            "avg_logprob": -0.7055922821164131,
            "compression_ratio": 0.7575757575757576,
            "no_speech_prob": 0.07772325724363327,
            "words": [
                {
                    "start": 0.3,
                    "end": 1.42,
                    "word": "This",
                    "probability": 0.0498960018157959,
                },
                {
                    "start": 1.7,
                    "end": 1.78,
                    "word": "Is",
                    "probability": 0.8493287563323975,
                },
                {
                    "start": 1.78,
                    "end": 2.2,
                    "word": "A",
                    "probability": 0.938616931438446,
                },
                {
                    "start": 2.2,
                    "end": 2.64,
                    "word": "Test",
                    "probability": 0.7141004800796509,
                },
                {
                    "start": 2.64,
                    "end": 2.96,
                    "word": "!",
                    "probability": 0.9338691830635071,
                },
            ],
        }
    ],
    "info": {
        "language": "en",
        "language_probability": 0.9488623142242432,
        "duration": 3.0,
        "duration_after_vad": 2.696,
        "transcription_options": [],  # These are empty because they are irrelevant for us
        "vad_options": [0.5, 250, "Infinity", 2000, 400],
    },
}


# Helper functions
def read_wav_file_into_chunks(file_path, chunk_duration=1000):
    audio = AudioSegment.from_file(file_path)
    chunks = []
    for i in range(0, len(audio), chunk_duration):
        chunks.append(audio[i : i + chunk_duration].raw_data)
    return chunks


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


def test_start_stream_and_response_to_text():
    client = TestClient(app)

    with client.websocket_connect("/") as websocket:
        websocket.send_text("Hello")
        response = websocket.receive_text()
        assert response == "control message unknown"


def test_send_eof_and_expect_connection_close():
    client = TestClient(app)
    with client.websocket_connect("/") as websocket:
        websocket.send_text("eof")
        try:
            response = websocket.receive_text()
            assert isinstance(response, str)
            assert len(response) == 32
        except RuntimeError as e:
            if "disconnect message" not in str(e):
                raise
        except Exception as e:
            print(f"Exception: {e}")
            raise


@patch(
    "src.websocket.stream_transcriber.Transcriber._transcribe",
    return_value=TRANSCRIPTION_MOCK,
)
def test_start_stream_and_response_to_audio_bytes(mock_spock):
    start_time = time.time()
    client = TestClient(app)

    audio_data = read_wav_file_into_chunks(EXAMPLE_WAV_FILE)
    assert len(audio_data) > 0
    with client.websocket_connect("/") as websocket:
        messages = []
        # just walk away when all audio data was send
        # eof test is above
        while time.time() - start_time < TEST_TIMEOUT_SECONDS and len(audio_data) > 0:
            try:
                if len(audio_data) > 0:
                    websocket.send_bytes(audio_data.pop(0))
                message = websocket.receive_json()
                print(f"Message received: {message}", flush=True)
                messages.append(message)
            except RuntimeError as e:
                if "disconnect message" in str(e):
                    break
                raise
            except Exception as e:
                print(f"Exception: {e}")
                raise
        websocket.close()
        if time.time() - start_time > TEST_TIMEOUT_SECONDS:
            raise Exception("Test timeout")

        for message in messages:
            # assert partials
            if "partial" in message:
                assert message == {"partial": "This Is A Test !"}
            else:
                # otherwise this is final
                assert message["text"] == "This Is A Test !"


@patch(
    "src.websocket.stream_transcriber.Transcriber._transcribe",
    return_value=TRANSCRIPTION_MOCK,
)
def test_eof_for_stream_returns_id(mock_spock):
    start_time = time.time()
    client = TestClient(app)

    eof_sent = False

    # Short audio data -> we dont need a lot of data for this test
    audio_data = read_wav_file_into_chunks(EXAMPLE_WAV_FILE)[:5]
    assert len(audio_data) > 0
    with client.websocket_connect("/") as websocket:
        messages = []
        while time.time() - start_time < TEST_TIMEOUT_SECONDS and not eof_sent:
            try:
                if len(audio_data) > 0:
                    websocket.send_bytes(audio_data.pop(0))
                    message = websocket.receive_json()
                else:
                    websocket.send_text("eof")
                    eof_sent = True
                    message = websocket.receive_text()
                print(f"Message received: {message}", flush=True)
                messages.append(message)
            except RuntimeError as e:
                if "disconnect message" in str(e):
                    break
                raise
            except Exception as e:
                print(f"Exception: {e}")
                raise
        websocket.close()
        if time.time() - start_time > TEST_TIMEOUT_SECONDS:
            raise Exception("Test timeout")
        expected_id = messages[-1]
        assert isinstance(expected_id, str)
        # IDs are always of length 32
        assert len(expected_id) == 32

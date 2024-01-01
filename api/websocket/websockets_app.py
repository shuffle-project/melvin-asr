"""WebSocket server to receive audio data from the client."""
import asyncio
import json
import os
import uuid
import websockets
from pydub import AudioSegment
from config import AUDIO_FILE_PATH, STATUS_PATH
from src.helper.convert_save_received_audio_files import convert_to_wav
from src.transcription_request_handling.transcription import (
    Transcription,
    TranscriptionStatusValue,
)

from websocket.websockets_transcriptions_config import WebsocketsTranscriptionsConfig

WAIT_FOR_TRANSCRIPTION = 4  # seconds to wait for transcription
TRANSCRIPTION_TIMEOUT_SLEEP = 60  # seconds to sleep after timeout
TIMEOUT_COUNT = 3  # number of timeouts before stopping the server


class WebSocketServer:
    """Class to handle the WebSocket server"""

    def __init__(self, port=1235, host="localhost"):
        self.server = None
        self.host = host
        self.port = port
        self.config = WebsocketsTranscriptionsConfig()
        self.timeout_counter = 0

    async def start_server(self):
        """Function to start the WebSocket server"""
        async with websockets.serve(self.echo, self.host, self.port):
            print(f"Starting WebSocket server on {self.host}:{self.port}...")
            await asyncio.Future()

    async def echo(self, websocket):
        """Function to handle the WebSocket connection"""
        if self.timeout_counter > TIMEOUT_COUNT:
            await websocket.close()
            await asyncio.sleep(TRANSCRIPTION_TIMEOUT_SLEEP)
            self.timeout_counter = 0

        audio_data = bytearray()
        async for message in websocket:
            audio_data.extend(message)
            break
        await self.handle_transcription(audio_data, websocket)

    async def handle_transcription(self, audio_data, websocket):
        """Initiates the transcription process and waits for the result."""
        # parse and post audio data to runner
        transcription_id = self.post_audio_data(audio_data)
        if transcription_id is None:
            await websocket.send("Error posting audio data")
            return

        # wait for transcription to be ready and send it back to the client
        response = await self.wait_for_transcription(transcription_id)
        if response is None:
            response = "Transcription timed out"
            self.timeout_counter += 1
        else:
            self.timeout_counter = 0

        if isinstance(response, dict):
            await websocket.send(json.dumps(response))
        else:
            await websocket.send(str(response))

    async def wait_for_transcription(
        self, transcription_id, timeout=WAIT_FOR_TRANSCRIPTION
    ):
        """Waits for a specific amount of time for the transcription to be ready."""
        check_interval = 0.1  # Time interval between checks
        total_wait_time = 0

        while total_wait_time < timeout:
            try:
                file_path = os.path.join(
                    os.getcwd() + STATUS_PATH, f"{transcription_id}.json"
                )
                if os.path.exists(file_path):
                    with open(file_path, "r", encoding="utf-8") as file:
                        transcription = json.load(file)
                        if transcription["status"] == "error":
                            return "Transcription error: " + transcription["error_message"]
                        if transcription["status"] == "done":
                            return transcription["transcript"]
                await asyncio.sleep(check_interval)
                total_wait_time += check_interval
            # need to catch all exceptions here
            # pylint: disable=W0718
            except Exception as e:
                print(f"Error wait_for_transcription: {e}")
        return None

    def post_audio_data(self, audio_data):
        """Function to parse the audio data"""
        try:
            audio_segment = AudioSegment(
                data=audio_data, sample_width=2, frame_rate=16000, channels=1
            )
            transcription_id = self.post_wav_to_runner(audio_segment)
        # need to catch all exceptions here
        # pylint: disable=W0718
        except Exception as e:
            print(f"Error post_audio_data: {e}")
            transcription_id = None
        return transcription_id

    def post_wav_to_runner(self, file) -> str:
        """Function to post the WAV file to the runner"""
        transcription = Transcription(uuid.uuid4())
        result = convert_to_wav(file, AUDIO_FILE_PATH, transcription.transcription_id)

        transcription.settings = self.config.get_settings()

        if result["success"] is not True:
            transcription.status = TranscriptionStatusValue.ERROR
            transcription.error_message = result["message"]
            print(f"Error post_wav_to_runner: {result['message']}")

        transcription.save_to_file()
        return transcription.transcription_id

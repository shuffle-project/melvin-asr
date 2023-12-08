"""WebSocket server to receive audio data from the client."""
import asyncio
import json
import os
import time
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

OUTPUT_FILE = os.getcwd() + "/output.wav"
print(OUTPUT_FILE)


class WebSocketServer:
    """Class to handle the WebSocket server"""

    def __init__(self, port=1235, host="localhost", output_file=OUTPUT_FILE):
        self.host = host
        self.port = port
        self.output_file = output_file or os.getcwd() + "/output.wav"
        self.config = WebsocketsTranscriptionsConfig()

    async def start_server(self):
        """Function to start the WebSocket server"""
        async with websockets.serve(self.echo, self.host, self.port):
            print(f"Starting WebSocket server on {self.host}:{self.port}...")
            await asyncio.Future()

    async def echo(self, websocket):
        """Function to handle the WebSocket connection"""
        print("echo starts")
        # receive data
        audio_data = bytearray()
        async for message in websocket:
            audio_data.extend(message)
            break
        await self.handle_transcription(audio_data, websocket)

    async def handle_transcription(self, audio_data, websocket):
        """Fetches incoming audio_data and returns the transcription via websocket"""
        try:
            # Create an AudioSegment from the raw audio data
            audio_segment = AudioSegment(
                data=audio_data, sample_width=2, frame_rate=16000, channels=1
            )
            transcription_id = self.post_wav_to_runner(audio_segment)
        except Exception as e:
            print(f"Error loading audio segment: {e}")
            await websocket.send(f"Error loading audio segment: {e}")

        timeout = 100
        t = 0
        while t < timeout:
            t += 1
            file_path = os.path.join(
                os.getcwd() + STATUS_PATH, f"{transcription_id}.json"
            )
            if os.path.exists(file_path):
                with open(file_path, "r", encoding="utf-8") as file:
                    transcription = json.load(file)
                    print(transcription["status"])
                    if transcription["status"] == "error":
                        await websocket.send(transcription["error_message"])
                        return
                    if transcription["status"] == "done":
                        with open(file_path, "r", encoding="utf-8") as file:
                            text = ""
                            for transcript in transcription["transcript"]["transcription"]:
                                text += "\n" + transcript["text"] + "\n"
                            await websocket.send(text)
                            return
                    else:
                        time.sleep(0.1)
                time.sleep(0.1)
            else:
                await websocket.send("Transcription not found")
                return

    def post_wav_to_runner(self, file) -> str:
        """Function to post the WAV file to the runner"""
        transcription = Transcription(uuid.uuid4())
        result = convert_to_wav(file, AUDIO_FILE_PATH, transcription.transcription_id)

        transcription.settings = self.config.get_settings()

        if result["success"] is not True:
            transcription.status = TranscriptionStatusValue.ERROR
            transcription.error_message = result["message"]

        transcription.save_to_file()
        return transcription.transcription_id

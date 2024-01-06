"""Sends audio data from a file to the websocket server."""
import asyncio
import websockets
from pydub import AudioSegment

class FileAudioSender:
    """Sends audio data from a file to the websocket server."""

    def __init__(self, file_path='./input.wav'):
        self.file_path = file_path

    async def send_file_as_websocket(self):
        """Sends the input file to the WebSocket server."""
        audio_segment = AudioSegment.from_file(self.file_path, format="wav")
        resampled_audio = audio_segment.set_frame_rate(16000).set_channels(1)
        audio_data = resampled_audio.raw_data

        async with websockets.connect("ws://localhost:1338") as websocket:
            await websocket.send(audio_data)
            print("Sent audio data")
            response = await websocket.recv()
            print("Received response:", response)

    def start_sending(self):
        """Starts sending the audio file."""
        asyncio.run(self.send_file_as_websocket())

if __name__ == "__main__":
    sender = FileAudioSender()
    sender.start_sending()

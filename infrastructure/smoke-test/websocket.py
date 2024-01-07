"""Sends audio data from a file to the websocket server."""
import asyncio
import sys
import websockets
from pydub import AudioSegment

# This script sends audio data from a specified file to a WebSocket server on a specified port.

# Usage:
# The script is run from the command line.
# A port number can be provided as a CLI argument. If no port is given, it defaults to 1338.
# The audio file to be sent is named 'input.wav' in the script's directory.


class FileAudioSender:
    """Class to send audio data from a file to the websocket server."""

    def __init__(self, file_path="./input.wav", port=1338):
        self.file_path, self.port = file_path, port

    async def send_file(self):
        """Sends the audio file to the websocket server."""
        audio = AudioSegment.from_file(self.file_path, format="wav")
        audio_data = audio.set_frame_rate(16000).set_channels(1).raw_data
        async with websockets.connect(f"ws://localhost:{self.port}") as ws:
            await ws.send(audio_data)
            print("Sent audio data, received response:", await ws.recv())

    def start_sending(self):
        """Starts the sending process."""
        asyncio.run(self.send_file())


if __name__ == "__main__":
    arg_port = int(sys.argv[1]) if len(sys.argv) > 1 else 1338
    FileAudioSender(port=arg_port).start_sending()

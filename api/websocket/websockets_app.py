"""WebSocket server to receive audio data from the client."""
import asyncio
import os
import wave
import websockets

OUTPUT_FILE = os.getcwd() + "/output.wav"
print(OUTPUT_FILE)


class WebSocketServer:
    """Class to handle the WebSocket server"""

    def __init__(self, port=1235, host="localhost", output_file=OUTPUT_FILE):
        self.host = host
        self.port = port
        self.output_file = output_file or os.getcwd() + "/output.wav"

    def bytes_to_wav(self, data):
        """Converts an audio byte stream to a 16kHz mono WAV file."""
        with wave.open(self.output_file, "wb") as wav_file:
            # wave.open does return Wave_write object, pylint does not recognize it
            # pylint: disable=E1101
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 16-bit samples
            wav_file.setframerate(16000)
            wav_file.writeframes(data)

    async def echo(self, websocket):
        """Function to handle the WebSocket messaging"""
        print("Connection from", websocket.remote_address)
        audio_data = bytearray()
        async for message in websocket:
            if isinstance(message, str) and 'config' in message:
                print("Config received:", message)
                await websocket.send("Config received")
                break
            if isinstance(message, str) and message == "END":
                self.bytes_to_wav(audio_data)
                await websocket.send("File processed and saved as WAV")
                break
            audio_data.extend(message)

    async def start_server(self):
        """Function to start the WebSocket server"""
        async with websockets.serve(self.echo, self.host, self.port):
            print(f"Starting WebSocket server on {self.host}:{self.port}...")
            await asyncio.Future()  # Run forever

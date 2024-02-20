"""A simple WebSocket server that echoes received messages back."""
import asyncio
import os
import wave
import websockets

print("Starting Web Socket server...")

OUTPUT_FILE = os.getcwd() + "/output.wav"
print(OUTPUT_FILE)


def bytes_to_wav(data, outfile=OUTPUT_FILE):
    """Converts an audio byte stream to a 16kHz mono WAV file."""
    with wave.open(outfile, "wb") as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16-bit samples
        wav_file.setframerate(16000)
        wav_file.writeframes(data)


async def echo(websocket):
    """Echoes the received message back."""
    print("Connection from", websocket.remote_address)
    audio_data = bytearray()
    async for message in websocket:
        if message == "END":
            bytes_to_wav(audio_data)
            await websocket.send("File processed and saved as WAV")
            break
        audio_data.extend(message)


async def main():
    """Starts the WebSocket server."""
    async with websockets.serve(echo, "localhost", 1338):
        await asyncio.Future()  # Run forever


if __name__ == "__main__":
    asyncio.run(main())

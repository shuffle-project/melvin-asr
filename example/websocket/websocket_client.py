""" Example of sending a file to the WebSocket server using the websockets library. """
import asyncio
import os
import subprocess
import sys
import websockets

print("Starting WebSocket client...")

INPUT_FILE = os.getcwd() + "/input.wav"
print(INPUT_FILE)

# Check if the input file exists
if not os.path.exists(INPUT_FILE):
    print(f"Error: The input file '{INPUT_FILE}' does not exist.")
    sys.exit(1)


async def resample_ffmpeg_async(infile):
    """Resamples the input file to 16kHz mono using FFmpeg."""
    cmd = f"ffmpeg -nostdin -loglevel quiet -i '{infile}' -ar 16000 -ac 1 -f s16le -"
    return await asyncio.create_subprocess_shell(cmd, stdout=subprocess.PIPE)


async def send_file_as_websocket(infile):
    """Sends the input file to the WebSocket server."""
    async with websockets.connect("ws://localhost:1338") as websocket:
        proc = await resample_ffmpeg_async(infile)
        while True:
            data = await proc.stdout.read(2000)
            if not data:
                break
            await websocket.send(data)
        await websocket.send("END")  # Indicate the end of the file transmission
        response = await websocket.recv()
        print("Server response:", response)


asyncio.run(send_file_as_websocket(INPUT_FILE))

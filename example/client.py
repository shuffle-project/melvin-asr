""" This is a websocket client example for ASR-API"""

# required pip installs for this file:
# 1. pip install websockets

import asyncio
import subprocess
from websockets.sync.client import connect

SAMPLE_RATE = 16000.0


class WebSocketClient:
    def __init__(self, url = "ws://localhost:1235/echo"):
        self.url = url
        self.websocket = connect(self.url)
        self.send("Hello world!")
        print(f"Received: {self.receive()}")

    def send(self, message):
        self.websocket.send(message)

    def receive(self):
        return self.websocket.recv()

    def close(self):
        self.websocket.close()

async def resample_ffmpeg_async(infile = "output4.wav"):
    cmd = "ffmpeg -nostdin -loglevel quiet "\
    "-i \'{}\' -ar {} -ac 1 -f s16le -".format(str(infile), SAMPLE_RATE)
    print(cmd)
    return await asyncio.create_subprocess_shell(cmd, stdout=subprocess.PIPE)

async def sendFileAsWebsocket():
    proc = await resample_ffmpeg_async()
    websocket = WebSocketClient()
    while True:
        line = await proc.stdout.readline()
        if not line:
            break
        websocket.send(line)
        print(f"Received: {websocket.receive()}")

asyncio.run(sendFileAsWebsocket())
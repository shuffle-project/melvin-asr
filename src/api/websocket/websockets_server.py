"""Module to handle the WebSocket server"""
import asyncio
import websockets
from src.api.websocket.stream import Stream
from src.api.websocket.stream_transcriber import Transcriber
from src.helper.logger import Logger


class WebSocketServer:
    """Class to handle a WebSocket ASR server"""
    Transcriber = Transcriber()

    async def __init__(self, host: str, port: int):
        self.logger = Logger("WebSocketServer", True, Logger.Color.BRIGHT_CYAN)
        self.stream_counter = 0
        async with websockets.serve(self.handle_new_client, host, port):
            await asyncio.Future()  # run forever

    async def handle_new_client(self, websocket, path):
        """Function to handle a new client connection"""
        self.stream_counter += 1
        self.logger.print_log(f"New Stream Client connected. Stream ID: {self.stream_counter}")
        Stream(Transcriber, self.stream_counter).echo(websocket=websocket, path=path)

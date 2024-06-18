"""Module to handle the WebSocket server"""
import asyncio
import websockets
from src.api.websocket.stream import Stream


class WebSocketServer:
    """Class to handle a WebSocket ASR server"""

    async def __init__(self, host: str, port: int):
        self.stream_counter = 0
        async with websockets.serve(self.handle_new_client, host, port):
            await asyncio.Future()  # run forever

    async def handle_new_client(self, websocket, path):
        """Function to handle a new client connection"""
        self.stream_counter += 1
        Stream(self.stream_counter).echo(websocket=websocket, path=path)
        

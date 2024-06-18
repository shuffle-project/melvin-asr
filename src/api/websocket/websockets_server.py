"""Module to handle the WebSocket server"""
import asyncio
import websockets


class WebSocketServer:
    """Class to handle a WebSocket ASR server"""

    async def main(self):
        async with websockets.serve(self.handle_new_client, self.host, self.port):
            await asyncio.Future()  # run forever

    async def handle_new_client(self, websocket, path):
        """Function to handle a new client connection"""
        

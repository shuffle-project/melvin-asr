"""
This module contains the Flask app and the API endpoints.
"""
import asyncio
from src.api.websocket.websockets_app import WebSocketServer


# startup functions for flask & websockets apps
def run_websocket_app(websocket_port, host):
    """Starts the websocket server."""
    web_socket_server = WebSocketServer(port=websocket_port, host=host)
    asyncio.run(web_socket_server.start_server())

"""Entry point for the Websocket API."""

import asyncio
import logging
from src.websocket.websockets_server import WebSocketServer


def run_websocket_api(websocket_port, host):
    """Starts the websocket server."""
    logger = logging.getLogger(__name__)
    logger.info(f"Starting Websockets server on '{host}:{websocket_port}'")
    web_socket_server = WebSocketServer(port=websocket_port, host=host)
    asyncio.run(web_socket_server.start_server())

""" Entry point for the Websocket API. """
import asyncio
from src.helper.logger import Color, Logger
from src.websocket.websockets_server import WebSocketServer


def run_websocket_api(websocket_port, host):
    """Starts the websocket server."""
    log = Logger("run_websocket_app", True, Color.CYAN)
    log.print_log(f"Starting Websockets server on '{host}:{websocket_port}'")
    web_socket_server = WebSocketServer(port=websocket_port, host=host)
    asyncio.run(web_socket_server.start_server())

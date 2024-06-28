""" Entry point for the Websocket API. """
import asyncio
from src.helper.logger import Color, Logger


def run_websocket_api(websocket_port, host):
    """Starts the websocket server."""
    print(f"Starting Websockets server currently disabled'")
    # log = Logger("run_websocket_app", True, Color.UNDERLINE)
    # log.print_log(f"Starting Websockets server on '{host}:{websocket_port}'")
    # web_socket_server = WebSocketServer(port=websocket_port, host=host)
    # asyncio.run(web_socket_server.main())

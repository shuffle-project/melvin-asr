"""Entry point for the WebSocket API."""

import logging

import uvicorn

logger = logging.getLogger(__name__)


def run_websocket_api(websocket_port, host):
    """Starts the WebSocket API server."""
    logger.info(f"Starting Websockets server on '{host}:{websocket_port}'")
    uvicorn.run("src.websocket.websockets_server:app", host=host,
                port=websocket_port, log_level="info")

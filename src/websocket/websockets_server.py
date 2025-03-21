"""Module to handle the WebSocket server"""

import asyncio
import json
import logging

from fastapi import FastAPI, WebSocket, WebSocketDisconnect

from src.helper.config import CONFIG
from src.websocket.stream import Stream
from src.websocket.stream_transcriber import Transcriber

GET_WORKER_RETRY_TIME_SECONDS = 10
WAITING_MESSAGE = f"No transcription workers available. Retrying in {GET_WORKER_RETRY_TIME_SECONDS} seconds"

LOGGER = logging.getLogger(__name__)

app = FastAPI()


class WebSocketServer:
    """Class to handle a WebSocket ASR server"""

    gpu_config: dict = None
    cpu_config: dict = None

    gpu_transcriber: Transcriber = None
    cpu_transcriber: Transcriber = None

    gpu_worker_seats: int = 0  # Counts available GPU worker seats
    cpu_worker_seats: int = 0  # Counts available CPU worker seats

    stream_counter: int = 0

    def __init__(self, config: dict = CONFIG):
        self.gpu_config = config["websocket_stream"]["cuda"]
        LOGGER.info(f"GPU Config: {self.gpu_config}")
        self.cpu_config = config["websocket_stream"]["cpu"]
        LOGGER.info(f"CPU Config: {self.cpu_config}")

        # Setup GPU Transcriber
        if self.gpu_config["active"]:
            if not all(
                key in list(self.gpu_config.keys())
                for key in ["model", "device_index", "worker_seats"]
            ):
                LOGGER.warning("GPU Config is not set correctly")
                raise ValueError("GPU Config is not set correctly")
            self.gpu_transcriber = Transcriber.for_gpu(
                model_name=self.gpu_config["model"],
                device_index=self.gpu_config["device_index"],
            )
            self.gpu_worker_seats = self.gpu_config["worker_seats"]
            LOGGER.info(
                f"GPU Stream Transcriber is active, Worker Seats: {self.gpu_worker_seats}"
            )

        # Setup CPU Transcriber
        if self.cpu_config["active"]:
            if not all(
                self.cpu_config.get(key)
                for key in ["model", "cpu_threads", "worker_seats"]
            ):
                LOGGER.warning("CPU Config is not set correctly")
                raise ValueError("CPU Config is not set correctly")
            self.cpu_transcriber = Transcriber.for_cpu(
                model_name=self.cpu_config["model"],
                cpu_threads=self.cpu_config["cpu_threads"],
                num_workers=self.cpu_config["worker_seats"],
            )
            self.cpu_worker_seats = self.cpu_config["worker_seats"]
            LOGGER.info(
                f"CPU Stream Transcriber is active, Worker Seats: {self.cpu_worker_seats}"
            )

    async def authenticate_new_client(self, websocket: WebSocket) -> bool:
        msg = await websocket.receive()

        if not "text" in msg:
            LOGGER.info("Initial websocket message was not string")
            await websocket.send_text("Initial message was not text and therefore did not match the expected auth format")
            return False

        msg = msg["text"]
        try:
            data = json.loads(msg)
            if data["Authorization"] in CONFIG["api_keys"]:
                return True
        except:
            LOGGER.info("Initial websocket message was invalid json")
            await websocket.send_text("Initial websocket message contained invalid json")

        return False

    async def handle_new_client(self, websocket: WebSocket):
        """Function to handle a new client connection"""
        self.stream_counter += 1
        client_id = self.stream_counter
        LOGGER.debug(
            f"New client connected: {websocket.client}, Stream ID: {client_id}"
        )

        searching = True
        while searching:
            if self.gpu_transcriber and self.gpu_worker_seats > 0:
                self.gpu_worker_seats -= 1
                LOGGER.debug(f"Client {client_id} is using GPU worker")
                searching = False
                try:
                    await Stream(
                        transcriber=self.gpu_transcriber, 
                        id=client_id,
                    ).echo(
                        websocket=websocket
                    )
                except Exception as e:
                    LOGGER.error(
                        f"Client {client_id} disconnected with an exception while using a worker: {e}"
                    )
                finally:
                    self.gpu_worker_seats += 1
                    LOGGER.debug(f"Client {client_id} returned GPU worker")

            elif self.cpu_transcriber and self.cpu_worker_seats > 0:
                self.cpu_worker_seats -= 1
                LOGGER.debug(f"Client {client_id} is using CPU worker")
                searching = False
                try:
                    await Stream(
                        transcriber=self.cpu_transcriber, 
                        id=client_id,
                    ).echo(
                        websocket=websocket
                    )
                except Exception as e:
                    LOGGER.warning(
                        f"Client {client_id} disconnected with an exception while using a worker: {e}"
                    )
                finally:
                    self.cpu_worker_seats += 1
                    LOGGER.debug(f"Client {client_id} returned CPU worker")

            if searching:
                try:
                    await websocket.send_text(WAITING_MESSAGE)
                except WebSocketDisconnect:
                    LOGGER.debug(
                        f"Client {client_id} disconnected while waiting for a worker"
                    )
                    return

                LOGGER.debug(
                    f"Client {client_id} is waiting for a worker, available seats - GPU: {self.gpu_worker_seats}, CPU: {self.cpu_worker_seats}"
                )
                await asyncio.sleep(GET_WORKER_RETRY_TIME_SECONDS)


# Initialize WebSocketServer
websocket_server = WebSocketServer()


@app.websocket("/")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        if not (await websocket_server.authenticate_new_client(websocket)):
            LOGGER.info("Client disconnected due to invalid auth")
            await websocket.close()
            return
        LOGGER.info("Client sucessfully authenticated")
        await websocket_server.handle_new_client(websocket)
    except WebSocketDisconnect:
        LOGGER.info("Client disconnected")


@app.get("/health", include_in_schema=False)
async def health_check():
    return {"status": "ok"}


@app.options("/health", include_in_schema=False)
async def health_options():
    return {"status": "ok"}

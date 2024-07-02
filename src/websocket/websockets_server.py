"""Module to handle the WebSocket server"""
import asyncio
import websockets
from src.helper.config import CONFIG
from src.websocket.stream import Stream
from src.websocket.stream_transcriber import Transcriber
from src.helper.logger import Color, Logger

GET_WORKER_RETRY_TIME_SECONDS = 10
WAITING_MESSAGE = f"No transcription workers available. Retrying in {GET_WORKER_RETRY_TIME_SECONDS} seconds"


class WebSocketServer:
    """Class to handle a WebSocket ASR server"""

    gpu_config: dict = None
    cpu_config: dict = None

    gpu_transcriber: Transcriber = None
    cpu_transcriber: Transcriber = None

    gpu_worker_seats: int = 0  # Counts the available GPU worker seats, If there 2 seats and 2 clients are connected, the variable will be 0
    cpu_worker_seats: int = 0  # Counts the available CPU worker seats, If there 2 seats and 2 clients are connected, the variable will be 0

    stream_counter: int = 0

    def __init__(self, host: str, port: int, config: dict = CONFIG):
        self.should_stop = False
        self.log = Logger("WebSocketServer", True, Color.CYAN)
        self.host = host
        self.port = port

        # Setup the GPU and CPU Transcribers
        self.gpu_config = config["websocket_stream"]["cuda"]
        self.log.print_log(f"GPU Config: {self.gpu_config}")
        self.cpu_config = config["websocket_stream"]["cpu"]
        self.log.print_log(f"CPU Config: {self.cpu_config}")

        if self.gpu_config["active"]:
            if (
                (self.gpu_config["model"] is None)
                or (self.gpu_config["device_index"] is None)
                or (self.gpu_config["worker_seats"] is None)
            ):
                self.log.print_log("GPU Config is not set correctly")
                raise ValueError("GPU Config is not set correctly")
            self.gpu_transcriber = Transcriber.for_gpu(
                model_name=self.gpu_config["model"],
                device_index=self.gpu_config["device_index"],
            )
            self.gpu_worker_seats = self.gpu_config["worker_seats"]
            self.log.print_log(
                f"GPU Stream Transcriber is active, Worker Seats: {self.gpu_worker_seats}"
            )

        if self.cpu_config["active"]:
            if (
                self.cpu_config["model"] is None
                or self.cpu_config["cpu_threads"] is None
                or self.cpu_config["worker_seats"] is None
            ):
                self.log.print_log("CPU Config is not set correctly")
                raise ValueError("CPU Config is not set correctly")
            self.cpu_transcriber = Transcriber.for_cpu(
                model_name=self.cpu_config["model"],
                cpu_threads=self.cpu_config["cpu_threads"],
                num_workers=self.cpu_config["worker_seats"],
            )
            self.cpu_worker_seats = self.cpu_config["worker_seats"]
            self.log.print_log(
                f"CPU Stream Transcriber is active, Worker Seats: {self.cpu_worker_seats}"
            )

    async def start_server(self):
        self.should_stop = False
        async with websockets.serve(self.handle_new_client, self.host, self.port):
            while not self.should_stop:
                await asyncio.sleep(1)  # Check every second if the server should stop

    def stop_server(self):
        self.should_stop = True

    async def handle_new_client(self, websocket, path):
        """Function to handle a new client connection"""

        self.stream_counter += 1
        id = self.stream_counter
        self.log.print_log(
            f"New client connected: {websocket.remote_address}, Stream ID: {id}"
        )

        searching = True
        while searching:
            if self.gpu_transcriber is not None and self.gpu_worker_seats > 0:
                self.gpu_worker_seats -= 1
                self.log.print_log(f"Client {id} is using GPU worker")
                searching = False
                try:
                    await Stream(transcriber=self.gpu_transcriber, id=id).echo(
                        websocket=websocket, path=path
                    )
                except Exception as e:
                    self.log.print_error(
                        f"Client {id} disconnected with an exception while using a worker: {e}"
                    )
                finally:
                    self.gpu_worker_seats += 1
                    self.log.print_log(f"Client {id} returned GPU worker")

            elif self.cpu_transcriber is not None and self.cpu_worker_seats > 0:
                self.cpu_worker_seats -= 1
                self.log.print_log(f"Client {id} is using CPU worker")
                searching = False
                try:
                    await Stream(transcriber=self.cpu_transcriber, id=id).echo(
                        websocket=websocket, path=path
                    )
                except Exception as e:
                    self.log.print_log(
                        f"Client {id} disconnected with an exception while using a worker: {e}"
                    )
                finally:
                    self.cpu_worker_seats += 1
                    self.log.print_log(f"Client {id} returned CPU worker")

            if searching:
                try:
                    await websocket.send(WAITING_MESSAGE)
                except Exception:
                    self.log.print_log(
                        f"Client {id} disconnected while waiting for a worker"
                    )

                self.log.print_log(
                    f"Client {id} is waiting for a worker,\navailable seats for GPU: {self.gpu_worker_seats}, CPU: {self.cpu_worker_seats},\nconfigured seats for GPU: {self.gpu_config['worker_seats']}, CPU: {self.cpu_config['worker_seats']}"
                )
                await asyncio.sleep(GET_WORKER_RETRY_TIME_SECONDS)

"""Module to handle the WebSocket server"""
import asyncio
import json
import time
import websockets

from src.config import CONFIG
from src.api.websocket.websockets_settings import default_websocket_settings
from src.helper.logger import Color, Logger
from src.transcription.transcriber import Transcriber

LOGGER = Logger("WebSocketServer", True, Color.BRIGHT_YELLOW)

# To Calculate the seconds of audio in a chunk of 16000 Hz, 2 bytes per sample and 1 channel (as typically used in Whisper):
# 16000 Hz * 2 bytes * 1 channel = 32000 bytes per second
BYTES_PER_SECOND = 32000

# We want to print a final transcription after a certain amount of time
# This is the number of seconds we want to wait before printing a final transcription
FINAL_TRANSCRIPTION_TIMEOUT = 6

# We want to print a partial transcription after a certain amount of time
# This is the number of seconds we want to wait before printing a partial transcription
PARTIAL_TRANSCRIPTION_TIMEOUT = 1


class WebSocketServer:
    """Class to handle a WebSocket ASR server"""

    def __init__(self, port: int, host: str = "localhost"):
        self.port = port
        self.host = host
        LOGGER.print_log("Websocket Transcriber Config: {}".format(CONFIG["stream_runner"][0]))
        self.transcriber = Transcriber(model_name=CONFIG["stream_runner"][0]["model"], device=CONFIG["stream_runner"][0]["device"], compute_type=CONFIG["stream_runner"][0]["compute_type"])

        # Cache for the last few chunks of audio
        self.recently_added_chunk_cache = b""

        # Cache for the transcribed partials since the last final
        self.partials_transcribed_since_last_final = b""

        # Cache for the chunks since the last final
        self.chunk_cache = b""

        # indicates that the server is in use
        self.is_busy = False

        # calculate the overall bytes of audio and transcribed bytes
        self.overall_transcribed_bytes = b""
        self.overall_audio_bytes = b""

        # Byte threshold for partial and final transcriptions
        # If the cache is larger than the threshold, we transcribe
        self.final_treshold = BYTES_PER_SECOND * FINAL_TRANSCRIPTION_TIMEOUT
        self.partial_treshold = BYTES_PER_SECOND * PARTIAL_TRANSCRIPTION_TIMEOUT

    async def main(self):
        async with websockets.serve(self.echo, self.host, self.port):
            await asyncio.Future()  # run forever

    async def echo(self, websocket, path):
        print("echo started")
        self.overall_audio_bytes = b""
        self.overall_transcribed_bytes = b""
        while True:
            try:
                message = await websocket.recv()
                if isinstance(message, bytes) is True:
                    self.chunk_cache += message
                    self.recently_added_chunk_cache += message
                    self.overall_audio_bytes += message

                    if len(self.chunk_cache) >= self.final_treshold:
                        LOGGER.print_log("********** NEW FINAL **********")
                        asyncio.ensure_future(
                            self.transcribe_all_chunk_cache(
                                websocket,
                                self.chunk_cache,
                                self.recently_added_chunk_cache,
                            )
                        )
                        self.recently_added_chunk_cache = b""
                        self.chunk_cache = b""

                    if len(self.recently_added_chunk_cache) >= self.partial_treshold:
                        LOGGER.print_log("********** NEW PARTIAL **********")
                        # Here we need to ensure that the transcribe_chunk_partial does not run longer than the length of the chunks.
                        asyncio.ensure_future(
                            self.transcribe_chunk_partial(
                                websocket,
                                self.chunk_cache,
                                self.recently_added_chunk_cache,
                            )
                        )
                        self.recently_added_chunk_cache = b""

                else:
                    LOGGER.print_log("Received message: {}".format(message))
                    await websocket.send("wrong data type")

            except websockets.exceptions.ConnectionClosedOK:
                LOGGER.print_log("Client left")
                break
            except websockets.exceptions.ConnectionClosedError:
                LOGGER.print_error("Client left unexpectedly")
                break
            except Exception as e:
                LOGGER.print_error("Error while receiving message: {}".format(e))
                break

    async def transcribe_all_chunk_cache(
        self, websocket, chunk_cache, recent_cache
    ) -> str:
        """Function to transcribe a chunk of audio"""
        start_time = time.time()
        result: str = ""
        data = self.transcriber.transcribe_audio_audio_chunk(chunk_cache, settings=default_websocket_settings())
        self.adjust_threshold_on_latency()
        self.overall_transcribed_bytes += recent_cache
        if "segments" in data:
            result = []
            text = ""
            for segment in data["segments"]:
                for word in segment["words"]:
                    # make float with 6 digits after point
                    start = float("{:.6f}".format(float(word["start"])))
                    end = float("{:.6f}".format(float(word["end"])))
                    conf = float("{:.6f}".format(float(word["probability"])))
                    word = word["word"].strip()
                    result.append(
                        {"conf": conf, "start": start, "end": end, "word": word}
                    )
                text = text + segment["text"]
            result = json.dumps({"result": result, "text": text}, indent=2)
        await websocket.send(result)
        end_time = time.time()
        LOGGER.print_log("Final Transcription took {:.2f} s".format(end_time - start_time))

    async def transcribe_chunk_partial(
        self, websocket, chunk_cache, recent_cache
    ) -> str:
        start_time = time.time()
        result: str = "Missing data"

        data = self.transcriber.transcribe_audio_audio_chunk(chunk_cache, settings=default_websocket_settings())
        self.adjust_threshold_on_latency()
        self.overall_transcribed_bytes += recent_cache
        if "segments" in data:
            text = ""
            for segment in data["segments"]:
                text += segment["text"]
            result = json.dumps({"partial": text}, indent=2)
        else:
            LOGGER.print_error("Transcription Data is empty, no segments found")
        await websocket.send(result)

        end_time = time.time()
        LOGGER.print_log("Partial transcription took {:.2f} s".format(end_time - start_time))

    def adjust_threshold_on_latency(self):
        """Adjusts the partial threshold based on the latency"""
        seconds_received = len(self.overall_audio_bytes) / BYTES_PER_SECOND
        seconds_transcribed = (
            len(self.overall_transcribed_bytes) / BYTES_PER_SECOND
        )
        # Calculate the latency of the connection
        seconds_difference_received_transcribed = (
            seconds_received - seconds_transcribed
        )
        LOGGER.print_log(
            "Difference received transcribed: {}".format(
                seconds_difference_received_transcribed
            )
        )

        # we need to exclude the partial threshold from the calculation, because the if the threshold is reached, the latency is always bad
        seconds_difference_received_transcribed_exclude_partial = (
            seconds_difference_received_transcribed - self.partial_treshold / BYTES_PER_SECOND
        )
        LOGGER.print_log("Difference received, excluding Partial threshold: {}".format(seconds_difference_received_transcribed_exclude_partial))

        # FINAL TRANSCRIPTION TIMEOUT is out definition of bad latency
        if seconds_difference_received_transcribed_exclude_partial > FINAL_TRANSCRIPTION_TIMEOUT-2:
            LOGGER.print_log("Latency is too high, increasing partial threshold")
            self.partial_treshold = self.partial_treshold * 1.5
            if self.partial_treshold > self.final_treshold:
                self.partial_treshold = self.final_treshold
                # this is a bad case, maximum threshold
                LOGGER.print_error("Partial threshold is now equal to final threshold")
        
        if seconds_difference_received_transcribed_exclude_partial < FINAL_TRANSCRIPTION_TIMEOUT / 6:
            LOGGER.print_log("Latency is low, decreasing partial threshold")
            self.partial_treshold = self.partial_treshold * 0.75
            if self.partial_treshold < BYTES_PER_SECOND * PARTIAL_TRANSCRIPTION_TIMEOUT:
                self.partial_treshold = BYTES_PER_SECOND * PARTIAL_TRANSCRIPTION_TIMEOUT
                LOGGER.print_log("Partial threshold is now equal to the default threshold")

        LOGGER.print_log("Partial threshold is now: {}".format(self.partial_treshold / BYTES_PER_SECOND))

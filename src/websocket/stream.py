import asyncio
import json
import time
import traceback
import uuid

from fastapi import WebSocket, WebSocketDisconnect
from pydub import AudioSegment

from src.helper import logger
from src.helper.data_handler import DataHandler
from src.websocket.stream_transcriber import Transcriber

# Constants
BYTES_PER_SECOND = 32000

# This is the number of seconds we wait before printing a final transcription
FINAL_TRANSCRIPTION_TIMEOUT = 6

# This is the number of seconds we wait before printing a partial transcription
PARTIAL_TRANSCRIPTION_TIMEOUT = 1


class Stream:
    def __init__(self, transcriber: Transcriber, id: int):
        self.logger = logger.get_logger_with_id(__name__, id)
        self.transcriber = transcriber
        self.id = id
        self.close_stream = False

        # Cache for the last few chunks of audio
        self.recently_added_chunk_cache = b""

        # Cache for the chunks since the last final
        self.chunk_cache = b""
        # Last final bytes and text to check for duplicates and create prompts
        self.last_final_result_object = {"text": "", "result": []}
        self.last_final_bytes = b""
        self.final_transcriptions = []
        self.export_audio = b""
        self.overall_transcribed_bytes = b""
        self.overall_audio_bytes = b""
        # If the cache is larger than the threshold, we transcribe
        self.final_treshold = BYTES_PER_SECOND * FINAL_TRANSCRIPTION_TIMEOUT
        self.partial_treshold = BYTES_PER_SECOND * PARTIAL_TRANSCRIPTION_TIMEOUT

    async def echo(self, websocket: WebSocket) -> None:
        try:
            while not self.close_stream:
                message = await websocket.receive()

                if "bytes" in message:
                    message = message["bytes"]
                    self.chunk_cache += message
                    self.recently_added_chunk_cache += message
                    self.overall_audio_bytes += message
                    self.export_audio = self.concatenate_audio_with_crossfade(
                        self.export_audio, message
                    )

                    if len(self.chunk_cache) >= self.final_treshold:
                        self.logger.debug(
                            f"NEW FINAL: length of chunk cache: {len(self.chunk_cache)}"
                        )
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
                        self.logger.info(
                            f"NEW PARTIAL: length of chunk cache: {len(self.recently_added_chunk_cache)}"
                        )
                        # Here we need to ensure that the transcribe_chunk_partial does not run longer than the length of the chunks.
                        asyncio.ensure_future(
                            self.transcribe_chunk_partial(
                                websocket,
                                self.chunk_cache,
                                self.recently_added_chunk_cache,
                            )
                        )
                        self.recently_added_chunk_cache = b""

                elif "text" in message:
                    message = message["text"]
                    self.logger.debug(f"Received control message (string): {message}")
                    if "eof" in message:
                        if "eof-finalize" in message:
                            # Non default behaviour but useful for some scenarios, like testing
                            await self.transcribe_all_chunk_cache(
                                websocket,
                                self.chunk_cache,
                                self.recently_added_chunk_cache,
                                skip_send=True,
                            )
                        name = self.export_transcription_and_wav()
                        await websocket.send_text(name)
                        await websocket.close()
                        self.logger.info("eof received")
                        self.close_stream = True
                    else:
                        await websocket.send_text("control message unknown")

        except WebSocketDisconnect:
            self.logger.debug("Client disconnected")
            self.close_stream = True
        except Exception:
            self.logger.error(
                f"Error while receiving message: {traceback.format_exc()}"
            )
            self.close_stream = True
        finally:
            await websocket.close()

    async def transcribe_all_chunk_cache(
        self, websocket: WebSocket, chunk_cache, recent_cache, skip_send=False
    ) -> None:
        """Function to transcribe a chunk of audio"""
        try:
            start_time = time.time()
            bytes_to_transcribe = self.last_final_bytes + chunk_cache
            data = self.transcriber._transcribe(
                bytes_to_transcribe,
                "Beginning of transcription:" + self.last_final_result_object["text"],
            )
            self.adjust_threshold_on_latency()
            overall_transcribed_seconds = (
                len(self.overall_transcribed_bytes) / BYTES_PER_SECOND
            )
            last_final_bytes_seconds = len(self.last_final_bytes) / BYTES_PER_SECOND
            overall_transcribed_seconds -= last_final_bytes_seconds
            self.overall_transcribed_bytes += recent_cache

            result = {"result": [], "text": ""}
            if "segments" in data:
                words = []
                for segment in data["segments"]:
                    for word in segment["words"]:
                        start = float(f"{float(word['start']):.6f}")
                        end = float(f"{float(word['end']):.6f}")
                        conf = float(f"{float(word['probability']):.6f}")
                        words.append(
                            {
                                "conf": conf,
                                # the start time and end time is the time of the word minus the time of the current final
                                "start": start
                                + overall_transcribed_seconds
                                - FINAL_TRANSCRIPTION_TIMEOUT,
                                "end": end
                                + overall_transcribed_seconds
                                - FINAL_TRANSCRIPTION_TIMEOUT,
                                "word": word["word"].strip(),
                            }
                        )
                result = {"result": words, "text": " ".join([x["word"] for x in words])}
                self.last_final_result_object = result
                self.last_final_bytes = chunk_cache
                self.final_transcriptions.append(result)

            if not skip_send:
                await websocket.send_text(json.dumps(result, indent=2))
            self.logger.debug(
                f"Final Transcription took {time.time() - start_time:.2f} s"
            )

        except Exception:
            self.logger.error(
                f"Error while transcribing audio: {traceback.format_exc()}"
            )
            self.close_stream = True

    async def transcribe_chunk_partial(self, websocket, chunk_cache, recent_cache):
        try:
            # Ensure the chunk_cache is not empty before proceeding
            if len(chunk_cache) == 0:
                self.logger.warning("Received empty chunk, skipping transcription.")
                return  # Skip transcription for empty chunk

            start_time = time.time()
            result: str = "Missing data"

            # Pass the chunk to the transcriber
            data = self.transcriber._transcribe(chunk_cache)

            self.adjust_threshold_on_latency()

            self.overall_transcribed_bytes += recent_cache
            if "segments" in data:
                text = ""
                for segment in data["segments"]:
                    text += segment["text"]
                result = json.dumps({"partial": text}, indent=2)
            else:
                self.logger.error("Transcription Data is empty, no segments found")

            await websocket.send_text(result)

            end_time = time.time()
            self.logger.debug(
                "Partial transcription took {:.2f} s".format(end_time - start_time)
            )

        except Exception:
            self.logger.error(
                "Error while transcribing audio: {}".format(traceback.format_exc())
            )
            self.close_stream = True

    def adjust_threshold_on_latency(self):
        seconds_received = len(self.overall_audio_bytes) / BYTES_PER_SECOND
        seconds_transcribed = len(self.overall_transcribed_bytes) / BYTES_PER_SECOND
        # Calculate the latency of the connection
        seconds_difference = seconds_received - seconds_transcribed

        if seconds_difference > FINAL_TRANSCRIPTION_TIMEOUT - 2:
            self.partial_treshold = min(
                self.partial_treshold * 1.5, self.final_treshold
            )
        elif seconds_difference < FINAL_TRANSCRIPTION_TIMEOUT / 6:
            self.partial_treshold = max(
                self.partial_treshold * 0.75,
                BYTES_PER_SECOND * PARTIAL_TRANSCRIPTION_TIMEOUT,
            )

    def export_transcription_and_wav(self):
        DATA_HANDLER = DataHandler()
        name = uuid.uuid4().hex
        DATA_HANDLER.export_wav_file(self.export_audio, name)
        DATA_HANDLER.export_dict_to_json_file(self.final_transcriptions, name)
        return name

    def concatenate_audio_with_crossfade(
        self, audio_chunk1: bytes, audio_chunk2: bytes, crossfade_duration=20
    ) -> bytes:
        """
        Concatenates two audio chunks with crossfade to avoid click sounds.

        :param audio_chunk1: First audio chunk in bytes.
        :param audio_chunk2: Second audio chunk in bytes.
        :param crossfade_duration: Duration of the crossfade in milliseconds.
        :return: Concatenated audio chunk in bytes.
        """
        segment1 = AudioSegment(
            data=audio_chunk1, sample_width=2, frame_rate=16000, channels=1
        )
        segment2 = AudioSegment(
            data=audio_chunk2, sample_width=2, frame_rate=16000, channels=1
        )
        # Check the length of segments to avoid crossfade errors, when starting the stream
        if len(segment1) < crossfade_duration or len(segment2) < crossfade_duration:
            crossfade_duration = min(len(segment1), len(segment2), crossfade_duration)
        combined = segment1.append(segment2, crossfade=crossfade_duration)
        return combined.raw_data

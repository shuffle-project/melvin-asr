import asyncio
import json
import time
import uuid
import websockets
import traceback
from pydub import AudioSegment
from src.helper import logger
from src.helper.data_handler import DataHandler
from src.websocket.stream_transcriber import Transcriber

# To Calculate the seconds of audio in a chunk of 16000 Hz, 2 bytes per sample and 1 channel (as typically used in Whisper):
# 16000 Hz * 2 bytes * 1 channel = 32000 bytes per second
BYTES_PER_SECOND = 32000

# We want to print a final transcription after a certain amount of time
# This is the number of seconds we want to wait before printing a final transcription
FINAL_TRANSCRIPTION_TIMEOUT = 6

# We want to print a partial transcription after a certain amount of time
# This is the number of seconds we want to wait before printing a partial transcription
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
        self.last_final_result_object = {
            "text": "",
            "result": [],
        }  # requires empty objects to avoid errors at start
        self.last_final_bytes = b""

        # stores all final transcription objects and audio for export
        self.final_transcriptions = []
        self.export_audio = b""

        # calculate the overall bytes of audio and transcribed bytes
        self.overall_transcribed_bytes = b""
        self.overall_audio_bytes = b""

        # Byte threshold for partial and final transcriptions
        # If the cache is larger than the threshold, we transcribe
        self.final_treshold = BYTES_PER_SECOND * FINAL_TRANSCRIPTION_TIMEOUT
        self.partial_treshold = BYTES_PER_SECOND * PARTIAL_TRANSCRIPTION_TIMEOUT

    async def echo(self, websocket, path) -> None:
        while self.close_stream is False:
            try:
                # message type: Union[str, bytes]
                message = await websocket.recv()
                if isinstance(message, bytes) is True:
                    self.chunk_cache += message
                    self.recently_added_chunk_cache += message
                    self.overall_audio_bytes += message
                    self.export_audio = self.concatenate_audio_with_crossfade(
                        self.export_audio, message
                    )

                    # Final will be created
                    if len(self.chunk_cache) >= self.final_treshold:
                        self.logger.debug(
                            "NEW FINAL: length of chunk cache: {}".format(
                                len(self.chunk_cache)
                            )
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

                    # Partial will be created
                    if len(self.recently_added_chunk_cache) >= self.partial_treshold:
                        self.logger.info(
                            "NEW PARTIAL: length of chunk cache: {}".format(
                                len(self.recently_added_chunk_cache)
                            )
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
                elif isinstance(message, str) is True:
                    self.logger.debug(
                        "Received control message (string): {}".format(message)
                    )
                    if "eof" in message:
                        name = self.export_transcription_and_wav()
                        await websocket.send(name)
                        await websocket.close()
                        self.logger.info("eof received")
                        self.close_stream = True
                    else:
                        await websocket.send("control message unknown")

            except websockets.exceptions.ConnectionClosedOK:
                self.logger.debug("Client left")
                self.close_stream = True
            except websockets.exceptions.ConnectionClosedError:
                self.logger.debug("Client left unexpectedly")
                self.close_stream = True
            except Exception:
                self.logger.error(
                    "Error while receiving message: {}".format(traceback.format_exc())
                )
                self.close_stream = True

    async def transcribe_all_chunk_cache(
        self, websocket, chunk_cache, recent_cache
    ) -> str:
        """Function to transcribe a chunk of audio"""
        try:
            start_time = time.time()
            result: str = ""
            bytes_to_transcribe = self.last_final_bytes + chunk_cache
            data = self.transcriber._transcribe(
                bytes_to_transcribe,
                "Beginning of transcription:" + self.last_final_result_object["text"],
            )
            self.adjust_threshold_on_latency()
            # we want the time when the final started, so it is the self.overall_transcribed_bytes time minus the recently added bytes
            overall_transcribed_seconds = (
                len(self.overall_transcribed_bytes) / BYTES_PER_SECOND
            )
            # We need to remove the time of the repeatedly transcribed bytes from the overall transcribed seconds
            last_final_bytes_seconds = len(self.last_final_bytes) / BYTES_PER_SECOND
            overall_transcribed_seconds -= last_final_bytes_seconds

            self.overall_transcribed_bytes += recent_cache

            if "segments" in data:
                words = []
                for segment in data["segments"]:
                    for word in segment["words"]:
                        # make float with 6 digits after point
                        start = float("{:.6f}".format(float(word["start"])))
                        end = float("{:.6f}".format(float(word["end"])))
                        conf = float("{:.6f}".format(float(word["probability"])))
                        word = word["word"].strip()
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
                                "word": word,
                            }
                        )
                        # create an object { result: list[{conf: float, start: float, end: fload, word: string}], text: string }
                        result = {
                            "result": words,
                            "text": " ".join([x["word"] for x in words]),
                        }

                # Save text and bytes for later use
                self.last_final_result_object = result
                self.last_final_bytes = chunk_cache
                self.final_transcriptions.append(result)
            await websocket.send(json.dumps(result, indent=2))
            end_time = time.time()
            self.logger.debug(
                "Final Transcription took {:.2f} s".format(end_time - start_time)
            )

        except Exception:
            self.logger.error(
                "Error while transcribing audio: {}".format(traceback.format_exc())
            )
            self.close_stream = True

    async def transcribe_chunk_partial(
        self, websocket, chunk_cache, recent_cache
    ) -> str:
        try:
            start_time = time.time()
            result: str = "Missing data"

            data = self.transcriber._transcribe(
                chunk_cache,
            )
            self.adjust_threshold_on_latency()
            self.overall_transcribed_bytes += recent_cache
            if "segments" in data:
                text = ""
                for segment in data["segments"]:
                    text += segment["text"]
                result = json.dumps({"partial": text}, indent=2)
            else:
                self.logger.error("Transcription Data is empty, no segments found")
            await websocket.send(result)

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
        """Adjusts the partial threshold based on the latency"""
        seconds_received = len(self.overall_audio_bytes) / BYTES_PER_SECOND
        seconds_transcribed = len(self.overall_transcribed_bytes) / BYTES_PER_SECOND
        # Calculate the latency of the connection
        seconds_difference_received_transcribed = seconds_received - seconds_transcribed
        self.logger.info(
            f"Latency: {seconds_difference_received_transcribed} s, Partial Threshhold {self.partial_treshold / BYTES_PER_SECOND}"
        )

        # we need to exclude the partial threshold from the calculation, because the if the threshold is reached, the latency is always bad
        seconds_difference_received_transcribed_exclude_partial = (
            seconds_difference_received_transcribed
            - self.partial_treshold / BYTES_PER_SECOND
        )

        # FINAL TRANSCRIPTION TIMEOUT is out definition of bad latency
        if (
            seconds_difference_received_transcribed_exclude_partial
            > FINAL_TRANSCRIPTION_TIMEOUT - 2
        ):
            self.logger.debug("Latency is too high, increasing partial threshold")
            self.partial_treshold = self.partial_treshold * 1.5
            if self.partial_treshold > self.final_treshold:
                self.partial_treshold = self.final_treshold
                # this is a bad case, maximum threshold

        if (
            seconds_difference_received_transcribed_exclude_partial
            < FINAL_TRANSCRIPTION_TIMEOUT / 6
        ):
            self.partial_treshold = self.partial_treshold * 0.75
            if self.partial_treshold < BYTES_PER_SECOND * PARTIAL_TRANSCRIPTION_TIMEOUT:
                self.partial_treshold = BYTES_PER_SECOND * PARTIAL_TRANSCRIPTION_TIMEOUT
                # Partial threshold is now equal to the default threshold

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
        # Convert the byte data to AudioSegment
        segment1 = AudioSegment(
            data=audio_chunk1,
            sample_width=2,  # Assuming 16-bit PCM
            frame_rate=16000,
            channels=1,
        )
        segment2 = AudioSegment(
            data=audio_chunk2,
            sample_width=2,  # Assuming 16-bit PCM
            frame_rate=16000,
            channels=1,
        )

        # Check the length of segments to avoid crossfade errors, when starting the stream
        if len(segment1) < crossfade_duration or len(segment2) < crossfade_duration:
            crossfade_duration = min(len(segment1), len(segment2), crossfade_duration)

        combined = segment1.append(segment2, crossfade=crossfade_duration)
        return combined.raw_data

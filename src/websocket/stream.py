import asyncio
import json
import time
from typing import Callable
import uuid
import websockets
from pydub import AudioSegment
from src.helper.data_handler import DataHandler
from src.helper.logger import Color, Logger

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
    def __init__(self, transcription_callable: Callable, id: int):

        self.logger = Logger(f"Stream{id}", True, Color.random())
        self.transcription_callable = transcription_callable
        self.id = id
        self.close_stream = False

        # Initialize the transcribe function, if seat is available
        # self.transcribe = StreamTranscriber.get_transcribe()

        # Cache for the last few chunks of audio
        self.recently_added_chunk_cache = b""

        # Cache for the transcribed partials since the last final
        self.partials_transcribed_since_last_final = b""

        # Cache for the chunks since the last final
        self.chunk_cache = b""

        # indicates that the server is in use
        self.is_busy = False

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

    # def __del__(self):
    # We should delete the stream object if it is no longer in use and return the worker here
    # rather than in the echo method
    # self.transcriber.return_worker()

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

                    if len(self.chunk_cache) >= self.final_treshold:
                        self.logger.print_log(
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

                    if len(self.recently_added_chunk_cache) >= self.partial_treshold:
                        self.logger.print_log(
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
                    self.logger.print_log(
                        "Received control message (string): {}".format(message)
                    )
                    if "eof" in message:
                        name = self.export_transcription_and_wav()
                        await websocket.send(name)
                        await websocket.close()
                        self.logger.print_log("eof received")
                        self.close_stream = True
                    else:
                        await websocket.send("control message unknown")

            except websockets.exceptions.ConnectionClosedOK:
                self.logger("Client left")
                self.close_stream = True
            except websockets.exceptions.ConnectionClosedError:
                self.logger("Client left unexpectedly")
                self.close_stream = True
            except Exception as e:
                self.logger("Error while receiving message: {}".format(e))
                self.close_stream = True

    async def transcribe_all_chunk_cache(
        self, websocket, chunk_cache, recent_cache
    ) -> str:
        """Function to transcribe a chunk of audio"""
        try:
            start_time = time.time()
            result: str = ""
            data = self.transcription_callable(chunk_cache)
            self.adjust_threshold_on_latency()
            # we want the time when the final started, so it is the self.overall_transcribed_bytes time minus the recently added bytes
            overall_transcribed_seconds = (
                len(self.overall_transcribed_bytes) / BYTES_PER_SECOND
            ) - (len(recent_cache) / BYTES_PER_SECOND)
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
                            {
                                "conf": conf,
                                "start": start + overall_transcribed_seconds,
                                "end": end + overall_transcribed_seconds,
                                "word": word,
                            }
                        )

                    text = text + segment["text"]
                result = {"result": result, "text": text}
                self.final_transcriptions.append(result)
            await websocket.send(json.dumps(result, indent=2))
            end_time = time.time()
            self.logger.print_log(
                "Final Transcription took {:.2f} s".format(end_time - start_time)
            )
        except Exception as e:
            self.logger.print_error("Error while transcribing audio: {}".format(str(e)))
            self.close_stream = True

    async def transcribe_chunk_partial(
        self, websocket, chunk_cache, recent_cache
    ) -> str:
        try:
            start_time = time.time()
            result: str = "Missing data"

            data = self.transcription_callable(chunk_cache)
            self.adjust_threshold_on_latency()
            self.overall_transcribed_bytes += recent_cache
            if "segments" in data:
                text = ""
                for segment in data["segments"]:
                    text += segment["text"]
                result = json.dumps({"partial": text}, indent=2)
            else:
                self.logger.print_error(
                    "Transcription Data is empty, no segments found"
                )
            await websocket.send(result)

            end_time = time.time()
            self.logger.print_log(
                "Partial transcription took {:.2f} s".format(end_time - start_time)
            )
        except Exception as e:
            self.logger.print_error("Error while transcribing audio: {}".format(str(e)))
            self.close_stream = True

    def adjust_threshold_on_latency(self):
        """Adjusts the partial threshold based on the latency"""
        seconds_received = len(self.overall_audio_bytes) / BYTES_PER_SECOND
        seconds_transcribed = len(self.overall_transcribed_bytes) / BYTES_PER_SECOND
        # Calculate the latency of the connection
        seconds_difference_received_transcribed = seconds_received - seconds_transcribed
        self.logger.print_log(
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
            self.logger.print_log("Latency is too high, increasing partial threshold")
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


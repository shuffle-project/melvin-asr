import json
import time
from typing import Dict, List
import uuid
import traceback

from fastapi import WebSocket, WebSocketDisconnect
from fastapi.websockets import WebSocketState
from faster_whisper.transcribe import Word
from pydub import AudioSegment

from src.helper import logger
from src.helper.data_handler import DataHandler
from src.helper.local_agreement import LocalAgreement
from src.websocket.stream_transcriber import Transcriber

# To Calculate the seconds of audio in a chunk of 16000 Hz, 2 bytes per sample and 1 channel (as typically used in Whisper):
# 16000 Hz * 2 bytes * 1 channel = 32000 bytes per second
BYTES_PER_SECOND = 32000

# This is the number of words we wait before printing a final transcription
FINAL_TRANSCRIPTION_THRESHOLD = 6

# Max size of window defined in bytes
MAX_WINDOW_SIZE_BYTES = BYTES_PER_SECOND * 30

# This is the number of seconds we wait before printing a partial transcription
PARTIAL_TRANSCRIPTION_TIMEOUT = 1


class Stream:
    def __init__(self, transcriber: Transcriber, id: int):
        self.logger = logger.get_logger_with_id(__name__, str(id))
        self.transcriber = transcriber
        self.id = id
        self.close_stream = False

        self.sliding_window = b""
        self.total_bytes = b""
        self.window_start_timestamp = 0
        self.agreement = LocalAgreement()
        self.bytes_received_since_last_transcription = 0
        self.final_transcriptions = []
        self.export_audio = b""
        self.previous_byte_count = 0

    async def echo(self, websocket: WebSocket) -> None:
        try:
            while not self.close_stream and websocket.client_state != WebSocketState.DISCONNECTED:
                message = await websocket.receive()
                websocket.client_state

                if "bytes" in message:
                    message = message["bytes"]
                    self.bytes_received_since_last_transcription += len(message)
                    self.sliding_window += message
                    self.total_bytes += message
                    self.export_audio = self.concatenate_audio_with_crossfade(
                        self.export_audio, message
                    )

                    if self.bytes_received_since_last_transcription >= PARTIAL_TRANSCRIPTION_TIMEOUT:
                        self.logger.info(
                            f"NEW PARTIAL: length of current window: {len(self.sliding_window)}"
                        )
                        await self.transcribe_sliding_window(
                            websocket,
                            self.sliding_window
                        )

                    # Send final if either threshhold is reached or sentence ended
                    if self.agreement.get_confirmed_length() > FINAL_TRANSCRIPTION_THRESHOLD or self.agreement.contains_has_sentence_end():
                        self.logger.debug(
                            f"NEW FINAL: length of chunk cache: {len(self.sliding_window)}"
                        )
                        # does this need to be async?
                        await self.flush_final(
                            websocket,
                            self.sliding_window,
                        )

                        # Move finalize and pending pointer
                        if len(self.sliding_window) > MAX_WINDOW_SIZE_BYTES:
                            bytes_to_cut_off = len(self.sliding_window) - MAX_WINDOW_SIZE_BYTES
                            self.logger.debug(f"Reducing sliding window size by {bytes_to_cut_off} bytes")
                            self.previous_byte_count += bytes_to_cut_off
                            self.window_start_timestamp += bytes_to_cut_off / BYTES_PER_SECOND
                            self.sliding_window = self.sliding_window[bytes_to_cut_off:]

                elif "text" in message:
                    message = message["text"]
                    self.logger.debug(f"Received control message (string): {message}")
                    if "eof" in message:
                        if "eof-finalize" in message and self.bytes_received_since_last_transcription > 0:
                            # Non default behaviour but useful for some scenarios, like testing
                            result = await self.finalize_transcript()
                            self.last_final_result_object = result
                            self.final_transcriptions.append(result)
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


    async def finalize_transcript(self) -> Dict:
        current_transcript = self.agreement.flush_confirmed() + self.agreement.unconfirmed
        return await self.build_result_from_words(current_transcript)

    async def flush_final(
        self, websocket: WebSocket, chunk_cache
    ) -> None:
        """Function to transcribe a chunk of audio"""
        try:
            agreed_results = []
            if self.agreement.contains_has_sentence_end():
                agreed_results = self.agreement.flush_at_sentence_end()
            else:
                agreed_results = self.agreement.flush_confirmed(FINAL_TRANSCRIPTION_THRESHOLD)

            result = await self.build_result_from_words(agreed_results)
            self.last_final_result_object = result
            self.last_final_bytes = chunk_cache
            self.final_transcriptions.append(result)

            await websocket.send_text(json.dumps(result, indent=2))
            self.logger.debug(
                f"Published final of {len(agreed_results)}."
            )

        except Exception:
            self.logger.error(
                f"Error while transcribing audio: {traceback.format_exc()}"
            )
            self.close_stream = True

    async def build_result_from_words(self, words: List[Word]) -> Dict:
        overall_transcribed_seconds = self.previous_byte_count / BYTES_PER_SECOND

        cutoff_timestamp = 0
        if len(self.final_transcriptions) > 0:
            cutoff_timestamp = self.final_transcriptions[-1]["result"][-1]["end"]

        result = {"result": [], "text": ""}
        for word in words:
            start = float(f"{word.start:.6f}") + overall_transcribed_seconds
            end = float(f"{word.end:.6f}")  + overall_transcribed_seconds
            conf = float(f"{word.probability:.6f}")
            if end <= cutoff_timestamp:
                continue
            result["result"].append(
                {
                    "conf": conf,
                    # the start time and end time is the time of the word minus the time of the current final
                    "start": start,
                    "end": end,
                    "word": word.word.strip(),
                }
            )
        result["text"] = " ".join([x["word"] for x in result["result"]])
        return result


    async def transcribe_sliding_window(
        self, websocket, window_content
    ) -> None:
        try:
            # Ensure the chunk_cache is not empty before proceeding
            if len(window_content) == 0:
                self.logger.warning("Received empty chunk, skipping transcription.")
                return  # Skip transcription for empty chunk

            start_time = time.time()
            result: str = "Missing data"

            # Pass the chunk to the transcriber
            segments, _ = self.transcriber._transcribe(
                window_content,
            )

            cutoff_timestamp = 0
            if len(self.final_transcriptions) > 0:
                # Absolute timestamp - thrown out bytes -> timestamp in the current window
                self.logger.debug(len(self.final_transcriptions))
                self.logger.debug(self.final_transcriptions[-1])
                cutoff_timestamp = self.final_transcriptions[-1]["result"][-1]["end"] - (self.previous_byte_count / BYTES_PER_SECOND)

            new_words = []

            for segment in list(segments):
                if segment.words is None:
                    continue
                for word in segment.words:
                    new_words.append(word)

            text = ""

            if len(self.agreement.unconfirmed) > 0:
                text = " ".join([w.word for w in new_words if w.start >= cutoff_timestamp])

            self.agreement.merge(new_words)

            # Sometimes the local agreement cannot be sure for quite a while
            # Therefore we just overwrite it
            if len(self.agreement.get_confirmed_text()) > 0:
                text = self.agreement.get_confirmed_text()

            result = json.dumps({"partial": text}, indent=2)

            await websocket.send_text(result)

            end_time = time.time()
            self.logger.debug(
                "Partial transcription took {:.2f} s".format(end_time - start_time)
            )
            self.bytes_received_since_last_transcription = 0

        except Exception:
            self.logger.error(
                "Error while transcribing audio: {}".format(traceback.format_exc())
            )
            self.close_stream = True

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

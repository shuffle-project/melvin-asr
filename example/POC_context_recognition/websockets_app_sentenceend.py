"""Module to handle the WebSocket server"""
import asyncio
import json
import time
import websockets

from websockets_settings import default_websocket_settings
from transcriber import Transcriber

# To Calculate the seconds of audio in a chunk of 16000 Hz, 2 bytes per sample and 1 channel (as typically used in Whisper):
# 16000 Hz * 2 bytes * 1 channel = 32000 bytes per second
BYTES_PER_SECOND = 32000

# We want to print a final transcription after a certain amount of time
# This is the number of seconds we want to wait before printing a final transcription
FINAL_TRANSCRIPTION_TIMEOUT = 120

# We want to print a partial transcription after a certain amount of time
# This is the number of seconds we want to wait before printing a partial transcription
PARTIAL_TRANSCRIPTION_TIMEOUT = 1


class WebSocketServer:
    """Class to handle a WebSocket ASR server"""

    def __init__(self, port: int, host: str = "localhost"):
        self.port = port
        self.host = host

        self.transcriber = Transcriber()

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
            print("Server started at port {}".format(self.port))
            await asyncio.Future()  # run forever

    async def echo(self, websocket, path):
        print("echo started")
        self.overall_audio_bytes = b""
        self.overall_transcribed_bytes = b""
        self.chunk_cache = b""
        self.recently_added_chunk_cache = b""
        while True:
            try:
                message = await websocket.recv()
                if isinstance(message, bytes) is True:
                    self.chunk_cache += message
                    self.recently_added_chunk_cache += message
                    self.overall_audio_bytes += message

                    if len(self.recently_added_chunk_cache) >= self.partial_treshold:
                        print("********** NEW PARTIAL **********")
                        # Here we need to ensure that the transcribe_chunk_partial does not run longer than the length of the chunks.
                        asyncio.ensure_future(
                            self.transcribe_sentences(
                                websocket,
                                self.chunk_cache,
                            )
                        )
                        self.recently_added_chunk_cache = b""

                else:
                    print("Received message: {}".format(message))
                    await websocket.send("wrong data type")

            except websockets.exceptions.ConnectionClosedOK:
                print("Client left")
                break
            except websockets.exceptions.ConnectionClosedError:
                print("Client left unexpectedly")
                break
            except Exception as e:
                print("Error while receiving message: {}".format(e))
                break

    async def transcribe_sentences(self, websocket, chunk_cache):
        data = self.transcriber.transcribe_audio_audio_chunk(
            chunk_cache, settings=default_websocket_settings()
        )
        if "segments" not in data:
            raise NameError()

        cut_second = 0
        text = ""
        for segment in data["segments"]:
            text = text + segment["text"]

        if self.contains_sentence_ending_punctuation(text) is False:
            result = json.dumps({"partial": text}, indent=2)
            await websocket.send(result)
            return

        for segment in data["segments"]:
            for word in segment["words"]:
                if self.contains_sentence_ending_punctuation(word["word"]):
                    # print(word["word"])
                    cut_second = float("{:.6f}".format(float(word["end"])))
                    # print(cut_second)
                    break

        index = round(cut_second * BYTES_PER_SECOND)
        final_sentence = self.chunk_cache[:index]
        self.chunk_cache = self.chunk_cache[index + 1 :]

        data = self.transcriber.transcribe_audio_audio_chunk(
            final_sentence, settings=default_websocket_settings()
        )
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
                print(text)
            result = json.dumps({"result": result, "text": text}, indent=2)
        await websocket.send(result)

    def contains_sentence_ending_punctuation(websocket, s):
        sentence_endings = {".", "!", "?"}
        return any(char in sentence_endings for char in s)


if __name__ == "__main__":
    try:
        server = WebSocketServer("1234")
        asyncio.run(server.main())
    except KeyboardInterrupt as e:
        print("interrupted by user")
        exit()

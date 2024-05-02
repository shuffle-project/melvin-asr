import asyncio
import json
import time
import websockets

from streaming_model_handler import StreamingModelHandler

transcribe_bytes = StreamingModelHandler(3).transcribe_bytes

PORT = 8764

# To Calculate the seconds of audio in a chunk of 16000 Hz, 2 bytes per sample and 1 channel (as typically used in Whisper):
# 16000 Hz * 2 bytes * 1 channel = 32000 bytes per second
BYTES_PER_SECOND = 32000

# We want to print a final transcription after a certain amount of time
# This is the number of seconds we want to wait before printing a final transcription
FINAL_TRANSCRIPTION_TIMEOUT = 10

# We want to print a partial transcription after a certain amount of time
# This is the number of seconds we want to wait before printing a partial transcription
PARTIAL_TRANSCRIPTION_TIMEOUT = 2


class VoskWebSocketServer:
    """Class to handle a Vosk like WebSocket ASR server"""

    def __init__(self):
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

    async def main(self):
        async with websockets.serve(self.echo, "localhost", PORT):
            print("Server started at port {}".format(PORT))
            await asyncio.Future()  # run forever

    async def echo(self, websocket, path):
        self.overall_audio_bytes = b""
        self.overall_transcribed_bytes = b""
        start_time_new_connection = time.time()
        while True:
            try:
                message = await websocket.recv()
                print("********** NEW MESSAGE **********")
                print("Time since last connection: {}".format(time.time() - start_time_new_connection))
                print(
                    "overall audio bytes: {}".format(
                        str(len(self.overall_audio_bytes) / BYTES_PER_SECOND)
                    )
                )
                print(
                    "overall transcribed bytes: {}".format(
                        str(len(self.overall_transcribed_bytes) / BYTES_PER_SECOND)
                    )
                )
                print(
                    "difference in s: {}".format(
                        str(
                            (
                                len(self.overall_audio_bytes)
                                - len(self.overall_transcribed_bytes)
                            )
                            / BYTES_PER_SECOND
                        )
                    )
                )
                if isinstance(message, bytes) is True:
                    self.chunk_cache += message
                    self.recently_added_chunk_cache += message
                    self.overall_audio_bytes += message
                    print("Received audio data ({} bytes)".format(len(message)))
                    print(
                        "Cache size: {} bytes".format(
                            len(self.recently_added_chunk_cache)
                        )
                    )
                    print(
                        "Cache size: {} bytes".format(
                            len(self.recently_added_chunk_cache)
                        )
                    )
                    if (
                        len(self.chunk_cache)
                        >= BYTES_PER_SECOND * FINAL_TRANSCRIPTION_TIMEOUT
                    ):
                        print("********** NEW FINAL **********")
                        asyncio.ensure_future(
                            self.transcribe_all_chunk_cache(
                                websocket, self.chunk_cache, message
                            )
                        )
                        self.chunk_cache = b""
                    if (
                        len(self.recently_added_chunk_cache)
                        >= BYTES_PER_SECOND * PARTIAL_TRANSCRIPTION_TIMEOUT
                    ):
                        print("********** NEW PARTIAL **********")
                        # Here we need to ensure that the transcribe_chunk_partial does not run longer than the length of the chunks.
                        asyncio.ensure_future(
                            self.transcribe_chunk_partial(
                                websocket, self.chunk_cache, message
                            )
                        )
                        self.recently_added_chunk_cache = b""

                else:
                    print("Received message: {}".format(message))
                    await websocket.send("wrong data type")
            except websockets.exceptions.ConnectionClosedOK:
                break
            except websockets.exceptions.ConnectionClosedError:
                print("Client left unexpectedly")
                break
            except Exception as e:
                print(e)
                break

    async def transcribe_all_chunk_cache(self, websocket, chunk_cache, message) -> str:
        """Function to transcribe a chunk of audio"""
        start_time = time.time()
        result: str = ""
        data = await transcribe_bytes(chunk_cache)
        self.overall_transcribed_bytes += message
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
        print("Sent transcription (took {:.2f} s)".format(end_time - start_time))

    async def transcribe_chunk_partial(self, websocket, chunk_cache, message) -> str:
        start_time = time.time()
        result: str = "Missing data"

        data = await transcribe_bytes(chunk_cache)
        self.overall_transcribed_bytes += message
        if "segments" in data:
            text = ""
            for segment in data["segments"]:
                text += segment["text"]
            result = json.dumps({"partial": text}, indent=2)
        else:
            print("Transcription Data is empty, no segments found")
        await websocket.send(result)

        end_time = time.time()
        print(
            "Start time: {}".format(
                time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(start_time))
                + f".{int((start_time % 1) * 1000):03d}"
            )
        )
        print(
            "End time: {}".format(
                time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(end_time))
                + f".{int((end_time % 1) * 1000):03d}"
            )
        )
        print("Partial transcription took {:.2f} s".format(end_time - start_time))


if __name__ == "__main__":
    server = VoskWebSocketServer()
    asyncio.run(server.main())

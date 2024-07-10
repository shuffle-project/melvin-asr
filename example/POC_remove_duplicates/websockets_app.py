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
FINAL_TRANSCRIPTION_TIMEOUT = 6

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

        # Last final for duplicates
        self.last_final = b""

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

                    if len(self.chunk_cache) >= self.final_treshold:
                        print("********** NEW FINAL **********")
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
                        print("********** NEW PARTIAL **********")
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

    async def transcribe_all_chunk_cache(
        self, websocket, chunk_cache, recent_cache
    ) -> str:
        """Function to transcribe a chunk of audio"""
        start_time = time.time()
        result: str = ""
        data = self.transcriber.transcribe_audio_audio_chunk(
            chunk_cache,
            "Last words of the audio: " + self.last_final,
            settings=default_websocket_settings(),
        )
        print(self.last_final)
        # self.adjust_threshold_on_latency()
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
                clean_final = self.remove_duplicates(self.last_final, text)
            result = json.dumps({"result": result, "text": clean_final}, indent=2)
        await websocket.send(result)
        self.last_final = text
        end_time = time.time()
        print("Final Transcription took {:.2f} s".format(end_time - start_time))

    async def transcribe_chunk_partial(
        self, websocket, chunk_cache, recent_cache
    ) -> str:
        start_time = time.time()
        result: str = "Missing data"

        prompt = ""
        data = self.transcriber.transcribe_audio_audio_chunk(
            chunk_cache, prompt, settings=default_websocket_settings()
        )
        # self.adjust_threshold_on_latency()
        self.overall_transcribed_bytes += recent_cache
        if "segments" in data:
            text = ""
            for segment in data["segments"]:
                text += segment["text"]
            result = json.dumps({"partial": text}, indent=2)
        else:
            print("Transcription Data is empty, no segments found")
        await websocket.send(result)

        end_time = time.time()
        print("Partial transcription took {:.2f} s".format(end_time - start_time))

    def remove_duplicates(self, last_final, current_final):
        # Zerlege die Texte in Wörterlisten
        words1 = last_final.split()
        words2 = current_final.split()

        # Nimm die letzten 2 Wörter von text1 und die ersten 2 Wörter von text2
        last_five_words_text1 = words1[-2:]
        first_five_words_text2 = words2[:2]

        # Erstelle eine Liste der Wörter in text2 ohne die Duplikate
        new_words2 = first_five_words_text2.copy()
        for word in first_five_words_text2:
            if word in last_five_words_text1:
                new_words2.remove(word)

        # Kombiniere die neuen Wörter von text2 mit dem Rest der Wörter von text2
        unique_text2 = new_words2 + words2[2:]

        # Erstelle den neuen Text2 String
        return " ".join(unique_text2)


if __name__ == "__main__":
    try:
        server = WebSocketServer("1234")
        asyncio.run(server.main())
    except KeyboardInterrupt as e:
        print("interrupted by user")
        exit()

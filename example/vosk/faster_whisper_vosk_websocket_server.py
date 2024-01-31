# pylint: disable-all

import asyncio
import io
import json
from faster_whisper import WhisperModel
import wave

from websockets import serve
import websockets

from segment_info_parser import parse_segments_and_info_to_dict

model = WhisperModel("tiny", device="cpu", compute_type="int8")


class VoskWebSocketServer:
    """Class to handle a Vosk like WebSocket ASR server"""

    def __init__(self):
        self.moving_chunk_cache = b""
        self.all_chunk_cache = b""

        # transcription parameters
        # number of chunks to cache for partial transcription
        self.moving_chunk_cache_size = 100

        # audio parameters
        self.sample_rate = 16000
        self.num_channels = 1
        self.sampwidth = 2

        # helper variables
        self.is_busy = (
            False  # Flag to indicate if the server is currently handling a client
        )

    async def main(self):
        async with serve(self.echo, "localhost", 8764):
            await asyncio.Future()  # run forever

    async def echo(self, websocket):
        """Function to handle the WebSocket connection"""

        while True:
            try:
                message = await websocket.recv()
                if isinstance(message, bytes):
                    print("bytes")
                    response = self.transcribe_chunk_partial(message)
                    await websocket.send(response)
                else:
                    print(message)
                    if "config" in message:
                        print("Adjusting Config...")
                        config = json.loads(message)
                        self.sample_rate = config["config"]["sample_rate"]
                        print("Sample Rate: " + str(self.sample_rate))
                        continue
                    if "eof" in message:
                        response = self.transcribe_all_chunk_cache()
                        print("sending final")
                        await websocket.send(response)
                        self.moving_chunk_cache = b""
                        self.all_chunk_cache = b""
            except websockets.exceptions.ConnectionClosedOK:
                print("ConnectionClosedOK")
                break

    def transcribe_all_chunk_cache(
        self,
    ) -> str:
        """Function to transcribe a chunk of audio"""
        if len(self.all_chunk_cache) > 0:
            data = self.transcribe_bytes(self.moving_chunk_cache)
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
                return json.dumps({"result": result, "text": text}, indent=2)
        return json.dumps({"result": [], "text": ""}, indent=2)

    def transcribe_chunk_partial(
        self,
        chunk,
    ) -> str:
        """Function to transcribe a chunk of audio"""
        self.moving_chunk_cache = self.moving_chunk_cache + chunk
        self.all_chunk_cache = self.all_chunk_cache + chunk
        # If the chunk cache is larger than 10 times the size of the chunk
        if len(self.moving_chunk_cache) >= (len(chunk) * self.moving_chunk_cache_size):
            # cut the first bytes of the length of the new chunk
            self.moving_chunk_cache = self.moving_chunk_cache[len(chunk) :]
        # Create a WAV file in memory with the correct headers
        if len(self.moving_chunk_cache) > 0:
            data = self.transcribe_bytes(self.moving_chunk_cache)
            if "segments" in data:
                text = ""
                for segment in data["segments"]:
                    text = text + segment["text"]
                return json.dumps({"partial": text}, indent=2)

    def transcribe_bytes(self, audio_chunk: bytes):
        """Function to transcribe a chunk of audio"""
        with io.BytesIO() as wav_io:
            with wave.open(wav_io, "wb") as wav_file:
                # Set the parameters of the wav file
                wav_file.setnchannels(self.num_channels)
                wav_file.setsampwidth(self.sampwidth)
                wav_file.setframerate(self.sample_rate)
                wav_file.writeframes(audio_chunk)
            # Seek to the beginning so it can be read by model
            wav_io.seek(0)
            # Transcribe the audio chunk
            segments, info = model.transcribe(wav_io, word_timestamps=True)
            return parse_segments_and_info_to_dict(segments, info)


if __name__ == "__main__":
    server = VoskWebSocketServer()
    asyncio.run(server.main())

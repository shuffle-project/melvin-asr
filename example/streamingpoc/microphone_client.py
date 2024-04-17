"""Example of using the Websocket Server by sending Microphone audio asynchronously."""
import asyncio
import json
import threading
import time
import queue
import speech_recognition as sr
from pydub import AudioSegment
import websockets

AUDIO_FILE_LENGTH = 4  # seconds


class SpeechListener:
    """Listens to the microphone and sends the audio data to the websocket server."""

    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.stop_event = threading.Event()
        self.audio_queue = queue.Queue()
        self.loop = asyncio.new_event_loop()
        self.websocket_task = threading.Thread(target=self.start_websocket_task)
        self.listen_thread = None

    async def send_file_as_websocket(self):
        """Sends the input file to the WebSocket server."""
        while not self.stop_event.is_set():
            try:
                data = self.audio_queue.get(timeout=1)
            except queue.Empty:
                continue

            async with websockets.connect("ws://localhost:8764") as websocket:
                await websocket.send(data)
                print("Sent audio data")
                response = await websocket.recv()
                print("\033[90m" + response + "\033[0m")
                # try:
                #     data = json.loads(response)
                #     if "segments" in data:
                #         for segment in data["segments"]:
                #             print("\033[96m" + segment[4] + "\033[0m")
                # except Exception as e:
                #     print("\033[93m" + str(e) + "\033[0m")

    def listen_for_speech(self):
        """Listens to the microphone and puts the audio data into the queue."""
        with sr.Microphone() as source:
            while not self.stop_event.is_set():
                print("Say something!")
                start_time = time.time()
                audio_data = self.recognizer.record(source, duration=AUDIO_FILE_LENGTH)

                elapsed_time = time.time() - start_time
                if elapsed_time < AUDIO_FILE_LENGTH:
                    # If recording is shorter than AUDIO_FILE_LENGTH seconds,
                    # add silence to make it AUDIO_FILE_LENGTH seconds long
                    silence_duration = AUDIO_FILE_LENGTH - elapsed_time
                    silence = AudioSegment.silent(duration=silence_duration * 1000)
                    audio_segment = AudioSegment(
                        data=audio_data.get_wav_data(),
                        sample_width=audio_data.sample_width,
                        frame_rate=audio_data.sample_rate,
                        channels=1,
                    )
                    audio_segment += silence
                else:
                    audio_segment = AudioSegment(
                        data=audio_data.get_wav_data(),
                        sample_width=audio_data.sample_width,
                        frame_rate=audio_data.sample_rate,
                        channels=1,
                    )

                resampled_audio = audio_segment.set_frame_rate(16000).set_channels(1)
                resampled_audio_data = resampled_audio.raw_data
                self.audio_queue.put(resampled_audio_data)

    def start_listening(self):
        """Starts the listening thread and the websocket task."""
        self.listen_thread = threading.Thread(target=self.listen_for_speech)
        self.listen_thread.start()
        self.websocket_task.start()

    def start_websocket_task(self):
        """Starts the websocket task."""
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self.send_file_as_websocket())

    def stop_listening(self):
        """Stops the listening thread and the websocket task."""
        self.stop_event.set()
        self.listen_thread.join()
        self.loop.call_soon_threadsafe(self.loop.stop)
        self.websocket_task.join()


if __name__ == "__main__":
    listener = SpeechListener()
    listener.start_listening()

    try:
        while True:
            time.sleep(2)  # Sleep briefly to avoid busy waiting
    except KeyboardInterrupt:
        listener.stop_listening()

    print("Program ended.")

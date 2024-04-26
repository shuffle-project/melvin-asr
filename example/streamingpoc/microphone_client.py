"""Example of using the Websocket Server by sending Microphone audio asynchronously."""
import pyaudio
import asyncio
import json
import threading
import time
import queue
import speech_recognition as sr
from pydub import AudioSegment
import websockets

phrase_time_limit = 0.5  # seconds


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
        """Sends the input file to the WebSocket server and prints responses."""
        while not self.stop_event.is_set():
            try:
                data = self.audio_queue.get(timeout=1)
            except queue.Empty:
                continue

            async with websockets.connect("ws://localhost:8764") as websocket:
                await websocket.send(data)
                print("Sent audio data")
                response = await websocket.recv()
                print_response = json.loads(response)
                if 'partial' in print_response:
                    print(f"Transcription: {print_response['partial']}")
                else:
                    print("Received: ", response)

    def listen_for_speech(self):
        """Listens to the microphone and puts the audio data into the queue in smaller chunks."""
        with sr.Microphone() as source:
            p = pyaudio.PyAudio()
            stream = p.open(format=pyaudio.paInt16,
                            channels=1,
                            rate=16000,
                            input=True,
                            frames_per_buffer=320)  # 20 ms of audio per buffer
            print("Listening for speech...")
            while not self.stop_event.is_set():
                audio_data = self.recognizer.listen(source, phrase_time_limit)  # Capture continuously in 0.5 sec chunks
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

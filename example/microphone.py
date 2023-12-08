import asyncio
import threading
import time
import speech_recognition as sr
from pydub import AudioSegment
import websockets
import queue


class SpeechListener:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.stop_event = threading.Event()
        self.audio_queue = queue.Queue()
        self.loop = asyncio.new_event_loop()
        self.websocket_task = threading.Thread(target=self.start_websocket_task)

    async def send_file_as_websocket(self):
        while not self.stop_event.is_set():
            try:
                data = self.audio_queue.get(timeout=1)
            except queue.Empty:
                continue

            async with websockets.connect("ws://localhost:1338") as websocket:
                await websocket.send(data)
                print("Sent audio data")
                response = await websocket.recv()
                print("\n**************")
                print("Server response:", response)
                print("**************\n")

    def listen_for_speech(self):
        with sr.Microphone() as source:
            while not self.stop_event.is_set():
                print("Say something!")
                audio_data = self.recognizer.listen(source, phrase_time_limit=2)

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
        self.listen_thread = threading.Thread(target=self.listen_for_speech)
        self.listen_thread.start()
        self.websocket_task.start()

    def start_websocket_task(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self.send_file_as_websocket())

    def stop_listening(self):
        self.stop_event.set()
        self.listen_thread.join()
        self.loop.call_soon_threadsafe(self.loop.stop)
        self.websocket_task.join()


if __name__ == "__main__":
    listener = SpeechListener()
    listener.start_listening()
    print("Listening stopped.")

    try:
        while True:
            time.sleep(2)  # Sleep briefly to avoid busy waiting
    except KeyboardInterrupt:
        pass

    listener.stop_listening()
    print("Program ended.")

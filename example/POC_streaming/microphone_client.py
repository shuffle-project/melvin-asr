import asyncio
import threading
import time
import queue
import speech_recognition as sr
from pydub import AudioSegment
import websockets

# Capture continuously in seconds
AUDIO_FILE_LENGTH = 0.5


class SpeechListener:
    """Listens to the microphone and sends the audio data to the websocket server."""

    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.stop_event = threading.Event()
        self.audio_queue = queue.Queue()
        self.loop = asyncio.new_event_loop()
        self.websocket_task = threading.Thread(target=self.run_websocket_tasks)
        self.listen_thread = threading.Thread(target=self.listen_for_speech)
        self.websocket_url = "ws://141.62.73.33:8764"

    async def send_file_as_websocket(self, websocket):
        """Sends the input file to the WebSocket server and prints responses."""
        try:
            data = self.audio_queue.get(timeout=AUDIO_FILE_LENGTH/10)
            await websocket.send(data)
        except queue.Empty:
            # print("Queue is empty.")
            return

    async def receive_from_websocket(self, websocket):
        """Receives the response from the WebSocket server."""
        # print("Receiving from WebSocket server...")
        try:
            response = await asyncio.wait_for(websocket.recv(), timeout=AUDIO_FILE_LENGTH/10)
            print(f"Received from server: {response}")
        except asyncio.TimeoutError:
            return

    def listen_for_speech(self):
        """Listens to the microphone and puts the audio data into the queue in smaller chunks."""
        with sr.Microphone() as source:
            # print("Listening for speech...")
            while not self.stop_event.is_set():
                audio_data = self.recognizer.listen(source, phrase_time_limit=AUDIO_FILE_LENGTH)
                audio_segment = AudioSegment(
                    data=audio_data.get_wav_data(),
                    sample_width=audio_data.sample_width,
                    frame_rate=audio_data.sample_rate,
                    channels=1,
                )
                resampled_audio = audio_segment.set_frame_rate(16000).set_channels(1)
                self.audio_queue.put(resampled_audio.raw_data)

    def run_websocket_tasks(self):
        """Manages WebSocket tasks."""
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self.websocket_tasks())

    async def websocket_tasks(self):
        async with websockets.connect(self.websocket_url) as websocket:
            while not self.stop_event.is_set():
                send_task = asyncio.create_task(self.send_file_as_websocket(websocket))
                receive_task = asyncio.create_task(self.receive_from_websocket(websocket))
                await asyncio.gather(send_task, receive_task)

    def start_listening(self):
        """Starts the listening thread and the websocket task."""
        self.listen_thread.start()
        self.websocket_task.start()

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

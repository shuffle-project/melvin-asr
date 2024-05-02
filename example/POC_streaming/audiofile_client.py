import asyncio
import threading
import time
import queue
from pydub import AudioSegment
import websockets

# Constants
AUDIO_FILE_PATH = "scholz.wav"
AUDIO_CHUNK_LENGTH = 500  # milliseconds

class SpeechListener:
    """Handles sending audio data from a file to a WebSocket server."""

    def __init__(self, websocket_url):
        self.websocket_url = websocket_url
        self.loop = asyncio.new_event_loop()
        self.websocket_thread = threading.Thread(target=self.run_websocket_tasks)
        self.stop_event = threading.Event()
        self.audio_chunks = []

    def process_audio_file(self):
        """Reads and queues audio from the file."""
        audio = AudioSegment.from_wav(AUDIO_FILE_PATH)
        for chunk in audio[::AUDIO_CHUNK_LENGTH]:
            resampled_chunk = chunk.set_frame_rate(16000).set_channels(1)
            self.audio_chunks.append(resampled_chunk)
        print(f"Audio file processed into {len(self.audio_chunks)} chunks.")

    async def websocket_tasks(self):
        """Connects to the WebSocket server and handles sending/receiving."""
        async with websockets.connect(self.websocket_url) as websocket:
            while not self.stop_event.is_set():
                print("receive_task")
                send_task = asyncio.create_task(self.send_audio_to_websocket(websocket))
                print("receive_task")
                receive_task = asyncio.create_task(self.receive_from_websocket(websocket))
                await asyncio.gather(send_task, receive_task)

    async def send_audio_to_websocket(self, websocket):
        """Sends queued audio data to the WebSocket server."""
        try:
            if (len(self.audio_chunks) == 0):
                print("No more chunks to send.")
                exit()

            data = self.audio_chunks.pop(0).raw_data
            print("chunks left: ", len(self.audio_chunks))
            await websocket.send(data)
            time.sleep(AUDIO_CHUNK_LENGTH / 1000.0 / 2.5)  # Maintain sending rate as per chunk length
        except queue.Empty:
            return

    async def receive_from_websocket(self, websocket):
        """Receives responses from the WebSocket server."""
        try:
            response = await asyncio.wait_for(websocket.recv(), timeout=AUDIO_CHUNK_LENGTH / 1000.0/ 2.5)
            print(f"Received from server: {response}")
        except asyncio.TimeoutError:
            print("Timeout error")

    def run_websocket_tasks(self):
        """Manages WebSocket tasks using asyncio."""
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self.websocket_tasks())

    def start(self):
        """Starts the audio processing and WebSocket communication threads."""
        self.process_audio_file()
        self.websocket_thread.start()

    def stop(self):
        """Signals threads to stop and waits for them to finish."""
        self.stop_event.set()
        self.audio_processing_thread.join()
        self.loop.call_soon_threadsafe(self.loop.stop)
        self.websocket_thread.join()

if __name__ == "__main__":
    websocket_url = "ws://localhost:8764"
    listener = SpeechListener(websocket_url)
    listener.start()

    try:
        while True:
            time.sleep(2)
    except KeyboardInterrupt:
        listener.stop()
        print("Program ended.")

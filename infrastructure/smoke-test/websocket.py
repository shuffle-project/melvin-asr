import asyncio
import json
import sys
import threading
import time
import queue
from pydub import AudioSegment
import websockets

# Constants
AUDIO_FILE_PATH = "scholz_in_kurz.wav"
AUDIO_CHUNK_LENGTH = 1 # seconds
BYTES_PER_SECOND = 32000  # 16 kHz, 16-bit audioGPU Usage Metrics 

class SpeechListener:
    """Handles sending audio data from a file to a WebSocket server."""

    def __init__(self, websocket_url):
        self.websocket_url = websocket_url
        self.loop = asyncio.new_event_loop()
        self.websocket_thread = threading.Thread(target=self.run_websocket_tasks)
        self.stop_event = threading.Event()
        self.audio_chunks = []
        self.reveived_from_server = []

    def process_audio_file(self):
        """Reads and queues audio from the file."""
        audio = AudioSegment.from_wav(AUDIO_FILE_PATH)
        resampled_audio = audio.set_frame_rate(16000).set_channels(1)
        raw_audio = resampled_audio.raw_data
        chunk_length = int(AUDIO_CHUNK_LENGTH * BYTES_PER_SECOND)
        num_chunks = len(raw_audio) // chunk_length
        for i in range(num_chunks):
            chunk = raw_audio[i * chunk_length : (i + 1) * chunk_length]
            self.audio_chunks.append(chunk)
        remaining_bytes = len(raw_audio) % chunk_length
        if remaining_bytes > 0:
            last_chunk = raw_audio[-remaining_bytes:]
            self.audio_chunks.append(last_chunk)
        print(f"Audio file processed into {len(self.audio_chunks)} chunks.")

    async def websocket_tasks(self):
        """Connects to the WebSocket server and handles sending/receiving."""
        async with websockets.connect(self.websocket_url) as websocket:
            while not self.stop_event.is_set():
                send_task = asyncio.create_task(self.send_audio_to_websocket(websocket))
                receive_task = asyncio.create_task(self.receive_from_websocket(websocket))
                await asyncio.gather(send_task, receive_task)

    async def send_audio_to_websocket(self, websocket):
        """Sends queued audio data to the WebSocket server."""
        try:
            if (len(self.audio_chunks) == 0):
                print("No more chunks to send. Waiting for server response...")
                await asyncio.sleep(3)
                print("\n".join(self.reveived_from_server))
                exit()

            data = self.audio_chunks.pop(0)
            await websocket.send(data)
            time.sleep(AUDIO_CHUNK_LENGTH / 2)  # Maintain sending rate as per chunk length
        except queue.Empty:
            return

    async def receive_from_websocket(self, websocket):
        """Receives responses from the WebSocket server."""
        try:
            response = await asyncio.wait_for(websocket.recv(), timeout=AUDIO_CHUNK_LENGTH / 2)
            json_response = json.loads(response)
            if 'text' in json_response:
                print(f"Received final: {json_response['text']}")
                self.reveived_from_server.append(json_response['text'])
            else:
                print(response)
            time.sleep(AUDIO_CHUNK_LENGTH / 4)
        except asyncio.TimeoutError:
            print("Waiting for responses from server...")

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

    PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    host = "localhost"
    websocket_url = f"ws://{host}:{PORT}"
    listener = SpeechListener(websocket_url)
    listener.start()

    try:
        while True:
            time.sleep(2)
    except KeyboardInterrupt:
        listener.stop()
        print("Program ended.")

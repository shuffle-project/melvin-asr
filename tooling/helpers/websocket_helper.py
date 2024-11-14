import asyncio
import websockets
import wave
import json


async def read_wav_file(file_path):
    with wave.open(file_path, "rb") as wav_file:
        return wav_file.readframes(wav_file.getnframes())


# Wrap asyncio execution
def transcribe_file_websocket(filepath: str) -> str:
    loop = asyncio.get_event_loop()
    res = loop.run_until_complete(asyncio.gather(__transcribe_file_websocket(filepath)))
    print(res)
    return res[0]


# websockets is heavily integrated with asyncio...so we have to do this in an asyncio way
async def __transcribe_file_websocket(filepath: str) -> str:
    audio_data = await read_wav_file(filepath)

    messages = []
    try:
        async with websockets.connect("ws://localhost:8394") as websocket_connection:
            await websocket_connection.send(audio_data)
            # Wait...the server needs a few seconds anyway
            await asyncio.sleep(3)

            while True:
                try:
                    message = await asyncio.wait_for(
                        websocket_connection.recv(), timeout=15.0
                    )
                    messages.append(message)
                except asyncio.TimeoutError:
                    # We could also close the connection once we dont have audio frames left
                    # However this seems more error resistant
                    await websocket_connection.close()
                    break
            assert len(messages) > 0
    except websockets.exceptions.ConnectionClosedOK:
        # This is the expected behaviour
        pass
    return json.loads(" ".join(messages))["text"]

import asyncio
import time
from typing import List, Tuple
from helpers.data_helper import WebsocketResult, WebsocketResultBlock
import websockets
from pydub import AudioSegment
import requests
import json
from http import HTTPStatus

TRANSCRIPTION_WEBSOCKET_TIMEOUT = 60.0

async def read_wav_file_into_chunks(file_path, chunk_duration_ms=1000):
    audio = AudioSegment.from_file(file_path)
    chunks = []
    for i in range(0, len(audio), chunk_duration_ms):
        chunks.append(audio[i : i + chunk_duration_ms].raw_data)
    return chunks


def safe_to_json(text: str) -> dict | None:
    data = None
    try:
        data = json.loads(text)
    except ValueError:
        # text was not valid json
        pass
    return data


# TODO: this function can be merged with the rest transcription once the export apis for rest and websockets have been unified
def fetch_transcription(id: str, api_key: str) -> str:
    # This means the returned id is NOT! a transcription id
    if len(id) > 32 or len(id) == 0 or not id.isalnum():
        return ""

    r = requests.get(
        f"http://localhost:8393/export/transcript/{id}",
        headers={"Authorization": api_key},
    )
    if r.status_code == HTTPStatus.OK:
        data = r.json()
        res = ""
        for segment in data:
            if "text" in segment:
                res += f" {segment['text']}"
        return res

    print("Desired ID could not be resolved")
    # Make sure the benchmark does not terminate if one file fails
    # Faulty files are marked in the final table either way
    return ""

def transcribe_file_websocket(filepath: str, api_key:str, scale:str, debug=False) -> WebsocketResult:
    result = WebsocketResult(scale=scale)
    start_time = time.time()
    loop = asyncio.get_event_loop()
    res = loop.run_until_complete(
        asyncio.gather(__transcribe_file_websocket(filepath, debug))
    )
    partials, transciption_id  = res[0]
    if  partials is None or len(transciption_id) == 0:
        result.faulty = True
        return result

    result.partial_blocks = partials
    result.duration = time.time() - start_time

    fetched_transcript = fetch_transcription(transciption_id, api_key)

    if len(fetched_transcript) == 0:
        result.faulty = True
        return result

    result.combined_transcript = fetched_transcript 

    return result

# websockets is heavily integrated with asyncio...so we have to do this in an asyncio way
async def __transcribe_file_websocket(filepath: str, debug=False) -> Tuple[List[WebsocketResultBlock] | None, str]:
    audio_data = await read_wav_file_into_chunks(filepath)
    result: List[WebsocketResultBlock] = [WebsocketResultBlock()]
    id: str = ""
    message_count = 0
    try:
        async with websockets.connect("ws://localhost:8394") as websocket_connection:
            while True:
                try:
                    if len(audio_data) > 0:
                        await websocket_connection.send(audio_data.pop(0))

                    message = await asyncio.wait_for(
                        websocket_connection.recv(),
                        # Wait for 1 second after sending 1 second of audio -> If no audio is sent then we wait longer
                        timeout=TRANSCRIPTION_WEBSOCKET_TIMEOUT if len(audio_data) == 0 else 1,
                    )
                    message_count+=1
                    try:
                        d = json.loads(message)
                        if "partial" in d:
                            result[-1].partials.append(d["partial"])
                            if debug:
                                print(f"Partial: {d['partial']}")
                        elif "text" in d:
                            result[-1].final = d["text"]
                            result.append(WebsocketResultBlock())
                            if debug:
                                print(f"Final: {d['text']}")

                    except json.JSONDecodeError:
                        pass
                except asyncio.TimeoutError:
                    if message_count != 0 and len(audio_data) == 0:
                        break
            if message_count == 0:
                print(f"Empty messages for filepath {filepath}. This should not happen")
                return (None, id)

            await websocket_connection.send("eof-finalize")
            try:
                id = await asyncio.wait_for(
                    websocket_connection.recv(),
                    timeout=TRANSCRIPTION_WEBSOCKET_TIMEOUT
                )
            except Exception:
                pass
            await websocket_connection.close()
    except websockets.exceptions.ConnectionClosedOK:  # This is the expected behaviour
        pass
    return (result, id)


import asyncio
from typing import Dict
import jiwer
import websockets
from pydub import AudioSegment
import requests
import json
from http import HTTPStatus

from helpers.WER_helper import TRANSFORM_DEFAULT

TRANSCRIPTION_WEBSOCKET_TIMEOUT = 15.0


async def read_wav_file_into_chunks(file_path, chunk_duration=1000):
    audio = AudioSegment.from_file(file_path)
    chunks = []
    for i in range(0, len(audio), chunk_duration):
        chunks.append(audio[i : i + chunk_duration].raw_data)
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
def fetch_transcription(id: str, api_key: str):
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


# Wrap asyncio execution
def transcribe_file_websocket(filepath: str, api_key: str, debug=False) -> str:
    loop = asyncio.get_event_loop()
    transcribe_res = loop.run_until_complete(
        asyncio.gather(__transcribe_file_websocket(filepath, debug))
    )
    result = fetch_transcription(transcribe_res[0]["id"], api_key)
    return result


def evaluate_partial_websocket(filepath: str, expected: str, debug=False) -> float:
    loop = asyncio.get_event_loop()
    transcribe_res = loop.run_until_complete(
        asyncio.gather(__transcribe_file_websocket(filepath, debug))
    )
    sum = 0
    for partial in transcribe_res[0]["partials"]:
        sum += jiwer.wer(TRANSFORM_DEFAULT(partial), expected)
    return sum / len(transcribe_res[0]["partials"])


# websockets is heavily integrated with asyncio...so we have to do this in an asyncio way
async def __transcribe_file_websocket(filepath: str, debug=False) -> Dict:
    audio_data = await read_wav_file_into_chunks(filepath)
    messages = []
    result = {"id": "", "partials": []}
    try:
        async with websockets.connect("ws://localhost:8394") as websocket_connection:
            while True:
                try:
                    if len(audio_data) > 0:
                        await websocket_connection.send(audio_data.pop(0))
                    message = await asyncio.wait_for(
                        websocket_connection.recv(),
                        timeout=TRANSCRIPTION_WEBSOCKET_TIMEOUT,
                    )
                    messages.append(message)
                    try:
                        d = json.loads(message)
                        if "partial" in d:
                            result["partials"].append(d["partial"])
                            if debug:
                                print(f"Partial: {d['partial']}")
                        elif "text" in d:
                            pass
                            # result["partials"].append(d["text"])
                            # if debug:
                            # print(f"Final: {d['text']}")

                    except json.JSONDecodeError:
                        pass
                except asyncio.TimeoutError:
                    if len(messages) != 0:
                        break
            if len(messages) == 0:
                print(f"Empty messages for filepath {filepath}. This should not happen")
                return result

            await websocket_connection.send("eof-finalize")
            id = await asyncio.wait_for(websocket_connection.recv(), timeout=15.0)
            result["id"] = id
            await websocket_connection.close()

    except websockets.exceptions.ConnectionClosedOK:  # This is the expected behaviour
        pass
    return result

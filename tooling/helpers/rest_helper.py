from http import HTTPStatus
import requests
import time

from helpers.data_helper import RestResult


def await_transcription_finish(id: str, api_key: str):
    is_finished = False
    # TODO: add time cap
    while not is_finished:
        # Sleep for 10
        # This MAY be a bit long but keeps possible impact on performance as low as possible
        time.sleep(10)
        r = requests.get(
            "http://localhost:8393/transcriptions",
            headers={"Authorization": api_key},
        )
        data = r.json()
        for status in data:
            if status["transcription_id"] != id:
                continue
            if status["status"] not in ["in_progress", "in_query"]:
                is_finished = True


def transcribe_file_rest(filepath: str, api_key: str, scale: str) -> RestResult:
    result = RestResult(scale=scale)
    start_time = time.time()
    r = None
    with open(filepath, "rb") as f:
        r = requests.post(
            "http://localhost:8393/transcriptions",
            files={"file": f},
            headers={"Authorization": api_key},
        )
    if r.status_code != HTTPStatus.OK:
        print(f"Unexpected HTTP response from REST: Wanted {HTTPStatus.OK} got {r.status_code}")
        result.faulty = True
        return result
    id = r.json()["transcription_id"]
    await_transcription_finish(id, api_key)
    transcription_result = requests.get(
        f"http://localhost:8393/transcriptions/{id}",
        headers={"Authorization": api_key},
    )
    try:
        result.transcript = transcription_result.json()["transcript"]["text"]
        result.duration = time.time() - start_time
    except Exception:
        result.faulty = True
    return result

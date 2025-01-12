from http import HTTPStatus
import requests
import time

from helpers.data_helper import RestResult

# 30 minutes in seconds
TRANSCRIPT_WAIT_MAX_TIME = 30 * 60
TRANSCRIPT_ITERATION_WAIT_TIME = 10

def await_transcription_finish(id: str, api_key: str) -> bool:
    count = 0
    while count < (TRANSCRIPT_WAIT_MAX_TIME/TRANSCRIPT_ITERATION_WAIT_TIME):
        # Sleep for 10
        # This MAY be a bit long but keeps possible impact on performance as low as possible
        time.sleep(TRANSCRIPT_ITERATION_WAIT_TIME)
        r = requests.get(
            "http://localhost:8393/transcriptions",
            headers={"Authorization": api_key},
        )
        data = r.json()
        for status in data:
            if status["transcription_id"] != id:
                continue
            if status["status"] not in ["in_progress", "in_query"]:
                return True
        count+=1
    print("Wait time for rest transcription was reached. This could be an error or your machine being slow (in the latter case increase the limit)")
    return False


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
    if not await_transcription_finish(id, api_key):
        result.faulty = True 
        return result
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

import argparse
from jiwer.transforms import (
    Compose,
    RemoveMultipleSpaces,
    Strip,
    ToLowerCase,
    ExpandCommonEnglishContractions,
    RemoveKaldiNonWords,
    RemoveWhiteSpace,
    ReduceToSingleSentence,
)
import tqdm
import requests
import os
import time
import jiwer
from pathlib import Path

transform_default = Compose(
    [
        ToLowerCase(),
        ExpandCommonEnglishContractions(),
        RemoveKaldiNonWords(),
        RemoveWhiteSpace(replace_by_space=True),
        RemoveMultipleSpaces(),
        Strip(),
        ReduceToSingleSentence(),
    ]
)


def load_file_list(size: str):
    dirpath = os.path.join(os.getcwd(), "data", size)
    return [
        os.path.join(dirpath, f)
        for f in os.listdir(dirpath)
        if os.path.isfile(os.path.join(dirpath, f)) and f.endswith(".wav")
    ]


def get_expected_transcription(path: str):
    content = Path(f"{path}.txt").read_text()
    content = content.replace("\n", "")
    return transform_default(str(content))


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


def transcribe_file(filepath: str, api_key: str) -> str:
    r = None
    with open(filepath, "rb") as f:
        r = requests.post(
            "http://localhost:8393/transcriptions",
            files={"file": f},
            headers={"Authorization": api_key},
        )
    if r.status_code != 200:
        print(r.status_code)
        print("Something went wrong")
        return ""
    id = r.json()["transcription_id"]
    await_transcription_finish(id, api_key)
    transcription_result = requests.get(
        f"http://localhost:8393/transcriptions/{id}",
        headers={"Authorization": api_key},
    )
    return transcription_result.json()["transcript"]["text"]


def benchmark(settings):
    if settings.target == "websocket":
        pass
    audio_files = load_file_list(settings.scale)
    sum = 0
    print(settings.debug)
    for filepath in tqdm.tqdm(audio_files, desc="Transcribing"):
        transcription = transcribe_file(filepath, settings.overwrite_api_key)
        expected = get_expected_transcription(filepath)
        transcription = transform_default(transcription)
        if settings.debug:
            print(f"Expected: {expected}")
            print(f"Received: {transcription}")
        sum += jiwer.wer(" ".join(transcription), " ".join(expected))

    print(f"Total WER: {sum/len(audio_files)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        "melvin-benchmarker",
        description="Simple tool for benchmarking the melvin-asr rest/websocket api based on the word error rate",
    )
    parser.add_argument("--scale", "-s", default="small", choices=["small", "big"])
    parser.add_argument(
        "--target", "-t", default="rest", choices=["rest", "websocket", "all"]
    )
    parser.add_argument("--parallel", default=False)
    parser.add_argument("--overwrite-api-key", default="shuffle2024")
    parser.add_argument("--debug", action="store_true")
    benchmark(parser.parse_args())

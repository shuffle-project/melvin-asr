import argparse
from dataclasses import asdict
import json
import os
import tqdm
from helpers.file_helper import (
    clean_export_dir,
    get_file_name,
    load_file_list,
)
from helpers.rest_helper import transcribe_file_rest
from helpers.websocket_helper import (
    transcribe_file_websocket,
)
from helpers.data_helper import BenchmarkResult
from helpers.evaluate_helper import eval_export_dir

def perform_fetches(settings):
    clean_export_dir()
    audio_files = load_file_list(settings.scale)
    # calculate upper limit
    limit = int((int(settings.scale_percentage) / 100) * len(audio_files))
    if settings.scale_percentage != 100:
        audio_files = audio_files[:limit]
    for count, filepath in enumerate(
        tqdm.tqdm(
            audio_files, desc="Transcribing", disable=settings.disable_progress_bar
        )
    ):
        rest_result = None
        websocket_result = None
        if settings.target == "rest" or settings.target == "all":
            rest_result = transcribe_file_rest(
                filepath, settings.overwrite_api_key, settings.scale
            )
        if settings.target == "websocket" or settings.target == "all":
            websocket_result = transcribe_file_websocket(
                filepath, settings.overwrite_api_key, settings.scale, settings.debug)
        key = get_file_name(filepath, settings.scale)
        export_file = os.path.join(os.getcwd(), "export", f"{key[:-4]}.json")

        grouped_result = BenchmarkResult(filename=key , rest=rest_result, websocket=websocket_result, scale=settings.scale)

        with open(export_file, "w+") as f:
            json.dump(asdict(grouped_result),f)

    if settings.scale_percentage != "100":
        print(
            f"Premature termination after {limit} (dataset total length: {len(audio_files)}) evaluated audios. This was caused by the set limit percentage of {settings.scale_percentage}"
        )

def benchmark(settings):
    if not settings.skip_fetch:
        perform_fetches(settings)

    res = eval_export_dir()
    print(f"{'-'*5} DATA {'-'*5}")
    print(res)
    print(f"{'-'*5} DESCR {'-'*5}")
    print(res.describe())
    res.to_csv("./export.csv")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        "melvin-benchmarker",
        description="Simple tool for benchmarking the melvin-asr rest/websocket api based on the word error rate",
    )
    parser.add_argument(
        "--scale",
        "-s",
        default="small",
        choices=["small", "big"],
        help="Set the dataset to use. Affects duration and accuracy of benchmark",
    )
    parser.add_argument(
        "--scale-percentage",
        "-sp",
        default="100",
        help="Percentage of dataset that should be used. Allows for running the big dataset partially.",
    )
    parser.add_argument(
        "--target",
        "-t",
        default="rest",
        choices=["rest", "websocket", "all"],
        help="Set the target api",
    )
    parser.add_argument("--parallel", default=False, help="NOT IMPLEMENTED")
    parser.add_argument(
        "--overwrite-api-key",
        default="shuffle2024",
        help="Set api key to be used. The default value should work fine for local dev",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug log for transcription want and received. This (for obvious reasons) kinda clashes with the progress bar...but oh well",
    )
    parser.add_argument(
        "--disable-progress-bar",
        action="store_true",
        help="Disable the progress bar. This means there is no way of monitoring the progress of the benchmark",
    )
    parser.add_argument(
        "--export-markdown",
        action="store_true",
        help="Export table as markdown to results.md",
    )
    parser.add_argument(
        "--skip-fetch",
        action="store_true",
        help="Dont perform any requests but rather just use the data already present in the export dir",
    )
    benchmark(parser.parse_args())

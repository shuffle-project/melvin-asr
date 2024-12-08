import argparse
import time

import jiwer
import tqdm
from helpers.file_helper import (
    get_expected_transcription,
    get_file_name,
    load_file_list,
)
from helpers.rest_helper import transcribe_file_rest
from helpers.table_helpers import ERR_CODE, render_table
from helpers.websocket_helper import (
    TRANSCRIPTION_WEBSOCKET_TIMEOUT,
    evaluate_partial_websocket,
    transcribe_file_websocket,
)
from helpers.WER_helper import TRANSFORM_DEFAULT


def benchmark(settings):
    audio_files = load_file_list(settings.scale)
    results = {
        "key": [],
        "wer_rest": [],
        "duration_rest": [],
        "wer_websocket": [],
        "duration_websocket": [],
    }
    # calculate upper limit
    limit = (int(settings.scale_percentage) / 100) * len(audio_files)
    for count, filepath in enumerate(
        tqdm.tqdm(
            audio_files, desc="Transcribing", disable=settings.disable_progress_bar
        )
    ):
        if settings.scale_percentage != "100" and count >= limit:
            break
        rest_transcription = None
        rest_duration = None
        websocket_transcription = None
        websocket_duration = None
        websocket_partial_result = 0.0
        expected = TRANSFORM_DEFAULT(get_expected_transcription(filepath))
        if settings.target == "rest" or settings.target == "all":
            start_time = time.time()
            rest_transcription = transcribe_file_rest(
                filepath, settings.overwrite_api_key
            )
            rest_duration = time.time() - start_time
        if settings.target == "websocket" or settings.target == "all":
            start_time = time.time()
            if settings.use_partials_for_websocket:
                websocket_partial_result = evaluate_partial_websocket(
                    filepath, " ".join(expected), settings.debug
                )
            else:
                websocket_transcription = transcribe_file_websocket(
                    filepath, settings.overwrite_api_key, settings.debug
                )
            # During transcription we wait for timeout once
            # Therefore we subtract it from the recorded transcription time
            websocket_duration = (
                time.time() - start_time - TRANSCRIPTION_WEBSOCKET_TIMEOUT
            )
        if settings.debug:
            print(f"Expected: {expected}")

        results["key"] += [get_file_name(filepath, settings.scale)]
        for val in [
            (rest_transcription, rest_duration, "rest"),
            (websocket_transcription, websocket_duration, "websocket"),
        ]:
            transcription, duration, method_key = val

            if settings.use_partials_for_websocket and method_key == "websocket":
                results[f"wer_{method_key}"] += [websocket_partial_result]
                results[f"duration_{method_key}"] += [duration]
                continue

            if transcription is None or duration is None:
                results[f"wer_{method_key}"] += [None]
                results[f"duration_{method_key}"] += [None]
                continue

            results[f"duration_{method_key}"] += [duration]

            # This can only happen if backend or benchmark encounter an error
            # However it WOULD terminate the entire benchmarking process
            if len(transcription) == 0:
                results[f"wer_{method_key}"] += [ERR_CODE]
                continue

            transcription = TRANSFORM_DEFAULT(transcription)
            if settings.debug:
                print(f"Received({method_key}): {transcription}")

            curr_wer = jiwer.wer(" ".join(transcription), " ".join(expected))
            results[f"wer_{method_key}"] += [curr_wer]

    if settings.scale_percentage != "100":
        print(
            f"Premature termination after {int(limit)} (dataset total length: {len(audio_files)}) evaluated audios. This was caused by the set limit percentage of {settings.scale_percentage}"
        )

    render_table(results, export=settings.export_markdown)


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
        "--use-partials-for-websocket",
        action="store_true",
        help="Overwrite websocket benchmark to the live partials and finals instead of the final transcription export. This will calculate the average over all partials and finals when compared to the whole expected text. Therefore this is NOT(!) meant to be compared to REST WER or the final export ws WER.",
    )
    benchmark(parser.parse_args())

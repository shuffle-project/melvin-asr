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
import time
import jiwer

from helpers.file_helper import (
    get_file_name,
    load_file_list,
    get_expected_transcription,
)

from helpers.rest_helper import transcribe_file_rest
from helpers.websocket_helper import (
    TRANSCRIPTION_WEBSOCKET_TIMEOUT,
    transcribe_file_websocket,
)
from helpers.table_helpers import render_table, ERR_CODE


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


def benchmark(settings):
    audio_files = load_file_list(settings.scale)
    results = {
        "key": [],
        "wer_rest": [],
        "duration_rest": [],
        "wer_websocket": [],
        "duration_websocket": [],
    }
    for filepath in tqdm.tqdm(
        audio_files, desc="Transcribing", disable=settings.disable_progress_bar
    ):
        rest_transcription = None
        rest_duration = None
        websocket_transcription = None
        websocket_duration = None
        if settings.target == "rest" or settings.target == "all":
            start_time = time.time()
            rest_transcription = transcribe_file_rest(
                filepath, settings.overwrite_api_key
            )
            rest_duration = time.time() - start_time
        if settings.target == "websocket" or settings.target == "all":
            start_time = time.time()
            websocket_transcription = transcribe_file_websocket(
                filepath, settings.overwrite_api_key
            )
            # During transcription we wait for timeout once
            # Therefore we subtract it from the recorded transcription time
            websocket_duration = (
                time.time() - start_time - TRANSCRIPTION_WEBSOCKET_TIMEOUT
            )
        expected = transform_default(get_expected_transcription(filepath))
        if settings.debug:
            print(f"Expected: {expected}")

        results["key"] += [get_file_name(filepath, settings.scale)]
        for val in [
            (rest_transcription, rest_duration, "rest"),
            (websocket_transcription, websocket_duration, "websocket"),
        ]:
            transcription, duration, method_key = val
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

            transcription = transform_default(transcription)
            if settings.debug:
                print(f"Received({method_key}): {transcription}")

            curr_wer = jiwer.wer(" ".join(transcription), " ".join(expected))
            results[f"wer_{method_key}"] += [curr_wer]
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
    benchmark(parser.parse_args())

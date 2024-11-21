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
import os
import time
import jiwer
import prettytable

from helpers.file_helper import (
    load_file_list,
    DATA_BASE_PATH,
    get_expected_transcription,
    transform_value_for_table,
)

from helpers.rest_helper import transcribe_file_rest
from helpers.websocket_helper import transcribe_file_websocket


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
    if settings.target == "websocket":
        print("As of now the transcription via websockets is not parallel.")
        print(
            "Meaning: The benchmark duration of files via websockets = sum(length of audio files)"
        )
    wer_dict = {}
    duration_dict = {}
    audio_files = load_file_list(settings.scale)
    wer_sum = 0
    duration_sum = 0
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
            websocket_duration = time.time() - start_time
        expected = transform_default(get_expected_transcription(filepath))
        if settings.debug:
            print(f"Expected: {expected}")

        wer_vals = []
        diff_vals = []
        for val in [
            (rest_transcription, rest_duration),
            (websocket_transcription, websocket_duration),
        ]:
            transcription, duration = val
            if transcription is None or duration is None:
                wer_vals.append(None)
                diff_vals.append(None)
                continue

            diff_vals.append(duration)

            # This can only happen if backend or benchmark encounter an error
            # However it WOULD terminate the entire benchmarking process
            if len(transcription) == 0:
                # -1000 = error encountered
                wer_vals.append(-1000)
                continue

            transcription = transform_default(transcription)
            if settings.debug:
                print(f"Received: {transcription}")

            curr_wer = jiwer.wer(" ".join(transcription), " ".join(expected))
            wer_vals.append(curr_wer)
            wer_sum += curr_wer
            duration_sum += duration

        if settings.table:
            wer_dict[
                filepath.replace(f"{os.path.join(DATA_BASE_PATH, settings.scale)}/", "")
            ] = wer_vals
            duration_dict[
                filepath.replace(f"{os.path.join(DATA_BASE_PATH, settings.scale)}/", "")
            ] = diff_vals

    if settings.table:
        table = prettytable.PrettyTable()
        table.field_names = [
            "File",
            "Rest WER",
            "Rest Duration",
            "WS WER",
            "WS Duration",
        ]
        for key in wer_dict:
            row = [key]
            wer_vals = wer_dict[key]
            duration_vals = duration_dict[key]
            for i in range(2):
                row.append(transform_value_for_table(wer_vals[i]))
                row.append(transform_value_for_table(duration_vals[i]))
            table.add_row(row)
        print(table)

    print(
        f"Average WER: {round(wer_sum/len(audio_files),5)}\tAverage duration: {round(duration_sum/len(audio_files),2)}"
    )


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
        "--overwrite-api-key", default="shuffle2024", help="Set api key to be used"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug log for transcription want and received",
    )
    parser.add_argument(
        "--table",
        action="store_true",
        help="Print the word error rate and duration per file as a table",
    )
    parser.add_argument(
        "--disable-progress-bar",
        action="store_true",
        help="Disable the progress bar. This means there is no way of monitoring the progress of the benchmark",
    )
    benchmark(parser.parse_args())

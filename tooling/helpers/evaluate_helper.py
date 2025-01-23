from dataclasses import asdict
import json
from helpers.data_helper import BenchmarkResult, RestEvalResult, RestResult, WebsocketEvalResult, WebsocketResult, WebsocketResultBlock
from helpers.WER_helper import TRANSFORM_DEFAULT
from helpers.file_helper import (
    get_file_id,
    load_export_file_list
)
import jiwer
import pandas
from Levenshtein import distance as lev

def load_benchmark_result_from_file(filepath: str) -> BenchmarkResult | None:
    try:
        with open(filepath,"r") as filehandle:
            content = json.load(filehandle)
        return BenchmarkResult(**content)
    except Exception as e:
        print(f"Could not read file {filepath} due to an error: {e}")
        return None

def eval_export_dir() -> pandas.DataFrame:
    export_files = load_export_file_list()
    # Axes type = list type -> dont listen to type errors if present
    rest_df = pandas.DataFrame(columns=['file_id','duration','wer'])
    websocket_df = pandas.DataFrame(columns=['file_id','duration','wer', 'average_levenshtein_distance'])
    for filepath in export_files:
        if (benchmark_res := load_benchmark_result_from_file(filepath)) is None:
            continue
        
        if benchmark_res.expected_transcription is None:
            continue

        if benchmark_res.rest is not None: 
            if benchmark_res.rest.faulty:
                rest_df.loc[len(rest_df)] = {'file_id': get_file_id(filepath), 'duration': benchmark_res.rest.duration, 'wer': None}
            else:
                if (res := eval_rest(benchmark_res.rest, filepath, benchmark_res.expected_transcription)) is None:
                    rest_df.loc[len(rest_df)] = {'file_id': get_file_id(filepath), 'duration': benchmark_res.rest.duration, 'wer':None}
                else:
                    rest_df.loc[len(rest_df)] = asdict(res)

        if benchmark_res.websocket is not None: 
            if benchmark_res.websocket.faulty:
                websocket_df.loc[len(websocket_df)] = {'file_id': get_file_id(filepath), 'duration': benchmark_res.rest.duration, 'wer': None, 'average_levenshtein_distance': None}
            else:
                if (res := eval_websocket(benchmark_res.websocket, filepath, benchmark_res.expected_transcription)) is None:
                    websocket_df.loc[len(websocket_df)] = {'file_id': get_file_id(filepath), 'duration': benchmark_res.rest.duration, 'wer': None, 'average_levenshtein_distance': None}
                else:
                    websocket_df.loc[len(websocket_df)] = asdict(res)
    if rest_df.size == 0:
        return websocket_df
    if websocket_df.size == 0:
        return websocket_df
    return pandas.merge(rest_df, websocket_df, on='file_id', how='inner', suffixes=('_rest', '_websocket'))

def eval_rest(rest_benchmark_result: RestResult, result_filepath: str, expected: str) -> RestEvalResult | None:
    expected_transcription = TRANSFORM_DEFAULT(expected)
    actual_transcription = TRANSFORM_DEFAULT(rest_benchmark_result.transcript)
    if len(expected_transcription) == 0 or len(actual_transcription) == 0:
        return None
    wer = jiwer.wer(" ".join(actual_transcription), " ".join(expected_transcription))
    return RestEvalResult(
        file_id=get_file_id(result_filepath), 
        duration=rest_benchmark_result.duration, 
        wer=wer
    )

def eval_websocket_partial_block(block: WebsocketResultBlock) -> float:
    if len(block.partials) <= 1:
        return 0
    res = 0
    partials = block.partials + [block.final]
    for i in range(len(partials)-1):
        res += lev(partials[i], partials[i+1][:len(partials[i])])
    return res/len(block.partials)

def eval_websocket(websocket_benchmark_result: WebsocketResult, result_filepath: str, expected: str) -> WebsocketEvalResult | None:
    if len(websocket_benchmark_result.partial_blocks) == 0:
        return None
    expected_transcription = TRANSFORM_DEFAULT(expected)
    actual_transcription = TRANSFORM_DEFAULT(websocket_benchmark_result.combined_transcript)
    if len(expected_transcription) == 0 or len(actual_transcription) == 0:
        print("invalid transcriptions")
        return None
    wer = jiwer.wer(" ".join(actual_transcription), " ".join(expected_transcription))
    dist = 0.0
    for block in websocket_benchmark_result.partial_blocks:
        dist += eval_websocket_partial_block(block)

    return WebsocketEvalResult(
        file_id=get_file_id(result_filepath), 
        duration=websocket_benchmark_result.duration, 
        wer=wer,
        average_levenshtein_distance=dist/len(websocket_benchmark_result.partial_blocks),
    )

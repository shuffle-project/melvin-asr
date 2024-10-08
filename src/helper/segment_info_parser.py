"""Function to parse the segment and info results from the faster whisper transcription to dict"""

import json
import math


def parse_segments_and_info_to_dict(segments: tuple, info) -> dict:
    """parses the segments and info to a dictionary"""
    segments_list = list(segments)

    combined_dict = {
        "segments": parse_transcription_segments_to_dict(segments_list),
        "info": parse_transcription_info_to_dict(info),
    }
    return combined_dict


def parse_transcription_info_to_dict(info) -> dict:
    """Parses the transcription info to a dictionary"""

    def filter_infinity_values(options):
        """Filters out infinity values or replaces them with a string representation."""
        json_list = json.loads(json.dumps(options))
        # should return a list of values
        if (not isinstance(json_list, list)):
            print("parse_transcription_info_to_dict: options is not a list")
            return options

        filtered_options = []
        for item in json_list:
            if isinstance(item, float) and math.isinf(item):
                filtered_options.append('Infinity' if item > 0 else '-Infinity')
            elif isinstance(item, float) and math.isnan(item):
                filtered_options.append('NaN')
            else:
                filtered_options.append(item)
        return filtered_options 

    info_dict = {
        "language": info.language,
        "language_probability": info.language_probability,
        "duration": info.duration,
        "duration_after_vad": info.duration_after_vad,
        # do not include all_language_probs because it is too large
        # "all_language_probs": info.all_language_probs,
        "transcription_options": filter_infinity_values(info.transcription_options),
        "vad_options": filter_infinity_values(info.vad_options),
    }
    return info_dict


def parse_segment_words_to_dict(words_array):  # type words_array: [[]] -> [dict]
    """Parses the transcription segment word to a dictionary"""
    new_word_array = []
    if words_array is None:
        return new_word_array
    for word_array in words_array:
        if not isinstance(word_array[2], str):
            continue  # Skip if word is not a string
        word_dict = {
            "start": word_array[0],
            "end": word_array[1],
            "word": word_array[2],
            "probability": word_array[3],
        }
        new_word_array.append(word_dict)
    return new_word_array


def parse_transcription_segments_to_dict(segment):  # type segment -> [dict]
    """Parses the transcription segment to a dictionary"""
    segments_array = json.loads(json.dumps(segment))
    new_segments_array = []
    if segment is None:
        return new_segments_array
    for segment_array in segments_array:
        segment_dict = {
            "id": segment_array[0],
            "seek": segment_array[1],
            "start": segment_array[2],
            "end": segment_array[3],
            "text": segment_array[4],
            "tokens": segment_array[5],
            "temperature": segment_array[6],
            "avg_logprob": segment_array[7],
            "compression_ratio": segment_array[8],
            "no_speech_prob": segment_array[9],
            "words": parse_segment_words_to_dict(segment_array[10]),
        }
        new_segments_array.append(segment_dict)
    return new_segments_array

def parse_stable_whisper_result(result) -> dict:
    """Parses the stable whisper result to a dictionary"""
    data = result.to_dict()

    text = ""
    segments = []
    for segment in data["segments"]:
        text += segment["text"]

        words = []
        for word in segment["words"]:
            words.append({
                "text": word["word"],
                "start": word["start"],
                "end": word["end"],
                "probability": word["probability"],
            })

        segments.append({
            "text": segment["text"],
            "start": segment["start"],
            "end": segment["end"],
            "words": words,
        })

    return {
        "text": text,
        "segments": segments,
    }

"""Function to parse the segment and info results from the faster whisper transcription to dict"""

import json


# This is the function to use
def parse_segments_and_info_to_dict(segments: tuple, info) -> dict:
    """parses the segments and info to a dictionary"""
    segments_list = list(segments)

    combined_dict = {
        "segments": parse_transcription_segments_to_dict(segments_list),
        "info": parse_transcription_info_to_dict(info),
    }
    return combined_dict


# These are the helper functions
def parse_transcription_info_to_dict(info) -> dict:
    """Parses the transcription info to a dictionary"""

    info_dict = {
        "language": info.language,
        "language_probability": info.language_probability,
        "duration": info.duration,
        "duration_after_vad": info.duration_after_vad,
        # do not include all_language_probs because it is too large
        # "all_language_probs": info.all_language_probs,
        "transcription_options": info.transcription_options,
        "vad_options": info.vad_options,
    }
    return info_dict


def parse_segment_words_to_dict(words_array: [[]]) -> [dict]:
    """Parses the transcription segment word to a dictionary"""
    new_word_array = []
    for word_array in words_array:
        word_dict = {
            "start": word_array[0],
            "end": word_array[1],
            "word": word_array[2],
            "probability": word_array[3],
        }
        new_word_array.append(word_dict)
    return new_word_array


def parse_transcription_segments_to_dict(segment) -> [dict]:
    """Parses the transcription segment to a dictionary"""
    segments_array = json.loads(json.dumps(segment))
    new_segments_array = []
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

"""Module calls the run_whisper function returning the results as JSON"""
import json
import os
from whispercpp_binding.transcribe import transcribe


# Need to have this many arguments to fulfill whisper.cpp parameters
# pylint: disable=R0913
# pylint: disable=R0914
def transcript_to_json(
    main_path,
    model_path,
    audio_file_path,
    output_file,
    debug=False,
    threads=4,
    processors=1,
    offset_t=0,
    offset_n=0,
    duration=0,
    max_context=-1,
    max_len=0,
    split_on_word=False,
    best_of=2,
    beam_size=-1,
    word_thold=0.01,
    entropy_thold=2.40,
    logprob_thold=-1.00,
    debug_mode=False,
    translate=False,
    diarize=False,
    tinydiarize=False,
    no_fallback=False,
    no_timestamps=False,
    language="en",
    detect_language=False,
    prompt=None,
    ov_e_device="CPU",
):
    """calls the run_whisper function returning the results as JSON object"""
    try:
        output_json = True
        transcribe(
            main_path=main_path,
            model_path=model_path,
            audio_file_path=audio_file_path,
            output_file=output_file,
            output_json=output_json,
            debug=debug,
            threads=threads,
            processors=processors,
            offset_t=offset_t,
            offset_n=offset_n,
            duration=duration,
            max_context=max_context,
            max_len=max_len,
            split_on_word=split_on_word,
            best_of=best_of,
            beam_size=beam_size,
            word_thold=word_thold,
            entropy_thold=entropy_thold,
            logprob_thold=logprob_thold,
            debug_mode=debug_mode,
            translate=translate,
            diarize=diarize,
            tinydiarize=tinydiarize,
            no_fallback=no_fallback,
            no_timestamps=no_timestamps,
            language=language,
            detect_language=detect_language,
            prompt=prompt,
            ov_e_device=ov_e_device,
        )
        transcript = read_json_file(output_file, debug)
        if transcript is False:
            raise RuntimeError("Could not get transcription JSON from output_file path")
        return transcript

    # Need to catch all Exceptions here
    # pylint: disable=W0718
    except Exception as e:
        raise RuntimeError("run_whisper() failed for" + str(e)) from e


def read_json_file(path: str, debug: bool) -> any:
    """reads a json file of a path and returns the results as JSON object"""
    json_path = os.getcwd() + path + ".json"
    if debug:
        print("JSON output path:" + json_path)
    if os.path.isfile(json_path):
        with open(json_path, "r", encoding="utf-8") as json_file:
            output_json = json.load(json_file)
            return output_json
    else:
        return False

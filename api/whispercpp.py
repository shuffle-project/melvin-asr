import subprocess
import os
import json


def run_whisper(
    main_path,
    model_path,
    audio_file_path,
    output_json=False,
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
    output_txt=False,
    output_vtt=False,
    output_srt=False,
    output_lrc=False,
    output_words=False,
    font_path=None,
    output_csv=False,
    output_file=None,
    print_special=False,
    print_colors=False,
    print_progress=False,
    no_timestamps=False,
    language="en",
    detect_language=False,
    prompt=None,
    ov_e_device="CPU",
    log_score=False,
):
    """
    Run the whisper.cpp executable with the provided arguments.
    """

    # Base command with model and file
    command = [
        os.getcwd() + main_path,
    ]

    # Add optional arguments based on the function parameters
    command += [
        "-t",
        str(threads),
        "-p",
        str(processors),
        "-ot",
        str(offset_t),
        "-on",
        str(offset_n),
        "-d",
        str(duration),
        "-mc",
        str(max_context),
        "-ml",
        str(max_len),
        "-bo",
        str(best_of),
        "-bs",
        str(beam_size),
        "-wt",
        str(word_thold),
        "-et",
        str(entropy_thold),
        "-lpt",
        str(logprob_thold),
        "-l",
        str(language),
        "-oved",
        str(ov_e_device),
    ]

    # Flags without parameters
    if split_on_word:
        command.append("-sow")
    if debug_mode:
        command.append("-debug")
    if translate:
        command.append("-tr")
    if diarize:
        command.append("-di")
    if tinydiarize:
        command.append("-tdrz")
    if no_fallback:
        command.append("-nf")
    if output_txt:
        command.append("-otxt")
    if output_vtt:
        command.append("-ovtt")
    if output_srt:
        command.append("-osrt")
    if output_lrc:
        command.append("-olrc")
    if output_words:
        command.append("-owts")
    if output_csv:
        command.append("-ocsv")
    if output_json:
        command.append("-oj")
    if print_special:
        command.append("-ps")
    if print_colors:
        command.append("-pc")
    if print_progress:
        command.append("-pp")
    if no_timestamps:
        command.append("-nt")
    if detect_language:
        command.append("-dl")
    if log_score:
        command.append("-ls")

    # Optional arguments with potential default values
    if font_path:
        command.append("-fp")
        command.append("{font_path}")
    if output_file:
        command.append("-of")
        command.append("{output_file}")
    if prompt:
        command.append("--prompt")
        command.append("{prompt}") 

    command += [
        "-m",
        os.getcwd() + model_path,
        "-f",
        os.getcwd() + audio_file_path,
    ]

    process = subprocess.run(
        command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True
    )

    # Process the output
    if len(process.stderr) == 0:
        print("Command executed successfully.")
        return process.stdout
    else:
        print("----------")
        print("Command:")
        print(command)
        print("----------")
        print("STDOUT:")
        print(process.stdout)
        print("----------")
        print("STDERR:")
        print(process.stderr)
        raise ValueError("An error occurred:" + process.stderr)


# Example of calling the function
output = run_whisper(
    main_path="/whisper.cpp/main",
    model_path="/whisper.cpp/models/ggml-small.bin",
    audio_file_path="/whisper.cpp/samples/jfk.wav",
    output_json=True,
)

# If you want to capture the JSON in a variable, make sure to pass output_json=True
if output:
    try:
        output_data = json.loads(output)
        print(output_data)
    except json.JSONDecodeError as e:
        print("Failed to decode JSON output:", e)

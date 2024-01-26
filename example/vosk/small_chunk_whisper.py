# pylint: disable-all

import io
import json
from faster_whisper import WhisperModel
import wave
import sys
import traceback

model = WhisperModel("tiny", device="cpu", compute_type="int8")


def parse_transcription_info_to_dict(info) -> dict:
    """Function to convert the transcription info to a dictionary"""

    info_dict = {
        "language": info.language,
        "language_probability": info.language_probability,
        "duration": info.duration,
        "duration_after_vad": info.duration_after_vad,
        # "all_language_probs": info.all_language_probs,
        "transcription_options": info.transcription_options,
        "vad_options": info.vad_options,
    }
    return info_dict


def make_segments_and_info_to_dict(segments: tuple, info) -> dict:
    """Function to convert the segments and info to a dictionary"""
    segments_list = list(segments)

    combined_dict = {
        "segments": segments_list,
        "info": parse_transcription_info_to_dict(info),
    }
    return combined_dict


def transcribe_chunk(chunk, sample_rate, num_channels, sampwidth):
    # Create a WAV file in memory with the correct headers
    with io.BytesIO() as wav_io:
        with wave.open(wav_io, "wb") as wav_file:
            wav_file.setnchannels(num_channels)
            wav_file.setsampwidth(sampwidth)
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(chunk)
        # Seek to the beginning so it can be read by model
        wav_io.seek(0)
        # Transcribe the audio chunk
        segments, info = model.transcribe(wav_io)
    return make_segments_and_info_to_dict(segments, info)


def main(audio_file_path):
    with wave.open(audio_file_path, "rb") as wf:
        sample_rate = wf.getframerate()
        num_channels = wf.getnchannels()
        sampwidth = wf.getsampwidth()
        buffer_size = int(sample_rate * 2)  # Adjust buffer size if needed

        try:
            while True:
                data = wf.readframes(buffer_size)
                if len(data) == 0:
                    break

                data = transcribe_chunk(data, sample_rate, num_channels, sampwidth)
                try:
                    if "segments" in data:
                        for segment in data["segments"]:
                            print("\033[96m" + segment[4] + "\033[0m")
                # pylint: disable=broad-except
                except Exception as e:
                    print("\033[93m" + str(e) + "\033[0m")

        except Exception as err:
            print(
                "".join(traceback.format_exception(type(err), err, err.__traceback__))
            )


if __name__ == "__main__":
    main(sys.argv[1])

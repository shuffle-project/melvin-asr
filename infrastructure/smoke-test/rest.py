"""Sends audio data as an HTTP request to a localhost server and checks the transcription status."""
import sys
import json
import time
import requests

# This script sends an audio file as an HTTP POST request to a
# specified port on localhost at the /transcriptions endpoint and then
# checks the transcription status using the provided transcription_id.

# Usage:
# - The script is executed from the command line.
# - The port and a key for the header are provided as command-line arguments.
#   If not provided, defaults are used (port 8080, key 'default-key').
# - The audio file is assumed to be 'input.wav' in the script's directory,
#   but this can be changed in the code.


def send_file_http(file_path="./input.wav", port=8080, key="your-key"):
    """Sends the audio file to the server and checks transcription status."""
    url = f"http://localhost:{port}/transcriptions"
    headers = {"key": key}
    #pylint: disable=consider-using-with
    files = {"file": open(file_path, "rb")}

    # Sending the audio file to the server
    response = requests.post(url, files=files, headers=headers, timeout=10)
    print("Response from server:", response.text)

    # Extracting transcription_id from the response
    try:
        transcription_id = json.loads(response.text).get("transcription_id")
    except (json.JSONDecodeError, KeyError):
        print("Could not retrieve transcription ID from the response.")
        return

    print(f"Transcription ID: {transcription_id}")
    print("Waiting for 10 seconds...")
    time.sleep(10)

    if transcription_id:
        # Constructing the URL for checking transcription status
        status_url = f"http://localhost:{port}/transcriptions/{transcription_id}"

        # Checking the status of the transcription
        status_response = requests.get(status_url, headers=headers, timeout=10)
        print(f"Status for {transcription_id}: {status_response.text}")


if __name__ == "__main__":
    arg_port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    arg_key = sys.argv[2] if len(sys.argv) > 2 else "default-key"
    send_file_http(port=arg_port, key=arg_key)

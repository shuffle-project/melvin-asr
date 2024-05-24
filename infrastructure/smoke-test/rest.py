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
#
# Example: python3 rest.py 8080 your-key


def send_file_http(file_path="./Scholz_in_kurz.wav", port=8393, key="your-key"):
    """Sends the audio file to the server and checks transcription status."""
    url = f"http://localhost:{port}/transcriptions"
    headers = {"key": key}
    files = {"file": open(file_path, "rb")}

    # Sending the audio file to the server
    try:
        response = requests.post(url, files=files, headers=headers, timeout=10)
        print("Response from server:", response.text)
    except requests.exceptions.ConnectionError:
        print("Could not connect to the server.")
        return False

    # Extracting transcription_id from the response
    try:
        transcription_id = json.loads(response.text).get("transcription_id")
    except (json.JSONDecodeError, KeyError):
        print("Could not retrieve transcription ID from the response.")
        return False

    print(f"Transcription ID: {transcription_id}")
    print("Waiting for 3 seconds...")
    time.sleep(3)

    # Constructing the URL for checking transcription status
    status_url = f"http://localhost:{port}/transcriptions/{transcription_id}"

    # Trying for 60 seconds if the status is not 'Succeeded'
    print("Checking transcription status..")
    counter = 0
    while counter < 10:
        # Checking the status of the transcription
        status_response = requests.get(status_url, headers=headers, timeout=10)

        # If the status is 'Succeeded', break the loop early
        response_dict = json.loads(status_response.text)
        if "status" in response_dict:
            if response_dict["status"] == "finished":
                transcipt = response_dict["transcript"]
                transcipt_string = ""
                if "segments" in transcipt:
                    for segment in transcipt["segments"]:
                        transcipt_string += segment[4]

                if "And so my fellow Americans" in transcipt_string:
                    print("Transcription succeeded.")
                    return True
                print("Transcription text is incorrect.")
                print(response_dict["transcript"])
                return False

        # Wait for 5 seconds before the next check
        time.sleep(5)
        counter += 1
        print("Checking again...")

    print("Could not retrieve successful transcription status.")
    return False


if __name__ == "__main__":
    PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    KEY = sys.argv[2] if len(sys.argv) > 2 else "default-key"
    RES = send_file_http(port=PORT, key=KEY)
    if RES:
        sys.exit(0)
    sys.exit(1)

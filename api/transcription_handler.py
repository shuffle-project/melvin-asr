from flask import jsonify
from status_json_generator import generate_status_json, save_json_to_file
from datetime import datetime
import os
import uuid
import json

transcriptions_directory = "transcriptions"

class TranscriptionNotFoundError(Exception):
    pass

def get_transcription_filepath(transcription_id):
    return os.path.join(transcriptions_directory, f"{transcription_id}.json")

def handle_transcription_request():
    transcription_id = generate_unique_transcription_id()
    start_time = get_current_timestamp()

    # Using the Status JSON generator to create the status file
    transcription_data = generate_status_json(
        status="Pending",
        transcription_id=transcription_id,
        start_time=start_time
    )

    directory = "transcriptions"

    if not os.path.exists(directory):
        os.makedirs(directory)

    # Save the transcription status data to a file
    save_json_to_file(transcription_data, f"transcriptions/{transcription_id}.json")

    return jsonify(transcription_data)

def generate_unique_transcription_id():
    return str(uuid.uuid4())

def get_current_timestamp():
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

def get_transcription_status(transcription_id):
    filename = os.path.join("transcriptions", f"{transcription_id}.json")

    if not os.path.exists(filename):
        return jsonify({"error": "Transcription not found"}), 404

    with open(filename, "r") as file:
        transcription_data = json.load(file)

    return jsonify(transcription_data)

# Will be used to update the status of the transcription internally in the transcription pipeline
# Pending -> In Progress -> Done | Failed
def update_transcription_field(transcription_id, field_key, field_value):
    filepath = get_transcription_filepath(transcription_id)

    if not os.path.exists(filepath):
        raise TranscriptionNotFoundError("Transcription not found")

    with open(filepath, "r") as file:
        transcription_data = json.load(file)

    transcription_data[field_key] = field_value

    save_json_to_file(transcription_data, filepath)

# Example usage of the update_transcription_field function:
# update_transcription_field("transcription_id", "status", "InProgress")
# update_transcription_field("transcription_id", "end_time", get_current_timestamp())
# update_transcription_field("transcription_id", "transcript", "This is an example")
# update_transcription_field("transcription_id", "error_message", "An error occurred")
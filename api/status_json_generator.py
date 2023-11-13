"""
This module contains the functions to generate a status JSON and save it to a file.
"""
import json

def generate_status_json(status, transcription_id, start_time):
    """
    Generate a status JSON based on the provided parameters.

    Parameters:
    - status (str): The status of the transcription.
    - transcription_id (str): The unique identifier for the transcription.
    - start_time (str): The start time of the transcription (formatted as "YYYY-MM-DDTHH:mm:ssZ").
    - end_time (str): The end time of the transcription (formatted as "YYYY-MM-DDTHH:mm:ssZ").
    - transcript (str): The transcription text (optional).
    - error_message (str): Any error message in case of failure (optional).

    Returns:
    - dict: The generated status JSON.
    """
    transcription_data = {
        "status": status,
        "transcription_id": transcription_id,
        "start_time": start_time
    }

    return transcription_data

def save_json_to_file(data, file_path):
    """
    Save JSON data to a file.

    Parameters:
    - data (dict): The JSON data to be saved.
    - file_path (str): The file path where the JSON data will be saved.
    """
    with open(file_path, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, indent=2)

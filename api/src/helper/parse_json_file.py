""" Helper function to parse a JSON file into a Python object """
import json

def parse_json_file(file_path):
    """ Function to parse a JSON file into a Python object """
    try:
        with open(file_path, 'r', encoding="utf-8") as file:
            return json.load(file)
    # Need to catch all Exceptions
    # pylint: disable=W0718
    except Exception as e:
        return str(e)

# Example usage:
# Replace 'your_json_file_path.json' with your actual file path
# parsed_object = parse_json_file('your_json_file_path.json')

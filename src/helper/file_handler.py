""" This module contains a JSON FileHandler to simplify reading and writing JSON files."""
import json
import os


class FileHandler:
    """This class handles the reading and writing of JSON files."""

    def read_json(self, file_path):
        """Reads a JSON file and returns the data."""
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)
        return data

    def write_json(self, file_path, data) -> bool:
        """Writes a JSON file."""
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(data, file)
        return True

    def delete(self, file_path) -> bool:
        """Deletes a file."""
        os.remove(file_path)
        return True

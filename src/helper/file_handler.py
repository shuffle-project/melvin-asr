""" This module contains a JSON FileHandler to simplify reading and writing JSON files."""
import json
import os

from src.helper.logger import Logger, Color

# Need to catch all Exceptions here
# pylint: disable=W0718


class FileHandler:
    """This class handles the reading and writing of JSON files."""

    def __init__(self):
        self.log = Logger("FileHandler", False, Color.YELLOW)

    def read_json(self, file_path):
        """Reads a JSON file and returns the data."""
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                data = json.load(file)
            return data
        except Exception as e:
            self.log.print_error("Error reading JSON file: " + str(e))
            return None

    def write_json(self, file_path, data) -> bool:
        """Writes a JSON file."""
        try:
            with open(file_path, "w", encoding="utf-8") as file:
                json.dump(data, file)
            return True
        except Exception as e:
            self.log.print_error("Error writing JSON file: " + str(e))
            return False

    def create(self, file_path, data) -> bool:
        """Creates a JSON file."""
        try:
            with open(file_path, "x", encoding="utf-8") as file:
                json.dump(data, file)
            return True
        except Exception as e:
            self.log.print_error("Error creating JSON file: " + str(e))
            return False

    def delete(self, file_path) -> bool:
        """Deletes a file."""
        try:
            os.remove(file_path)
            return True
        except Exception as e:
            self.log.print_error("Error deleting file: " + str(e))
            return False

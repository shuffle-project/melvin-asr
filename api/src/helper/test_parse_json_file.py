"""Tests for the parse_json_file function."""
import unittest
import os
from parse_json_file import parse_json_file  # make sure to import your function

class TestParseJsonFile(unittest.TestCase):
    """Test cases for the parse_json_file function."""
    
    def test_parse_json_file_success(self):
        """Tests if the parse_json_file function successfully parses a JSON file."""
        # Create a dummy JSON content and a temporary JSON file
        dummy_json_content = '{"name": "Jane", "age": 25, "city": "Los Angeles"}'
        temp_json_file = 'temp_data.json'
        
        # Write the dummy JSON content to a file
        with open(temp_json_file, 'w', encoding="utf-8") as file:
            file.write(dummy_json_content)
        
        # Call the function under test
        parsed_data = parse_json_file(temp_json_file)
        
        # Define the expected result
        expected_data = {
            "name": "Jane",
            "age": 25,
            "city": "Los Angeles"
        }
        
        # Check if the parsed data matches the expected result
        self.assertEqual(parsed_data, expected_data, "The parsed data does not match the expected result.")
        
        # Clean up the created temporary JSON file after the test
        os.remove(temp_json_file)

if __name__ == "__main__":
    unittest.main()

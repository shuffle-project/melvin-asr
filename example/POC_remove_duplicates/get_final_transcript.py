import json


def concatenate_text(json_data):
    concatenated_text = ""
    for entry in json_data:
        concatenated_text += entry.get("text", "") + " "
    return concatenated_text.strip()


# Read the JSON data from the file
with open("example_file.json", "r", encoding="utf-8") as file:
    json_data = json.load(file)

# Concatenate the text
result_text = concatenate_text(json_data)
print(result_text)

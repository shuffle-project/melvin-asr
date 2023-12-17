""" gets in file as parameter, formats it to wav 16khz and saves it to a path"""
import os


# audio is a pydub AudioSegment
def convert_to_wav(
    audio, output_directory: str, output_filename: str
) -> {"success": bool, "message": str}:
    """
    Converts an uploaded audio file to a 16kHz mono WAV file.

    Parameters:
    file (FileStorage): The uploaded file.
    output_directory (str): The directory to save the converted file.
    output_filename (str): The filename to use for the converted file, without the extension.

    Returns:
    str: The path to the converted WAV file or an error message.
    """
    # remove first "/" from output_directory to make it work with CONFIG paths
    output_directory = output_directory[1:]

    # Check if the output directory exists, if not, create it
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # Define the output file path
    output_file_path = os.path.join(output_directory, output_filename + ".wav")

    try:
        # Convert to 16kHz mono WAV
        audio = audio.set_frame_rate(16000).set_channels(1)

        # Export the converted file
        audio.export(output_file_path, format="wav")

        return {"success": True, "message": "Data converted successfully"}

    # Need to catch all Exceptions
    # pylint: disable=W0718
    except Exception as e:
        return {"success": False, "message": f"An unknown Exception occurred: {str(e)}"}


# Example usage within Flask route:
# @app.route('/upload', methods=['POST'])
# def upload_file():
#     if 'file' not in request.files:
#         return "No file part"
#     file = request.files['file']
#     if file.filename == '':
#         return "No selected file"
#     if file:
#         result = convert_to_wav(file, "path/to/your/output/directory", "output_filename")
#         return result

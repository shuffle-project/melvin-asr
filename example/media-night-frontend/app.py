from flask import Flask, render_template, jsonify, request
import subprocess
import json
import threading
import time

app = Flask(__name__)
microphone_process = None
TRANSCRIPTION_FILE = 'transcription.txt'  # File to read the transcription from

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start_microphone', methods=['POST'])
def start_microphone():
    global microphone_process
    if microphone_process is None:
        try:
            microphone_process = subprocess.Popen(["python", "microphone_client.py"])
            return jsonify({"status": "Microphone started"})
        except Exception as e:
            return jsonify({"status": f"Error starting microphone: {str(e)}"}), 500
    else:
        return jsonify({"status": "Microphone already running"}), 400

@app.route('/stop_microphone', methods=['POST'])
def stop_microphone():
    global microphone_process
    if microphone_process is not None:
        microphone_process.terminate()
        microphone_process = None
        return jsonify({"status": "Microphone stopped"})
    else:
        return jsonify({"status": "Microphone not running"}), 400

@app.route('/transcription', methods=['GET'])
def get_transcription():
    print("get_transcription called")
    try:
        with open(TRANSCRIPTION_FILE, 'r') as f:
            transcription = f.read()
        data = json.loads(transcription)
        if "partial" in data:
            partial_text = data["partial"]
        elif "text" in data:
            partial_text = data["text"]
        else:
            return jsonify({"partial": "No valid transcription key found"}), 400
        
        return jsonify({"partial": partial_text})
    except FileNotFoundError:
        return jsonify({"partial": "No transcription available"}), 404
    except (json.JSONDecodeError, KeyError):
        return jsonify({"partial": "Invalid transcription format"}), 400

@app.route('/transcription_full', methods=['GET'])
def get_transcription2():
    global full_text
    print("get_transcription called")
    try:
        with open(TRANSCRIPTION_FILE, 'r') as f:
            transcription = f.read()
        data = json.loads(transcription)
        if "text" in data:
            full_text = data["text"]
        else:
            return jsonify({"full": "No valid transcription key found"}), 400
        
        return jsonify({"full": full_text})
    except FileNotFoundError:
        return jsonify({"full": "No transcription available"}), 404
    except (json.JSONDecodeError, KeyError):
        return jsonify({"full": "Invalid transcription format"}), 400
    

if __name__ == '__main__':
    app.run(debug=True)

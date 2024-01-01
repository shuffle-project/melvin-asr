"""This File initializes the runners for the transcription process"""
from dotenv import dotenv_values
from src.runner import Runner

# .env setup
config = dotenv_values()
print("DOTENV: " + str(config))
if "MODEL" in config:
    MODEL = config["MODEL"]

runner = Runner(MODEL)
runner.run()

"""This File initializes the runners for the transcription process"""
from dotenv import dotenv_values
from src.runner import Runner

# .env setup
config = dotenv_values()
print("DOTENV: " + str(config))
if "MODEL" in config:
    MODEL = config["MODEL"]
if "RUNNER_TYPE" in config:
    RUNNER_TYPE = config["RUNNER_TYPE"]
    # see runner types here api/src/transcription_request_handling/transcription.py
    if (RUNNER_TYPE != "rest") and (RUNNER_TYPE != "stream"):
        print("RUNNER_TYPE not valid, fallback to rest")
        RUNNER_TYPE = "rest"


runner = Runner(MODEL, RUNNER_TYPE)
runner.run()

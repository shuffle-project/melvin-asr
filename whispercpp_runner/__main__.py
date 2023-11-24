"""This File initializes the runners for the transcription process"""


from src.runner import Runner


RUNNER_COUNT = 1
# Make it possible to run the app directly from the command line

runner = Runner(1, "large-v1")
runner.run()

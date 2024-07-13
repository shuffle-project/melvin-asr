import concurrent.futures
import time

from faster_whisper import WhisperModel

cpu_threads = 1
num_workers = 1

model = WhisperModel(
    "tiny",
    device="cpu",
    compute_type="int8",
    num_workers=num_workers,
    cpu_threads=cpu_threads,
)

files = [
    "audio.wav",
    "audio.wav",
]


def transcribe_file(file_path, counter):
    start_time = time.time()  # Record the start time
    print(f"Transcribing {file_path}")
    segments, info = model.transcribe(file_path)
    segments = list(segments)
    end_time = time.time()  # Record the end time
    elapsed_time = end_time - start_time  # Calculate elapsed time
    print(f"counter {counter} took {elapsed_time:.4f} seconds to execute.")


with concurrent.futures.ThreadPoolExecutor(10) as executor:
    executor.counter = 0
    results = []
    for i, file in enumerate(files):
        executor.counter += 1
        print(f"Submitting {file}, Executor counter: {executor.counter}")
        result = executor.submit(transcribe_file, file, counter=executor.counter)
        results.append(result)

    for result in concurrent.futures.as_completed(results):
        print(result.result())  # this is required to wait for the function to conclude
        print("Done")

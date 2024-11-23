# expects big-unstructured as base folder

import os
import shutil
import uuid
import subprocess

import tqdm


PATH = "./big-unstructured/"


def get_files_and_dirs(path: str):
    files = []
    dirs = []
    for filename in os.listdir(path):
        f = os.path.join(path, filename)
        # checking if it is a file
        if os.path.isfile(f):
            if f.endswith(".mp3"):
                files.append(f)
        else:
            dirs.append(f)
    return (files, dirs)


def main():
    if os.path.exists("./big"):
        shutil.rmtree("./big")
    dirs = [PATH]
    files = []
    while len(dirs) > 0:
        f, d = get_files_and_dirs(dirs.pop())
        dirs += d
        files += f
    print(f"Found {len(files)} mp3 files.")
    os.mkdir("./big")
    cnt = 0
    for filepath in tqdm.tqdm(files, desc="Converting to wav and saving"):
        # we could also use the og filename but chances of collision are higher
        id = str(uuid.uuid4())
        json_path = filepath[:-3] + "json"
        # Does json path exist?
        if not os.path.exists(json_path):
            continue
        if not os.path.isfile(json_path):
            continue
        subprocess.run(
            [
                f"ffmpeg -i {filepath} -hide_banner -loglevel error -ar 16000 -ac 1 -sample_fmt s16 ./big/{id}.wav"
            ],
            shell=True,
            stdout=subprocess.DEVNULL,
        )
        shutil.copy(json_path, os.path.join("./big", f"{id}.json"))
        cnt += 1
    print(f"Copied {cnt} files.")


if __name__ == "__main__":
    main()

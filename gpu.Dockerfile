FROM nvidia/cuda:12.4.1-base-ubuntu22.04

EXPOSE 8394
EXPOSE 8393

WORKDIR /asr-api

COPY ./src ./src
COPY ./app.py ./app.py
COPY ./requirements.txt ./requirements.txt

# Install Python and pip
RUN apt-get update && apt-get install -y python3.10 python3-pip ffmpeg

RUN pip install -r ./requirements.txt

# using unbuffered output "-u" to stdout, so that we can see the output in docker logs in real time
CMD ["python3", "-u", "app.py"]

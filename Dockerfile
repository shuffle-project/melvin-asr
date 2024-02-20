FROM python:3.10

EXPOSE 8394
EXPOSE 8393

WORKDIR /asr-api

COPY ./src ./src
COPY ./app.py ./app.py
COPY ./requirements.txt ./requirements.txt

RUN apt-get update && apt-get install -y ffmpeg

RUN pip install -r ./requirements.txt

# using unbuffered output "-u" to stdout, so that we can see the output in docker logs in real time
CMD ["python", "-u", "app.py"]

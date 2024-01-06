FROM python:3.12

WORKDIR /api

COPY . .
COPY ./.env.prod ./.env

RUN apt-get update && apt-get install -y ffmpeg

RUN pip install -r ./requirements.txt

WORKDIR /

EXPOSE 8394
EXPOSE 8393

# using unbuffered output "-u" to stdout, so that we can see the output in docker logs in real time
CMD ["python", "-u", "api"]

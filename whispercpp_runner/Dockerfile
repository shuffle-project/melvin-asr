FROM debian:11

WORKDIR /whispercpp_runner

COPY . .

RUN apt-get update && apt-get install -y git python3 python3-pip build-essential libsdl2-dev alsa-utils g++ make wget

RUN pip install -r ./requirements.txt

WORKDIR /

CMD ["python3", "whispercpp_runner"]

FROM debian:11

WORKDIR /whispercpp_runner

COPY . .

RUN apt-get update && apt-get install -y git python3 python3-pip build-essential libsdl2-dev alsa-utils g++ make wget
RUN git clone https://github.com/ggerganov/whisper.cpp.git
RUN make -C /whispercpp_runner/whisper.cpp

RUN pip install -r ./requirements.txt

WORKDIR /

# using unbuffered output "-u" to stdout, so that we can see the output in docker logs in real time
CMD ["python3", "-u", "whispercpp_runner"]

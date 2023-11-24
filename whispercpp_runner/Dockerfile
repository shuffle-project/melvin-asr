FROM debian:11

WORKDIR /whispercpp_runner

COPY . .
# Create data folders
RUN mkdir -p /data
RUN mkdir -p /data/audio_files
RUN mkdir -p /data/settings
RUN mkdir -p /data/transcripts
# Copy test audio file in audo_files folder
COPY ./infrastrucure/jfk.wav /data/audio_files/jfk.wav

# build Whisper.cpp
RUN apt-get update && apt-get install -y git python3 python3-pip build-essential libsdl2-dev alsa-utils g++ make wget
RUN git clone https://github.com/ggerganov/whisper.cpp.git
RUN make -C /whispercpp_runner/whisper.cpp
RUN python3 ./infrastrucure/setup_whispercpp.py

RUN pip install -r ./requirements.txt

WORKDIR /

CMD ["python3", "whispercpp_runner"]

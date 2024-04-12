# Use a CUDA image that includes cuDNN
FROM nvidia/cuda:12.4.1-runtime-ubuntu22.04

EXPOSE 8394
EXPOSE 8393

WORKDIR /asr-api

COPY ./src ./src
COPY ./app.py ./app.py
COPY ./requirements.txt ./requirements.txt

# Install Python, pip, and additional dependencies
RUN apt-get update && apt-get install -y python3.10 python3-pip ffmpeg && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    pip install --no-cache-dir -r requirements.txt

# Set unbuffered output for Python, facilitating real-time log output
CMD ["python3", "-u", "app.py"]

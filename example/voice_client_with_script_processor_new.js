var context;
var source;
var processor;
var streamLocal;
var webSocket;
var outputParagraph;
var text = "";
var isRecording = false;
var enabledSVG;
var disabledSVG;
var header;
var refreshSVG;
const bufferSize = 16384;
const sampleRate = 16000;
const wsURL = "ws://localhost:1338";
var initComplete = false;

(function () {
  document.addEventListener("DOMContentLoaded", (event) => {
    header = document.getElementById("header");
    enabledSVG = document.getElementById("enabled");
    disabledSVG = document.getElementById("disabled");
    refreshSVG = document.getElementById("refresh");
    outputParagraph = document.getElementById("q");

    const listenButton = document.getElementById("recordToggle");

    refreshSVG.addEventListener("mousedown", function () {
      //refresh the page
      location.reload();
    });

    listenButton.addEventListener("mousedown", function () {
      if (!isRecording) {
        console.log("start recording ");

        initWS();
        navigator.mediaDevices
          .getUserMedia({
            audio: {
              echoCancellation: true,
              noiseSuppression: true,
              channelCount: 1,
              sampleRate,
            },
            video: false,
          })
          .then(handleSuccess1);
        initComplete = true;
        isRecording = true;
      } else {
        if (initComplete === true) {
          console.log("trying to close");
          enabledSVG.style.display = "none";
          refreshSVG.style.display = "inline";

          header.innerText = "Tap to reload page";
          webSocket.close();

          source.disconnect(processor);
          processor.disconnect(context.destination);
          if (streamLocal.active) {
            streamLocal.getTracks()[0].stop();
          }
          initComplete = false;
          isRecording = false;
          // outputParagraph.innerText = "";
        }
      }
    });
  });
})();

const handleSuccess1 = function (stream) {
  enabledSVG.style.display = "inline";
  disabledSVG.style.display = "none";
  header.innerText = "Listening...";
  streamLocal = stream;
  context = new AudioContext({ sampleRate: sampleRate });
  source = context.createMediaStreamSource(stream);
  processor = context.createScriptProcessor(bufferSize, 1, 1);

  source.connect(processor);
  processor.connect(context.destination);

  processor.onaudioprocess = function (audioDataChunk) {
    console.log(audioDataChunk.inputBuffer);
    sendAudio(audioDataChunk);
  };
};

// Constants for audio accumulation
const targetDuration = 4; // target duration in seconds
const samplesPerSecond = sampleRate;
const targetBufferSize = targetDuration * samplesPerSecond;
let accumulatedSamples = 0;
let accumulatedBuffer = new Float32Array(targetBufferSize);

function sendAudio(audioDataChunk) {
  // if (!webSocket.readyState === WebSocket.OPEN) {
  //   initWS();
  // }

  const inputData =
    audioDataChunk.inputBuffer.getChannelData(0) ||
    new Float32Array(bufferSize);

  // Check if we have enough space in the accumulatedBuffer
  if (accumulatedSamples + inputData.length <= targetBufferSize) {
    // Accumulate samples
    accumulatedBuffer.set(inputData, accumulatedSamples);
    accumulatedSamples += inputData.length;
  } else {
    // We have more samples than needed, so we fill the remaining space and send
    const remainingSpace = targetBufferSize - accumulatedSamples;
    accumulatedBuffer.set(
      inputData.slice(0, remainingSpace),
      accumulatedSamples
    );
    accumulatedSamples += remainingSpace;

    // Send the accumulated audio
    console.log("trying to send");
    if (webSocket.readyState === WebSocket.OPEN) {
      const targetBuffer = new Int16Array(targetBufferSize);
      for (let index = 0; index < targetBufferSize; index++) {
        targetBuffer[index] = 32767 * Math.min(1, accumulatedBuffer[index]);
      }
      console.log("sending");
      webSocket.send(targetBuffer.buffer);
    }

    // Reset the accumulated buffer and samples
    accumulatedSamples = 0;
    accumulatedBuffer = new Float32Array(targetBufferSize);

    // Store any leftover samples from inputData
    if (inputData.length > remainingSpace) {
      const leftoverSamples = inputData.length - remainingSpace;
      accumulatedBuffer.set(
        inputData.slice(remainingSpace, inputData.length),
        0
      );
      accumulatedSamples = leftoverSamples;
    }
  }
}

function initWS() {
  webSocket = new WebSocket(wsURL);
  // webSocket.binaryType = "arraybuffer";

  webSocket.onopen = function (event) {
    console.log("New connection established");
  };

  webSocket.onclose = function (event) {
    console.log("closing web socket");
    console.log(event);
    initWS();
  };

  webSocket.onerror = function (event) {
    console.error(event.data);
  };

  webSocket.onmessage = function (event) {
    if (event.data) {
      let parsed = JSON.parse(event.data);
      let message = "";
      for (const segment of parsed.segments) {
        console.log(segment[4]);
        message += segment[4];
      }
      outputParagraph.innerText = message;
    }
  };
}

const WS_URL = "ws://localhost:8394";
const liveTranscriptOutput = document.getElementById('liveTranscriptOutput');
const recordButton = document.getElementById("recordButton");
let audioContext, audioProcessorNode, socket;
let isStreaming = false;
let accumulatedPartials = '';
let previousPartial = '';
let accumulatedTranscription = '';
let previousFinal = '';

/**
 * @typedef {Object} WebSocketMessage
 * @property {string} [partial] - The partial transcription text (optional).
 * @property {string} [result] - The components of a transcription text (optional).
 * @property {string} [text] - The final transcription text (optional)
 */

recordButton.addEventListener("click", toggleRecording);

async function toggleRecording() {
  if (!isStreaming) {
    // Currently not recording, start recording
    await startRecording();
  } else {
    // Currently recording, stop recording
    stopRecording();
  }
  recordButton.classList.toggle("recording");
  isStreaming = !isStreaming; // Toggle the recording state
}

async function startRecording() {
  // Initialize WebSocket
  socket = new WebSocket(WS_URL);

  socket.onopen = async () => {
    console.log("WebSocket connection established");

    // Initialize AudioContext and Audio Worklet
    audioContext = new AudioContext({sampleRate: 16000});
    await audioContext.audioWorklet.addModule('processor.js');

    // Capture microphone input
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    const source = audioContext.createMediaStreamSource(stream);

    // Create AudioWorkletNode
    audioProcessorNode = new AudioWorkletNode(audioContext, 'audio-processor');
    source.connect(audioProcessorNode);

    // Handle audio chunks
    isStreaming = true;
    audioProcessorNode.port.onmessage = (event) => {
      if (isStreaming && socket.readyState === WebSocket.OPEN) {
        socket.send(event.data); // Send audio chunks
      }
    };

    // Handle incoming messages
    socket.onmessage = (event) => {
       /** @type {WebSocketMessage} */
      const message = JSON.parse(event.data);

      if (message.partial) {
        console.log("Partial Transcription:", message.partial);
        if (message.text !== previousPartial && message.text !== '') {
          accumulatedPartials += message.partial
          liveTranscriptOutput.innerHTML = `<span class="new-partial">${accumulatedPartials}</span> `;
          previousPartial = message.partial;
        }


      } else if (message.hasOwnProperty('result')) {
        console.log("Final Transcription:", message.text);
          if (message.text !== previousFinal && message.text !== '') {
            accumulatedTranscription += ` ${message.text}`; // Space in between final transcriptions
            liveTranscriptOutput.innerHTML = `<span class="transcript">${accumulatedTranscription}</span> `;
            previousFinal = message.text;
          }
      }

      liveTranscriptOutput.scrollTop = liveTranscriptOutput.scrollHeight;
    };

    socket.onerror = (error) => console.error("WebSocket error:", error);
    socket.onclose = () => console.log("WebSocket connection closed");
  };
}

function stopRecording() {
  // Send EOF message to server
  if (socket && socket.readyState === WebSocket.OPEN) {
    socket.send(JSON.stringify({type: "eof"}));
    socket.close();
  }

  // Disconnect audio processor
  if (audioProcessorNode) {
    audioProcessorNode.disconnect();
  }

  if (audioContext) {
    audioContext.close();
  }

  console.log("Recording stopped, EOF sent");
}

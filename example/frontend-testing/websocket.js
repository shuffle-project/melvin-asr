// WebSocket URL
const WS_URL = "ws://localhost:8394";
let audioContext, audioProcessorNode, socket;
let isStreaming = false;

document.getElementById("startRecording").addEventListener("click", startRecording);
document.getElementById("stopRecording").addEventListener("click", stopRecording);

async function startRecording() {
  // Disable the Start button and enable the Stop button
  document.getElementById("startRecording").disabled = true;
  document.getElementById("stopRecording").disabled = false;

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
      const message = JSON.parse(event.data);

      if (message.type === "partial") {
        console.log("Partial Transcription:", message.text);
      } else if (message.type === "final") {
        console.log("Final Transcription:", message.text);
      }
    };

    socket.onerror = (error) => console.error("WebSocket error:", error);
    socket.onclose = () => console.log("WebSocket connection closed");
  };
}

function stopRecording() {
  // Stop audio streaming
  isStreaming = false;

  // Send EOF message to server
  if (socket && socket.readyState === WebSocket.OPEN) {
    socket.send(JSON.stringify({ type: "eof" }));
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

  // Enable the Start button and disable the Stop button
  document.getElementById("startRecording").disabled = false;
  document.getElementById("stopRecording").disabled = true;
}
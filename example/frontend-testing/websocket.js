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
        await startRecording();
    } else {
        stopRecording();
    }
    recordButton.classList.toggle("recording");
    isStreaming = !isStreaming;
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
        const stream = await navigator.mediaDevices.getUserMedia({audio: true});
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

            // Partial transcript
            if (message.partial) {
                console.log("Partial Transcription:", message.partial);

                // Update only if the partial text is new and not empty
                if (message.partial !== previousPartial && message.partial.trim() !== '') {
                    previousPartial = message.partial;
                    accumulatedPartials = `${accumulatedTranscription} ${message.partial}`.trim();

                    // Display partials styled differently to finals
                    liveTranscriptOutput.innerHTML =
                        `<span class="transcript">${accumulatedTranscription}</span>
                        <span class="new-partial">${message.partial}</span>`;
                }
            }

            // Final transcript
            else if (message.hasOwnProperty('result')) {
                console.log("Final Transcription:", message.text);

                // Update only if the final text is new and not empty
                if (message.text !== previousFinal && message.text.trim() !== '') {
                    accumulatedTranscription = `${accumulatedTranscription} ${message.text}`.trim(); // Append final transcript
                    previousFinal = message.text;

                    // Clear partials and update the display with final transcript
                    accumulatedPartials = '';
                    liveTranscriptOutput.innerHTML = `<span class="transcript">${accumulatedTranscription}</span>`;
                }
            }
            // Auto-scrolling of textbox
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

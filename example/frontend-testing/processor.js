class AudioProcessor extends AudioWorkletProcessor {
  constructor() {
    super();
    this.sampleRate = sampleRate; // Default: 16000 Hz
    this.chunkSize = 8000; // Default: 0.1 seconds at 16 kHz / 8000 samples: 0,5 seconds
    this.buffer = [];
  }

  process(inputs) {
    const input = inputs[0];
    if (input && input[0]) {
      const inputData = input[0]; // Mono channel
      this.buffer.push(...inputData);

      // Check if we have enough samples to form a chunk
      if (this.buffer.length >= this.chunkSize) {
        const chunk = this.buffer.slice(0, this.chunkSize);
        this.buffer = this.buffer.slice(this.chunkSize);

        // Convert Float32Array to Int16Array
        const int16Data = new Int16Array(chunk.length);
        for (let i = 0; i < chunk.length; i++) {
          // Perform mapping from float in (range -1 to +1) into signed 16 bit int realm (range -32,768 to +32,767)
          int16Data[i] = Math.max(-1, Math.min(1, chunk[i])) * 32767;
        }

        // Send Int16Array data to main thread via port
        this.port.postMessage(int16Data.buffer);
      }
    }
    return true; // Continue processing
  }
}

registerProcessor('audio-processor', AudioProcessor);
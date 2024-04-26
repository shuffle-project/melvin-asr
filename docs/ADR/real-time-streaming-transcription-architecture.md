# Real Time Streaming Transcription Architecture
## Status
*What is the status, such as proposed, accepted, rejected, deprecated, superseded, etc.?*
Pending

## Context
*What is the issue that we're seeing that is motivating this decision or change?*

Key factors for good real-time-transcription

### Partials & Full results
- Do we want to send text multiple times to a user as partials are extending (e.g. "hi" - "hi, I am" - "hi, I am Max")?

### Context-recognition & VAD

### Chunk size & Chunk cache size

### Model setup and size

### Transcription Workflow
Queueing, Async & Await

### Latency

## Decision
*What is the change that we're proposing and/or doing?*

### Test Setup
- Melvin Server incl. RTX A5000 for Faster_Whisper Models

## Consequences
*What becomes easier or more difficult to do because of this change?*
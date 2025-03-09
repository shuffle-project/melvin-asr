# Demo Frontend

This frontend is integrated for testing and demo purposes.
Currently, it features the following functionalities:

- [X] REST Transcription with file upload
- [X] REST Translation of previously transcripted file
- [X] REST Real-time Alignment visualization
- [X] Websocket Live Transcription with Microphone

The demo is Javascript only and uses the Media Capture and Streams API (Media Stream) to capture microphone input for 
websocket streams. 

## Configuration

Currently the demo only works with CORS (Cross-Origin Resource Sharing) being disabled in the browser.

MacOS:
For Safari, navigate to settings and tick the option 'Show features for web developers'. 
Subsequently activate 'Disable cross-origin restrictions'
from the developer tab.

Windows:
For Chromium-based browsers such as Brave, run (Win + R)

```brave.exe --user-data-dir="C://Chrome dev session" --disable-web-security "enter frontend URL here"```


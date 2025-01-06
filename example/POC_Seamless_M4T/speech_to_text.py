import os
import time

import scipy
import torchaudio
from transformers import AutoProcessor, SeamlessM4Tv2Model

script_dir = os.path.dirname(os.path.abspath(__file__))
relative_path = "../../src/helper/test_base/example.wav"
absolute_path = os.path.abspath(os.path.join(script_dir, relative_path))

# Load audio
print(torchaudio.list_audio_backends())
audio, orig_freq = torchaudio.load(uri=absolute_path, format="wav")

# Load processor and model
processor = AutoProcessor.from_pretrained("facebook/seamless-m4t-v2-large")
model = SeamlessM4Tv2Model.from_pretrained("facebook/seamless-m4t-v2-large")

# Process audio
start_time = time.time()
audio_inputs = processor(audios=audio, return_tensors="pt")
output_tokens = model.generate(**audio_inputs, tgt_lang="deu", generate_speech=False)
translated_text_from_audio = processor.decode(
    output_tokens[0].tolist()[0], skip_special_tokens=True
)
end_time = time.time()
print(translated_text_from_audio, "Time taken:", (end_time - start_time))

import os
import time

from transformers import AutoProcessor, SeamlessM4Tv2Model

script_dir = os.path.dirname(os.path.abspath(__file__))
relative_path = "../../src/helper/test_base/example.wav"
absolute_path = os.path.abspath(os.path.join(script_dir, relative_path))


# Load processor and model
processor = AutoProcessor.from_pretrained("facebook/seamless-m4t-v2-large")
model = SeamlessM4Tv2Model.from_pretrained("facebook/seamless-m4t-v2-large")

# Process text
start_time = time.time()
text_inputs = processor(
    text="And so my fellow Americans, ask not what your country can do for you, ask what you can do for your country.",
    src_lang="eng",
    return_tensors="pt",
)
output_tokens = model.generate(**text_inputs, tgt_lang="deu", generate_speech=False)
translated_text_from_audio = processor.decode(
    output_tokens[0].tolist()[0], skip_special_tokens=True
)
end_time = time.time()
print(translated_text_from_audio, "Time taken:", (end_time - start_time))

# Segmented
segments = [
    "And so my fellow Americans,",
    "ask not",
    "what your country can do for you,",
    "ask what you can do for your country.",
]
start_time = time.time()
for segment in segments:
    text_inputs = processor(
        text=segment,
        src_lang="eng",
        return_tensors="pt",
    )
    output_tokens = model.generate(**text_inputs, tgt_lang="deu", generate_speech=False)
    translated_text_from_audio = processor.decode(
        output_tokens[0].tolist()[0], skip_special_tokens=True
    )

    print(translated_text_from_audio)
end_time = time.time()
print("Time taken:", (end_time - start_time))

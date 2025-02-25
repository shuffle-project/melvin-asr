import torch
from transformers import SeamlessM4TTokenizer, SeamlessM4Tv2ForTextToText

device = "cuda"  # "cuda" or "cpu"

tokenizer = SeamlessM4TTokenizer.from_pretrained(
    "facebook/seamless-m4t-v2-large", cache_dir="models"
)
model = SeamlessM4Tv2ForTextToText.from_pretrained(
    "facebook/seamless-m4t-v2-large",
    cache_dir="models",
).to(device)

text = "And so, my fellow Americans, ask not what your country can do for you, ask what you can do for your country."
from_code = "eng"
to_code = "deu"

# Tokenize input
inputs = tokenizer(text, return_tensors="pt", src_lang=from_code).to(device)

# Generate translation
with torch.no_grad():
    outputs = model.generate(**inputs, tgt_lang=to_code)

# Decode translated text
translated_text = tokenizer.batch_decode(outputs, skip_special_tokens=True)[0]
print(translated_text)  # Translated sentence


# To run on Windows

# docker run --rm --gpus all --user root -v ${PWD}:/workspace -w /workspace nvidia/cuda:12.3.2-cudnn9-runtime-ubuntu22.04 bash -c "
#     apt-get update && apt-get install -y python3 python3-pip &&
#     pip3 install --upgrade pip &&
#     pip3 install -r requirements.txt &&
#     python3 example/POC_Seamless_M4T/text_to_text_dedicated.py"

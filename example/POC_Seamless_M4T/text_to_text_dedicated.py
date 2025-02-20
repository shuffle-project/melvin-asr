import torch
from fastapi import HTTPException
from transformers import AutoTokenizer, SeamlessM4Tv2ForTextToText

model = SeamlessM4Tv2ForTextToText.from_pretrained("facebook/seamless-m4t-v2-large")
tokenizer = AutoTokenizer.from_pretrained("facebook/seamless-m4t-v2-large")

text = "And so, my fellow Americans, ask not what your country can do for you, ask what you can do for your country."
from_code = "eng"
to_code = "deu"

# Tokenize input
inputs = tokenizer(text, return_tensors="pt", src_lang=from_code)

# Generate translation
with torch.no_grad():
    outputs = model.generate(**inputs, tgt_lang=to_code)

# Decode translated text
translated_text = tokenizer.batch_decode(outputs, skip_special_tokens=True)[0]
print(translated_text)  # Translated sentence

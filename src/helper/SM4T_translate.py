import torch
from fastapi import HTTPException
from transformers import AutoTokenizer, SeamlessM4Tv2ForTextToText

model = SeamlessM4Tv2ForTextToText.from_pretrained("facebook/seamless-m4t-v2-large")
tokenizer = AutoTokenizer.from_pretrained("facebook/seamless-m4t-v2-large")


def translate_text(text, from_code, to_code):
    """
    Translates the given text from the origin language to the target language.

    Parameters:
        text (str): The text to translate.
        from_code (str): The code of the origin language (e.g., 'en' for English).
        to_code (str): The code of the target language (e.g., 'de' for German).

    Returns:
        str: The translated text.
    """

    try:
        inputs = tokenizer(text, return_tensors="pt", src_lang=from_code)

        with torch.no_grad():
            outputs = model.generate(**inputs, tgt_lang=to_code)
        return outputs

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during translation: {e}")

import torch
from fastapi import HTTPException
from transformers import AutoTokenizer, SeamlessM4Tv2ForTextToText

from src.helper.types.translation_consts import LANGUAGE_MAP, POSSIBLE_LANGUAGES

# TODO: this should be dynamically, currently it just loads it on start
model = SeamlessM4Tv2ForTextToText.from_pretrained("facebook/seamless-m4t-v2-large")
tokenizer = AutoTokenizer.from_pretrained("facebook/seamless-m4t-v2-large")

# From https://huggingface.co/facebook/seamless-m4t-v2-large#supported-languages


def check_language_supported_guard(language):
    language = LANGUAGE_MAP[language] if language in LANGUAGE_MAP else language
    if language not in POSSIBLE_LANGUAGES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported language code: {language}, supported languages: {LANGUAGE_MAP}",
        )


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

        inputs = tokenizer(text, return_tensors="pt", src_lang=LANGUAGE_MAP[from_code])

        with torch.no_grad():
            outputs = model.generate(**inputs, tgt_lang=LANGUAGE_MAP[to_code])
        return tokenizer.batch_decode(outputs, skip_special_tokens=True)[0]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during translation: {e}")

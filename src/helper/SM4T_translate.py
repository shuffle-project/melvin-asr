from typing import Dict

import os
import torch
from fastapi import HTTPException
from langchain.text_splitter import RecursiveCharacterTextSplitter
from transformers import SeamlessM4TTokenizer, SeamlessM4Tv2ForTextToText

from src.helper.config import CONFIG
from src.helper.types.translation_consts import LANGUAGE_MAP, POSSIBLE_LANGUAGES


def check_language_supported_guard(language: str):
    language = LANGUAGE_MAP[language] if language in LANGUAGE_MAP else language
    if language not in POSSIBLE_LANGUAGES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported language code: {language}, supported languages: {LANGUAGE_MAP}",
        )


class Translator:
    def __init__(self, config: Dict[str, str]):
        full_model_path = os.path.join(os.getcwd(), CONFIG["model_path"])
        self.device: str = (
            f"cuda:{config['device_index']}"
            if config["translation_device"] == "cuda"
            else config["translation_device"]
        )
        self.tokenizer = SeamlessM4TTokenizer.from_pretrained(
            config["translation_model"],
            cache_dir=full_model_path
        )
        self.model = SeamlessM4Tv2ForTextToText.from_pretrained(
            config["translation_model"], cache_dir=full_model_path
        )

        self.model.config.max_new_tokens = 512
        self.model.to(self.device)

    def translate_text(self, text: str, from_code: str, to_code: str) -> str:
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
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=512)
            text_splitted: list[str] = text_splitter.split_text(text)
            translated_chunks: list[str] = []
            for chunk in text_splitted:
                inputs = self.tokenizer(
                    chunk,
                    return_tensors="pt",
                    src_lang=LANGUAGE_MAP[from_code],
                ).to(self.device)

                with torch.no_grad():
                    outputs = self.model.generate(
                        **inputs, tgt_lang=LANGUAGE_MAP[to_code]
                    )
                translated_text: str = self.tokenizer.batch_decode(
                    outputs, skip_special_tokens=True
                )[0]
                translated_chunks.append(translated_text)

            return " ".join(translated_chunks)

        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Error during translation: {e}"
            )

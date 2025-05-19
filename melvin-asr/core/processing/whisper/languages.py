from faster_whisper.tokenizer import _LANGUAGE_CODES


def get_supported_languages() -> list:
    return list(_LANGUAGE_CODES)

def is_language_supported(language: str) -> bool:
    return language in list(_LANGUAGE_CODES)
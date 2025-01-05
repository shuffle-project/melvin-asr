import argostranslate.package
import argostranslate.translate
from fastapi import HTTPException


def install_language_pack_if_needed(from_code, to_code):
    """
    Installs the language pack for the specified language pair if not already installed.

    Parameters:
        from_code (str): The code of the origin language (e.g., 'en' for English).
        to_code (str): The code of the target language (e.g., 'de' for German).
    """

    # TODO: error handling for:
    # - language Code unavailable
    # - package download failed
    # - package installation failed
    # - package installation successful but translation failed
    # - package installation successful but translation successful

    try:
        installed_packages = argostranslate.package.get_installed_packages()
        if not any(
            pkg.from_code == from_code and pkg.to_code == to_code
            for pkg in installed_packages
        ):
            argostranslate.package.update_package_index()
            available_packages = argostranslate.package.get_available_packages()
            package_to_install = next(
                filter(
                    lambda x: x.from_code == from_code and x.to_code == to_code,
                    available_packages,
                ),
                None,
            )
            if not package_to_install:
                raise ValueError(
                    f"No language pack available for {from_code} to {to_code}."
                )
            argostranslate.package.install_from_path(package_to_install.download())
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Error installing language pack: {e}"
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
    install_language_pack_if_needed(from_code, to_code)
    try:
        return argostranslate.translate.translate(text, from_code, to_code)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error during translation: {e}")

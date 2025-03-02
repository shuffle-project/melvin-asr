"""Model handler class to handle the models and storage of the models."""

import logging
import os
from faster_whisper.utils import download_model
from src.helper.config import CONFIG

LOGGER = logging.getLogger(__name__)


class ModelHandler:
    """Class to handle the models"""

    def __init__(self, model_path=CONFIG["model_path"]):
        self.model_path = model_path

    def setup_model(self, model_to_load: str) -> bool:
        """Function to setup the models"""
        LOGGER.info(f"Setting up model.. {model_to_load}")

        model = self.get_model(model_to_load)
        if model is None:
            LOGGER.info(f"Model {model_to_load} not found, downloading..")
            self.download_model(model_to_load)
            return True
        LOGGER.debug(f"Model {model_to_load} found, skipping download..")
        return False

    def get_model_path(self, model_name: str) -> str:
        """Function to get the model path"""
        model_path = os.path.join(os.getcwd(), self.model_path, model_name)
        LOGGER.warning(model_path)
        return model_path

    def download_model(self, model_name: str) -> None:
        """Function to download a model"""
        try:
            LOGGER.info(download_model(model_name, self.get_model_path(model_name)))
        except ValueError as e:
            LOGGER.error(f"tried to download_model for an INVALID MODEL NAME: {e}")

    def get_model(self, model_name: str) -> str:
        """Function to get a model"""
        model_path = self.get_model_path(model_name)
        if os.path.exists(model_path):
            return model_path
        return None

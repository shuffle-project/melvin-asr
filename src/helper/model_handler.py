"""Model handler class to handle the models and storage of the models."""
import os
from faster_whisper.utils import download_model
from src.config import CONFIG
from src.helper.logger import Logger


class ModelHandler:
    """Class to handle the models"""

    def __init__(self):
        self.log = Logger("ModelHandler", True)

    def setup_models(self, models_to_load: [str]) -> None:
        """Function to setup the models"""
        self.log.print_log(f"Setting up models.. {models_to_load}")

        for model_name in models_to_load:
            model = self.get_model(model_name)
            if model is None:
                self.log.print_log(f"Model {model_name} not found, downloading..")
                self.download_model(model_name)

        # print the models in the model path
        self.log.print_log(f"Models available in {CONFIG['MODEL_PATH']}:")
        for model in os.listdir(os.getcwd() + CONFIG["MODEL_PATH"]):
            if model.endswith(".gitignore"):
                continue
            self.log.print_log(f" - {model}")

    def get_model_path(self, model_name: str) -> str:
        """Function to get the model path"""
        model_path = os.getcwd() + CONFIG["MODEL_PATH"] + model_name
        return model_path

    def download_model(self, model_name: str) -> None:
        """Function to download a model"""
        try:
            self.log.print_log(download_model(model_name, self.get_model_path(model_name)))
        except ValueError as e:
            self.log.print_error(
                f"tried to download_model for an INVALID MODEL NAME: {e}"
            )

    def get_model(self, model_name: str) -> str:
        """Function to get a model"""
        model_path = self.get_model_path(model_name)
        if os.path.exists(model_path):
            return model_path
        return None

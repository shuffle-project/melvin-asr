"""This File contains tests for the ModelHandler class."""
import os
import shutil
from src.helper.model_handler import ModelHandler

MODEL_HANDLER_TEST_PATH = "./src/helper/test/test_models/"


def test_setup_model_and_get_model_path():
    """Setup Should download the model tiny"""
    # see that the model does not exist
    expected_model_path = os.path.join(os.getcwd(), MODEL_HANDLER_TEST_PATH, "tiny")
    assert not os.path.exists(expected_model_path)

    # setup the tiny model
    model_handler = ModelHandler(MODEL_HANDLER_TEST_PATH)

    assert model_handler.get_model_path("tiny") == expected_model_path

    res = model_handler.setup_model("tiny")

    # see that the tiny model exists
    assert os.path.exists(expected_model_path)
    assert model_handler.get_model("tiny") == expected_model_path
    assert res is True

    # setup the tiny model again
    res = model_handler.setup_model("tiny")
    assert res is False

    # remove the tiny model
    shutil.rmtree(expected_model_path)

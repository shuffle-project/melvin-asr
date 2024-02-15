"""This File contains tests for the ModelHandler class."""
# pylint: disable=redefined-outer-name
# pylint: disable=unused-argument
# pylint: disable=unused-import

import os
import shutil

from src.helper.model_handler import ModelHandler

MODEL_HANDLER_TEST_PATH = "/src/helper/test/test_models/"

def test_setup_model_and_get_model_path():
    """Setup Should download the model tiny"""
    # see that the model does not exist
    expected_model_path = os.getcwd() + MODEL_HANDLER_TEST_PATH + "tiny"
    assert not os.path.exists(expected_model_path)

    # setup the tiny model
    model_handler = ModelHandler(MODEL_HANDLER_TEST_PATH)
    res = model_handler.setup_model("tiny")

    # see that the tiny model exists
    assert os.path.exists(expected_model_path)
    assert model_handler.get_model_path("tiny") == expected_model_path
    assert model_handler.get_model("tiny") == expected_model_path
    # see that the setup_model function returns True, it downloaded the model
    assert res is True

    # setup the tiny model again
    res = model_handler.setup_model("tiny")
    # see that the setup_model function returns False, it did not download the model
    assert res is False

    # remove the tiny model
    shutil.rmtree(expected_model_path)

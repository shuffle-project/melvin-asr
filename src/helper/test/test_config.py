"""This File contains tests for the FileHandler class."""
# ignore unused-import because of pytest fixtures
# ruff: noqa: F811
# ruff: noqa: F401

import os
from src.helper.config import CONFIG, read_config

TEST_CONFIG_SUCCESS_PATH = os.getcwd() + "/src/helper/test/test_config_success.yml"
TEST_CONFIG_RAISE_PATH = os.getcwd() + "/src/helper/test/test_config_raise.yml"

def test_read_config_success():
    """Tests reading a config.yml successfully."""

    TEST_CONFIG = read_config(TEST_CONFIG_SUCCESS_PATH)

    assert TEST_CONFIG["host"] == "some_host"
    assert TEST_CONFIG["debug"] is True
    assert TEST_CONFIG["api_keys"] == ["key1"]
    assert TEST_CONFIG["rest_runner"] == [{'compute_type': 'int8', 'device': 'cpu', 'model': 'tiny'}]
    assert TEST_CONFIG["stream_runner"] == [{'compute_type': 'int8', 'device': 'cpu', 'model': 'tiny'}]

def test_read_config_raise_error():
    """Tests reading a config.yml and raising an error."""
    try:
        read_config(TEST_CONFIG_RAISE_PATH)
    except ValueError as e:
        assert str(e) == "Configuration error: 'api_keys' is not set in .env as an environment variable or as a default value"

def test_read_config_raise_error():
    """Tests reading a config.yml and raising an error."""
    try:
        read_config(TEST_CONFIG_RAISE_PATH)
    except ValueError as e:
        assert str(e) == "Configuration error: 'api_keys' is not set in .env as an environment variable or as a default value"



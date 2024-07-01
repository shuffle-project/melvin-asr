"""This file contains tests for the FileHandler class."""
# ignore unused-import because of pytest fixtures
# ruff: noqa: F811
# ruff: noqa: F401

import os
from src.helper.config import read_config

TEST_CONFIG_SUCCESS_PATH = os.getcwd() + "/src/helper/test/test_config_success.yml"
TEST_CONFIG_RAISE_PATH = os.getcwd() + "/src/helper/test/test_config_raise.yml"

def test_read_config_success():
    """Tests reading a config.yml successfully."""
    TEST_CONFIG = read_config(TEST_CONFIG_SUCCESS_PATH)

    assert TEST_CONFIG["host"] == "localhost"
    assert TEST_CONFIG["debug"] is True
    assert TEST_CONFIG["api_keys"] == ["shuffle2024", "api_key_1", "api_key_2"]
    assert TEST_CONFIG["rest_runner"] == [{'device': 'cpu', 'model': 'large-v3', 'compute_type': 'int8', 'device_index': 0, 'num_workers': 1, 'cpu_threads': 4}]
    assert TEST_CONFIG["websocket_stream"]["cpu"]["active"] is True
    assert TEST_CONFIG["websocket_stream"]["cpu"]["model"] == "tiny"
    assert TEST_CONFIG["websocket_stream"]["cpu"]["cpu_threads"] == 4
    assert TEST_CONFIG["websocket_stream"]["cpu"]["worker_seats"] == 1
    assert TEST_CONFIG["websocket_stream"]["cuda"]["active"] is False
    assert TEST_CONFIG["websocket_stream"]["cuda"]["model"] == "tiny"
    assert TEST_CONFIG["websocket_stream"]["cuda"]["device_index"] == 0
    assert TEST_CONFIG["websocket_stream"]["cuda"]["worker_seats"] == 1

def test_read_config_raise_error():
    """Tests reading a config.yml and raising an error."""
    try:
        read_config(TEST_CONFIG_RAISE_PATH)
    except ValueError as e:
        assert str(e) == "Configuration error: 'api_keys' is not set in .env as an environment variable or as a default value"
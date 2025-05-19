import logging

from core.config import config

log_levels = {
    "info": logging.INFO,
    "warn": logging.WARN,
    "error": logging.ERROR,
}

log_config = logging.basicConfig(
    level=log_levels[config.log_level],
    format='%(asctime)s [%(levelname)s]: %(message)s (%(name)s)',
    handlers=[logging.StreamHandler()]
)

def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
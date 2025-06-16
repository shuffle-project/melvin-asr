import logging

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {"format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"},
        "access": {"format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"},
    },
    "handlers": {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
        },
        "access": {
            "formatter": "access",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
        },
    },
    "loggers": {
        "uvicorn.error": {
            "level": "INFO",
            "handlers": ["default"],
            "propagate": False,
        },
        "uvicorn.access": {
            "level": "INFO",
            "handlers": ["access"],
            "propagate": False,
        },
    },
    "root": {
        "level": "INFO",
        "handlers": ["default"],
    }
}

logging.config.dictConfig(LOGGING_CONFIG)

log_levels = {
    "info": logging.INFO,
    "warn": logging.WARN,
    "error": logging.ERROR,
}

# log_config = logging.basicConfig(
#     level=log_levels[config.log_level],
#     format='%(asctime)s [%(levelname)s]: %(message)s (%(name)s)',
#     handlers=[logging.StreamHandler()]
# )

def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
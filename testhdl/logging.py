import logging
import logging.config

logging_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {
            "format": "%(levelname)s: %(message)s"
        }
    },
    "handlers": {
        "stdout": {
            "class": "logging.StreamHandler",
            "formatter": "simple",
            "level": "DEBUG",
            "stream": "ext://sys.stdout",
        }
    },
    "loggers": {
        # The root logger's name is '' in python 3.6 
        "": {"level": "DEBUG", "handlers": ["stdout"]}
    },
}

def setup_logging():
    logging.config.dictConfig(config=logging_config)

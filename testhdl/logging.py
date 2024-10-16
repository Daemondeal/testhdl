import logging
import logging.config
import datetime as dt
import json
import logging

from pathlib import Path

# fmt: off
def get_logging_config(logdir: Path):
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "color_formatter": {
                "()": "testhdl.logging.CustomColorFormatter",
            },
            "json": {
                "()": "testhdl.logging.MyJSONFormatter",
                "fmt_keys": {
                    "level": "levelname",
                    "message": "message",
                    "timestamp": "timestamp",
                    "logger": "name",
                    "module": "module",
                    "function": "funcName",
                    "line": "lineno",
                    "thread_name": "threadName"
                }
            }
        },
        "handlers": {
            "stdout": {
                "class": "logging.StreamHandler",
                "formatter": "color_formatter",
                "level": "INFO",
                "stream": "ext://sys.stdout",
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": "json",
                "level": "DEBUG",
                "filename": (logdir / "testhdl_logs.jsonl").as_posix(),
                "maxBytes": 1024 * 1024 * 3, # 3 MB
                "backupCount": 3,
            }
        },
        "loggers": {
            # The root logger's name is '' in python 3.6 
            "": {"level": "DEBUG", "handlers": ["stdout", "file"]}
        },
    }
# fmt: on


# Taken from https://stackoverflow.com/questions/384076/how-can-i-color-python-logging-output
class CustomColorFormatter(logging.Formatter):
    grey = "\x1b[36;20m"
    yellow = "\x1b[33;20m"
    green = "\x1b[32;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"

    log_format = "[%(name)20s] %(levelname)7s: %(message)s"

    FORMATS = {
        logging.DEBUG: grey + log_format + reset,
        logging.INFO: log_format,
        logging.WARNING: yellow + log_format + reset,
        logging.ERROR: red + log_format + reset,
        logging.CRITICAL: bold_red + log_format + reset,
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)

        if (
            log_fmt is not None
            and "success" in record.__dict__
            and record.__dict__["success"]
        ):
            log_fmt = self.green + log_fmt + self.reset

        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


# Taken from https://github.com/mCodingLLC/VideosSampleCode/blob/master/videos/135_modern_logging/mylogger.py
LOG_RECORD_BUILTIN_ATTRS = {
    "args",
    "asctime",
    "created",
    "exc_info",
    "exc_text",
    "filename",
    "funcName",
    "levelname",
    "levelno",
    "lineno",
    "module",
    "msecs",
    "message",
    "msg",
    "name",
    "pathname",
    "process",
    "processName",
    "relativeCreated",
    "stack_info",
    "thread",
    "threadName",
    "taskName",
}


class MyJSONFormatter(logging.Formatter):
    def __init__(
        self,
        *,
        fmt_keys=None,
    ):
        super().__init__()
        self.fmt_keys = fmt_keys if fmt_keys is not None else {}

    def format(self, record: logging.LogRecord) -> str:
        message = self._prepare_log_dict(record)
        return json.dumps(message, default=str)

    def _prepare_log_dict(self, record: logging.LogRecord):
        always_fields = {
            "message": record.getMessage(),
            "timestamp": dt.datetime.fromtimestamp(
                record.created, tz=dt.timezone.utc
            ).isoformat(),
        }
        if record.exc_info is not None:
            always_fields["exc_info"] = self.formatException(record.exc_info)

        if record.stack_info is not None:
            always_fields["stack_info"] = self.formatStack(record.stack_info)

        message = {}

        for key, val in self.fmt_keys.items():
            msg_val = always_fields.pop(val, None)
            if msg_val is not None:
                v = msg_val
            else:
                v = getattr(record, val)
            message[key] = v

        # message = {
        #     key: (
        #         msg_val
        #         if (msg_val := always_fields.pop(val, None)) is not None
        #         else getattr(record, val)
        #     )
        #     for key, val in self.fmt_keys.items()
        # }
        message.update(always_fields)

        for key, val in record.__dict__.items():
            if key not in LOG_RECORD_BUILTIN_ATTRS:
                message[key] = val

        return message


def setup_logging(log_dir: Path):
    if not log_dir.exists():
        log_dir.mkdir()

    logging.config.dictConfig(config=get_logging_config(log_dir))

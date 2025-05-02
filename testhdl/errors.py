from pathlib import Path
from typing import Optional

from testhdl.models import TestCase


class SimulatorError(Exception):
    message: str
    logs_file: Optional[Path]

    def __init__(self, message, logs_file):
        super().__init__(self, message)
        self.message = message
        self.logs_file = logs_file

    def __str__(self):
        return self.message


class ValidationError(Exception):
    pass


class TestRunError(Exception):
    message: str
    logs_file: Optional[Path]

    def __init__(self, message, logs_file=None):
        super().__init__(self, message)
        self.message = message
        self.logs_file = logs_file

    def __str__(self):
        return f"Test failed - {self.message}"

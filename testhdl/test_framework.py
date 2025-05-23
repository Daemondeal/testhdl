from abc import ABC, abstractmethod
from pathlib import Path
from typing import List

from testhdl.models import TestCase


class TestFrameworkBase(ABC):
    @abstractmethod
    def get_top_entity(self, test: TestCase) -> str:
        return ""

    @abstractmethod
    def get_arguments(self, test: TestCase) -> List[str]:
        return []

    @abstractmethod
    def get_number_of_errors(self, test: TestCase, path_logfile: Path) -> int:
        return 0


class TestFrameworkVHDL(TestFrameworkBase):
    def get_top_entity(self, test: TestCase) -> str:
        return test.name

    def get_arguments(self, test: TestCase) -> List[str]:
        return test.runtime_args

    def get_number_of_errors(self, test: TestCase, path_logfile: Path) -> int:
        errors = 0

        with open(path_logfile, "r") as logfile:
            for line in logfile:
                if "Error:" in line:
                    errors += 1

        return errors


class TestFrameworkUVM(TestFrameworkBase):
    top_entity: str
    max_quit_count: int

    def __init__(self, top_entity: str, max_quit_count: int = 0):
        self.top_entity = top_entity
        self.max_quit_count = max_quit_count

    def get_top_entity(self, test: TestCase) -> str:
        return self.top_entity

    def get_arguments(self, test: TestCase) -> List[str]:
        args = [f"+UVM_TESTNAME={test.name}"]

        if self.max_quit_count > 0:
            args.append(f"+UVM_MAX_QUIT_COUNT={self.max_quit_count}")

        return args + test.runtime_args

    def get_number_of_errors(self, test: TestCase, path_logfile: Path) -> int:
        errors = 0

        with open(path_logfile, "r") as logfile:
            for line in logfile:
                if "UVM Report Summary" in line:
                    break
                if (
                    "UVM_ERROR" in line
                    or "UVM_FATAL" in line
                    or "ERROR-" in line
                    or "FATAL-" in line
                ):
                    errors += 1

        return errors

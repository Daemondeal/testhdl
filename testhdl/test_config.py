from abc import ABC, abstractmethod
from typing import List

from testhdl.models import TestCase


class TestConfigBase(ABC):
    @abstractmethod
    def get_top_entity(self, test: TestCase) -> str:
        return ""

    @abstractmethod
    def get_arguments(self, test: TestCase) -> List[str]:
        return []


class TestConfigSeparateEntities(TestConfigBase):
    def get_top_entity(self, test: TestCase) -> str:
        return test.name

    def get_arguments(self, test: TestCase) -> List[str]:
        return test.runtime_args


class TestConfigUVM(TestConfigBase):
    top_entity: str

    def __init__(self, top_entity: str):
        self.top_entity = top_entity

    def get_top_entity(self, test: TestCase) -> str:
        return self.top_entity

    def get_arguments(self, test: TestCase) -> List[str]:
        return [f"+UVM_TEST={test}"]

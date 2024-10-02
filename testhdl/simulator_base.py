from abc import ABC, abstractmethod
from pathlib import Path

from testhdl.source_library import SourceLibrary


class SimulatorBase(ABC):
    workdir: Path

    def __init__(self, workdir: Path):
        self.workdir = workdir

    def validate(self):
        pass

    def setup(self):
        pass

    def clean(self):
        pass

    def compile(self, library: SourceLibrary):
        pass

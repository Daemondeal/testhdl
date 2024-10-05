from abc import ABC, abstractmethod
from pathlib import Path

from testhdl.run_config import RunConfig
from testhdl.source_library import SourceLibrary


class SimulatorBase(ABC):
    workdir: Path
    logsdir: Path

    def __init__(self, workdir: Path, logsdir: Path):
        self.workdir = workdir
        self.logsdir = logsdir

    def validate(self):
        pass

    def setup(self):
        pass

    def clean(self):
        pass

    def compile(self, library: SourceLibrary, config: RunConfig):
        pass

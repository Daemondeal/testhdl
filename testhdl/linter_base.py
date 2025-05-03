from abc import ABC, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING

# if TYPE_CHECKING:
#     from testhdl.source_library import SourceLibrary
#     from testhdl.run_config import RunConfig


class LinterBase:
    workdir: Path
    logsdir: Path

    def __init__(self, workdir: Path, logsdir: Path):
        self.workdir = workdir
        self.logsdir = logsdir

    def lint(self, config: "RunConfig", library: "SourceLibrary", top_entity: str):
        pass

    def add_source_library(self, source_library: "SourceLibrary", top_entity: str):
        pass

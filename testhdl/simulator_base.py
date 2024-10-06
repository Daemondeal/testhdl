from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, TYPE_CHECKING

from testhdl.source_library import SourceLibrary

if TYPE_CHECKING:
    from testhdl.run_config import RunConfig


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

    def compile(self, library: SourceLibrary, config: "RunConfig"):
        pass

    def run_simulation(
        self,
        top_entity: str,
        path_outdir: Path,
        path_simlogs: Path,
        extra_args: List[str],
        config: "RunConfig",
    ):
        pass

    def did_error_happen(self, path_logs: Path) -> bool:
        return False

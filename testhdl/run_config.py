from pathlib import Path
from dataclasses import dataclass
from typing import List, Optional

from testhdl.source_library import SourceLibrary
from testhdl.test_config import TestConfigBase
from testhdl.simulator_base import SimulatorBase
from testhdl.models import TestCase


@dataclass
class RunConfig:
    path_workdir: Path
    path_logsdir: Path

    seed: int

    test_to_run: Optional[TestCase]

    tests: List[TestCase]

    compile_args: List[str]
    runtime_args: List[str]
    runtime_run_args: List[str]
    log_all_waves: bool

    libraries: List[SourceLibrary]
    simulator: SimulatorBase
    test_config: TestConfigBase

    resolution: str

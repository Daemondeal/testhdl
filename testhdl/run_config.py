from pathlib import Path
from dataclasses import dataclass
from typing import List, Optional

from testhdl.source_library import SourceLibrary
from testhdl.test_framework import TestFrameworkBase
from testhdl.simulator_base import SimulatorBase
from testhdl.linter_frontend import Linter
from testhdl.models import TestCase


@dataclass
class RunConfig:
    path_workdir: Path
    path_logsdir: Path

    seed: int

    linters: List[Linter]

    test_to_run: Optional[TestCase]

    tests: List[TestCase]

    compile_args: List[str]
    runtime_args: List[str]
    runtime_run_args: List[str]
    log_all_waves: bool
    wave_config_file: Path | None

    libraries: List[SourceLibrary]
    simulator: SimulatorBase
    test_framework: TestFrameworkBase

    additional_files: List[Path]

    coverage_enabled: bool

    resolution: str
    verbose: bool

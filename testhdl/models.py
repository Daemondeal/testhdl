from enum import Enum
from pathlib import Path
from dataclasses import dataclass
from typing import List, Optional

from testhdl.source_library import SourceLibrary
from testhdl.test_config import TestConfigBase
from testhdl.simulator_base import SimulatorBase


class HardwareLanguage(Enum):
    VHDL = "vhdl"
    VERILOG = "verilog"
    SYSTEMVERILOG = "systemverilog"


class RunAction(Enum):
    LIST_TESTS = 0
    COMPILE_ONLY = 1
    RUN_SINGLE_TEST = 2
    RUN_ALL = 3


@dataclass
class SourceList:
    paths: List[Path]
    compile_args: List[str]
    defines: List[str]
    language: HardwareLanguage
    coverage_enabled: bool
    incdir: Optional[str]


@dataclass
class TestCase:
    name: str
    runtime_args: List[str]


@dataclass
class TestCaseResult:
    pass


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

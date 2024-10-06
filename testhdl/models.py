from enum import Enum
from pathlib import Path
from dataclasses import dataclass
from typing import List, Optional


class HardwareLanguage(Enum):
    VHDL = "vhdl"
    VERILOG = "verilog"
    SYSTEMVERILOG = "systemverilog"


class RunAction(Enum):
    LIST_TESTS = 0
    CLEAN = 1
    COMPILE_ONLY = 2
    RUN_SINGLE_TEST = 3
    RUN_ALL = 4


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

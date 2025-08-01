from enum import Enum
from pathlib import Path
from dataclasses import dataclass
from typing import List, Optional

from testhdl.hooks import TestHook


class HardwareLanguage(Enum):
    VHDL = "vhdl"
    VERILOG = "verilog"
    SYSTEMVERILOG = "systemverilog"


class RunAction(Enum):
    LIST_TESTS = 0
    CLEAN = 1
    COMPILE_ONLY = 2
    LINT_ONLY = 3
    RUN_SINGLE_TEST = 4
    RUN_ALL = 5
    DUMP_FILESETS = 6
    SHOW_WAVES = 7
    SHOW_COVERAGE = 8


@dataclass
class SourceList:
    paths: List[Path]
    compile_args: List[str]
    defines: List[str]
    language: HardwareLanguage
    coverage_enabled: bool
    incdir: Optional[Path]


@dataclass
class TestCase:
    name: str
    runtime_args: List[str]
    pre_hooks: List[TestHook]
    post_hooks: List[TestHook]


@dataclass
class TestCaseResult:
    pass

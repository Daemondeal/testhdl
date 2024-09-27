from enum import Enum
from pathlib import Path
from dataclasses import dataclass
from typing import List, Optional


class HardwareLanguage(Enum):
    VHDL = "vhdl"
    VERILOG = "verilog"
    SYSTEMVERILOG = "systemverilog"


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

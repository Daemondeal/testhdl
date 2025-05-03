from typing import List

from testhdl.source_library import SourceLibrary
from testhdl.linter_base import LinterBase

from dataclasses import dataclass


@dataclass
class LintConfig:
    library: SourceLibrary
    top_entity: str


@dataclass
class Linter:
    linter: LinterBase
    configs: List[LintConfig]

    def add_config(self, library: SourceLibrary, top_entity: str):
        self.configs.append(LintConfig(library, top_entity))

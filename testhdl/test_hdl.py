from testhdl.logging import setup_logging
from testhdl.models import HardwareLanguage, SourceList
from testhdl.errors import ValidationError

from typing import List, Optional
from pathlib import Path

import logging

log = logging.getLogger("testhdl")


class TestHDL:
    workdir: Path
    logsdir: Path
    source_lists: List[SourceList]
    default_seed: Optional[int]

    def __init__(self):
        self.workdir = Path("build")
        self.logsdir = Path("logs")
        self.source_lists = []

    @staticmethod
    def from_args(logging_enabled: bool = True):
        if logging_enabled:
            setup_logging()

        return TestHDL()

    def set_default_seed(self, seed: int):
        """Set the default seed that will be used by the simulation if arguments
        relating to seeds are not given. If not given, the seed will default
        to be random.

        :param seed: the seed to set
        """
        self.default_seed = seed

    def set_workdir(self, workdir: str):
        """Set the directory where the simulator will get called. Defaults to 'build'

        :param workdir: path to the directory
        """
        self.workdir = Path(workdir)

    def set_logdir(self, logdir: str):
        """Set the directory where the reports will get stored. Defaults to 'logs'

        :param logdir: path to the directory
        """
        self.logsdir = Path(logdir)

    def add_vhdl_sources(
        self,
        *paths: str,
        args: List[str] = [],
        defines: List[str] = [],
        incdir: Optional[str] = None,
        coverage_enabled: bool = False
    ):
        """Adds a list of VHDL sources that will get compiled together.

        :param paths: the paths of all source files.
        :param args: compile time arguments to pass to the eda tool
        :param defines: compile time defines to pass to the eda tool.
            format: NAME=VALUE, or just NAME if no value is needed.
        :param incdir: include dir, any file in this folder will be checked to
            determine if a rebuild is needed.
        :param coverage_enabled: wheter or not coverage data should be collected
            for these sources. Defaults to False.
        """

        return self.add_sources(
            list(paths),
            language=HardwareLanguage.VHDL,
            args=args,
            defines=defines,
            incdir=incdir,
            coverage_enabled=coverage_enabled,
        )

    def add_verilog_sources(
        self,
        *paths: str,
        args: List[str] = [],
        defines: List[str] = [],
        incdir: Optional[str] = None,
        coverage_enabled: bool = False
    ):
        """Adds a list of Verilog sources that will get compiled together.

        :param paths: the paths of all source files.
        :param args: compile time arguments to pass to the eda tool
        :param defines: compile time defines to pass to the eda tool.
            format: NAME=VALUE, or just NAME if no value is needed.
        :param incdir: include dir, any file in this folder will be checked to
            determine if a rebuild is needed.
        :param coverage_enabled: wheter or not coverage data should be collected
            for these sources. Defaults to False.
        """

        return self.add_sources(
            list(paths),
            language=HardwareLanguage.VERILOG,
            args=args,
            defines=defines,
            incdir=incdir,
            coverage_enabled=coverage_enabled,
        )

    def add_systemverilog_sources(
        self,
        *paths: str,
        args: List[str] = [],
        defines: List[str] = [],
        incdir: Optional[str] = None,
        coverage_enabled: bool = False
    ):
        """Adds a list of SystemVerilog sources that will get compiled together.

        :param paths: the paths of all source files.
        :param args: compile time arguments to pass to the eda tool
        :param defines: compile time defines to pass to the eda tool.
            format: NAME=VALUE, or just NAME if no value is needed.
        :param incdir: include dir, any file in this folder will be checked to
            determine if a rebuild is needed.
        :param coverage_enabled: wheter or not coverage data should be collected
            for these sources. Defaults to False.
        """

        return self.add_sources(
            list(paths),
            language=HardwareLanguage.SYSTEMVERILOG,
            args=args,
            defines=defines,
            incdir=incdir,
            coverage_enabled=coverage_enabled,
        )

    def add_sources(
        self,
        paths: List[str],
        language: HardwareLanguage,
        *,
        args: List[str] = [],
        defines: List[str] = [],
        incdir: Optional[str] = None,
        coverage_enabled: bool = False
    ):

        path_sources = []
        for path in paths:
            source = Path(path)
            if not source.exists():
                log.critical("Cannot find source file %s", source)
                exit(-1)

            path_sources.append(source)

        self.source_lists.append(
            SourceList(
                paths=path_sources,
                compile_args=args,
                defines=defines,
                language=language,
                coverage_enabled=coverage_enabled,
                incdir=incdir,
            )
        )

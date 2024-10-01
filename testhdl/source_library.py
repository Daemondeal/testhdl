from typing import List, Optional
from testhdl.models import HardwareLanguage, SourceList
from pathlib import Path

import logging

log = logging.getLogger("testhdl")


class SourceLibrary:
    name: str
    source_lists: List[SourceList]

    def __init__(self, name: str):
        self.name = name
        self.source_lists = []

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

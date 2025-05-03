from testhdl.errors import ValidationError
from testhdl.linter_base import LinterBase
from testhdl.models import HardwareLanguage
from testhdl.run_config import RunConfig
from testhdl.source_library import SourceLibrary

import testhdl.utils as utils

VERILATOR = "verilator"


class LinterVerilator(LinterBase):
    def lint(self, config: RunConfig, library: SourceLibrary, top_entity: str):
        # fmt: off
        args = [
            VERILATOR, "--lint-only",
            "-Wall",
        ]
        # fmt: on

        for source_list in library.source_lists:
            if (
                source_list.language != HardwareLanguage.SYSTEMVERILOG
                and source_list.language != HardwareLanguage.VERILOG
            ):
                raise ValidationError("Verilator can only lint systemverilog sources")

            if source_list.incdir is not None:
                args.append(f"-I{source_list.incdir.as_posix()}")

            for path in source_list.paths:
                args.append(path.as_posix())

            for define in source_list.defines:
                args.append(f"-D{define}")

        args += ["--top-module", top_entity]
        path_stdout = self.logsdir / f"lint_{library.name}.log"

        utils.run_program(
            args,
            cwd=self.workdir,
            stdout_out=path_stdout,
            echo=True,
        )

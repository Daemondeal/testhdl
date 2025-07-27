from pathlib import Path
from typing import List
from testhdl import utils
from testhdl.errors import SimulatorError, UnimplementedError, ValidationError
from testhdl.models import HardwareLanguage
from testhdl.run_config import RunConfig
from testhdl.simulator_base import SimulatorBase
from testhdl.source_library import SourceLibrary

import os
import time
import shutil
import logging

log = logging.getLogger("vivado")

XVLOG = "xvlog"
XELAB = "xelab"
XSIM = "xsim"


class SimulatorVivado(SimulatorBase):
    def validate(self):
        if shutil.which("xsim") is None:
            raise ValidationError("Program `xsim` was not found")

    def setup(self):
        pass

    def clean(self):
        log.debug("cleaning files")
        raise UnimplementedError("SimulatorVivado clean")

    def compile(self, library: SourceLibrary, config: RunConfig):
        utils.run_program(["vlib", library.name], cwd=self.workdir, echo=config.verbose)

        log.info("Compiling library %s", library.name)
        time_start = time.perf_counter()

        for source_list in library.source_lists:
            args = []

            if source_list.language == HardwareLanguage.VHDL:
                raise UnimplementedError("SimulatorVivado compile VHDL")
            elif source_list.language == HardwareLanguage.VERILOG:
                args.append(XVLOG)
            elif source_list.language == HardwareLanguage.SYSTEMVERILOG:
                args += [XVLOG, "--sv"]
            else:
                assert False, "unreachable"

            if source_list.coverage_enabled:
                raise UnimplementedError("SimulatorVivado compile coverage_enabled")

            args += source_list.compile_args
            args += config.compile_args

            for define in source_list.defines:
                args += ["-d", define]

            if source_list.incdir is not None:
                incdir_path = os.path.relpath(source_list.incdir, self.workdir)
                args += ["-i", incdir_path]

            for path in source_list.paths:
                new_path = os.path.relpath(path, self.workdir)
                args.append(new_path)

            path_logs = self.logsdir / f"compile_{library.name}.log"
            rc = utils.run_program(
                args, cwd=self.workdir, stdout_out=path_logs, echo=config.verbose
            )

            if rc != 0:
                raise SimulatorError("Compilation Failed", path_logs)

        elapsed = time.perf_counter() - time_start
        log.info("Done! Took %.2f seconds", elapsed)

    def show_waves(self, path_logs: Path, config: RunConfig):
        _ = path_logs, config
        raise UnimplementedError("SimulatorVivado show_waves")

    def run_simulation(
        self,
        top_entity: str,
        path_outdir: Path,
        path_simlogs: Path,
        extra_args: List[str],
        config: RunConfig,
    ):
        # Vivado needs to elaborate before simulating
        path_elaboratelog = path_outdir / f"elaborate_{top_entity}.log"
        # fmt: off
        xelab_args = [
            XELAB,
            "-debug", "typical",
            "-timescale", f"{config.resolution}/{config.resolution}",
            "-override_timeunit", "-override_timeprecision",
            top_entity,
        ]
        # fmt: on

        rc = utils.run_program(
            xelab_args,
            self.workdir,
            path_elaboratelog,
            echo=config.verbose,
        )
        if rc != 0:
            raise SimulatorError(
                "Elaboration failed, Vivado exited with nonzero return code",
                path_elaboratelog,
            )

        path_wavefile = os.path.relpath(path_outdir / "wave.vcd", self.workdir)

        path_simscript = self.workdir / "sim.tcl"
        with open(path_simscript, "w") as simscript:
            simscript.write(f"open_vcd {path_wavefile}\n")
            simscript.write(f"log_vcd *\n")
            simscript.write(f"log_wave -r /*\n")

            for argument in config.runtime_run_args:
                simscript.write(f"{argument}\n")

            simscript.write(f"run -all\n")
            simscript.write(f"close_vcd\n")
            simscript.write(f"exit\n")

        if config.coverage_enabled:
            raise UnimplementedError("SimulatorVivado run_simulation coverage_enabled")

        # fmt: off
        args = [
            "xsim", f"{top_entity}",
            "-t", "sim.tcl",
            *extra_args,
            *config.runtime_args,
        ]
        # fmt: on

        rc = utils.run_program(args, self.workdir, path_simlogs, echo=config.verbose)

        if rc != 0:
            raise SimulatorError(
                "Simulator exited with nonzero return code", path_simlogs
            )

    def did_error_happen(self, path_logs: Path) -> bool:
        with open(path_logs, "r") as logfile:
            for line in logfile:
                if "Fatal:" in line:
                    return True

        return False

    def show_coverage(self, path_logsdir: Path):
        _ = path_logsdir
        raise UnimplementedError("SimulatorVivado show_coverage")

    def merge_coverages(self, path_dest: Path, path_sources: List[Path]):
        _ = path_dest
        _ = path_sources
        raise UnimplementedError("SimulatorVivado show_coverage")

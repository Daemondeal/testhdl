from pathlib import Path
from typing import List
from testhdl import utils
from testhdl.errors import SimulatorError, ValidationError
from testhdl.models import HardwareLanguage
from testhdl.run_config import RunConfig
from testhdl.simulator_base import SimulatorBase
from testhdl.source_library import SourceLibrary

import os
import shutil
import logging

log = logging.getLogger("testhdl.questasim")


class SimulatorQuestaSim(SimulatorBase):
    def validate(self):
        if shutil.which("vsim") is None:
            raise ValidationError("Program `vsim` was not found")

    def setup(self):
        # Sometimes when QuestaSim crashes it will leave the lockfile behind,
        # which then in turn blocks the simulator from running. Removing the
        # _lockfile manually should work.
        path_lockfile = self.workdir / "work" / "_lock"
        if path_lockfile.exists():
            log.warning("deleting lock file")
            os.remove(path_lockfile)

    def clean(self):
        log.debug("cleaning files")
        utils.run_program(["vdel", "-all"], cwd=self.workdir)

    def compile(self, library: SourceLibrary, config: RunConfig):
        utils.run_program(["vlib", library.name], cwd=self.workdir)
        log.info("compiling library %s", library.name)

        for source_list in library.source_lists:
            if source_list.language == HardwareLanguage.VHDL:
                program = "vcom"
            elif source_list.language in [
                HardwareLanguage.VERILOG,
                HardwareLanguage.SYSTEMVERILOG,
            ]:
                program = "vlog"
            else:
                assert False, "unreachable"

            args = [program]

            if source_list.coverage_enabled:
                args += ["-coveropt", "3", "+cover", "-coverexcludedefault"]

            args += source_list.compile_args
            args += config.compile_args

            for define in source_list.defines:
                args.append(f"+define+{define}")

            if source_list.incdir is not None:
                incdir_path = os.path.relpath(source_list.incdir, self.workdir)
                args.append(f"+incdir+{incdir_path}")

            for path in source_list.paths:
                new_path = os.path.relpath(path, self.workdir)
                args.append(new_path)

            log.info("%s", utils.join_args(args))

            path_logs = self.logsdir / f"compile_{library.name}.log"
            rc = utils.run_program(
                args, cwd=self.workdir, stdout_out=path_logs, echo=config.verbose
            )

            if rc != 0:
                raise SimulatorError("Compilation Failed", path_logs)

    def run_simulation(
        self,
        top_entity: str,
        path_outdir: Path,
        extra_args: List[str],
        config: RunConfig,
    ):
        path_wavefile = os.path.relpath(path_outdir / "wave.wlf", self.workdir)

        if config.coverage_enabled:
            extra_args.append("-coverage")
            extra_args.append("-cvgperinstance")

        # fmt: off
        args = [
            "vsim", "-c",
            "-wave", path_wavefile,
            "-t", config.resolution,
            "-vopt", "-voptargs=+acc",
            "-sv_seed", str(config.seed),
            *extra_args,
            *config.runtime_args,
            f"{top_entity}"
        ]
        # fmt: on

        if config.coverage_enabled:
            path_coverfile = os.path.relpath(
                path_outdir / "coverage.ucdb", self.workdir
            )
            args += [
                "-do",
                f"coverage save -onexit -directive -codeAll -cvg {path_coverfile}",
            ]

        # UVM components don't get instantiated until after the first timestep of the simulation,
        # so we advance the simulation just a little in order to log them in the waveform file.
        args += ["-do", f"run {config.resolution}"]
        if config.log_all_waves:
            args += ["-do", "log -r /*"]
        args += config.runtime_run_args

        args += ["-do", "run -all"]
        args += ["-do", "quit"]

        log.info("%s", utils.join_args(args))

        path_simlogs = path_outdir / "simulation.log"

        utils.run_program(args, self.workdir, path_simlogs, echo=config.verbose)

from pathlib import Path
from typing import List
import webbrowser
from testhdl import utils
from testhdl.errors import SimulatorError, ValidationError
from testhdl.models import HardwareLanguage
from testhdl.run_config import RunConfig
from testhdl.simulator_base import SimulatorBase
from testhdl.source_library import SourceLibrary

import os
import time
import shutil
import logging

# log = logging.getLogger("testhdl.questasim")
log = logging.getLogger("questasim")


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
        utils.run_program(["vlib", library.name], cwd=self.workdir, echo=config.verbose)

        log.info("Compiling library %s", library.name)
        time_start = time.perf_counter()

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

            if program == "vcom":
                args.append("-2008")
                args.append("-mixedsvvh")
                args.append("pc")

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

            path_logs = self.logsdir / f"compile_{library.name}.log"
            rc = utils.run_program(
                args, cwd=self.workdir, stdout_out=path_logs, echo=config.verbose
            )

            if rc != 0:
                raise SimulatorError("Compilation Failed", path_logs)

        elapsed = time.perf_counter() - time_start
        log.info("Done! Took %.2f seconds", elapsed)

    def show_waves(
        self,
        path_logs: Path,
        config: RunConfig,
    ):

        path_wavefile = path_logs / "wave.wlf"
        path_wavefile_rel = os.path.relpath(path_logs / "wave.wlf", self.workdir)

        if not path_wavefile.exists():
            raise SimulatorError(
                "Wavefile not found. Make sure you run the simulation first", None
            )

        args = ["vsim", "-view", path_wavefile_rel]

        if config.wave_config_file is not None:
            args += ["-do", config.wave_config_file.as_posix()]

        rc = utils.run_program(args, cwd=self.workdir, echo=config.verbose)

        if rc != 0:
            raise SimulatorError("Could not show waves", None)

    def run_simulation(
        self,
        top_entity: str,
        path_outdir: Path,
        path_simlogs: Path,
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
            args += [
                "-do",
                "set WildcardFilter [lsearch -not -all -inline $WildcardFilter Memory]",
            ]
            args += ["-do", "log -r /*"]
        args += config.runtime_run_args

        args += ["-do", "run -all"]
        args += ["-do", "quit"]

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
        path_logs = path_logsdir / "coverage.ucdb"
        if not path_logs.exists():
            raise SimulatorError(
                f'Couldn\'t find "{path_logs.as_posix()}"', logs_file=None
            )

        relpath_logs = os.path.relpath(path_logs.as_posix(), self.workdir)

        # fmt: off
        args = [
            "vcover", "report", "-details",
            "-html", relpath_logs,
            "-output", "./html_cov",
        ]
        # fmt: on

        path_vcoverlog = self.workdir / "vcover_html.log"
        rc = utils.run_program(args, self.workdir, path_vcoverlog)
        if rc != 0:
            raise SimulatorError(
                "Vcover exited with nonzero return code", path_vcoverlog
            )

        webbrowser.open((self.workdir / "html_cov" / "index.html").as_posix())

    def merge_coverages(self, path_dest: Path, path_sources: List[Path]):
        path_dest_rel = os.path.relpath(
            (path_dest / "coverage.ucdb").as_posix(), self.workdir
        )
        args = ["vcover", "merge", path_dest_rel]

        for source in path_sources:
            path_ucdb = (source / "coverage.ucdb").as_posix()
            path_rel = os.path.relpath(path_ucdb, self.workdir)

            args.append(path_rel)

        path_vcoverlog = self.workdir / "vcover_merge.log"

        rc = utils.run_program(args, self.workdir, path_vcoverlog)
        if rc != 0:
            raise SimulatorError(
                "Vcover exited with nonzero return code", path_vcoverlog
            )

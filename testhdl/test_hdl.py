from typing import List, Optional
from collections.abc import Callable
from pathlib import Path

import random
import logging
import argparse

from testhdl.hooks import TestHook
from testhdl import utils
from testhdl.linter_verilator import LinterVerilator
from testhdl.linter_frontend import Linter
from testhdl.logging import setup_logging
from testhdl.models import RunAction, TestCase
from testhdl.errors import (
    SimulatorError,
    TestRunError,
    UnimplementedError,
    ValidationError,
)
from testhdl.simulator_questasim import SimulatorQuestaSim
from testhdl.simulator_vivado import SimulatorVivado
from testhdl.source_library import SourceLibrary
from testhdl.runner import Runner
from testhdl.run_config import RunConfig
from testhdl.test_framework import (
    TestFrameworkBase,
    TestFrameworkVHDL,
    TestFrameworkUVM,
)

log = logging.getLogger("testhdl")

SUPPORTED_SIMULATORS = {
    "questasim": SimulatorQuestaSim,
    "modelsim": SimulatorQuestaSim,
    "vivado": SimulatorVivado,
}

SUPPORTED_LINTERS = {
    "verilator": LinterVerilator,
}


class TestHDL:
    workdir: Path
    logsdir: Path
    default_seed: Optional[int]

    test_framework: TestFrameworkBase
    simulator: str
    libraries: List[SourceLibrary]
    tests: List[TestCase]

    compile_args: List[str]
    runtime_args: List[str]
    runtime_run_args: List[str]

    additional_files: List[Path]

    linters: List[Linter]

    coverage_enabled: bool

    wave_config_file: Path | None
    wave_config_file_generator: Callable[[Path, Path], None] | None

    flags: List[str]

    resolution: str

    def __init__(self, args, logdir):
        self.args = args
        self.workdir = Path("build")
        self.logsdir = logdir
        self.libraries = []
        self.tests = []
        self.test_framework = TestFrameworkVHDL()
        self.resolution = "100ps"
        self.simulator = ""
        self.default_seed = None
        self.coverage_enabled = False
        self.log_all_waves = False
        self.verbose_simulation = True
        self.additional_files = []

        self.wave_config_file = None
        self.wave_config_file_generator = None

        self.compile_args = []
        self.runtime_args = []
        self.runtime_run_args = []
        self.linters = []

        self.flags = [flag.lower() for flag in args.flag]

    @staticmethod
    def from_args(logdir: Path = Path("logs"), logging_enabled: bool = True):
        if logging_enabled:
            setup_logging(logdir)

        parser = argparse.ArgumentParser()

        parser.add_argument(
            "test_name",
            help="name of the test to run",
            type=str,
            nargs="?",
            default="",
        )

        parser.add_argument(
            "--show-waves",
            help="show only the waves. Requires to have run the simulation of the specified test at least once",
            action="store_true",
        )

        parser.add_argument(
            "--clean", help="clean all temporary files", action="store_true"
        )

        parser.add_argument(
            "--coverage",
            help="shows the coverage in a browser file",
            action="store_true",
        )

        parser.add_argument(
            "-a", "--all", help="run all available tests", action="store_true"
        )

        parser.add_argument(
            "-c",
            "--compile-only",
            help="run only the compilation step",
            action="store_true",
        )

        parser.add_argument(
            "--lint",
            help="run all linters",
            action="store_true",
        )

        parser.add_argument(
            "--dump-files",
            help="dump all filesets to stdout",
            action="store_true",
        )

        parser.add_argument(
            "-v",
            "--verbose",
            help="show output even for tests that are not failing",
            action="store_true",
        )

        parser.add_argument(
            "-f", "--flag", help="add build flags", action="append", default=[]
        )

        parser.add_argument("--seed", type=int, help="set a fixed seed for simulation")

        parser.add_argument(
            "--seed-random",
            action="store_true",
            help="override default seed and pick one at random",
            default=False,
        )

        args = parser.parse_args()

        return TestHDL(args, logdir)

    def is_flag_enabled(self, flag: str) -> bool:
        """Check if a compile time flag is enabled or not.
        Changing flags in the CLI will force a recompilation

        :param flag: the flag to check
        """
        return flag.lower() in self.flags

    def set_verbose_simulation(self):
        """Tell the simulator to show sim output even without --verbose flag"""
        self.verbose_simulation = True

    def set_log_all_waves(self):
        """Tell the simulator to log all waves during simulation"""
        self.log_all_waves = True

    def set_wave_config_file_generator(self, generator: Callable[[Path, Path], None]):
        """Generate a config file to show waves.
        This is mostly a workaround for gtkwave, if you want to use something
        to generate the .gtkw file since the format is not meant to be written
        by hand.

        :param generator: the function to generate the wavefile. It gets as input
                          the path to the VCD file and the path where to generate
                          the resulting config file.
        """

        self.wave_config_file_generator = generator

    def set_wave_config_file(self, file: str | Path):
        """Give the simulator a config file to show the waves

        :param file: the wavefile"""

        file = Path(file)
        if not file.exists():
            raise ValidationError(f"File {file.as_posix()} does not exist")
        self.wave_config_file = file

    def set_resolution(self, resolution: str):
        """Set the resolution of the simulator. The default is 100ps

        :param resolution: the resolution to use.
        """
        self.resolution = resolution

    def set_default_seed(self, seed: int):
        """Set the default seed that will be used by the simulation if arguments
        relating to seeds are not given. If not given, the seed will default
        to be random.

        :param seed: the seed to set
        """
        self.default_seed = seed

    def enable_coverage(self):
        """Enables coverage collection"""
        self.coverage_enabled = True

    def set_workdir(self, workdir: str):
        """Set the directory where the simulator will get called. Defaults to 'build'

        :param workdir: path to the directory
        """
        self.workdir = Path(workdir)

    def add_library(self, name: str) -> SourceLibrary:
        """Add a new design library

        :param name: the name of the library
        """
        library = SourceLibrary(name)
        self.libraries.append(library)
        return library

    def set_framework(self, framework: TestFrameworkBase):
        """Sets a custom TestFramework

        :param framework: the framework to set
        """

        self.test_framework = framework

    def set_framework_uvm(self, top_entity: str, max_quit_count: int = 0):
        """Set UVM as the test framework

        :param top_entity: the top entity to use for UVM simulations
        :param max_quit_count: the maximum amount of errors before quitting earl
        """
        self.test_framework = TestFrameworkUVM(
            top_entity, max_quit_count=max_quit_count
        )

    def set_simulator(self, simulator_name: str):
        """Set the simulator to used

        :param simulator_name: the name of the simulator to use. Read the docs for the list of supported simulators.
        """
        if simulator_name not in SUPPORTED_SIMULATORS:
            log.critical("Invalid simulator %s", simulator_name)
            exit(-1)

        self.simulator = simulator_name

    def add_compile_argument(self, argument: str):
        """Adds a compiler argument to the simulator

        :param arg: the argument to add
        """

        self.compile_args.append(argument)

    def add_runtime_argument(self, argument: str):
        """Adds a runtime argument to the simulator

        :param arg: the argument to add
        """

        self.runtime_args.append(argument)

    def add_runtime_run_arguments(self, *arguments: str):
        """Adds runtime arguments to the simulator to be run after the first tick is simulated.
        Can be useful to add more waves in the logfile.

        :param arg: the arguments to add
        """

        self.runtime_run_args += arguments

    def add_file(self, file: str):
        """Copies a file in the working directory. Useful for managing testvectors.

        :param file: the path for the file to copy
        """

        path_file = Path(file)
        if not path_file.exists():
            raise ValidationError(f"File {path_file.as_posix()} not found")

        self.additional_files.append(path_file)

    def add_linter(self, linter_name: str) -> Linter:
        """Add a linter

        :param linter_name: the name of the linter to use. Read the docs for the list of supported linters
        """

        if linter_name not in SUPPORTED_LINTERS:
            log.critical("Invalid linter %s", linter_name)
            exit(-1)

        linter_backend = SUPPORTED_LINTERS[linter_name](self.workdir, self.logsdir)
        linter = Linter(linter=linter_backend, configs=[])

        self.linters.append(linter)

        return linter

    def add_test(
        self,
        test_name: str,
        *,
        runtime_args: Optional[List[str]] = None,
        pre_hooks: Optional[List[TestHook]] = None,
        post_hooks: Optional[List[TestHook]] = None,
    ):
        """Add a test to the tests list.

        :param test_name: the name of the test to add
        :param runtime_args: optional list of arguments to add to the simulator for this test
        """
        if runtime_args is None:
            runtime_args = []

        if pre_hooks is None:
            pre_hooks = []

        if post_hooks is None:
            post_hooks = []

        self.tests.append(TestCase(test_name, runtime_args, pre_hooks, post_hooks))

    def _validate(self):
        if len(self.tests) <= 0:
            raise ValidationError("No tests defined.")

        if self.simulator == "":
            simulators = "\n- ".join(SUPPORTED_SIMULATORS.keys())
            raise ValidationError(
                f"No simulator chosen. Supported simulators are: \n- {simulators}"
            )

    def _find_test(self, test_name: str) -> Optional[TestCase]:
        for test in self.tests:
            if test.name == test_name:
                return test

    def _run_impl(self, action):
        test_to_run = None
        self._validate()

        if action == RunAction.RUN_SINGLE_TEST or action == RunAction.SHOW_WAVES:
            test_to_run = self._find_test(self.args.test_name)

            if test_to_run is None:
                raise ValidationError(f"Cannot find test {self.args.test_name}")

        if self.args.seed is None:
            if self.default_seed is not None and not self.args.seed_random:
                seed = self.default_seed
            else:
                seed = random.randrange(0, 2**31 - 1)
        else:
            seed = self.args.seed

        simulator = SUPPORTED_SIMULATORS[self.simulator](self.workdir, self.logsdir)

        simulator.validate()

        config = RunConfig(
            path_workdir=self.workdir,
            path_logsdir=self.logsdir,
            test_to_run=test_to_run,
            tests=self.tests,
            seed=seed,
            linters=self.linters,
            resolution=self.resolution,
            compile_args=self.compile_args,
            runtime_args=self.runtime_args,
            runtime_run_args=self.runtime_run_args,
            log_all_waves=self.log_all_waves,
            verbose_simulation=self.verbose_simulation,
            libraries=self.libraries,
            simulator=simulator,
            test_framework=self.test_framework,
            wave_config_file=self.wave_config_file,
            wave_config_file_generator=self.wave_config_file_generator,
            verbose=self.args.verbose,
            coverage_enabled=self.coverage_enabled,
            additional_files=self.additional_files,
        )

        runner = Runner(config)
        runner.run(action)

    def run(self):
        """Start the simulation"""

        if self.args.coverage:
            action = RunAction.SHOW_COVERAGE
        elif self.args.show_waves:
            action = RunAction.SHOW_WAVES
        elif self.args.clean:
            action = RunAction.CLEAN
        elif self.args.compile_only:
            action = RunAction.COMPILE_ONLY
        elif self.args.lint:
            action = RunAction.LINT_ONLY
        elif self.args.all:
            action = RunAction.RUN_ALL
        elif self.args.test_name != "":
            action = RunAction.RUN_SINGLE_TEST
        elif self.args.dump_files:
            action = RunAction.DUMP_FILESETS
        else:
            action = RunAction.LIST_TESTS

        try:
            self._run_impl(action)
        except UnimplementedError as e:
            log.critical("Unimplemented: %s", e)
            exit(-1)
        except ValidationError as e:
            log.critical("Simulator error: %s", e)
            exit(-1)
        except TestRunError as e:
            if not self.args.verbose and e.logs_file is not None:
                utils.print_file(e.logs_file)

            log.error("%s", e.message)
            exit(-1)
        except SimulatorError as e:
            if not self.args.verbose and e.logs_file is not None:
                utils.print_file(e.logs_file)

            log.critical("%s", e.message)
            exit(-1)

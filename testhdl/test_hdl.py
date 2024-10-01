from typing import List, Optional
from pathlib import Path

import random
import logging
import argparse

from testhdl.logging import setup_logging
from testhdl.models import RunAction, TestCase
from testhdl.errors import ValidationError
from testhdl.simulator_base import SimulatorBase
from testhdl.simulator_questasim import SimulatorQuestaSim
from testhdl.source_library import SourceLibrary
from testhdl.test_config import (
    TestConfigBase,
    TestConfigUVM,
    TestConfigSeparateEntities,
)

log = logging.getLogger("testhdl")

SUPPORTED_SIMULATORS = {
    "questasim": SimulatorQuestaSim,
    "modelsim": SimulatorQuestaSim,
}


class TestHDL:
    workdir: Path
    logsdir: Path
    default_seed: Optional[int]
    test_config: TestConfigBase
    simulator: Optional[SimulatorBase]

    libraries: List[SourceLibrary]
    tests: List[TestCase]

    resolution: str

    def __init__(self, args):
        self.args = args
        self.workdir = Path("build")
        self.logsdir = Path("logs")
        self.libraries = []
        self.tests = []
        self.test_config = TestConfigSeparateEntities()
        self.resolution = "100ps"
        self.simulator = None
        self.default_seed = None

    @staticmethod
    def from_args(logging_enabled: bool = True):
        if logging_enabled:
            setup_logging()

        parser = argparse.ArgumentParser()

        parser.add_argument(
            "test_name",
            help="name of the test to run",
            type=str,
            nargs="?",
            default="",
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

        return TestHDL(args)

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

    def add_library(self, name: str) -> SourceLibrary:
        """Add a new design library

        :param name: the name of the library
        """
        library = SourceLibrary(name)
        self.libraries.append(library)
        return library

    def set_config_uvm(self, top_entity: str):
        """Set UVM as the test environment

        :param top_entity: the top entity to use for UVM simulations
        """
        self.test_config = TestConfigUVM(top_entity)

    def set_simulator(self, simulator_name: str):
        """Set the simulator to used

        :param simulator_name: the name of the simulator to use. Read the docs for the list of supported simulators.
        """
        if simulator_name not in SUPPORTED_SIMULATORS:
            log.critical("Invalid simulator %s", simulator_name)
            exit(-1)

        self.simulator = SUPPORTED_SIMULATORS[simulator_name]()

    def add_test(self, test_name: str, *, runtime_args: Optional[List[str]] = None):
        """Add a test to the tests list.

        :param test_name: the name of the test to add
        :param runtime_args: optional list of arguments to add to the simulator for this test
        """
        if runtime_args is None:
            runtime_args = []

        self.tests.append(TestCase(test_name, runtime_args))

    def _validate(self):
        if len(self.tests) <= 0:
            raise ValidationError("No tests defined.")

        if self.simulator is None:
            raise ValidationError(
                f"No simulator chosen. Supported simulators are: \n- {'\n- '.join(SUPPORTED_SIMULATORS.keys())}"
            )

    def run(self):
        """Start the simulation"""
        try:
            self._validate()
        except ValidationError as e:
            log.error("%s", e)
            return

        if self.args.compile_only:
            action = RunAction.COMPILE_ONLY
        elif self.args.all:
            action = RunAction.RUN_ALL
        elif self.args.test_name != "":
            action = RunAction.RUN_SINGLE_TEST
        else:
            action = RunAction.LIST_TESTS

        if self.args.seed is None:
            if self.default_seed is not None and not self.args.seed_random:
                seed = self.default_seed
            else:
                seed = random.randrange(0, 2**31 - 1)
        else:
            seed = self.args.seed

        if action == RunAction.RUN_ALL or action == RunAction.RUN_SINGLE_TEST:
            log.info("Seed chosen: %d", seed)

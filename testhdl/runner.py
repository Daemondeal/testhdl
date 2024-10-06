from testhdl import utils
from testhdl.models import RunAction, TestCase
from testhdl.run_config import RunConfig

import time
import shutil
import logging

log = logging.getLogger("testhdl")


class Runner:
    config: RunConfig

    def __init__(self, config: RunConfig):
        self.config = config

    def _compile(self):
        log.info("Starting compilation")
        time_start_compile = time.perf_counter()

        for library in self.config.libraries:
            self.config.simulator.compile(library, self.config)

        elapsed = time.perf_counter() - time_start_compile
        log.info("Compilation done; took %.2f seconds", elapsed)

    def _run_test(self, test: TestCase):
        time_test_start = time.perf_counter()
        log.info("Running test %s", test.name)

        path_outdir = self.config.path_logsdir / test.name
        utils.rmdir_if_exists(path_outdir)
        path_outdir.mkdir(parents=True)

        top_entity = self.config.test_config.get_top_entity(test)
        args = self.config.test_config.get_arguments(test)
        args += test.runtime_args

        self.config.simulator.run_simulation(top_entity, path_outdir, args, self.config)

        test_elapsed = time.perf_counter() - time_test_start
        log.info("Test done! Took %.2f seconds", test_elapsed)

    def _setup(self):
        utils.rmdir_if_exists(self.config.path_workdir)
        self.config.path_workdir.mkdir(parents=True)
        self.config.path_logsdir.mkdir(parents=True, exist_ok=True)
        self.config.simulator.setup()

    def _clean(self):
        log.info("Cleaning...")
        utils.rmdir_if_exists(self.config.path_workdir)
        utils.rmdir_if_exists(self.config.path_logsdir)

    def _list_tests(self):
        print("Available tests:")
        for test in self.config.tests:
            print(f" - {test.name}")

    def run(self, action: RunAction):
        if action == RunAction.CLEAN:
            self._clean()
        elif action == RunAction.LIST_TESTS:
            self._list_tests()
        elif action == RunAction.COMPILE_ONLY:
            self._setup()
            self._compile()
        elif action == RunAction.RUN_SINGLE_TEST:
            assert self.config.test_to_run is not None
            self._setup()
            self._compile()
            self._run_test(self.config.test_to_run)
        elif action == RunAction.RUN_ALL:
            assert False, "run all unimplemented"

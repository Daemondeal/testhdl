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
            self.config.simulator.compile(library)

        elapsed = time.perf_counter() - time_start_compile
        log.info("Compilation done; took %.2f seconds", elapsed)

    def _run_test(self, test: TestCase):
        time_test_start = time.perf_counter()
        log.info("Running test %d", test.name)

        path_outdir = self.config.path_logsdir / test.name
        if path_outdir.exists():
            shutil.rmtree(path_outdir)

        path_outdir.mkdir(parents=True)

        test_elapsed = time.perf_counter() - time_test_start
        log.info("Test done. Took %.2f seconds", test_elapsed)

    def run(self, action: RunAction):
        if action == RunAction.LIST_TESTS:
            print("Available tests:")
            for test in self.config.tests:
                print(f" - {test.name}")

            return

        if self.config.path_workdir.exists():
            shutil.rmtree(self.config.path_workdir)

        self.config.path_workdir.mkdir(parents=True)

        self.config.simulator.setup()

        self._compile()

        if action == RunAction.COMPILE_ONLY:
            return

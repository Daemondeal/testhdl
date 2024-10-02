from testhdl.models import RunAction, RunConfig

import logging

log = logging.getLogger("testhdl")


class Runner:
    config: RunConfig

    def __init__(self, config: RunConfig):
        self.config = config

    def _compile(self):
        pass

    def run(self, action: RunAction):
        if action == RunAction.LIST_TESTS:
            print("Available tests:")
            for test in self.config.tests:
                print(f" - {test.name}")

            return

        self._compile()

        if action == RunAction.COMPILE_ONLY:
            return

        log.info("Seed chosen: %d")

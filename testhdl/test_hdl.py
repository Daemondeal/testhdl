from testhdl.logging import setup_logging

import logging

log = logging.getLogger("testhdl")

class TestHDL:
    @staticmethod
    def from_argv():
        setup_logging()

        return TestHDL()

    def test(self):
        log.info("Hello world!")
        log.warning("This is a warning")
        log.error("This is an error")
        log.critical("This is a critical error")

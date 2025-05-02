from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from testhdl.run_config import RunConfig


class TestHook:
    def run_hook(self, config: "RunConfig"):
        pass

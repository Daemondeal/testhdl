from testhdl import utils
from testhdl.models import HardwareLanguage
from testhdl.simulator_base import SimulatorBase
from testhdl.source_library import SourceLibrary

import os


class SimulatorQuestaSim(SimulatorBase):
    def validate(self):
        pass

    def setup(self):
        pass

    def clean(self):
        pass

    def compile(self, library: SourceLibrary):
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

            for path in source_list.paths:
                new_path = os.path.relpath(path, self.workdir)
                args.append(new_path)

            utils.run_program(args, cwd=self.workdir)

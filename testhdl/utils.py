from pathlib import Path
from typing import List


def run_program(args: List[str], cwd: Path, stdout_out: Path, echo: bool = False):
    print(f"cd {cwd}")
    print(" ".join(args) + f" > {stdout_out.as_posix()}")

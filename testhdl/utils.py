from pathlib import Path
from typing import List, Optional


def run_program(
    args: List[str], cwd: Path, stdout_out: Optional[Path] = None, echo: bool = False
):
    print(f"cd {cwd}")

    if stdout_out is None:
        print(" ".join(args))
    else:
        print(" ".join(args) + f" > {stdout_out.as_posix()}")

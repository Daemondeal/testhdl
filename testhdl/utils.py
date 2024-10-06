from pathlib import Path
import shutil
from typing import List, Optional


def join_args(args: List[str]) -> str:
    cleaned_args = [f'"{arg}"' if " " in arg else arg for arg in args]
    return " ".join(cleaned_args)


def print_file(file: Path):
    with open(file, "r") as infile:
        print(infile.read())


def rmdir_if_exists(dir: Path):
    if dir.exists() and dir.is_dir():
        shutil.rmtree(dir)


def run_program(
    args: List[str], cwd: Path, stdout_out: Optional[Path] = None, echo: bool = False
) -> int:
    print(f"cd {cwd} && ", end="")

    if stdout_out is None:
        print(join_args(args))
    else:
        print(join_args(args) + f" > {stdout_out.as_posix()}")

    return 0

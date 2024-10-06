from pathlib import Path
from typing import List, Optional

import shutil
import subprocess


def join_args(args: List[str]) -> str:
    cleaned_args = [f'"{arg}"' if " " in arg else arg for arg in args]
    return " ".join(cleaned_args)


def print_file(file: Path):
    with open(file, "r") as infile:
        print(infile.read())


def rmdir_if_exists(dir: Path):
    if dir.exists() and dir.is_dir():
        shutil.rmtree(dir)


READ_CHUNK_SIZE = 4096


def run_program(
    args: List[str], cwd: Path, stdout_out: Optional[Path] = None, echo: bool = False
) -> int:

    file_out = None
    if stdout_out is not None:
        file_out = open(stdout_out, "wb")

    try:
        with subprocess.Popen(args, cwd=cwd, stdout=subprocess.PIPE) as proc:
            assert proc.stdout is not None

            while True:
                chunk = proc.stdout.read(1024)
                if len(chunk) == 0:
                    break

                if echo:
                    print(chunk.decode("utf-8"))
                if file_out is not None:
                    file_out.write(chunk)

            rc = proc.poll()
            assert rc is not None
            return rc

    finally:
        if file_out is not None:
            file_out.close()

    return run_program_stub(args, cwd, stdout_out, echo)


def run_program_stub(
    args: List[str], cwd: Path, stdout_out: Optional[Path] = None, echo: bool = False
) -> int:
    print(f"cd {cwd} && ", end="")

    if stdout_out is None:
        print(join_args(args))
    else:
        print(join_args(args) + f" > {stdout_out.as_posix()}")

    return 0

from pathlib import Path
from typing import List, Optional

import re
import sys
import select
import shutil
import logging
import subprocess

log = logging.getLogger("testhdl")


def join_args(args: List[str]) -> str:
    cleaned_args = [f'"{arg}"' if " " in arg else arg for arg in args]
    return " ".join(cleaned_args)


def print_file(file: Path):
    with open(file, "r") as infile:
        print(infile.read())


def rmdir_if_exists(dir: Path):
    if dir.exists() and dir.is_dir():
        shutil.rmtree(dir)


READ_CHUNK_SIZE = 1024 * 4

re_progress = r"{([0-9\.]+) ns}"


def run_program(
    args: List[str], cwd: Path, stdout_out: Optional[Path] = None, echo: bool = False
) -> int:
    log.debug("Running '%s'", join_args(args))
    found_timestamp = False

    file_out = None
    if stdout_out is not None:
        file_out = open(stdout_out, "wb")

    try:
        with subprocess.Popen(args, cwd=cwd, stdout=subprocess.PIPE) as proc:
            assert proc.stdout is not None

            while True:
                # chunk = proc.stdout.read(READ_CHUNK_SIZE)
                chunk = proc.stdout.readline()
                if not chunk:
                    break

                decoded = chunk.decode("utf-8")

                if "run -all" in decoded:
                    log.info("Simulation Started!")

                match = re.search(re_progress, decoded)
                if match:
                    if not echo:
                        print("\rLast timestamp: " + match.group(0), end="")
                    found_timestamp = True

                if echo:
                    # Better redirection
                    sys.stdout.buffer.write(chunk)
                if file_out is not None:
                    file_out.write(chunk)

            # TODO: Adding a timeout here could be important
            rc = proc.wait()
            return rc

    finally:
        if found_timestamp:
            print()
        if file_out is not None:
            file_out.close()

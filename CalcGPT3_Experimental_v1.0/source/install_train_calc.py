#!/usr/bin/env python3
"""Install the personal train_calc command without sudo or .command files."""
from __future__ import annotations

import os
import shlex
import stat
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
VENV = ROOT / ".venv"
VENV_PYTHON = VENV / "bin" / "python3"
BIN = Path.home() / ".local" / "bin"
COMMAND = BIN / "train_calc"
ZSHRC = Path.home() / ".zshrc"
PATH_LINE = 'export PATH="$HOME/.local/bin:$PATH"'


def run(*args: str) -> None:
    print("+", " ".join(shlex.quote(arg) for arg in args))
    subprocess.run(args, check=True)


def main() -> None:
    print("Installing TinyLM Mac trainer from:", ROOT)
    if not VENV_PYTHON.exists():
        run(sys.executable, "-m", "venv", str(VENV))
    run(str(VENV_PYTHON), "-m", "pip", "install", "--upgrade", "pip")
    run(str(VENV_PYTHON), "-m", "pip", "install", "-r", str(ROOT / "requirements.txt"))

    BIN.mkdir(parents=True, exist_ok=True)
    wrapper = f'''#!/bin/zsh
set -e
cd {shlex.quote(str(ROOT))}
read "epochs?How many additional training epochs? [20]: "
epochs="${{epochs:-20}}"
if [[ ! "$epochs" == <-> ]] || (( epochs < 1 || epochs > 100 )); then
  echo "Please enter a whole number from 1 through 100."
  exit 2
fi
{shlex.quote(str(VENV_PYTHON))} train_mac.py --epochs "$epochs"
echo
echo "Updated calculator files:"
echo "  {ROOT}/calculator/tinylm.py"
for file in {ROOT}/calculator/tinydata*.py; do echo "  $file"; done
'''
    COMMAND.write_text(wrapper)
    COMMAND.chmod(COMMAND.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

    existing = ZSHRC.read_text() if ZSHRC.exists() else ""
    if PATH_LINE not in existing.splitlines():
        with ZSHRC.open("a") as stream:
            if existing and not existing.endswith("\n"):
                stream.write("\n")
            stream.write(PATH_LINE + "\n")

    print("\nInstallation complete.")
    print("Run this once in the current Terminal:")
    print("  source ~/.zshrc")
    print("Then start or resume training with:")
    print("  train_calc")


if __name__ == "__main__":
    main()

"""Headless harness for the CalcGPT 3 calculator runtime.

It installs the ``tisim`` stubs, executes every generated ``tinydata`` installer
part into the simulated TI store, then executes the *real* calculator template
source (everything before its interactive event loop) so tests can call
``generate`` on exactly the code that ships to the calculator.
"""

from __future__ import annotations

import builtins
import importlib.util
import random
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent
CALCULATOR = SOURCE / "calculator"

# The interactive section starts at this exact statement in the template.
# It must be unique (clear_conversation also resets messages/entry/scroll).
LOOP_MARKER = 'messages=[]; entry=""; scroll=0; shift_once=False'


_TISIM = None


def _load_tisim():
    global _TISIM
    if _TISIM is None:
        spec = importlib.util.spec_from_file_location("tisim", HERE / "tisim.py")
        module = importlib.util.module_from_spec(spec)
        sys.modules["tisim"] = module
        spec.loader.exec_module(module)
        _TISIM = module
    return _TISIM


def store():
    """The simulated TI store used by the most recent installation."""

    return _load_tisim().STORE.lists


def reset_store() -> None:
    """Empty the simulated TI store, as a fresh problem would be."""

    tisim = _load_tisim()
    tisim.install()
    tisim.STORE.clear()


def installer_parts(folder: Path | None = None) -> list[Path]:
    """Return generated tinydata installers in execution order."""

    folder = folder or CALCULATOR
    parts = list(folder.glob("tinydata*.py"))

    def order(path: Path) -> tuple[int, str]:
        match = re.search(r"tinydata(\d*)", path.stem)
        number = int(match.group(1)) if match and match.group(1) else 1
        return (number, path.name)

    return sorted(parts, key=order)


def install_model(parts: list[Path] | None = None) -> None:
    """Execute the installer programs into the simulated TI store."""

    tisim = _load_tisim()
    tisim.install()
    parts = parts if parts is not None else installer_parts()
    if not parts:
        raise RuntimeError("no generated tinydata installers found")
    real_print = builtins.print
    builtins.print = lambda *a, **k: None
    try:
        for part in parts:
            namespace: dict = {"__name__": "__tinydata__", "input": lambda *a: ""}
            source = part.read_text()
            exec(compile(source, str(part), "exec"), namespace)
    finally:
        builtins.print = real_print
    return tisim


def load_runtime(seed: int = 12345, template: Path | None = None) -> dict:
    """Execute the calculator template and return its global namespace."""
    template = template or (CALCULATOR / "tinylm.py")
    source = template.read_text()
    index = source.index(LOOP_MARKER)
    runtime_source = source[:index]
    namespace: dict = {"__name__": "__tinylm_test__"}
    exec(compile(runtime_source, str(template), "exec"), namespace)
    namespace.setdefault("LAST_INTENT", -1)
    namespace.setdefault("LAST_ACT", 0)
    namespace.setdefault("LAST_EMOTION", 0)
    # The state line that begins the interactive section is what we truncated at,
    # so recreate the module-level state the control functions expect.
    namespace.update({"messages": [], "entry": "", "scroll": 0,
                      "shift_once": False, "caps": False, "NOTICE": "",
                      "PRINT_LATEST": False, "RESTORE": [], "LAST_PROMPT": ""})
    generator = random.Random(seed)
    namespace["random"] = generator.random
    namespace["_generator"] = generator
    return namespace


def load_runtime_source(source: str, seed: int = 12345, label: str = "<source>") -> dict:
    """Execute calculator runtime *source text* (e.g. read out of a .tns page).

    Same as :func:`load_runtime` but takes the source as a string, so a page
    embedded in a built document can be tested exactly as it ships.
    """
    index = source.index(LOOP_MARKER)
    namespace: dict = {"__name__": "__tinylm_test__"}
    exec(compile(source[:index], label, "exec"), namespace)
    namespace.setdefault("LAST_INTENT", -1)
    namespace.setdefault("LAST_ACT", 0)
    namespace.setdefault("LAST_EMOTION", 0)
    namespace.update({"messages": [], "entry": "", "scroll": 0,
                      "shift_once": False, "caps": False, "NOTICE": "",
                      "PRINT_LATEST": False, "RESTORE": [], "LAST_PROMPT": ""})
    generator = random.Random(seed)
    namespace["random"] = generator.random
    namespace["_generator"] = generator
    return namespace


class Runtime:
    """Convenience wrapper around a loaded template namespace."""

    def __init__(self, namespace: dict):
        self.ns = namespace

    def __getitem__(self, name: str):
        return self.ns[name]

    def generate(self, prompt: str, messages=None):
        messages = messages if messages is not None else []
        result, _scroll = self.ns["generate"](prompt, messages, 0)
        return result

    def reseed(self, seed: int) -> None:
        self.ns["_generator"].seed(seed)

    @property
    def vocab(self) -> list[str]:
        return self.ns["VOCAB"]

    @property
    def lookup(self) -> dict:
        return self.ns["LOOKUP"]


def build(parts: list[Path] | None = None, seed: int = 12345, quiet: bool = True,
          warm: bool = False):
    """Full pipeline: install data, load runtime, return a :class:`Runtime`.

    ``warm`` loads the weight tensors immediately so the runtime no longer
    depends on the simulated store (useful when tests install other models)."""

    real_print = builtins.print

    def silent(*args, **kwargs):
        if not quiet:
            real_print(*args, **kwargs)

    if quiet:
        builtins.print = silent
    try:
        reset_store()
        install_model(parts)
    finally:
        builtins.print = real_print
    runtime = Runtime(load_runtime(seed=seed))
    if warm:
        runtime.ns["ensure_model"]([], 0)
    return runtime

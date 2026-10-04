"""Desktop stand-ins for the TI-Nspire ``ti_system`` and ``ti_draw`` modules.

The calculator runtime imports these two modules directly.  Registering these
simulations in ``sys.modules`` lets the *unmodified* calculator source run under
CPython so behaviour, output, and timing can be tested without hardware.

The store mirrors TI's Nspire list variables closely enough for testing:
``store_list`` replaces a named list, ``recall_list`` returns a copy of it, and
recalling a name that was never stored raises (as TI does).
"""

from __future__ import annotations

import sys
import time
import types


class _Store:
    def __init__(self) -> None:
        self.lists: dict[str, list] = {}

    def store(self, name: str, values) -> None:
        self.lists[name] = list(values)

    def recall(self, name: str) -> list:
        if name not in self.lists:
            raise ValueError("variable not defined: " + name)
        return list(self.lists[name])

    def clear(self) -> None:
        self.lists.clear()


STORE = _Store()

# Milliseconds since module import, matching the monotonic clock get_time_ms uses.
_START = time.perf_counter()


def get_time_ms() -> int:
    return int((time.perf_counter() - _START) * 1000)


# Scripted key stream so the event loop can be driven deterministically.
_KEYS: list = []


def push_keys(*keys) -> None:
    _KEYS.extend(keys)


def clear_keys() -> None:
    _KEYS.clear()


def get_key(wait: int = 0):
    if _KEYS:
        return _KEYS.pop(0)
    # No scripted keys remain: raise so a running event loop unwinds instead of
    # blocking forever on desktop.
    raise KeyboardInterrupt("tisim: no scripted keys")


def make_system_module() -> types.ModuleType:
    module = types.ModuleType("ti_system")
    module.get_key = get_key
    module.get_time_ms = get_time_ms
    module.recall_list = STORE.recall
    module.store_list = STORE.store
    module.push_keys = push_keys
    module.clear_keys = clear_keys
    module.STORE = STORE
    return module


class _Canvas:
    """Records nothing but the call count; used only to keep the event loop alive."""

    def __init__(self) -> None:
        self.frames = 0
        self.texts: list[tuple[int, int, str]] = []

    def reset_frame(self) -> None:
        self.texts = []


CANVAS = _Canvas()


def _noop(*_args, **_kwargs) -> None:
    return None


def _draw_text(x, y, text) -> None:
    CANVAS.texts.append((x, y, text))


def _paint_buffer() -> None:
    CANVAS.frames += 1


def make_draw_module() -> types.ModuleType:
    module = types.ModuleType("ti_draw")
    module.use_buffer = _noop
    module.paint_buffer = _paint_buffer
    module.set_color = _noop
    module.set_pen = _noop
    module.set_pen_color = _noop
    module.fill_rect = _noop
    module.draw_rect = _noop
    module.fill_circle = _noop
    module.draw_circle = _noop
    module.draw_line = _noop
    module.draw_text = _draw_text
    module.clear = _noop
    module.CANVAS = CANVAS
    return module


def install() -> None:
    """Register the simulated modules so calculator code can import them."""

    sys.modules["ti_system"] = make_system_module()
    sys.modules["ti_draw"] = make_draw_module()

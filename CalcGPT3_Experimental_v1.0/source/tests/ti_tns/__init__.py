"""Vendored third-party decoder for TI-Nspire TNS method 13 payloads.

These files are not part of CalcGPT 3 and were not written for it. They are
vendored unchanged from the TnsTools project so that ``tests/verify_tns.py`` can
decode the TI-encrypted document XML in a ready-to-run .tns and therefore prove
that the embedded runtime runs against the model data actually stored inside the
shipped document.

Only the decoder is used. CalcGPT 3 never re-encodes method 13 payloads; see
``source/build_tns.py`` for why re-encoding is deliberately avoided.

Source:  https://github.com/MaksimirKurtov/TnsTools
License: MIT, reproduced in LICENSE in this directory.

Format documentation for what these files implement:
  https://www.hackspire.org/TNS_File_Format
"""

from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from tixc_decode import TixcDecodeError, decode_tixc  # noqa: E402
from tns_method13 import (  # noqa: E402
    HEADER_KEY,
    Method13Error,
    decrypt_method13_to_tixc,
)

__all__ = [
    "HEADER_KEY",
    "Method13Error",
    "TixcDecodeError",
    "decode_tixc",
    "decrypt_method13_to_tixc",
]
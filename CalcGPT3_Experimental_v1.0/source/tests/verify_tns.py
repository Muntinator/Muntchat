#!/usr/bin/env python3
"""End-to-end check of a built ready-to-run .tns document.

This is the strongest verification available without a TI-Nspire. It proves the
shipped artefact actually works, rather than merely that the generator produced
a file that looks right:

  1. parse the .tns container;
  2. decode TI's method 13 (3DES-CTR + raw deflate + TIXC) Problem1.xml;
  3. reconstruct the model variables stored inside the document;
  4. execute the tinylm.py page that is actually embedded in the .tns against
     exactly those variables, using the simulated ti_system/ti_draw;
  5. generate replies and compare them with the same runtime driven by the
     freshly exported installers.

Step 4 is the important one: it runs the page from the document, not the file in
source/calculator, against the model data from the document. If the two disagree,
the shipped document is broken even though every unit test passes.

Method 13 decoding uses the vendored reference decoder in ``tests/ti_tns``
(MIT, see that directory's LICENSE and __init__.py for provenance). CalcGPT 3
never re-encodes these payloads; see source/build_tns.py.
"""

from __future__ import annotations

import argparse
import io
import json
import pathlib
import re
import sys
import zlib

HERE = pathlib.Path(__file__).resolve().parent
SOURCE = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(SOURCE))

import build_tns  # noqa: E402
import harness  # noqa: E402
from ti_tns import decode_tixc, decrypt_method13_to_tixc  # noqa: E402


def decode_method13_xml(payload: bytes) -> str:
    """Decode a stored method 13 payload into XML text."""
    tixc = decrypt_method13_to_tixc(payload)
    return decode_tixc(tixc).decode("utf-8", "replace")





# ------------------------------------------------------------------ the test
def variables_from_document(entries, data: bytes) -> dict:
    """Rebuild the model variables stored in the document's Problem1.xml."""
    problem = None
    for entry in entries:
        if entry.name == "Problem1.xml":
            problem = entry
            break
    if problem is None:
        raise build_tns.TnsError("no Problem1.xml in the document")
    if not problem.blob:
        problem.load(data)
    xml = decode_method13_xml(problem.blob)
    found = {}
    for match in re.finditer(r"<n>(\w+)</n><v>\{([^}]*)\}</v>", xml):
        name, raw = match.group(1), match.group(2)
        values = []
        for item in raw.split(","):
            item = item.strip().replace("\u2212", "-")  # TIXC writes U+2212 for '-'
            item = item.replace("\uffff", "")             # and U+FFFF as filler
            if not item:
                continue
            if "." in item or "e" in item.lower():
                values.append(float(item))
            else:
                values.append(int(item))
        found[name] = values
    return found


def store_from_variables(variables: dict):
    """Flatten the document's variables into the flat lists the store expects.

    The installer writes packed weights as integers; the remaining variables are
    real-valued (for example ``tdscale``), so only whole numbers are truncated.
    """
    flat = {}
    for name, values in variables.items():
        flat[name] = [int(v) if float(v).is_integer() else v for v in values]
    return flat


def run(page_source: str, variables: dict):
    """Load *page_source* against *variables* and return a Runtime."""
    tisim = harness._load_tisim()
    tisim.install()
    tisim.STORE.clear()
    tisim.STORE.lists.update(store_from_variables(variables))
    return harness.Runtime(harness.load_runtime_source(page_source, seed=2026,
                                                       label="tinylm.py@document"))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("tns", help="the built .tns to verify")
    ap.add_argument("--runtime", default=str(HERE.parent / "calculator" / "tinylm.py"),
                    help="the exported runtime to compare against")
    args = ap.parse_args(argv)

    data = pathlib.Path(args.tns).read_bytes()
    entries, _ = build_tns.parse(data)
    print("document: %s (%d bytes)" % (args.tns, len(data)))
    for entry in entries:
        print("  %-14s method=%-2d stored=%d" % (entry.name, entry.method, entry.csize))

    variables = variables_from_document(entries, data)
    print("model variables recovered from Problem1.xml: %d (%s...)"
          % (len(variables), ", ".join(sorted(variables)[:5])))
    info = variables.get("tdinfo")
    if not info:
        raise build_tns.TnsError("tdinfo not found in the document")
    fmt, emb, hid, epochs, vocab = (int(x) for x in info[:5])
    print("tdinfo: format=%d E=%d H=%d epochs=%d vocab=%d model_id=%d"
          % (fmt, emb, hid, epochs, vocab, int(info[7])))

    meta_path = HERE.parent / "calculator" / "model_meta.json"
    meta = json.loads(meta_path.read_text())
    if fmt != meta["format"] or int(info[7]) != meta["model_id"]:
        raise build_tns.TnsError(
            "document model (format %s, id %s) does not match model_meta.json "
            "(format %s, id %s)" % (fmt, info[7], meta["format"], meta["model_id"])
        )
    print("model matches calculator/model_meta.json")

    page = None
    for entry in entries:
        if entry.name == "tinylm.py":
            entry.load(data)
            page = entry.payload.decode()
    if page is None:
        raise build_tns.TnsError("no tinylm.py page in the document")

    exported = pathlib.Path(args.runtime).read_text()
    if page != exported:
        raise build_tns.TnsError(
            "the tinylm.py page in the document differs from %s" % args.runtime
        )
    print("embedded tinylm.py matches the exported runtime (%d bytes)" % len(page))

    prompts = ["hello", "how are you", "i am going to the park", "thank you very much"]
    doc_rt = run(page, variables)
    exp_rt = run(exported, variables)

    print("\ngenerating from the DOCUMENT's own runtime and model data:")
    doc_replies = []
    for prompt in prompts:
        reply = doc_rt.generate(prompt, [])
        doc_replies.append(reply)
        print("  %-24r -> %r" % (prompt, reply))
        if not reply or not reply.strip():
            raise build_tns.TnsError("empty reply for %r from the document runtime" % prompt)
    print("\ngenerating from the freshly EXPORTED runtime and the same data:")
    for prompt, doc_reply in zip(prompts, doc_replies):
        reply = exp_rt.generate(prompt, [])
        if reply != doc_reply:
            raise build_tns.TnsError(
                "runtime in the document and exported runtime disagree on %r: %r vs %r"
                % (prompt, doc_reply, reply)
            )
        print("  %-24r -> %r  (identical)" % (prompt, reply))

    print("\nOK: the document's tinylm.py page runs on the document's own installed "
          "model data and matches the exported runtime exactly.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except build_tns.TnsError as exc:
        print("error: %s" % exc, file=sys.stderr)
        sys.exit(1)
"""Run the fixed prompt suite against a specific build and report metrics.

Usage:
    python tests/run_suite.py --template PATH/tinylm.py --data PATH/tinydata*.py \
        --json out.json [--label name]

Used to compare the original E40 build against the improved build with the same
prompts and seeds.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import harness
import quality_metrics

SUITE = [
    ("greeting", "hello"),
    ("greeting2", "good morning"),
    ("question", "what is your name"),
    ("howareyou", "how are you"),
    ("feeling", "i am feeling sad today"),
    ("weather", "the weather is nice today"),
    ("thanks", "thank you very much"),
    ("request", "can you help me please"),
    ("unknown", "quantum entanglement explained"),
    ("empty", ""),
    ("punct", "really?!?! that is amazing!!!"),
    ("caps", "I AM VERY ANGRY RIGHT NOW"),
    ("math", "what is two plus two"),
    ("followup", "what about germany"),
]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--template", type=Path, required=True)
    parser.add_argument("--data", nargs="*", type=Path, default=None)
    parser.add_argument("--json", type=Path, default=None)
    parser.add_argument("--label", default="build")
    args = parser.parse_args()

    import builtins
    real_print = builtins.print
    builtins.print = lambda *a, **k: None
    try:
        harness.install_model(args.data)
    finally:
        builtins.print = real_print
    rt = harness.Runtime(harness.load_runtime(template=args.template, seed=12345))

    rows = []
    for name, prompt in SUITE:
        rt.reseed(12345)
        reply = rt.generate(prompt, [])
        row = {"name": name, "prompt": prompt, "reply": reply}
        row.update(quality_metrics.evaluate_reply(rt, prompt, reply))
        rows.append(row)
    summary = quality_metrics.aggregate(rows)
    print("== " + args.label + " ==")
    for row in rows:
        print(f"  [{row['name']}] {row['prompt']!r} -> {row['reply']!r}")
    print("  summary:", summary)
    if args.json:
        args.json.write_text(json.dumps(
            {"label": args.label, "quality": rows, "quality_summary": summary},
            indent=2))


if __name__ == "__main__":
    sys.exit(main())

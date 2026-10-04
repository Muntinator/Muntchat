"""Benchmark and response-quality evaluation for the calculator runtime.

Run with:  .venv-test/bin/python tests/evaluate.py [--json out.json]

It measures the hot inference loops (model load, ``step``, ``logits``,
``choose``, full ``generate``) and prints a fixed prompt suite so quality
changes can be compared before and after a modification.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import harness
import quality_metrics

# A fixed, reproducible prompt suite. Seeds are fixed so changes are comparable.
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


def timeit(fn, repeats: int = 1) -> float:
    best = float("inf")
    for _ in range(repeats):
        start = time.perf_counter()
        fn()
        best = min(best, time.perf_counter() - start)
    return best


def benchmark(rt, repeats: int = 5) -> dict:
    ns = rt.ns
    # Ensure weights are resident before measuring step/logits.
    ns["ensure_model"]([], 0)
    H = ns["H"]
    N = ns["N"]
    E = ns["E"]
    h = [0.1] * H
    results = {}
    results["step_ms"] = timeit(lambda: ns["step"](10, h), repeats) * 1000
    results["logits_ms"] = timeit(lambda: ns["logits"](h), repeats) * 1000
    rt.reseed(7)
    scores = ns["logits"](h)
    results["choose_ms"] = timeit(
        lambda: ns["choose"](scores, {}, {}, -1, -1, {}, {}, 0.5, 0, {}), repeats) * 1000

    def one_generate():
        rt.reseed(3)
        rt.generate("hello how are you", [])

    results["generate_ms"] = timeit(one_generate, repeats) * 1000
    results["config"] = {"E": E, "H": H, "N": N}
    return results


def quality(rt) -> list[dict]:
    rows = []
    for name, prompt in SUITE:
        rt.reseed(12345)
        start = time.perf_counter()
        reply = rt.generate(prompt, [])
        row = {
            "name": name,
            "prompt": prompt,
            "reply": reply,
            "seconds": round(time.perf_counter() - start, 4),
        }
        row.update(quality_metrics.evaluate_reply(rt, prompt, reply))
        rows.append(row)
    return rows


def conversation(rt) -> list[dict]:
    """Two-turn follow-ups: does the second reply stay on the first topic?"""
    turns = [
        ("followup_topic", "i like music", "what about you"),
        ("followup_time", "i am going to the park", "when"),
    ]
    rows = []
    for name, first, second in turns:
        rt.reseed(99)
        messages: list = []
        r1, _ = rt.ns["generate"](first, messages, 0)
        messages.append(("user", first))
        messages.append(("bot", r1))
        r2, _ = rt.ns["generate"](second, messages, 0)
        rows.append({"name": name, "first": first, "reply1": r1,
                     "second": second, "reply2": r2})
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", type=Path, default=None)
    parser.add_argument("--repeats", type=int, default=5)
    parser.add_argument("--label", default="current")
    args = parser.parse_args()

    rt = harness.build(quiet=True)
    results = {"label": args.label}
    results["benchmark"] = benchmark(rt, args.repeats)
    results["quality"] = quality(rt)
    results["quality_summary"] = quality_metrics.aggregate(results["quality"])
    results["conversation"] = conversation(rt)

    print("== benchmark (ms) ==")
    for key, value in results["benchmark"].items():
        print(f"  {key}: {value}")
    print("== quality ==")
    for row in results["quality"]:
        print(f"  [{row['name']}] {row['prompt']!r} -> {row['reply']!r}")
    print("== quality summary ==")
    print("  " + str(results["quality_summary"]))
    print("== two-turn conversation ==")
    for row in results["conversation"]:
        print(f"  [{row['name']}] {row['first']!r} -> {row['reply1']!r}")
        print(f"      then {row['second']!r} -> {row['reply2']!r}")
    if args.json:
        args.json.write_text(json.dumps(results, indent=2))
        print("wrote", args.json)


if __name__ == "__main__":
    sys.exit(main())

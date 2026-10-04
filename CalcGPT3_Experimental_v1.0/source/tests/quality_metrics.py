"""Objective, harness-computable quality metrics for generated replies.

These are proxies, not a claim of semantic understanding. They rank replies on
properties the project can actually measure on desktop: completeness,
repetition, topical overlap with the prompt's learned associations, and
unknown-word handling. They exist to catch regressions when the decoder or
model changes.
"""

from __future__ import annotations

CONTINUATION = {"a", "an", "the", "this", "that", "these", "those", "my", "your",
                "our", "his", "her", "their", "some", "any", "very", "too", "and",
                "or", "but", "to", "of", "in", "on", "at", "from", "with", "for",
                "by", "about"}


def _words(text: str) -> list[str]:
    out = []
    word = ""
    for ch in text.lower():
        if ch.isalpha() or ch.isdigit() or ch == "'":
            word += ch
        else:
            if word:
                out.append(word)
                word = ""
    if word:
        out.append(word)
    return out


def evaluate_reply(rt, prompt: str, reply: str) -> dict:
    ns = rt.ns
    words = _words(reply)
    prompt_ids = ns["tokenize"](prompt)
    content_prompt = [t for t in prompt_ids if t not in ns["PUNCT_IDS"]]
    oov = sum(1 for t in content_prompt if t == 1)
    oov_ratio = oov / len(content_prompt) if content_prompt else 0.0

    counts: dict[str, int] = {}
    for word in words:
        counts[word] = counts.get(word, 0) + 1
    repeated = sum(c - 1 for c in counts.values() if c > 1)
    repetition = repeated / len(words) if words else 1.0
    max_freq = max(counts.values()) if counts else 0

    try:
        bias, confidence = ns["understand"](prompt_ids, [])
    except TypeError:
        bias, confidence = ns["understand"](prompt_ids)
    bias_words = {ns["VOCAB"][t] for t in bias}
    relevant = sum(1 for word in words if word in bias_words)
    relevance = relevant / len(words) if words else 0.0

    ends_sentence = bool(reply) and reply[-1] in ".!?"
    dangling = bool(words) and words[-1] in CONTINUATION

    # Composite: topical overlap and completeness dominate; repetition penalized.
    composite = (0.35 * relevance + 0.20 * (1.0 - min(1.0, repetition))
                 + 0.20 * (1.0 if ends_sentence else 0.0)
                 + 0.15 * (1.0 if not dangling else 0.0)
                 + 0.10 * (0.0 if max_freq > 3 else 1.0))
    return {
        "words": len(words),
        "repetition": round(repetition, 3),
        "max_freq": max_freq,
        "relevance": round(relevance, 3),
        "ends_sentence": ends_sentence,
        "dangling": dangling,
        "oov_ratio": round(oov_ratio, 3),
        "composite": round(composite, 3),
    }


def aggregate(rows: list[dict]) -> dict:
    if not rows:
        return {}
    keys = ("repetition", "relevance", "oov_ratio", "composite")
    summary = {k: round(sum(r[k] for r in rows) / len(rows), 3) for k in keys}
    summary["complete_rate"] = round(
        sum(1 for r in rows if r["ends_sentence"]) / len(rows), 3)
    summary["dangling_rate"] = round(
        sum(1 for r in rows if r["dangling"]) / len(rows), 3)
    summary["count"] = len(rows)
    return summary

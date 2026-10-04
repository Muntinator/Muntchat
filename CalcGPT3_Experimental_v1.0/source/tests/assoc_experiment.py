"""Compare the legacy association builder with a contrastive (PMI) builder.

Both are scored on held-out prompt/reply pairs: for each held-out prompt, does
the reference reply's content token appear among the top-N associations the
builder produced for the prompt's features? This is non-circular (the held-out
pairs never contributed to the counts) and directly measures retrieval quality.
"""

from __future__ import annotations

import io
import math
import random
import sys
import urllib.request
import zipfile
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from train_mac import build_associations, tokenize  # noqa: E402

BIGRAM_BASE = 32768
PUNCT = {".", ",", "!", "?", ";", ":"}


def download_pairs():
    pairs = []
    urls = (
        "https://huggingface.co/datasets/roskoN/dailydialog/resolve/main/train.zip",
        "https://yanran.li/files/ijcnlp_dailydialog.zip",
    )
    data = None
    for url in urls:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "assoc-eval"})
            data = urllib.request.urlopen(req, timeout=90).read()
            break
        except Exception:
            continue
    if data is None:
        raise RuntimeError("could not download corpus")
    with zipfile.ZipFile(io.BytesIO(data)) as bundle:
        text_name = next(n for n in bundle.namelist()
                         if n.endswith(("dialogues_text.txt", "dialogues_train.txt")))
        act_name = next(n for n in bundle.namelist() if "dialogues_act" in n)
        emo_name = next(n for n in bundle.namelist() if "dialogues_emotion" in n)
        rows = bundle.read(text_name).decode("utf-8", "ignore").splitlines()
        acts = bundle.read(act_name).decode("utf-8", "ignore").splitlines()
        emos = bundle.read(emo_name).decode("utf-8", "ignore").splitlines()
    for row, act_row, emo_row in zip(rows, acts, emos):
        turns = [t.strip() for t in row.split("__eou__") if t.strip()]
        a = [int(x) for x in act_row.split()]
        e = [int(x) for x in emo_row.split()]
        for i in range(len(turns) - 1):
            pairs.append((turns[i], turns[i + 1], a[i] - 1, e[i]))
    return pairs


def build_pmi(pairs, lookup, max_reply=4, min_support=2, pmi_scale=3.0):
    feature_reply = defaultdict(Counter)
    feature_total = Counter()
    reply_total = Counter()
    keep = {}
    total_pairs = 0
    for user, assistant, act, emotion in pairs:
        utok = [lookup[w] for w in tokenize(user) if w in lookup and w not in PUNCT]
        rtok = [lookup[w] for w in tokenize(assistant) if w in lookup and w not in PUNCT]
        if not utok or not rtok:
            continue
        total_pairs += 1
        feats = list(dict.fromkeys(utok))
        for left, right in zip(utok, utok[1:]):
            feats.append(BIGRAM_BASE + ((left * 257 + right * 17) % BIGRAM_BASE))
        feats = list(dict.fromkeys(feats))
        for f in feats:
            feature_total[f] += 1
            for t in dict.fromkeys(rtok):
                feature_reply[f][t] += 1
                reply_total[t] += 1
    result = {}
    bigram_keys = []
    for feature, choices in feature_reply.items():
        if feature_total[feature] < min_support:
            continue
        best = []
        for token, count in choices.items():
            if count < 2:
                continue
            pmi = math.log((count + 0.5) * total_pairs
                           / (feature_total[feature] * (reply_total[token] + 0.5)))
            if pmi > 0:
                best.append((pmi, token))
        if not best:
            continue
        best.sort(reverse=True)
        top = best[:max_reply]
        keep[feature] = [(token, round(1.8 * min(1.0, pmi / pmi_scale), 3))
                         for pmi, token in top]
        if feature >= BIGRAM_BASE:
            bigram_keys.append(feature)
    bigram_keys.sort(key=lambda f: feature_total[f], reverse=True)
    allowed_bigrams = set(bigram_keys[:768])
    for feature, choices in keep.items():
        if feature < BIGRAM_BASE or feature in allowed_bigrams:
            result[feature] = choices
    return result


def topn_hit(assoc, pairs, lookup, topn=3):
    hits = 0
    total = 0
    for user, assistant, _, _ in pairs:
        utok = [lookup[w] for w in tokenize(user) if w in lookup and w not in PUNCT]
        rtok = [lookup[w] for w in tokenize(assistant) if w in lookup and w not in PUNCT]
        if not utok or not rtok:
            continue
        ref = set()
        for w in tokenize(assistant):
            if w in lookup and w not in PUNCT:
                ref.add(lookup[w])
        if not ref:
            continue
        combined = {}
        feats = list(dict.fromkeys(utok))
        for left, right in zip(utok, utok[1:]):
            feats.append(BIGRAM_BASE + ((left * 257 + right * 17) % BIGRAM_BASE))
        for feature in feats:
            for rank, (token, weight) in enumerate(assoc.get(feature, [])[:topn]):
                combined[token] = combined.get(token, 0.0) + weight / (rank + 1)
        if not combined:
            total += 1
            continue
        picks = sorted(combined, key=lambda t: combined[t], reverse=True)[:topn]
        total += 1
        if any(token in ref for token in picks):
            hits += 1
    return hits, total


def main():
    pairs = download_pairs()
    print("pairs", len(pairs))
    random.Random(7).shuffle(pairs)
    split = int(len(pairs) * 0.9)
    train_pairs, held = pairs[:split], pairs[split:]

    # Vocabulary must match the shipped checkpoint.
    import torch
    ckpt = Path(__file__).resolve().parent.parent / "checkpoints" / "calcgpt3.pt"
    saved = torch.load(ckpt, map_location="cpu", weights_only=False)
    vocab = saved["vocab"]
    lookup = {w: i for i, w in enumerate(vocab)}

    # Legacy builder works on the flat token stream.
    tokens = []
    for user, assistant, act, emotion in train_pairs:
        tokens.append("<user>")
        tokens.extend(tokenize(user)[:14])
        tokens.append("<assistant>")
        tokens.extend(tokenize(assistant)[:16])
        tokens.append("<eos>")
    legacy = build_associations(tokens, lookup)
    new = build_pmi(train_pairs, lookup)

    for name, assoc in (("legacy", legacy), ("pmi", new)):
        for topn in (3, 5):
            hits, total = topn_hit(assoc, held, lookup, topn)
            print(f"{name:6s} top{topn} hit-rate {hits}/{total} = {hits/total:.3f}"
                  f"  features={len(assoc)}")


if __name__ == "__main__":
    main()

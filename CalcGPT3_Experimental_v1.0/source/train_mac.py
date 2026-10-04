#!/usr/bin/env python3
"""Train/resume a compact GRU and export a dependency-free TI-Nspire app.

Improvements over the v1.0 trainer:

* deterministic seeding of ``random`` and ``torch`` (``--seed``);
* a held-out validation split so training loss is never mistaken for quality
  (``--validation-fraction``);
* richer checkpoint metadata stored next to the checkpoint (architecture,
  format, validation loss, corpus size);
* configurable checkpoint/data directories so experiments never clobber the
  shipped E40 checkpoint;
* ``--limit-batches`` for fast end-to-end smoke tests of the whole pipeline.

The calculator-side architecture and the format-13 data layout are unchanged.
"""
from __future__ import annotations

import argparse
import io
import json
import random
import re
import urllib.request
import zipfile
from collections import Counter, defaultdict
from pathlib import Path

import torch
from torch import nn
from torch.utils.data import DataLoader, Dataset

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
CHECKPOINT = ROOT / "checkpoints" / "calcgpt3.pt"
CONFIG = {"vocab_size": 640, "embedding": 20, "hidden": 30,
          "sequence": 36, "batch": 96, "format": 13}
BUILD = 2
ACT_TOKENS = ["<act_info>", "<act_question>", "<act_directive>", "<act_commitment>"]
EMOTION_TOKENS = ["<emo_calm>", "<emo_anger>", "<emo_disgust>",
                  "<emo_fear>", "<emo_happy>", "<emo_sad>", "<emo_surprise>"]
SPECIAL = (["<pad>", "<unk>", "<bos>", "<eos>", "<user>", "<assistant>"]
           + ACT_TOKENS + EMOTION_TOKENS)
DAILY_URLS = (
    "https://huggingface.co/datasets/roskoN/dailydialog/resolve/main/train.zip",
    "https://yanran.li/files/ijcnlp_dailydialog.zip",
)
PUNCTUATION = frozenset({".", ",", "!", "?", ";", ":"})


def download_daily_dialogue_tokens(data_dir: Path = DATA):
    """Download the cleaner DailyDialog corpus and preserve reply boundaries."""
    data_dir.mkdir(exist_ok=True)
    archive = data_dir / "ijcnlp_dailydialog.zip"
    if archive.exists():
        valid = zipfile.is_zipfile(archive)
        if valid:
            with zipfile.ZipFile(archive) as cached:
                names = cached.namelist()
                valid = (any(name.endswith(("dialogues_text.txt", "dialogues_train.txt"))
                             for name in names)
                         and any("dialogues_act" in name for name in names)
                         and any("dialogues_emotion" in name for name in names))
        if not valid:
            print("Discarding an incomplete previous corpus download")
            archive.unlink()
    if not archive.exists():
        print("Downloading clean DailyDialog training corpus")
        failure = None
        for url in DAILY_URLS:
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "TinyLM trainer"})
                data = urllib.request.urlopen(req, timeout=90).read()
                # Some retired dataset URLs return an HTML page with HTTP 200.
                # Validate the bytes before preserving them as the cache.
                with zipfile.ZipFile(io.BytesIO(data)) as candidate:
                    names = candidate.namelist()
                    if not any(name.endswith(("dialogues_text.txt", "dialogues_train.txt")) for name in names):
                        raise zipfile.BadZipFile("dialogue text is missing")
                    if not any("dialogues_act" in name for name in names):
                        raise zipfile.BadZipFile("dialogue-act labels are missing")
                    if not any("dialogues_emotion" in name for name in names):
                        raise zipfile.BadZipFile("emotion labels are missing")
                archive.write_bytes(data)
                failure = None
                break
            except Exception as exc:
                failure = exc
        if failure is not None:
            raise RuntimeError("Could not download the DailyDialog corpus: " + str(failure))
    with zipfile.ZipFile(archive) as bundle:
        name = next(name for name in bundle.namelist()
                    if name.endswith(("dialogues_text.txt", "dialogues_train.txt")))
        raw = bundle.read(name).decode("utf-8", errors="ignore")
        act_name = next(name for name in bundle.namelist() if "dialogues_act" in name)
        emotion_name = next(name for name in bundle.namelist() if "dialogues_emotion" in name)
        raw_acts = bundle.read(act_name).decode("utf-8", errors="ignore")
        raw_emotions = bundle.read(emotion_name).decode("utf-8", errors="ignore")
    pairs = []
    intent_examples = []
    emotion_examples = []
    rows = zip(raw.splitlines(), raw_acts.splitlines(), raw_emotions.splitlines())
    for row, act_row, emotion_row in rows:
        turns = [turn.strip() for turn in row.split("__eou__") if turn.strip()]
        acts = [int(value) for value in act_row.split()]
        emotions = [int(value) for value in emotion_row.split()]
        for turn, act in zip(turns, acts):
            intent_examples.append((turn, act - 1))
        for turn, emotion in zip(turns, emotions):
            emotion_examples.append((turn, emotion))
        for index in range(len(turns) - 1):
            pairs.append((turns[index], turns[index + 1], acts[index] - 1, emotions[index]))
    random.Random(2026).shuffle(pairs)
    tokens = []
    for user, assistant, act, emotion in pairs:
        tokens.append("<user>")
        tokens.extend(tokenize(user)[:14])
        tokens.append(ACT_TOKENS[max(0, min(3, act))])
        tokens.append(EMOTION_TOKENS[max(0, min(6, emotion))])
        tokens.append("<assistant>")
        tokens.extend(tokenize(assistant)[:16])
        tokens.append("<eos>")
    return tokens, intent_examples, emotion_examples


def build_intent_model(examples, lookup):
    """Learn compact word evidence for four DailyDialog dialogue acts."""
    counts = defaultdict(lambda: [1, 1, 1, 1])
    priors = [1, 1, 1, 1]
    for text, label in examples:
        if not 0 <= label < 4:
            continue
        priors[label] += 1
        for word in set(tokenize(text)):
            if word in lookup and word not in PUNCTUATION:
                counts[lookup[word]][label] += 1
    model = {}
    for token, values in counts.items():
        total = sum(values)
        if total >= 12:
            model[token] = [round(255 * value / total) for value in values]
    total = sum(priors)
    return model, [round(255 * value / total) for value in priors]


def build_emotion_model(examples, lookup):
    """Learn word evidence for all seven human-labelled DailyDialog emotions."""
    counts = defaultdict(lambda: [1] * 7)
    priors = [1] * 7
    for text, label in examples:
        if not 0 <= label < 7:
            continue
        priors[label] += 1
        for word in set(tokenize(text)):
            if word in lookup and word not in PUNCTUATION:
                counts[lookup[word]][label] += 1
    model = {}
    for token, values in counts.items():
        total = sum(values)
        if total >= 14:
            model[token] = [round(255 * value / total) for value in values]
    total = sum(priors)
    return model, [round(255 * value / total) for value in priors]


def tokenize(text: str) -> list[str]:
    text = re.sub(r"\*{3} START OF (?:THE|THIS) PROJECT GUTENBERG.*?\*{3}", " ", text,
                  flags=re.I | re.S)
    text = text.lower().replace("\u2019", "'")
    return re.findall(r"[a-z]+(?:'[a-z]+)?|[0-9]+|[.!?,;:]", text)


class Sequences(Dataset):
    def __init__(self, ids: list[int], length: int, assistant_id: int, eos_id: int):
        self.ids, self.length = ids, length
        active = False
        self.reply_mask = []
        for token in ids:
            if token == assistant_id:
                active = True
            self.reply_mask.append(1.0 if active and token != assistant_id else 0.0)
            if token == eos_id:
                active = False

    def __len__(self):
        return max(0, (len(self.ids) - self.length - 1) // self.length)

    def __getitem__(self, index):
        start = index * self.length
        chunk = self.ids[start:start + self.length + 1]
        mask = self.reply_mask[start + 1:start + self.length + 1]
        return torch.tensor(chunk[:-1]), torch.tensor(chunk[1:]), torch.tensor(mask)


class TinyGRU(nn.Module):
    def __init__(self, vocab: int, embedding: int, hidden: int):
        super().__init__()
        self.embed = nn.Embedding(vocab, embedding)
        self.gru = nn.GRU(embedding, hidden, batch_first=True)
        self.output = nn.Linear(hidden, vocab)

    def forward(self, x, state=None):
        y, state = self.gru(self.embed(x), state)
        return self.output(y), state


def build_vocab(tokens: list[str]) -> list[str]:
    punctuation = PUNCTUATION
    prompt_counter = Counter()
    in_prompt = False
    for token in tokens:
        if token == "<user>":
            in_prompt = True
        elif token in ("<assistant>", "<eos>"):
            in_prompt = False
        elif in_prompt and token not in SPECIAL and token not in punctuation:
            prompt_counter[token] += 1
    capacity = CONFIG["vocab_size"] - len(SPECIAL)
    prompt_capacity = capacity // 2
    selected = [word for word, _ in prompt_counter.most_common(prompt_capacity)]
    selected_set = set(selected)
    for word, _ in Counter(tokens).most_common():
        if word not in SPECIAL and word not in selected_set:
            selected.append(word)
            selected_set.add(word)
            if len(selected) >= capacity:
                break
    return SPECIAL + selected


def build_associations(tokens: list[str], lookup: dict[str, int]):
    """Learn compact ordered prompt features -> likely response content.

    Note: a contrastive PMI/TF-IDF variant was benchmarked and reduced held-out
    top-3 retrieval from 0.393 to 0.112, so the frequency-weighted scheme is
    retained deliberately (see tests/assoc_experiment.py)."""
    counts = defaultdict(Counter)
    i = 0
    while i < len(tokens):
        if tokens[i] != "<user>":
            i += 1
            continue
        i += 1
        user = []
        while i < len(tokens) and tokens[i] != "<assistant>":
            if tokens[i] in lookup and tokens[i] not in PUNCTUATION and tokens[i] not in SPECIAL:
                user.append(lookup[tokens[i]])
            i += 1
        i += 1
        reply = []
        while i < len(tokens) and tokens[i] != "<eos>":
            if tokens[i] in lookup and tokens[i] not in PUNCTUATION:
                reply.append(lookup[tokens[i]])
            i += 1
        weak = {lookup[word] for word in ("i", "you", "he", "she", "we", "they", "the", "a", "an",
                "is", "are", "was", "were", "be", "to", "of", "and", "or", "but") if word in lookup}
        reply_top = [token for token, _ in Counter(token for token in reply if token not in weak).most_common(8)]
        features = list(set(user))[:14]
        for left, right in zip(user, user[1:]):
            features.append(32768 + ((left * 257 + right * 17) % 32768))
        for prompt_token in list(dict.fromkeys(features))[:24]:
            for response_token in reply_top:
                counts[prompt_token][response_token] += 1
    result = {}
    unigram_keys = [key for key in counts if key < 32768]
    bigram_keys = [key for key in counts if key >= 32768]
    bigram_keys.sort(key=lambda key: sum(counts[key].values()), reverse=True)
    for prompt_token in unigram_keys + bigram_keys[:512]:
        choices = counts[prompt_token]
        best = choices.most_common(3)
        if best:
            maximum = best[0][1]
            result[prompt_token] = [(token, round(1.8 * count / maximum, 3))
                                    for token, count in best]
    return result


@torch.no_grad()
def validation_loss(model, loader, loss_fn, vocab_size, device) -> float:
    model.eval()
    total = 0.0
    weight = 0.0
    for x, y, mask in loader:
        x, y, mask = x.to(device), y.to(device), mask.to(device)
        logits, _ = model(x)
        raw = loss_fn(logits.reshape(-1, vocab_size), y.reshape(-1))
        flat = mask.reshape(-1)
        total += (raw * flat).sum().item()
        weight += flat.sum().item()
    model.train()
    return total / max(1.0, weight)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--epochs", type=int, help="additional training epochs")
    parser.add_argument("--reset", action="store_true", help="discard the Mac checkpoint")
    parser.add_argument("--checkpoint", type=Path, default=CHECKPOINT)
    parser.add_argument("--data-dir", type=Path, default=DATA)
    parser.add_argument("--seed", type=int, default=2026)
    parser.add_argument("--validation-fraction", type=float, default=0.05)
    parser.add_argument("--limit-batches", type=int, default=0,
                        help="cap batches per epoch (0 = all); for smoke tests")
    parser.add_argument("--no-export", action="store_true")
    args = parser.parse_args()

    random.seed(args.seed)
    torch.manual_seed(args.seed)
    checkpoint = args.checkpoint

    if args.reset and checkpoint.exists():
        checkpoint.unlink()
    epochs = args.epochs
    if epochs is None:
        epochs = int(input("How many additional Mac training epochs? [20]: ") or "20")
    if not 1 <= epochs <= 100:
        raise SystemExit("Epochs must be from 1 through 100.")

    # DailyDialog is cleaner and more coherent than movie scripts. The new
    # format intentionally does not resume the older cinematic/book model.
    tokens, intent_examples, emotion_examples = download_daily_dialogue_tokens(args.data_dir)
    if checkpoint.exists():
        saved = torch.load(checkpoint, map_location="cpu", weights_only=False)
        if saved.get("config") == CONFIG:
            vocab = saved["vocab"]
            completed = saved["epochs"]
            print("Resuming compatible checkpoint at epoch", completed)
        else:
            print("Old checkpoint architecture is incompatible; starting the dialogue model fresh.")
            saved, completed = None, 0
            vocab = build_vocab(tokens)
    else:
        vocab = build_vocab(tokens)
        saved, completed = None, 0
    lookup = {word: i for i, word in enumerate(vocab)}
    associations = build_associations(tokens, lookup)
    intent_model, intent_priors = build_intent_model(intent_examples, lookup)
    emotion_model, emotion_priors = build_emotion_model(emotion_examples, lookup)
    ids = [lookup.get(word, 1) for word in tokens]

    # Held-out split so validation loss is reported alongside training loss.
    val_size = max(1, int(len(ids) * args.validation_fraction))
    train_ids = ids[:-val_size]
    val_ids = ids[-val_size:]
    dataset = Sequences(train_ids, CONFIG["sequence"], lookup["<assistant>"], lookup["<eos>"])
    val_dataset = Sequences(val_ids, CONFIG["sequence"], lookup["<assistant>"], lookup["<eos>"])
    loader = DataLoader(dataset, batch_size=CONFIG["batch"], shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=CONFIG["batch"])
    device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
    model = TinyGRU(len(vocab), CONFIG["embedding"], CONFIG["hidden"]).to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=0.0025, weight_decay=0.01)
    if saved:
        model.load_state_dict(saved["model"])
        optimizer.load_state_dict(saved["optimizer"])
    loss_fn = nn.CrossEntropyLoss(reduction="none")
    print(f"Tokens: {len(ids):,} | vocabulary: {len(vocab)} | device: {device}")
    print(f"Train sequences: {len(dataset):,} | validation sequences: {len(val_dataset):,}")
    model.train()
    last_val = None
    for local_epoch in range(epochs):
        total_loss = 0.0
        batches = 0
        for batch, (x, y, mask) in enumerate(loader, 1):
            x, y, mask = x.to(device), y.to(device), mask.to(device)
            optimizer.zero_grad(set_to_none=True)
            logits, _ = model(x)
            raw_loss = loss_fn(logits.reshape(-1, len(vocab)), y.reshape(-1))
            flat_mask = mask.reshape(-1)
            loss = (raw_loss * flat_mask).sum() / flat_mask.sum().clamp_min(1.0)
            loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            total_loss += loss.item()
            batches = batch
            if batch % 100 == 0:
                print(f"epoch {completed + local_epoch + 1} batch {batch}/{len(loader)} "
                      f"loss {total_loss / batch:.3f}")
            if args.limit_batches and batch >= args.limit_batches:
                break
        last_val = validation_loss(model, val_loader, loss_fn, len(vocab), device)
        print(f"Epoch {completed + local_epoch + 1}: "
              f"train loss {total_loss / max(1, batches):.3f} | val loss {last_val:.3f}")
        # Preserve an independently restorable snapshot after every epoch.
        history = checkpoint.parent / "history"
        history.mkdir(parents=True, exist_ok=True)
        epoch_number = completed + local_epoch + 1
        snapshot = {"model": model.to("cpu").state_dict(),
                    "optimizer": optimizer.state_dict(), "vocab": vocab,
                    "config": CONFIG, "epochs": epoch_number,
                    "validation_loss": last_val,
                    "associations": associations, "intent_model": intent_model,
                    "intent_priors": intent_priors, "emotion_model": emotion_model,
                    "emotion_priors": emotion_priors}
        torch.save(snapshot, history / f"calcgpt3_epoch_{epoch_number:03d}.pt")
        model.to(device)
    completed += epochs
    checkpoint.parent.mkdir(exist_ok=True)
    payload = {"model": model.to("cpu").state_dict(), "optimizer": optimizer.state_dict(),
               "vocab": vocab, "config": CONFIG, "epochs": completed,
               "validation_loss": last_val,
               "associations": associations, "intent_model": intent_model,
               "intent_priors": intent_priors, "emotion_model": emotion_model,
               "emotion_priors": emotion_priors}
    torch.save(payload, checkpoint)
    checkpoint.with_suffix(".json").write_text(json.dumps({
        "epochs": completed, "build": BUILD, "validation_loss": last_val,
        "train_tokens": len(train_ids), "validation_tokens": val_size,
        **CONFIG}, indent=2))
    if args.no_export:
        print("Skipping export (--no-export).")
        return
    from export_calculator import export
    output = export(checkpoint)
    print("Exported calculator app:", output)


if __name__ == "__main__":
    main()

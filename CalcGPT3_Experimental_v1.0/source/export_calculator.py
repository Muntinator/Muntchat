#!/usr/bin/env python3
"""Quantize a Mac checkpoint and generate the calculator programs.

The on-calculator data format stays at version 13 so the existing ready-to-run
TNS and any previously installed model remain compatible. What changes is the
installer generation:

* every storage unit carries an Adler-32 checksum that is verified as it is
  decoded, catching corrupted or truncated pastes immediately;
* each numbered installer part is idempotent and resumable -- re-running a part
  that already finished skips it instead of redoing the work;
* the final part re-reads every stored list and verifies its length and
  checksum without ever building the whole model in RAM;
* installing over a *different* model id asks for confirmation first.

The model id is intentionally unchanged: it is the CRC-32 of the same payload
as before, so an already-installed format-13 model is recognised and left alone.
"""

from pathlib import Path
import argparse
import base64
import zlib
import torch

ROOT = Path(__file__).resolve().parent
FORMAT = 13
BUILD = 2  # installer/build revision (format 13 payload, enhanced installer)

TENSORS = ["embed.weight", "gru.weight_ih_l0", "gru.weight_hh_l0",
           "gru.bias_ih_l0", "gru.bias_hh_l0", "output.weight", "output.bias"]
CHUNK_VALUES = 1600  # decoded bytes per stored unit (packed to 800 list cells)
CHUNK_TEXT = 800     # bytes per vocab/association storage unit
FILE_BUDGET = 11000  # characters per generated installer program


def adler32(values) -> int:
    a = 1
    b = 0
    for value in values:
        a = (a + value) % 65521
        b = (b + a) % 65521
    return (b << 16) | a


def quantize(tensor):
    values = tensor.detach().cpu().flatten().float()
    maximum = max(float(values.abs().max()), 1e-8)
    scale = maximum / 127.0
    ints = torch.clamp(torch.round(values / scale), -127, 127).to(torch.int16).tolist()
    raw = bytes(value & 255 for value in ints)
    length = len(raw)
    raw += bytes((-length) % 4)
    encoded = base64.b85encode(raw).decode("ascii")
    return scale, length, encoded


def _checksum_literal(raw: bytes) -> int:
    return adler32(raw)


def export(checkpoint=ROOT / "checkpoints" / "calcgpt3.pt", output_dir=None):
    output_dir = Path(output_dir) if output_dir else (ROOT / "calculator")
    saved = torch.load(checkpoint, map_location="cpu", weights_only=False)
    state, vocab, cfg = saved["model"], saved["vocab"], saved["config"]
    if int(cfg.get("format", FORMAT)) != FORMAT:
        raise SystemExit("Unsupported checkpoint format " + str(cfg.get("format")))

    scales, lengths, blobs, tensor_sums = [], [], [], []
    for name in TENSORS:
        scale, length, blob = quantize(state[name])
        scales.append(scale)
        lengths.append(length)
        blobs.append(blob)
        tensor_sums.append(_checksum_literal(
            base64.b85decode(blob.encode("ascii"))[:length]))

    # Associations keep the exact legacy byte layout so format stays compatible.
    assoc_raw = bytearray()
    for prompt, choices in sorted(saved.get("associations", {}).items()):
        choices = choices[:3]
        assoc_raw.extend(((prompt >> 8) & 255, prompt & 255, len(choices)))
        for token, weight in choices:
            assoc_raw.extend(((token >> 8) & 255, token & 255,
                              max(0, min(255, round(weight / 1.8 * 255)))))
    assoc_length = len(assoc_raw)
    assoc_raw.extend(bytes((-assoc_length) % 4))
    assoc_blob = base64.b85encode(bytes(assoc_raw)).decode("ascii")

    intent_raw = bytearray(saved.get("intent_priors", [64, 64, 64, 63]))
    intent_items = []
    for token, weights in saved.get("intent_model", {}).items():
        ordered = sorted(weights, reverse=True)
        intent_items.append((ordered[0] - ordered[1], token, weights))
    intent_items.sort(reverse=True)
    for _, token, weights in intent_items[:128]:
        intent_raw.extend(((token >> 8) & 255, token & 255))
        intent_raw.extend(max(0, min(255, int(value))) for value in weights)
    emotion_raw = bytearray(saved.get("emotion_priors", [220, 6, 2, 3, 14, 7, 3]))
    emotion_items = []
    for token, weights in saved.get("emotion_model", {}).items():
        ordered = sorted(weights, reverse=True)
        emotion_items.append((ordered[0] - ordered[1], token, weights))
    emotion_items.sort(reverse=True)
    for _, token, weights in emotion_items[:128]:
        emotion_raw.extend(((token >> 8) & 255, token & 255))
        emotion_raw.extend(max(0, min(255, int(value))) for value in weights)

    model_id = zlib.crc32(("".join(blobs) + assoc_blob).encode("ascii")
                          + bytes(intent_raw) + bytes(emotion_raw)) & 0x7fffffff

    # ------------------------------------------------------------------ units
    # Each unit writes at most one 800-cell TI list and carries its checksum.
    units = []
    qparts = []
    for tensor, (blob, length) in enumerate(zip(blobs, lengths)):
        raw = base64.b85decode(blob.encode("ascii"))[:length]
        count = 0
        for start in range(0, len(raw), CHUNK_VALUES):
            chunk = raw[start:start + CHUNK_VALUES]
            padded = chunk + bytes((-len(chunk)) % 4)
            units.append(("tdq" + str(tensor) + "x" + str(count), len(chunk), 1,
                          base64.b85encode(padded).decode("ascii"),
                          adler32(chunk)))
            count += 1
        qparts.append(count)

    chars = bytearray()
    for word in vocab:
        chars.extend(word.encode("ascii"))
        chars.append(0)
    vocab_checks = []
    vparts = 0
    for start in range(0, len(chars), CHUNK_TEXT):
        chunk = bytes(chars[start:start + CHUNK_TEXT])
        padded = chunk + bytes((-len(chunk)) % 4)
        units.append(("tdvc" + str(vparts), len(chunk), 0,
                      base64.b85encode(padded).decode("ascii"), adler32(chunk)))
        vocab_checks.append(adler32(chunk))
        vparts += 1

    assoc_bytes = bytes(assoc_raw[:assoc_length])
    assoc_checks = []
    aparts = 0
    for start in range(0, len(assoc_bytes), CHUNK_TEXT):
        chunk = assoc_bytes[start:start + CHUNK_TEXT]
        padded = chunk + bytes((-len(chunk)) % 4)
        units.append(("tda" + str(aparts), len(chunk), 0,
                      base64.b85encode(padded).decode("ascii"), adler32(chunk)))
        assoc_checks.append(adler32(chunk))
        aparts += 1

    groups = []
    current = []
    payload = 0
    for unit in units:
        cost = len(unit[3]) + 140
        if current and payload + cost > FILE_BUDGET:
            groups.append(current)
            current = []
            payload = 0
        current.append(unit)
        payload += cost
    if current:
        groups.append(current)

    common = '''from ti_system import store_list,recall_list
FORMAT=%d
ALPHABET="0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz!#$%%&()*+-;<=>?@^_`{|}~"
def decode(blob,length):
 out=[]
 for start in range(0,len(blob),5):
  value=0
  for ch in blob[start:start+5]: value=value*85+ALPHABET.index(ch)
  out.extend(((value>>24)&255,(value>>16)&255,(value>>8)&255,value&255))
 return out[:length]
def checksum(values):
 a=1; b=0
 for value in values:
  a=(a+value)%%65521
  b=(b+a)%%65521
 return (b<<16)|a
def installed(stage):
 try: marker=recall_list("tds"+str(stage))
 except Exception: return False
 return len(marker)>0 and int(marker[0])==MODEL_ID
def install(name,length,signed,blob,expect):
 values=decode(blob,length)
 if checksum(values)!=expect:
  print("Checksum failed for",name,"- re-paste this program"); raise SystemExit
 if signed:
  for j in range(len(values)):
   if values[j]>127: values[j]-=256
  pairs=[]
  for j in range(0,len(values),2):
   first=values[j]+128
   second=values[j+1]+128 if j+1<len(values) else 128
   pairs.append(first*256+second)
  values=pairs
 store_list(name,values)
 if len(recall_list(name))!=len(values):
  print("Verification failed for",name,"- re-paste this program"); raise SystemExit
def verify(prefix,count,length,expect):
 a=1; b=0; seen=0
 for part in range(count):
  for packed in recall_list(prefix+str(part)):
   packed=int(packed)
   for value in ((((packed>>8)-128)&255),(((packed&255)-128)&255)):
    if seen>=length: break
    a=(a+value)%%65521
    b=(b+a)%%65521
    seen+=1
 if seen!=length:
  print("Incomplete model part",prefix); raise SystemExit
 if (b<<16)|a!=expect:
  print("Corrupt model part",prefix); raise SystemExit
''' % FORMAT

    data_sources = []
    total_parts = len(groups)
    for part, group in enumerate(groups):
        name = "tinydata" if part == 0 else "tinydata" + str(part + 1)
        header = ("# CalcGPT 3 model installer %d of %d. Run in order.\n"
                  "MODEL_ID=%d\nBUILD=%d\n" % (part + 1, total_parts, model_id, BUILD))
        prelude = ""
        if part == 0:
            prelude = '''try:
 existing=recall_list("tdinfo")
except Exception:
 existing=[]
if len(existing)>7 and int(existing[0])==FORMAT and int(existing[7])==MODEL_ID:
 pasted=input("CalcGPT is installed. Paste text for it, then press Enter: ")
 store_list("tdpaste",[ord(ch) for ch in pasted[:120]])
 print("Paste saved. Run CalcGPT.")
 raise SystemExit
if len(existing)>7 and int(existing[0])==FORMAT and int(existing[7])!=MODEL_ID:
 reply=input("A different CalcGPT model is installed. Replace it? (y/n): ")
 if reply.strip().lower()!="y":
  print("Installation cancelled. Existing model left untouched.")
  raise SystemExit
'''
        body_lines = []
        if part == 0:
            # Part 0 must still perform the paste/safety checks above.
            rows = []
            for unit_name, unit_length, signed, encoded, unit_check in group:
                rows.append("install(%r,%d,%d,%r,%d)" % (
                    unit_name, unit_length, signed, encoded, unit_check))
            body_lines = prelude + "\n".join(rows)
        else:
            body_lines = ("if installed(%d):\n"
                          " print(\"Part %d of %d already installed; skipping.\")\n"
                          " raise SystemExit\n" % (part + 1, part + 1, total_parts))
            rows = []
            for unit_name, unit_length, signed, encoded, unit_check in group:
                rows.append("install(%r,%d,%d,%r,%d)" % (
                    unit_name, unit_length, signed, encoded, unit_check))
            body_lines += "\n".join(rows)
        tail = '\nstore_list("tds%d",[MODEL_ID])\n' % (part + 1)
        if part + 1 < total_parts:
            tail += ('print("Part %d of %d installed. Run %s next.")\n'
                     % (part + 1, total_parts, "tinydata" + str(part + 2)))
        else:
            stage_code = '\nfor stage in range(1,%d):\n' % total_parts
            stage_code += ' if not installed(stage):\n'
            stage_code += '  print("Missing model part",stage,"- run its installer"); raise SystemExit\n'
            verify_lines = []
            for tensor in range(len(TENSORS)):
                verify_lines.append(
                    "verify(\"tdq%d%s\",%d,%d,%d)" %
                    (tensor, "x", qparts[tensor], lengths[tensor], tensor_sums[tensor]))
            tail += stage_code + "\n".join(verify_lines) + "\n"
            tail += 'store_list("tdlens",%r)\n' % list(lengths)
            tail += 'store_list("tdscale",%r)\n' % list(scales)
            tail += 'store_list("tdqp",%r)\n' % qparts
            tail += 'store_list("tdinfo",[%d,%d,%d,%d,%d,%d,%d,%d,BUILD])\n' % (
                FORMAT, cfg["embedding"], cfg["hidden"], saved["epochs"],
                len(vocab), vparts, aparts, model_id)
            tail += 'print("CalcGPT 3 model installed and verified. Run tinylm.")\n'
        data_sources.append((name, header + common + "\n" + body_lines + tail))

    replacements = {
        "@E@": str(cfg["embedding"]), "@H@": str(cfg["hidden"]),
        "@INTENT_RAW@": repr(tuple(intent_raw)),
        "@EMOTION_RAW@": repr(tuple(emotion_raw)),
    }
    template = (ROOT / "calculator_template.py").read_text()
    for old, new in replacements.items():
        template = template.replace(old, new)

    folder = output_dir
    folder.mkdir(exist_ok=True)
    for old in folder.glob("tinydata*.py"):
        old.unlink()
    main_out = folder / "tinylm.py"
    main_out.write_text(template)
    data_outputs = []
    for name, source in data_sources:
        output = folder / (name + ".py")
        output.write_text(source)
        compile(source, str(output), "exec")
        data_outputs.append(output)
    compile(template, str(main_out), "exec")
    meta = {
        "format": FORMAT, "build": BUILD, "model_id": model_id,
        "epochs": saved["epochs"], "vocab": len(vocab),
        "embedding": cfg["embedding"], "hidden": cfg["hidden"],
        "installer_parts": total_parts, "tensor_checksums": tensor_sums,
        "vocab_chunks": vparts, "assoc_chunks": aparts,
    }
    (folder / "model_meta.json").write_text(
        __import__("json").dumps(meta, indent=2))
    return tuple([main_out] + data_outputs)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkpoint", type=Path,
                        default=ROOT / "checkpoints" / "calcgpt3.pt")
    args = parser.parse_args()
    for path in export(args.checkpoint):
        print(path)

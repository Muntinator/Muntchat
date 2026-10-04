CalcGPT 3.1 — ready-to-run TI-Nspire problem

Author: Fred Bennett
Runtime and tooling revision: CalcGPT 3.1 (E40 weights, unchanged)

## Download

`CalcGPT3_v3.1.tns` (179,094 bytes, sha256 `88a53099d632226f32e11bee86bc6f2722b723699e9fa761239b98efbcb485ba`)

Transfer it with TI-Nspire CX Student Software, open it on a TI-Nspire CX II,
open the `tinylm` Python page and press Ctrl+R. The E40 model is already installed
in the document, so there is nothing to paste.

## What this is

An experimental word-level neural language model that runs entirely in standard
TI-Nspire Python. No Ndless, no internet, no API, no third-party calculator-side
libraries. A 640-token, 30-state GRU trained on DailyDialog, exported as signed
8-bit weights and interpreted by a dependency-free inference engine written in
Python.

**It is a research demonstration, not an assistant.** It does not have reliable
semantic understanding. It frequently produces locally plausible English that does
not answer the prompt, and it has no hardcoded answer skills, so arithmetic,
factual and procedural questions are not answered correctly. The percentage in the
header is dialogue-act/emotion classifier separation, not answer accuracy.

The 3.1 release changes the runtime, decoder, installer and tooling. The model
weights are unchanged from 1.0, the on-calculator data format stays at 13, and the
model id stays at 1282619148, so version 1.0 installs keep working.

## Changes

Runtime — roughly 2x faster inference from inlining the packed-byte decode into
the GRU and output-projection loops and caching the dequantized biases. The
optimized math is verified numerically identical to the original (max abs
difference ~1e-15). Plus exact three-token repetition suppression, a frequency
penalty, an adaptive second candidate that only runs when the first reply fails an
absolute quality gate, a bounded rolling conversation context so short follow-ups
carry the previous turn's content words, and Ctrl+N (clear), Ctrl+R (regenerate),
Ctrl+T (temperature), Ctrl+L (response length) with a temperature readout in the
status bar.

Installer — every generated unit now carries an Adler-32 checksum verified as it is
decoded, with read-back length checks and a full re-verify of all stored weights in
the final part. Numbered parts are idempotent so an interrupted install resumes part
by part. Installing over a different model id asks first. Fixed a signed-offset
bug that made every export fail its own verification.

Trainer — held-out validation split with validation loss, deterministic seeding,
and `--checkpoint` / `--data-dir` / `--limit-batches` / `--no-export`.

Document — `source/build_tns.py` builds the ready-to-run problem by replacing only
the plain-text Python pages and copying TI's encrypted document XML byte-for-byte,
so the installed model data cannot be corrupted. `source/tests/verify_tns.py`
decodes the built document, recovers the model stored inside it, and runs the
runtime page the document actually ships against that data.

## Measurements

Desktop harness (CPython 3.10, torch CPU), per-call milliseconds:

    step                    1.580 -> 0.753   (2.10x)
    logits                  6.545 -> 3.267   (2.00x)
    choose                  1.087 -> 0.875   (1.24x)
    generate (full reply) 233.1  -> 118.8    (1.96x)

Fixed 14-prompt suite, same seeds, proxy metrics:

    composite     0.705 -> 0.720
    relevance     0.355 -> 0.390
    repetition    0.202 -> 0.189  (lower is better)
    complete      1.000 -> 1.000
    dangling      0.000 -> 0.000

These are desktop proxies, not a claim of semantic understanding. The quality
deltas are small; the clear win is the ~2x speedup without a quality regression.

A contrastive PMI/TF-IDF association builder and larger association tables were
both implemented, measured, and rejected. See `MODIFICATIONS.txt` section 6.

## Not verified

This release was developed and verified on the desktop against a simulated
`ti_system`/`ti_draw`. It was **not** run on a TI-Nspire or opened in TI-Nspire
Student Software, because no hardware was available. Still open: on-device launch
and response timings, peak document size and MemoryError behaviour, the physical
key names for Ctrl+N/R/T/L, `ti_draw` rendering of the status bar, the Shell
paste-helper workflow, and the TI editor paste-size limit. See
`KNOWN_ISSUES.txt` sections 16 and 17.

Please report what you find on real hardware, including timings.

## Tests

51 desktop tests run the real calculator code headlessly:

    cd source
    python3 -m venv .venv-test
    .venv-test/bin/python -m pip install -r requirements.txt
    .venv-test/bin/python -m unittest discover -s tests

## Licensing

Project code is MIT (`LICENSE_CODE.txt`). The model was trained on DailyDialog;
see `MODEL_LICENSE_AND_ATTRIBUTION.txt` for dataset terms (noncommercial,
share-alike). Not affiliated with Texas Instruments, OpenAI, or the DailyDialog
authors. "GPT" in the project name is descriptive branding: this is a GRU language
model, not an OpenAI GPT model.

Full change list with measurements: `MODIFICATIONS.txt`.
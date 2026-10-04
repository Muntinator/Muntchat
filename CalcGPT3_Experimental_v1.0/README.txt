CalcGPT 3 - Experimental Offline Neural Language Model for TI-Nspire CX II
Version 3.1 (E40 weights, improved runtime and tooling)
Author and primary tester: Fred Bennett
Runtime and tooling revision: CalcGPT 3.1

OVERVIEW
========

CalcGPT 3 is an experimental word-level neural language model that runs entirely
inside standard TI-Nspire Python. It does not use Ndless, internet access, an API,
or calculator-side third-party libraries. The model is trained on a Mac, exported
with signed 8-bit weights, stored in a TI-Nspire problem, and evaluated by a custom
GRU inference engine written in Python.

This release is a research and development starting point. It proves that a genuine
quantized neural text generator can run on a stock TI-Nspire CX II, but it does NOT
provide reliable language understanding. Typical failures include repeated
high-frequency phrases, weak prompt relevance, contradictions, incomplete grammar,
and confident-sounding nonsense. The header percentage is classifier separation
confidence, not answer accuracy.

WHAT IS NEW IN 3.1
==================

The version-1.0 model weights (E40) are unchanged; 3.1 improves the runtime, the
decoder, the installer, the tooling, and the documentation. The on-calculator data
format stays at version 13 and the model id is unchanged, so the existing
ready-to-run TNS and any previously installed model keep working.

- Roughly 2x faster inference (see MEASUREMENTS) from inlining the packed-byte
  decode into the GRU and output-projection loops and caching the small bias
  vectors. The optimized math is verified identical to the original implementation.
- A smarter decoder: exact three-token repetition suppression, a running frequency
  penalty, and an adaptive second candidate that only runs when the first reply
  fails an absolute quality gate. Benchmarking showed adaptive selection is both
  faster and slightly higher quality than always generating two candidates.
- Compact rolling conversation context: a short follow-up such as "what about
  Germany?" now carries the previous turn's content words into association lookup
  and dialogue-act/emotion classification, at reduced weight.
- Rewritten model installer: numbered parts carry an Adler-32 checksum that is
  verified as each unit is decoded, each numbered part is resumable/idempotent, the
  final part re-reads and verifies every stored weight, and installing over a
  different model id asks for confirmation first.
- New runtime controls: Ctrl+N clears the conversation, Ctrl+R regenerates the last
  reply, Ctrl+T cycles temperature, Ctrl+L cycles response length. The status bar
  shows the active temperature.
- A rebuilt ready-to-run problem, ready_to_run/CalcGPT3_v3.1.tns. The tool that
  produces it (source/build_tns.py) replaces only the plain-text Python pages and
  copies TI's encrypted document XML byte-for-byte, so the model data already
  installed in the document is preserved exactly. source/tests/verify_tns.py then
  decodes that document, recovers the stored model, and runs the runtime page the
  document actually ships.
- Training and testing tooling: validation split and loss reporting, deterministic
  seeding, configurable checkpoint paths, a desktop harness that runs the real
  calculator code, a 51-test unittest suite, and reproducible quality/benchmark
  scripts.

TESTED PERFORMANCE (version 1.0 baseline, unchanged hardware)
=============================================================

Hardware/software: TI-Nspire CX II using standard TI Python
Document size: approximately 175 KB (CalcGPT3_v3.1.tns is 179,094 bytes)
Ctrl+R to interface: approximately 40 seconds
First model load: approximately 30 seconds
Typical generated response: approximately 20 seconds
Later responses avoid the model-loading step until the app is exited.

Version 3.1 roughly halves per-response CPU work, so a typical response should
take noticeably less than 20 seconds on the same hardware. Absolute times must be
re-measured on a real calculator; see "Not verifiable without hardware".

MODEL
=====

- Architecture: single-layer word-level GRU
- Vocabulary: 640 tokens
- Embedding width: 20
- Hidden width: 30
- Training corpus: DailyDialog
- Training release: 40 epochs
- Quantization: signed 8-bit weights
- Output: adaptive one-or-two sampled candidates with relevance/grammar ranking
- Conditioning: dialogue act, emotion, capitalization, repeated punctuation,
  hesitation signals, unigram associations, ordered bigram associations, and a
  bounded rolling conversation context
- Calculator inference: dependency-free TI Python

QUICK START
===========

1. Transfer ready_to_run/CalcGPT3_v3.1.tns with TI-Nspire CX Student Software.
2. Open the document on a TI-Nspire CX II.
3. Open the tinylm Python page and press Ctrl+R.
4. Wait for the interface. The first response in each run loads the model.

ready_to_run/CalcGPT3_v3.1.tns is the version-3.1 document: the 3.1 runtime
embedded in the original E40 problem, with the E40 model already installed. The
older ready_to_run/CalcGPT3.tns is kept unchanged for comparison.

The document already contains the calculator programs and installed model
variables, so nothing needs pasting. To upgrade an existing installation instead,
replace only the tinylm page with source/calculator/tinylm.py (see UPGRADING); the
installed model data is compatible and does not need reinstalling.

CONTROLS
========

- Enter: send a message, including an empty message
- Up/Down: scroll by line
- Left/Right: scroll by page
- Shift: change the next letter's case
- Caps: toggle uppercase input where supported
- Var: enter a question mark
- Trig: enter an exclamation mark
- Ctrl+N: clear the conversation
- Ctrl+R: regenerate the last reply
- Ctrl+T: cycle temperature (0.25, 0.42, 0.60, 0.80)
- Ctrl+L: cycle response length (x0.7, x1.0, x1.3)
- Tab: show the calculator-safe paste instructions
- Menu: make the latest response available in the Shell after exit
- Esc: exit

TRAIN OR RESUME ON macOS
========================

Requirements:

- macOS on Apple Silicon or Intel
- Python 3
- Internet access on the first run to download dependencies and DailyDialog
- Approximately 1 GB free while installing PyTorch and its environment

The included source/checkpoints/calcgpt3.pt is the E40 checkpoint. It allows
developers to resume training without repeating the first 40 epochs.

Open Terminal and run:

  cd path/to/CalcGPT3_Experimental_v1.0/source
  python3 install_train_calc.py
  source ~/.zshrc
  train_calc

Enter the number of ADDITIONAL epochs. Training saves the active checkpoint at:

  source/checkpoints/calcgpt3.pt

It also exports calculator programs under:

  source/calculator/

To train without installing the convenience command:

  cd path/to/CalcGPT3_Experimental_v1.0/source
  python3 -m venv .venv
  source .venv/bin/activate
  python3 -m pip install -r requirements.txt
  python3 train_mac.py --epochs 5

Useful training options:

  --checkpoint PATH        write to a different checkpoint (protects E40)
  --data-dir PATH          corpus cache location
  --seed N                 reproducible seeding (default 2026)
  --validation-fraction F  held-out validation split (default 0.05)
  --limit-batches N        cap batches per epoch (fast smoke test)
  --no-export              train without regenerating calculator programs

Do not use --reset unless you intentionally want to discard the E40 checkpoint.
Do not publish .venv, cached datasets, __pycache__, or every history checkpoint.

EXPORT WITHOUT MORE TRAINING
============================

With the environment active:

  cd path/to/CalcGPT3_Experimental_v1.0/source
  python3 export_calculator.py

This writes calculator/tinylm.py plus numbered paste-safe installers
tinydata.py, tinydata2.py, ... and calculator/model_meta.json. Future exporters
remove obsolete generated data parts before writing a new matched set.

The on-calculator data format remains version 13. Keep CalcGPT 3.1's tinylm.py and
its tinydata installers together: the metadata is compatible with older runtimes,
but only the 3.1 runtime has the improved decoder and checksum-verified loader.

INSTALL ON THE CALCULATOR
=========================

The generated tinydata programs install one part at a time; no program ever builds
the whole model in memory.

1. In TI-Nspire Student Software, open the CalcGPT problem and add Python pages
   named tinydata, tinydata2, ... for every generated tinydata*.py file.
2. Paste each file's contents into the matching page (paste in clipboard chunks if
   the editor refuses a whole file; each file is under ~12 KB).
3. Run the pages in order: tinydata, then tinydata2, ... Each part prints progress
   and verifies its own checksum as it installs.
4. The final part re-reads every stored weight, checks its length and checksum,
   and prints "CalcGPT 3 model installed and verified."
5. Run tinylm and press Ctrl+R.

Interrupted installs are resumable: re-running a numbered part that already
finished prints "already installed" and stops. If a part is corrupt, its checksum
fails immediately and names the unit, so only that page needs re-pasting. If a
different model id is already installed, the first part asks before replacing it,
and cancels the install if you answer anything other than y.

TRAINING THE PASTE HELPER
=========================

After installation, running the tinydata program from the calculator's Shell
(rather than from the Python page) turns it into a paste helper: it reads a line
of text and stores it for CalcGPT. This is unchanged from version 1.0.

UPGRADING FROM AN OLDER RELEASE
===============================

The model data format and model id are unchanged, so:

- To gain only the 3.1 runtime, replace the tinylm page with the generated
  calculator/tinylm.py. Existing installed data keeps working.
- To also gain checksum verification and resumable installs, delete the old
  tinydata program, paste the new numbered tinydata parts, and run them. The first
  part recognises a same-id model and becomes the paste helper immediately; delete
  the "tdinfo" list first if you want a full re-verify.

TESTING
=======

All desktop-side tests run headlessly against the real generated calculator code
through a simulated ti_system/ti_draw, so no calculator is required:

  cd source
  python3 -m venv .venv-test
  .venv-test/bin/python -m pip install -r requirements.txt
  .venv-test/bin/python -m unittest discover -s tests -v

  # Before/after benchmark and fixed prompt suite
  .venv-test/bin/python tests/evaluate.py --label current

  # Compare any build against a reference build on the same prompts/seeds
  .venv-test/bin/python tests/run_suite.py --template PATH/tinylm.py \
      --data PATH/tinydata*.py --label build

  # Association-builder retrieval experiment (downloads DailyDialog)
  .venv-test/bin/python tests/assoc_experiment.py

The suite covers quantization/dequantization, exporter output, model-id stability,
installer generation, resumability, corruption detection, packed tensor
reconstruction, vocabulary/association/intent/emotion reconstruction, the
mathematical equivalence of the optimized GRU, the tokenizer, decoder edge cases
(empty, very long, unknown words, punctuation, uppercase), conversation context,
the control functions, model-missing, incomplete-install, and corrupted-install
handling, plus the ready-to-run document builder and its end-to-end verifier.

BUILD THE READY-TO-RUN DOCUMENT
===============================

To rebuild ready_to_run/CalcGPT3_v3.1.tns from a base document:

  cd source
  python3 build_tns.py --base ../ready_to_run/CalcGPT3.tns \
      --out ../ready_to_run/CalcGPT3_v3.1.tns \
      --runtime calculator/tinylm.py \
      --meta calculator/model_meta.json

  # End-to-end check of the built document
  .venv-test/bin/python tests/verify_tns.py ../ready_to_run/CalcGPT3_v3.1.tns

A .tns file is a ZIP container with a TI-specific first-entry signature and
end-of-central-directory signature. TI-Nspire Student Software stores the
document XML with a proprietary compression (method 13: 3DES-CTR, raw deflate,
then a tokenized XML form), while the Python program pages use ordinary deflate.

build_tns.py deliberately does NOT decode or re-encode the encrypted XML. It
copies Document.xml and Problem1.xml byte-for-byte, including their original
checksums, and rewrites only the plain-text Python pages. That is safe because it
cannot corrupt the installed model data, and it avoids depending on an
unverifiable re-implementation of TI's compression. For the same reason the tool
refuses to ADD a new Python page: a page only appears in the TI-Nspire interface
if Problem1.xml contains a matching card, and that XML cannot be edited safely.
Replacing the content of an existing page is fine.

Reusing the document's installed model data is valid only because the 3.1 runtime
keeps data format 13 and model id 1282619148. The builder checks model_meta.json
and refuses to build if either ever changes; rebuild the base document by hand in
that case.

verify_tns.py is the end-to-end check. It decodes the built document, recovers
the model variables that are actually stored inside it, then runs the tinylm.py
page that the document itself ships against those variables. It also confirms
that page is byte-identical to source/calculator/tinylm.py. The method 13 decoder
is vendored under source/tests/ti_tns/ from the MIT-licensed TnsTools project; see
that directory for provenance.

MEASUREMENTS
============

Desktop harness (CPython 3.10, torch CPU), per-call milliseconds:

  step    1.580 -> 0.753   (2.10x)
  logits  6.545 -> 3.267   (2.00x)
  choose  1.087 -> 0.875   (1.24x)
  generate (full reply) 233.1 -> 118.8 ms  (1.96x)

Fixed 14-prompt suite, same seeds, proxy metrics (see tests/quality_metrics.py):

  composite     0.705 -> 0.720
  relevance     0.355 -> 0.390
  repetition    0.202 -> 0.189  (lower is better)
  complete      1.000 -> 1.000
  dangling      0.000 -> 0.000

These are desktop proxies, not a claim of semantic understanding. On-device
absolute timings and the supplied screenshots' quality still need hardware
re-measurement.

VERIFIED NEGATIVE RESULT
========================

A contrastive PMI/TF-IDF association builder was implemented and scored on 7,513
held-out prompt/reply pairs. It reduced top-3 retrieval from 0.393 to 0.112 and
was rejected. Larger count-based association tables (up to 4,096 bigram features)
improved top-3 retrieval only from 0.393 to 0.403 while roughly quadrupling memory,
so the shipped frequency-weighted scheme is retained deliberately.

SOURCE LAYOUT
=============

ready_to_run/CalcGPT3_v3.1.tns
  Ready-to-run TI-Nspire problem with the 3.1 runtime and the installed E40 model.
  This is the document to use.

ready_to_run/CalcGPT3.tns
  The original version-1.0 ready-to-run problem, unchanged, kept for comparison
  and used as the base document by build_tns.py.

source/train_mac.py
  Downloads and parses DailyDialog, trains/resumes the GRU, learns conditioning
  evidence, saves checkpoints (with a validation split), and invokes the exporter.

source/export_calculator.py
  Quantizes the checkpoint and generates the runtime and the checksum-verified,
  resumable installer programs.

source/calculator_template.py
  TI-Nspire interface, model loader, classifiers, decoder, candidate ranking,
  scrolling, input, controls, and rendering code. Placeholders are substituted by
  the exporter.

source/build_tns.py
  Builds a ready-to-run .tns from a base document by replacing the plain-text
  Python pages and copying TI's encrypted document XML verbatim.

source/calculator/
  Generated from the E40 checkpoint: tinylm.py plus numbered tinydata installers
  and model_meta.json.

source/legacy/tinydata_e40_single_file.py
  The original single-file E40 installer, preserved for provenance.

source/tests/
  tisim.py, harness.py, evaluate.py, run_suite.py, quality_metrics.py,
  assoc_experiment.py, test_calcgpt3.py, test_tns.py, verify_tns.py,
  ti_tns/ (vendored MIT TNS method 13 decoder), and baseline_snapshot/ (the
  original v1.0 runtime and data for before/after comparison).

source/checkpoints/calcgpt3.pt
  Resumable E40 PyTorch checkpoint (unchanged weights).

screenshots/
  Release screenshots showing the interface and representative output.

KNOWN LIMITATIONS
=================

See KNOWN_ISSUES.txt. Most importantly, lower training loss does not establish
semantic understanding. At E40, the model often produces fluent fragments that
are unrelated to the prompt. Additional epochs alone are unlikely to fix this,
and the 3.0/3.1 changes do not change the model weights.

CONTRIBUTING
============

Bug fixes and experimental improvements are welcome. Read CONTRIBUTING.md and
IMPROVEMENT_ROADMAP.txt before changing the model format. Run the test suite
before and after a change, and report the exact calculator model/OS, program
version, reproduction steps, prompt, output, timing, and traceback when
applicable.

NOT VERIFIABLE WITHOUT HARDWARE
===============================

The following need a real TI-Nspire CX II (or the official computer preview) and
were not exercised here: true response/load timings, peak document size and
MemoryError behaviour, physical key names for the new Ctrl+N/R/T/L controls, the
ti_draw rendering of the status bar and messages, the Shell paste-helper workflow,
and the paste-size limit of the TI editor. See MODIFICATIONS.txt for the full list.

In particular, CalcGPT3_v3.1.tns was verified structurally and by executing its
embedded runtime against its own stored model data on the desktop, but it was
never opened in TI-Nspire Student Software or run on a calculator. That step is
still required before releasing it to end users.

LICENSES AND ATTRIBUTION
========================

Original project code is released under the MIT License; see LICENSE_CODE.txt.
The checkpoint was trained using DailyDialog. See MODEL_LICENSE_AND_ATTRIBUTION.txt
for dataset attribution and noncommercial/share-alike terms.

This project is not affiliated with Texas Instruments, OpenAI, or the DailyDialog
authors. "GPT" in the experimental project name is descriptive branding; this is
a GRU language model, not an OpenAI GPT model.

CREDITS
=======

Project concept, testing, and release: Fred Bennett
AI-assisted code development and documentation: OpenAI ChatGPT

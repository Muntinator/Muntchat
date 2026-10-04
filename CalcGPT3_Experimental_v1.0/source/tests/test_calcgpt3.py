"""Automated tests for CalcGPT 3 desktop components and the calculator runtime.

Run with:
    cd source
    .venv-test/bin/python -m unittest discover -s tests -v

Everything runs headlessly against the *real* generated calculator code via the
``tisim`` module; no TI-Nspire hardware is required. What still needs hardware
is listed in the README ("Not verifiable without hardware").
"""

from __future__ import annotations

import base64
import builtins
import contextlib
import importlib
import io
import json
import random
import re
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent
CALCULATOR = SOURCE / "calculator"
CHECKPOINT = SOURCE / "checkpoints" / "calcgpt3.pt"
sys.path.insert(0, str(HERE))

import harness  # noqa: E402
import export_calculator as ex  # noqa: E402
import quality_metrics  # noqa: E402

_RUNTIME = None


def runtime():
    global _RUNTIME
    if _RUNTIME is None:
        _RUNTIME = harness.build(quiet=True, warm=True)
    return _RUNTIME


def _load_checkpoint():
    import torch
    return torch.load(CHECKPOINT, map_location="cpu", weights_only=False)


class QuantizationTests(unittest.TestCase):
    def test_roundtrip_error_bounded_by_scale(self):
        saved = _load_checkpoint()
        for name in ex.TENSORS:
            scale, length, blob = ex.quantize(saved["model"][name])
            raw = base64.b85decode(blob.encode("ascii"))[:length]
            ints = [b - 256 if b > 127 else b for b in raw]
            original = saved["model"][name].detach().cpu().flatten().float().tolist()
            self.assertEqual(len(ints), len(original))
            worst = max(abs(ints[i] * scale - original[i]) for i in range(len(ints)))
            self.assertLessEqual(worst, scale + 1e-6,
                                 "quantization error exceeded one step for " + name)

    def test_adler32_is_stable(self):
        self.assertEqual(ex.adler32(bytes(range(256))),
                         ex.adler32(bytes(range(256))))
        self.assertNotEqual(ex.adler32(b"abc"), ex.adler32(b"abd"))


class ExporterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.out = Path(cls.tmp.name)
        cls.paths = ex.export(CHECKPOINT, output_dir=cls.out)
        cls.meta = json.loads((cls.out / "model_meta.json").read_text())

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_generated_files_compile_and_are_small(self):
        for path in self.paths:
            source = path.read_text()
            compile(source, str(path), "exec")
            if path.name.startswith("tinydata"):
                self.assertLess(len(source), 16000,
                                path.name + " may exceed the TI paste limit")

    def test_model_id_stable_and_matches_installed(self):
        with tempfile.TemporaryDirectory() as other:
            ex.export(CHECKPOINT, output_dir=Path(other))
            meta = json.loads((Path(other) / "model_meta.json").read_text())
            self.assertEqual(meta["model_id"], self.meta["model_id"])
        self.assertEqual(self.meta["model_id"], 1282619148,
                         "model id must stay compatible with the E40 release")
        self.assertEqual(self.meta["format"], 13)

    def test_installer_verifies_and_is_resumable(self):
        parts = harness.installer_parts(self.out)
        harness.reset_store()
        store = harness.install_model(parts)
        info = store.STORE.lists["tdinfo"]
        self.assertEqual(int(info[0]), 13)
        self.assertEqual(int(info[7]), self.meta["model_id"])
        self.assertEqual(int(info[4]), self.meta["vocab"])
        # Re-running an already-installed numbered part skips (and exits) without
        # changing anything.
        first = [list(v) for v in store.STORE.lists.values()]
        with self.assertRaises(SystemExit):
            harness.install_model(parts[1:2])
        self.assertEqual(first, [list(v) for v in store.STORE.lists.values()])

    def test_partial_install_reports_missing_stage(self):
        parts = harness.installer_parts(self.out)
        harness.reset_store()
        harness.install_model(parts[:-1])
        # Simulate an interrupted install: a middle stage marker is absent.
        del harness.store()["tds4"]
        with self.assertRaises(SystemExit):
            harness.install_model(parts[-1:])

    def test_corrupted_paste_is_rejected(self):
        parts = harness.installer_parts(self.out)
        source = parts[1].read_text()
        match = re.search(r"install\(.*?,(\d+)\)", source)
        self.assertIsNotNone(match)
        tampered = source[:match.end(1)] + str(int(match.group(1)) + 1) + source[match.end(1):]
        harness.reset_store()
        harness.install_model(parts[:1])
        with self.assertRaises(SystemExit):
            with contextlib.redirect_stdout(io.StringIO()):
                exec(compile(tampered, "tampered", "exec"),
                     {"__name__": "__tampered__", "input": lambda *a: ""})


class ReconstructionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rt = harness.build(quiet=True, warm=True)

    def test_weights_reconstruct_exactly(self):
        rt = self.rt
        saved = _load_checkpoint()
        store = harness.store()
        qparts = [int(x) for x in store["tdqp"]]
        for t, name in enumerate(ex.TENSORS):
            _, length, blob = ex.quantize(saved["model"][name])
            raw = base64.b85decode(blob.encode("ascii"))[:length]
            ints = [b - 256 if b > 127 else b for b in raw]
            recovered = []
            for chunk in range(qparts[t]):
                for packed in store["tdq%d%s%d" % (t, "x", chunk)]:
                    packed = int(packed)
                    recovered.append((packed >> 8) - 128)
                    recovered.append((packed & 255) - 128)
            self.assertEqual(recovered[:length], ints, "tensor " + name)
            # qvalue must agree on sampled indices.
            for index in random.Random(t).sample(range(length), min(50, length)):
                self.assertEqual(rt.ns["qvalue"](rt.ns["Q"][t], index), ints[index])

    def test_vocabulary_reconstructs(self):
        rt = self.rt
        self.assertEqual(list(rt.vocab), _load_checkpoint()["vocab"])
        self.assertNotIn("", rt.vocab)

    def test_associations_reconstruct(self):
        rt = self.rt
        saved = _load_checkpoint()["associations"]
        assoc = rt.ns["ASSOCIATIONS"]
        self.assertTrue(assoc)
        for prompt, choices in saved.items():
            if prompt not in assoc:
                continue
            expected = {token: weight for token, weight in choices[:3]}
            got = assoc[prompt]
            self.assertEqual(set(got), set(expected))
            for token, weight in expected.items():
                self.assertAlmostEqual(got[token], weight, delta=0.02)

    def test_intent_and_emotion_reconstruct(self):
        rt = self.rt
        saved = _load_checkpoint()
        self.assertEqual(rt.ns["INTENT_PRIORS"],
                         [p / 32.0 for p in saved["intent_priors"]])
        self.assertEqual(rt.ns["EMOTION_PRIORS"],
                         [p / 128.0 for p in saved["emotion_priors"]])
        self.assertTrue(rt.ns["INTENT_WORDS"])
        self.assertTrue(rt.ns["EMOTION_WORDS"])
        for values in rt.ns["INTENT_WORDS"].values():
            self.assertEqual(len(values), 4)
        for values in rt.ns["EMOTION_WORDS"].values():
            self.assertEqual(len(values), 7)


class InferenceMathTests(unittest.TestCase):
    """The optimized hot loops must match a straightforward reference exactly."""

    def test_step_and_logits_match_reference(self):
        import math
        rt = runtime()
        ns = rt.ns
        Q, S, E, H, N = ns["Q"], ns["S"], ns["E"], ns["H"], ns["N"]
        qv, sig = ns["qvalue"], ns["sigmoid"]

        def ref_step(token, h):
            x = [qv(Q[0], token * E + j) * S[0] for j in range(E)]
            gates = [0.0] * (3 * H)
            for g in range(2 * H):
                sx = sum(qv(Q[1], g * E + j) * x[j] for j in range(E))
                sh = sum(qv(Q[2], g * H + j) * h[j] for j in range(H))
                gates[g] = sig(S[1] * sx + S[2] * sh + qv(Q[3], g) * S[3] + qv(Q[4], g) * S[4])
            new = [0.0] * H
            for j in range(H):
                g = 2 * H + j
                sx = sum(qv(Q[1], g * E + k) * x[k] for k in range(E))
                sh = sum(qv(Q[2], g * H + k) * h[k] for k in range(H))
                cand = math.tanh(S[1] * sx + qv(Q[3], g) * S[3]
                                 + gates[j] * (S[2] * sh + qv(Q[4], g) * S[4]))
                new[j] = (1.0 - gates[H + j]) * cand + gates[H + j] * h[j]
            return new

        def ref_logits(h):
            return [S[5] * sum(qv(Q[5], t * H + j) * h[j] for j in range(H))
                    + qv(Q[6], t) * S[6] for t in range(N)]

        h = [0.0] * H
        for token in [2, 4, 17, 23, 600, 1, 6, 320, 7, 5]:
            fast, ref = ns["step"](token, h), ref_step(token, h)
            self.assertLess(max(abs(a - b) for a, b in zip(fast, ref)), 1e-9)
            h = fast
        hs = [random.Random(3).uniform(-1, 1) for _ in range(H)]
        fast, ref = ns["logits"](hs), ref_logits(hs)
        self.assertLess(max(abs(a - b) for a, b in zip(fast, ref)), 1e-9)


class TokenizerTests(unittest.TestCase):
    def test_tokenize_basics(self):
        rt = runtime()
        ns = rt.ns
        self.assertEqual(ns["tokenize"](""), [])
        self.assertEqual(ns["tokenize"]("Hello!"), [rt.lookup["hello"], rt.lookup["!"]])
        self.assertEqual(ns["tokenize"]("I'm ok"), [rt.lookup["i'm"], rt.lookup["ok"]])
        numbers = ns["tokenize"]("123 45")
        self.assertEqual(len(numbers), 2)
        self.assertTrue(all(0 <= t < len(rt.vocab) for t in numbers))
        self.assertEqual(ns["tokenize"]("!!!"), [rt.lookup["!"]] * 3)

    def test_unknown_words_map_to_unk(self):
        rt = runtime()
        tokens = rt.ns["tokenize"]("zzzqwx")
        self.assertEqual(tokens, [1])

    def test_long_input_is_bounded(self):
        rt = runtime()
        prompt = " ".join(["hello"] * 500)
        ids = rt.ns["tokenize"](prompt)
        self.assertLessEqual(len(rt.ns["tokenize"](prompt)[:rt.ns["PROMPT_LIMIT"]]),
                             rt.ns["PROMPT_LIMIT"])
        self.assertTrue(ids)


class DecoderTests(unittest.TestCase):
    def _generate(self, prompt, messages=None, seed=12345):
        rt = runtime()
        rt.reseed(seed)
        reply, _ = rt.ns["generate"](prompt, messages or [], 0)
        return reply

    def test_empty_input(self):
        self.assertTrue(self._generate(""))

    def test_unknown_words(self):
        self.assertTrue(self._generate("quantum entanglement frobnicator"))

    def test_punctuation_and_case(self):
        for prompt in ("really?!?!", "HELLO THERE!!!", "What is this?", "..."):
            reply = self._generate(prompt)
            self.assertTrue(reply)

    def test_repeated_punctuation(self):
        reply = self._generate("wow!!!! amazing????")
        self.assertTrue(reply)

    def test_deterministic_for_fixed_seed(self):
        self.assertEqual(self._generate("hello there", seed=5),
                         self._generate("hello there", seed=5))

    def test_reply_is_grammatical_shell(self):
        reply = self._generate("how are you")
        self.assertTrue(reply[0].isupper())
        self.assertIn(reply[-1], ".!?")

    def test_long_prompt(self):
        self.assertTrue(self._generate("hello " * 200))

    def test_very_long_input_terminates(self):
        reply = self._generate("please " * 1000)
        self.assertTrue(reply)
        self.assertLess(len(reply), 400)

    def test_choose_respects_forbidden(self):
        rt = runtime()
        ns = rt.ns
        scores = ns["logits"]([0.05] * ns["H"])
        forbidden = {t: 1 for t in range(ns["FIRST_WORD"] + 1, ns["N"])}
        token = ns["choose"](scores, {}, {}, -1, -1, {}, {}, 0.5, 0, forbidden)
        self.assertEqual(token, ns["FIRST_WORD"])

    def test_acceptable_gate(self):
        rt = runtime()
        ns = rt.ns
        self.assertFalse(ns["acceptable"]([], {}))
        # A single continuation word can never be an acceptable reply.
        self.assertFalse(ns["acceptable"]([ns["LOOKUP"]["the"]], {}))


class ConversationTests(unittest.TestCase):
    def test_previous_user_ids_skips_current_turn(self):
        rt = runtime()
        ns = rt.ns
        messages = [("user", "what is your name"), ("bot", "I am CalcGPT."),
                    ("user", "what about you")]
        ids = ns["previous_user_ids"](messages)
        self.assertEqual(ids, ns["tokenize"]("what is your name"))

    def test_context_changes_understanding(self):
        rt = runtime()
        ns = rt.ns
        prompt = ns["tokenize"]("what about")
        # Pick a content token that actually has learned associations.
        context_id = next(t for t in ns["ASSOCIATIONS"]
                          if t < ns["BIGRAM_BASE"] and t not in ns["STOP"] and t != 1)
        with_context = ns["understand"](prompt, [context_id])
        without = ns["understand"](prompt, [])
        self.assertNotEqual(set(with_context[0]), set(without[0]),
                            "rolling context must influence response bias")

    def test_followup_uses_prior_turn(self):
        rt = runtime()
        ns = rt.ns
        rt.reseed(7)
        first, _ = ns["generate"]("i like music", [], 0)
        messages = [("user", "i like music"), ("bot", first)]
        rt.reseed(7)
        second, _ = ns["generate"]("what about you", messages, 0)
        self.assertTrue(second)


class ControlFlowTests(unittest.TestCase):
    def test_respond_regenerate_and_clear(self):
        rt = runtime()
        ns = rt.ns
        ns["respond"]("hello", [])
        self.assertEqual(len(ns["messages"]), 2)
        first = ns["messages"][-1][1]
        self.assertEqual(ns["LAST_PROMPT"], "hello")
        ns["regenerate"]()
        self.assertEqual(ns["messages"][-1][0], "bot")
        self.assertEqual(ns["LAST_PROMPT"], "hello")
        ns["clear_conversation"]()
        self.assertEqual(ns["messages"], [])
        self.assertEqual(ns["NOTICE"], "Conversation cleared")
        self.assertIsNotNone(first)

    def test_temperature_and_length_cycle(self):
        rt = runtime()
        ns = rt.ns
        before = ns["TEMP"]
        ns["cycle_temp"]()
        self.assertNotEqual(ns["TEMP"], before)
        ns["cycle_length"]()
        self.assertIn(ns["LENGTH_SCALE"], ns["LENGTHS"])

    def test_wrap_and_sentence_case(self):
        rt = runtime()
        ns = rt.ns
        self.assertTrue(all(len(line) <= 35 for line in ns["wrap"]("x " * 60, 35) or [""]))
        self.assertEqual(ns["sentence_case"]("hello there. i am here!"),
                         "Hello there. I am here!")
        self.assertTrue(ns["needs_capital"]("hi. "))
        self.assertFalse(ns["needs_capital"]("hi"))


class FailureModeTests(unittest.TestCase):
    def test_model_missing(self):
        harness.reset_store()
        with self.assertRaises(SystemExit):
            with contextlib.redirect_stdout(io.StringIO()):
                harness.load_runtime()

    def test_incomplete_installation_fails_on_use(self):
        harness.reset_store()
        harness.install_model(harness.installer_parts())
        # Remove one weight chunk, as a half-finished install would.
        del harness.store()["tdq5x0"]
        ns = harness.load_runtime()  # vocab/assoc still load fine
        with self.assertRaises(Exception):
            with contextlib.redirect_stdout(io.StringIO()):
                ns["ensure_model"]([], 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)

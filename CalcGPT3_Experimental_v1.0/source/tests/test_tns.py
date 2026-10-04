"""Tests for the ready-to-run .tns builder and its end-to-end verifier.

These cover source/build_tns.py and tests/verify_tns.py. The important
guarantees are:

  * the rebuilt container parses, and TI's method 13 entries are copied
    byte-for-byte with their original CRC and uncompressed size;
  * only the pages that were actually replaced differ from the base document;
  * the tinylm.py page embedded in the built .tns is byte-identical to the
    generated runtime in source/calculator/;
  * the document's TI-encrypted Problem1.xml still describes the same model
    (format 13, model id 1282619148) and its stored variables actually drive the
    runtime that ships inside the document;
  * the builder refuses unsafe requests rather than producing a bad document.

Nothing here needs a TI-Nspire. What still does is listed in README.txt under
"Not verifiable without hardware".
"""

from __future__ import annotations

import json
import shutil
import sys
import tempfile
import unittest
import zlib
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent
CALCULATOR = SOURCE / "calculator"
READY = SOURCE.parent / "ready_to_run"
BASE_TNS = READY / "CalcGPT3.tns"
BUILT_TNS = READY / "CalcGPT3_v3.1.tns"
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(SOURCE))

import build_tns  # noqa: E402
import verify_tns  # noqa: E402

_MODEL_ID = 1282619148
_FORMAT = 13


def _entries(path: Path):
    data = path.read_bytes()
    ents = build_tns.parse(data)[0]
    for e in ents:
        e.load(data)
    return data, ents


@unittest.skipUnless(BASE_TNS.exists(), "base ready_to_run document is missing")
class ContainerTests(unittest.TestCase):
    def setUp(self):
        self.data, self.entries = _entries(BASE_TNS)
        self.by_name = {e.name: e for e in self.entries}

    def test_base_document_parses(self):
        self.assertEqual([e.name for e in self.entries],
                         ["Document.xml", "Problem1.xml", "tinylm.py", "tinydata.py"])
        self.assertEqual(self.data[:10], build_tns.TIMLP_MAGIC)
        self.assertEqual(self.data[-22:-18], build_tns.TIPD_EOCD)

    def test_pages_are_plain_deflate_and_xml_is_encrypted(self):
        self.assertEqual(self.by_name["tinylm.py"].method, 8)
        self.assertEqual(self.by_name["tinydata.py"].method, 8)
        self.assertEqual(self.by_name["Problem1.xml"].method, 13)

    def test_every_page_payload_inflates_and_crc_matches(self):
        for name in ("tinylm.py", "tinydata.py"):
            entry = self.by_name[name]
            self.assertEqual(zlib.crc32(entry.payload) & 0xFFFFFFFF, entry.crc32, name)
            self.assertEqual(len(entry.payload), entry.usize, name)

    def test_deflate_roundtrip(self):
        for text in (b"", b"a", b"print('hello')\n" * 40):
            self.assertEqual(build_tns.inflate(build_tns.deflate(text)), text)


@unittest.skipUnless(BUILT_TNS.exists(), "built 3.1 document is missing")
class BuiltDocumentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base_data, cls.base = _entries(BASE_TNS)
        cls.data, cls.built = _entries(BUILT_TNS)
        cls.base_by_name = {e.name: e for e in cls.base}
        cls.by_name = {e.name: e for e in cls.built}

    def test_encrypted_entries_are_byte_identical(self):
        for name in ("Document.xml", "Problem1.xml"):
            self.assertEqual(self.by_name[name].blob, self.base_by_name[name].blob, name)
            self.assertEqual(self.by_name[name].crc32, self.base_by_name[name].crc32, name)
            self.assertEqual(self.by_name[name].usize, self.base_by_name[name].usize, name)

    def test_only_the_runtime_page_changed(self):
        """The installer page we did not replace must survive untouched."""
        self.assertEqual(self.by_name["tinydata.py"].blob,
                         self.base_by_name["tinydata.py"].blob)
        self.assertNotEqual(self.by_name["tinylm.py"].blob,
                            self.base_by_name["tinylm.py"].blob)

    def test_embedded_page_matches_exported_runtime(self):
        exported = (CALCULATOR / "tinylm.py").read_text()
        self.assertEqual(self.by_name["tinylm.py"].payload.decode(), exported)

    def test_entries_are_contiguous_and_precede_the_central_directory(self):
        """Local headers must tile the file with no gaps before the directory."""
        offset = 0
        for entry in self.built:
            self.assertEqual(entry.loff, offset, entry.name)
            offset = entry.data_off + entry.csize
        eocd_off, _sig = build_tns.find_eocd(self.data)
        cd_off = build_tns._u32(self.data, eocd_off + 16)
        self.assertEqual(offset, cd_off,
                         "entries must end exactly where the central directory starts")
        self.assertEqual(cd_off + build_tns._u32(self.data, eocd_off + 12), eocd_off,
                         "central directory must sit immediately before the EOCD")

    def test_document_model_matches_model_meta(self):
        variables = verify_tns.variables_from_document(self.built, self.data)
        info = variables["tdinfo"]
        self.assertEqual(int(info[0]), _FORMAT)
        self.assertEqual(int(info[7]), _MODEL_ID)
        meta = json.loads((CALCULATOR / "model_meta.json").read_text())
        self.assertEqual(meta["format"], _FORMAT)
        self.assertEqual(meta["model_id"], _MODEL_ID)

    def test_document_runtime_generates_from_document_data(self):
        variables = verify_tns.variables_from_document(self.built, self.data)
        page = self.by_name["tinylm.py"].payload.decode()
        exported = (CALCULATOR / "tinylm.py").read_text()
        prompts = ("hello", "how are you", "i am going to the park")

        # A fresh runtime per side: generation is seeded and stateful, so both
        # runtimes must start from the same seed and the same seed sequence.
        doc_runtime = verify_tns.run(page, variables)
        doc_replies = [doc_runtime.generate(p, []) for p in prompts]
        for prompt, reply in zip(prompts, doc_replies):
            self.assertTrue(reply.strip(), prompt)

        exp_runtime = verify_tns.run(exported, variables)
        exp_replies = [exp_runtime.generate(p, []) for p in prompts]
        self.assertEqual(doc_replies, exp_replies,
                         "document runtime and exported runtime disagree")

    def test_signed_values_survive_the_tixc_decode(self):
        """TIXC writes U+2212 for '-', so the parser must map it back.

        Weights are packed two-per-byte, so a chunk mixes unsigned packed bytes
        with standalone signed values in the -128..127 range. Anything outside
        both ranges means a decode error.
        """
        variables = verify_tns.variables_from_document(self.built, self.data)
        flat = verify_tns.store_from_variables(variables)
        negatives = 0
        for name, values in flat.items():
            if not name.startswith("tdq"):
                continue
            self.assertLessEqual(max(values), 65535, name)
            negatives += sum(1 for v in values if v < 0)
        self.assertGreater(negatives, 0,
                           "expected negative signed weights to survive decoding")

    def test_every_variable_the_runtime_needs_is_in_the_document(self):
        """The 3.1 runtime must find all of its model data in the document."""
        import harness
        flat = verify_tns.store_from_variables(
            verify_tns.variables_from_document(self.built, self.data))
        info = flat["tdinfo"]
        need = set()
        for tensor in range(7):
            for part in range(int(flat["tdqp"][tensor])):
                need.add("tdq%dx%d" % (tensor, part))
        for part in range(int(info[5])):
            need.add("tdvc%d" % part)
        for part in range(int(info[6])):
            need.add("tda%d" % part)
        for name in ("tdinfo", "tdlens", "tdscale", "tdqp"):
            need.add(name)
        self.assertFalse(sorted(need - set(flat)),
                         "document is missing model variables")

    def test_document_model_bytes_match_a_fresh_installation(self):
        """Decoded document data must equal what the 3.1 installers produce.

        This is the real backward-compatibility proof: the ready-to-run document
        carries the E40 model in the 1.0 storage layout, and the 3.1 runtime
        must read the identical weights.
        """
        import harness
        harness.reset_store()
        harness.install_model()
        truth = {k: list(v) for k, v in harness.store().items()}
        flat = verify_tns.store_from_variables(
            verify_tns.variables_from_document(self.built, self.data))

        # tdinfo in 1.0 documents has no trailing build field.
        self.assertEqual(flat["tdinfo"][:8], [int(x) for x in truth["tdinfo"][:8]])
        for name, values in truth.items():
            if name in ("tdinfo", "tdscale"):
                continue  # metadata: build field and float text precision
            if name.startswith("tds") and name[3:].isdigit():
                continue  # per-part install markers, new in 3.1
            self.assertIn(name, flat, "document is missing %s" % name)
            self.assertEqual(len(flat[name]), len(values), name)
            self.assertEqual(flat[name], values, name)


class BuildGuardTests(unittest.TestCase):
    def test_refuses_new_page_names(self):
        """Adding a page would need a card in TI-encrypted Problem1.xml."""
        if not BASE_TNS.exists():
            self.skipTest("base ready_to_run document is missing")
        with tempfile.TemporaryDirectory() as tmp:
            new_page = Path(tmp) / "tinydata9.py"
            new_page.write_text("print('nope')\n")
            with self.assertRaises(build_tns.TnsError) as ctx:
                build_tns.main([
                    "--base", str(BASE_TNS),
                    "--out", str(Path(tmp) / "out.tns"),
                    "--runtime", str(CALCULATOR / "tinylm.py"),
                    "--replace", "tinydata9=%s" % new_page,
                    "--quiet",
                ])
        self.assertIn("Problem1.xml", str(ctx.exception))

    def test_refuses_mismatched_model_meta(self):
        if not BASE_TNS.exists():
            self.skipTest("base ready_to_run document is missing")
        with tempfile.TemporaryDirectory() as tmp:
            meta = json.loads((CALCULATOR / "model_meta.json").read_text())
            meta["model_id"] = 1
            bad = Path(tmp) / "model_meta.json"
            bad.write_text(json.dumps(meta))
            with self.assertRaises(build_tns.TnsError) as ctx:
                build_tns.check_model_compat(bad)
        self.assertIn("model_id", str(ctx.exception))

    def test_refuses_unknown_data_format(self):
        with tempfile.TemporaryDirectory() as tmp:
            meta = json.loads((CALCULATOR / "model_meta.json").read_text())
            meta["format"] = 99
            bad = Path(tmp) / "model_meta.json"
            bad.write_text(json.dumps(meta))
            with self.assertRaises(build_tns.TnsError) as ctx:
                build_tns.check_model_compat(bad)
        self.assertIn("format", str(ctx.exception))

    @unittest.skipUnless(BASE_TNS.exists(), "base ready_to_run document is missing")
    def test_build_is_reproducible(self):
        """Two builds from the same inputs must be byte-identical."""
        with tempfile.TemporaryDirectory() as tmp:
            outs = []
            for name in ("a.tns", "b.tns"):
                out = Path(tmp) / name
                build_tns.main([
                    "--base", str(BASE_TNS),
                    "--out", str(out),
                    "--runtime", str(CALCULATOR / "tinylm.py"),
                    "--meta", str(CALCULATOR / "model_meta.json"),
                    "--quiet",
                ])
                outs.append(out.read_bytes())
            self.assertEqual(outs[0], outs[1])

    @unittest.skipUnless(BASE_TNS.exists() and BUILT_TNS.exists(),
                         "documents are missing")
    def test_built_matches_a_fresh_build(self):
        """The committed .tns is what the builder produces today."""
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "fresh.tns"
            build_tns.main([
                "--base", str(BASE_TNS),
                "--out", str(out),
                "--runtime", str(CALCULATOR / "tinylm.py"),
                "--meta", str(CALCULATOR / "model_meta.json"),
                "--quiet",
            ])
            self.assertEqual(out.read_bytes(), BUILT_TNS.read_bytes())


if __name__ == "__main__":
    unittest.main(verbosity=2)
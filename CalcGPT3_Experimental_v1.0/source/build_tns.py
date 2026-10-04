#!/usr/bin/env python3
"""Build a ready-to-run CalcGPT 3 TI-Nspire problem from a base .tns document.

WHY THIS EXISTS
---------------
A TI-Nspire .tns file is a ZIP container with two TI-specific quirks:

  * the first local file header signature is "*TIMLP0900" (10 bytes) instead of
    "PK\\x03\\x04" (4 bytes), so that first local header is 6 bytes longer;
  * the end-of-central-directory signature is "TIPD" instead of "PK\\x05\\x06".

TI-Nspire Student Software stores the document XML (Document.xml, Problem1.xml)
with a proprietary compression, "method 13" (3DES-CTR, then raw deflate, then a
tokenized XML form called TIXC). The Python program pages (tinylm.py,
tinydata.py) are stored with ordinary deflate, "method 8", so they are plain text
that can be read and rewritten safely.

This tool deliberately takes the SURGICAL approach: it copies every method 13
entry byte-for-byte and only rewrites the method 8 Python pages. TI's encrypted
document XML is never decoded or re-encoded, so there is no risk of corrupting
the model data stored inside Problem1.xml, and no risk of producing a document
Student Software refuses to open.

A decode / edit / re-encode round-trip would require reproducing TI's method 13
encryption exactly. That cannot be validated without a calculator or Student
Software, so this tool does not attempt it.

REUSING THE INSTALLED MODEL
---------------------------
The model already installed in the base document is reused unchanged. That is only
valid because the CalcGPT 3.1 runtime keeps the same on-calculator data format
(13) and the same model id (1282619148), so the exporter still produces
byte-identical model blobs. build_tns.py checks model_meta.json and refuses to
build if the format ever changes.

Because the encrypted Problem1.xml cannot be edited safely, this tool refuses to
add new Python pages: a page only appears in the TI-Nspire UI if Problem1.xml
contains a matching card, and adding one would require re-encoding the document.
Replacing the content of an existing page is fine; adding a page is not.
"""

from __future__ import annotations

import argparse
import builtins
import contextlib
import json
import pathlib
import struct
import sys
import zlib

TIMLP_MAGIC = b"*TIMLP0900"
PK_LOCAL = b"PK\x03\x04"
PK_CENTRAL = b"PK\x01\x02"
PK_EOCD = b"PK\x05\x06"
TIPD_EOCD = b"TIPD"

# DOS timestamp for rewritten pages: 2026-10-04 00:00:00.
DOS_TIME = 0
DOS_DATE = ((2026 - 1980) << 9) | (10 << 5) | 4

# Version-needed-to-extract, copied from the base document.
VERSION_NEEDED = 20

FORMAT_SUPPORTED = 13
MODEL_ID_SUPPORTED = 1282619148

# Fixed fields of a local file header, after the signature.
_LOCAL_FIELDS = "<HHHHHIIIHH"   # version, flags, method, time, date, crc, csize, usize, nlen, xlen
_LOCAL_FIELDS_LEN = struct.calcsize(_LOCAL_FIELDS)   # 26
_CENTRAL_FIELDS = "<HHHHHHIIIHHHHHII"
_CENTRAL_FIELDS_LEN = struct.calcsize(_CENTRAL_FIELDS)   # 42


class TnsError(Exception):
    pass


def _u16(data: bytes, off: int) -> int:
    return struct.unpack_from("<H", data, off)[0]


def _u32(data: bytes, off: int) -> int:
    return struct.unpack_from("<I", data, off)[0]


class Entry:
    """One container entry.

    For method 8 entries, ``payload`` holds the uncompressed text after load().
    For method 13 entries, ``blob`` holds the raw stored bytes and must be
    copied verbatim; ``crc32``/``usize`` come from the base document because
    method 13 stores the CRC of the *decoded* XML, not of these bytes.
    """

    def __init__(self, name, method, crc32, csize, usize, loff, data_off,
                 mtime, mdate, first):
        self.name = name
        self.method = method
        self.crc32 = crc32      # CRC as recorded in the base document
        self.csize = csize
        self.usize = usize
        self.loff = loff
        self.data_off = data_off
        self.mtime = mtime
        self.mdate = mdate
        self.first = first
        self.payload = b""      # method 8 uncompressed text
        self.blob = b""         # stored bytes (method 13 verbatim; method 8 cached)
        self.dirty = False      # method 8 payload changed since load()

    def load(self, data: bytes) -> None:
        raw = data[self.data_off : self.data_off + self.csize]
        self.blob = raw
        if self.method == 8:
            self.payload = inflate(raw)


def inflate(payload: bytes) -> bytes:
    """Inflate a method 8 payload, tolerating raw or zlib-wrapped deflate."""
    if not payload:
        return b""
    errors = []
    for wbits in (-15, 15, 47):
        try:
            obj = zlib.decompressobj(wbits)
            return obj.decompress(payload) + obj.flush()
        except zlib.error as exc:
            errors.append(str(exc))
    raise TnsError("deflate inflate failed: " + "; ".join(errors))


def deflate(payload: bytes) -> bytes:
    """Raw deflate, matching how TI Student Software stores method 8 pages."""
    if not payload:
        # An empty page still needs a well-formed raw-deflate stream: the
        # 3-byte fixed-Huffman block that encodes zero bytes.
        return b"\x03\x00"
    obj = zlib.compressobj(9, zlib.DEFLATED, -15)
    return obj.compress(payload) + obj.flush()


def find_eocd(data: bytes):
    best = None
    for sig in (PK_EOCD, TIPD_EOCD):
        off = data.rfind(sig)
        if off >= 0 and off + 22 <= len(data):
            if best is None or off > best[0]:
                best = (off, sig)
    if best is None:
        raise TnsError("no end-of-central-directory record found")
    return best


def _read_local(data, name, loff):
    """Read a local header, tolerating the 6-byte first-signature delta."""
    want = name.encode()
    for cand in (loff, loff + 6, loff - 6):
        if cand < 0 or cand + 4 > len(data):
            continue
        first = data.startswith(TIMLP_MAGIC, cand)
        if not first and not data.startswith(PK_LOCAL, cand):
            continue
        base = cand + (10 if first else 4)
        if base + _LOCAL_FIELDS_LEN > len(data):
            continue
        (_ver, _flags, method, mtime, mdate, crc32, csize, usize,
         nlen, xlen) = struct.unpack_from(_LOCAL_FIELDS, data, base)
        header_len = (10 if first else 4) + _LOCAL_FIELDS_LEN + nlen + xlen
        if data[base + _LOCAL_FIELDS_LEN : base + _LOCAL_FIELDS_LEN + nlen] != want:
            continue
        if cand + header_len + csize > len(data):
            continue
        return Entry(name=name, method=method, crc32=crc32, csize=csize,
                     usize=usize, loff=cand, data_off=cand + header_len,
                     mtime=mtime, mdate=mdate, first=first)
    return None


def parse(data: bytes):
    """Parse the container. Returns (entries, eocd_offset)."""
    eocd_off, _sig = find_eocd(data)
    total = _u16(data, eocd_off + 10)
    cd_off = _u32(data, eocd_off + 16)

    starts = [cd_off]
    if cd_off >= 6:
        starts.append(cd_off - 6)
    first_central = data.find(PK_CENTRAL)
    if first_central >= 0:
        starts.append(first_central)

    for start in starts:
        if start < 0 or not data.startswith(PK_CENTRAL, start):
            continue
        found = []
        off = start
        for _ in range(total or 10000):
            if off + 4 + _CENTRAL_FIELDS_LEN > len(data) or not data.startswith(PK_CENTRAL, off):
                break
            (_vmade, _vneed, _flags, method, _mt, _md, crc32, csize, usize,
             nlen, xlen, clen, _dno, _ia, _ea, loff) = struct.unpack_from(
                _CENTRAL_FIELDS, data, off + 4)
            name = data[off + 4 + _CENTRAL_FIELDS_LEN :
                        off + 4 + _CENTRAL_FIELDS_LEN + nlen].decode("utf-8", "replace")
            entry = _read_local(data, name, loff)
            if entry is None:
                break
            # The central directory is authoritative for CRC and sizes.
            entry.method = method or entry.method
            entry.crc32 = crc32 or entry.crc32
            entry.csize = csize or entry.csize
            entry.usize = usize or entry.usize
            found.append(entry)
            off += 4 + _CENTRAL_FIELDS_LEN + nlen + xlen + clen
        if found and len(found) == (total or len(found)):
            return found, eocd_off
    raise TnsError("could not parse the central directory")


def build_local_header(name, method, crc32, csize, usize, first, mtime, mdate):
    raw = name.encode()
    fields = struct.pack(_LOCAL_FIELDS, VERSION_NEEDED, 0, method, mtime, mdate,
                         crc32, csize, usize, len(raw), 0)
    return (TIMLP_MAGIC if first else PK_LOCAL) + fields + raw


def build_central_header(entry, crc, csize, usize, loff):
    raw = entry.name.encode()
    return PK_CENTRAL + struct.pack(
        _CENTRAL_FIELDS, VERSION_NEEDED, VERSION_NEEDED, 0, entry.method,
        entry.mtime, entry.mdate, crc, csize, usize, len(raw), 0, 0, 0, 0, 0, loff,
    ) + raw


def write_tns(entries) -> bytes:
    """Serialize entries into a valid TNS container."""
    out = bytearray()
    central = bytearray()
    count = 0
    for entry in entries:
        if entry.method == 8:
            crc = zlib.crc32(entry.payload) & 0xFFFFFFFF
            usize = len(entry.payload)
            if entry.dirty:
                blob = deflate(entry.payload)
            else:
                # Untouched page: reuse the original compressed bytes verbatim so
                # the rebuilt document differs from the base only where it must.
                blob = entry.blob
        elif entry.method == 13:
            # Copied verbatim. The recorded CRC/usize describe the decoded XML,
            # which we never touch, so both must be carried over unchanged.
            blob = entry.blob
            crc = entry.crc32
            usize = entry.usize
        else:
            raise TnsError("unsupported method %d for %s" % (entry.method, entry.name))

        mtime = entry.mtime or DOS_TIME
        mdate = entry.mdate or DOS_DATE
        first = count == 0
        header = build_local_header(entry.name, entry.method, crc, len(blob),
                                    usize, first, mtime, mdate)
        loff = len(out)
        out += header
        out += blob
        central += build_central_header(entry, crc, len(blob), usize, loff)
        count += 1

    cd_off = len(out)
    out += central
    out += TIPD_EOCD + struct.pack("<HHHHIIH", 0, 0, count, count,
                                   len(central), cd_off, 0)
    return bytes(out)


def check_model_compat(meta_path):
    """Refuse to build unless the exported model matches the installed document."""
    meta = json.loads(pathlib.Path(meta_path).read_text())
    problems = []
    if int(meta.get("format", -1)) != FORMAT_SUPPORTED:
        problems.append("format is %s, expected %s" % (meta.get("format"), FORMAT_SUPPORTED))
    if int(meta.get("model_id", -1)) != MODEL_ID_SUPPORTED:
        problems.append("model_id is %s, expected %s" % (meta.get("model_id"), MODEL_ID_SUPPORTED))
    if problems:
        raise TnsError(
            "the exported model no longer matches the model installed in the base "
            "document (%s); rebuild the base document by hand instead" % "; ".join(problems)
        )
    return meta


def main(argv=None):
    ap = argparse.ArgumentParser(description="Build a CalcGPT 3 ready-to-run .tns")
    ap.add_argument("--base", required=True, help="base .tns document to start from")
    ap.add_argument("--out", required=True, help="output .tns path")
    ap.add_argument("--runtime", required=True, help="tinylm.py source to embed")
    ap.add_argument("--replace", nargs="*", default=[], metavar="NAME=PATH",
                    help="replace an existing page's content, e.g. tinydata.py=path")
    ap.add_argument("--meta", help="calculator/model_meta.json, checked for compatibility")
    ap.add_argument("--no-verify", dest="verify", action="store_false", default=True,
                    help="skip re-parsing the output")
    ap.add_argument("-q", "--quiet", action="store_true", help="suppress progress output")
    args = ap.parse_args(argv)

    if args.quiet:
        # Mirror the silence used elsewhere in this project: swap the builtin for
        # the duration of the build, then restore it.
        real_print = builtins.print

        def silent(*a, **k):
            pass

        builtins.print = silent
        try:
            return _build(args)
        finally:
            builtins.print = real_print
    return _build(args)


def _build(args):

    base = pathlib.Path(args.base)
    data = base.read_bytes()
    entries, _eocd = parse(data)
    by_name = {e.name: e for e in entries}

    print("base: %s (%d bytes)" % (base, len(data)))
    for e in entries:
        kind = "TI-encrypted" if e.method == 13 else "plain deflate"
        print("  %-14s method=%-2d %-13s stored=%d" % (e.name, e.method, kind, e.csize))

    if args.meta:
        meta = check_model_compat(args.meta)
        print("model_meta: format=%s build=%s model_id=%s -> reusing the installed "
              "model data unchanged" % (meta["format"], meta.get("build"), meta["model_id"]))

    for e in entries:
        e.load(data)

    if "tinylm.py" not in by_name:
        raise TnsError("base document has no tinylm.py page to replace")

    runtime = pathlib.Path(args.runtime).read_text()
    old = by_name["tinylm.py"].payload
    by_name["tinylm.py"].payload = runtime.encode()
    by_name["tinylm.py"].dirty = True
    print("tinylm.py: %d -> %d bytes" % (len(old), len(runtime)))

    for spec in args.replace:
        if "=" not in spec:
            raise TnsError("--replace expects NAME=PATH, got %r" % spec)
        name, path = spec.split("=", 1)
        if name not in by_name:
            raise TnsError(
                "cannot add a new page %r: a page only appears in the TI-Nspire UI "
                "if Problem1.xml holds a matching card, and that XML is TI-encrypted "
                "and cannot be edited safely" % name
            )
        text = pathlib.Path(path).read_text()
        prev = len(by_name[name].payload)
        by_name[name].payload = text.encode()
        by_name[name].dirty = True
        print("%s: %d -> %d bytes" % (name, prev, len(text)))

    entries.sort(key=lambda e: (e.name != "Document.xml", e.name != "Problem1.xml",
                                e.name != "tinylm.py", e.name))

    blob = write_tns(entries)
    out_path = pathlib.Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_bytes(blob)
    print("wrote %s (%d bytes, %+.1f%%)" % (out_path, len(blob),
                                            100.0 * (len(blob) - len(data)) / len(data)))

    if not args.verify:
        return 0

    check, _ = parse(blob)
    if [e.name for e in check] != [e.name for e in entries]:
        raise TnsError("entry order changed on re-parse")
    expected = {e.name: e for e in entries}
    for e in check:
        e.load(blob)
        want = expected[e.name]
        if e.method == 8:
            if e.payload != want.payload:
                raise TnsError("page payload mismatch after rebuild: %s" % e.name)
            if (zlib.crc32(e.payload) & 0xFFFFFFFF) != e.crc32:
                raise TnsError("page CRC mismatch after rebuild: %s" % e.name)
            if not want.dirty and e.blob != want.blob:
                raise TnsError("untouched page was re-encoded: %s" % e.name)
        else:
            if e.blob != want.blob:
                raise TnsError("TI-encrypted entry changed: %s" % e.name)
            if e.crc32 != want.crc32 or e.usize != want.usize:
                raise TnsError("TI-encrypted entry metadata changed: %s" % e.name)
    pages = sum(1 for e in check if e.method == 8)
    print("verified: %d entries; %d pages round-trip exactly; %d TI-encrypted "
          "entries byte-identical" % (len(check), pages, len(check) - pages))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except TnsError as exc:
        print("error: %s" % exc, file=sys.stderr)
        sys.exit(1)
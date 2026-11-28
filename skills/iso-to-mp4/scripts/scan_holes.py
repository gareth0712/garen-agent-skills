#!/usr/bin/env python3
"""Find damaged regions (download holes) in the m2ts clips of Blu-ray ISOs / BDMV folders BEFORE converting.

A damaged Baidu download extracts with 7z rc 0 and the right size; libbluray then logs "Skipping broken unit" and
ffmpeg ends early with exit 0. Two kinds of damage are reported, each as its own run list:
  zeros     units that are entirely 0x00 (the usual hole)
  bad-sync  units that are NOT all zero but fail the sync check: a healthy 6144-byte unit is 32 source packets of
            192 bytes and every packet has 0x47 at byte 4. (2026-11-28: a 41.9 MB non-zero damaged region at
            offset 26905884672..26947829760 was missed by the zero-only scan and found only when an encode stopped
            after 19.4 s.) Zero units are NOT counted again under bad-sync, so the two lists never overlap.

usage: scan_holes.py [--clips 00001,00002] [--min-kb 96] [--no-bad-sync] [--7z PATH] PATH [PATH ...]
  PATH         an .iso, a folder containing BDMV, or a folder holding several of either (searched recursively)
  --clips      only these clips (take them from the playlist `survey` chose); default = every BDMV/STREAM/*.m2ts
  --min-kb     shortest run to report (default 96 KB = 16 units)
  --no-bad-sync  only look for zero runs
Output per clip: size, 7z rc, then "zero runs" and "bad-sync runs" as "<percent of file>:<MB>(@start-end byte offsets)".
Exit code: 1 if any run found or any 7z rc != 0, else 0.
"""
import argparse
import shutil
import subprocess
import sys
from pathlib import Path

UNIT = 6144  # 32 x 192-byte source packets; holes are multiples of it


def find_sources(root: Path):
    if root.is_file() and root.suffix.lower() == ".iso":
        yield root
        return
    for iso in sorted(root.rglob("*.iso")):
        yield iso
    for b in sorted(root.rglob("BDMV")):
        if b.is_dir() and (b / "STREAM").is_dir():
            yield b / "STREAM"


def clip_names(sevenz: str, iso: Path):
    out = subprocess.run([sevenz, "l", "-ba", "-slt", str(iso), "BDMV/STREAM/*.m2ts"], capture_output=True,
                         text=True, errors="replace").stdout
    return sorted({Path(l.split(" = ", 1)[1].strip().replace("\\", "/")).stem
                   for l in out.splitlines() if l.startswith("Path = ") and l.lower().endswith(".m2ts")})


def damage_runs(stream, min_units: int, bad_sync: bool = True):
    """Return (total_bytes, zero_runs, bad_sync_runs); runs are (start, end) of at least min_units * UNIT bytes."""
    zero = bytes(UNIT)
    pos = 0
    cur = {"zeros": None, "bad-sync": None}
    runs = {"zeros": [], "bad-sync": []}

    def update(kind, flag, at):
        if flag and cur[kind] is None:
            cur[kind] = at
        elif not flag and cur[kind] is not None:
            runs[kind].append((cur[kind], at))
            cur[kind] = None

    while True:
        chunk = stream.read(UNIT * 1024)
        if not chunk:
            break
        for o in range(0, len(chunk), UNIT):
            unit = chunk[o:o + UNIT]
            is_zero = unit == zero[:len(unit)]
            bad = (bad_sync and not is_zero and len(unit) == UNIT
                   and any(unit[i * 192 + 4] != 0x47 for i in range(32)))
            update("zeros", is_zero, pos + o)
            update("bad-sync", bad, pos + o)
        pos += len(chunk)
    for kind in cur:
        if cur[kind] is not None:
            runs[kind].append((cur[kind], pos))
    keep = lambda rs: [(a, b) for a, b in rs if b - a >= UNIT * min_units]
    return pos, keep(runs["zeros"]), keep(runs["bad-sync"])


def describe(runs, total):
    return ", ".join(f"{x / max(total, 1) * 100:.1f}%:{(y - x) / 1e6:.1f}MB(@{x}-{y})" for x, y in runs) or "none"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="+", type=Path)
    ap.add_argument("--clips", help="comma list of clip names, e.g. 00001,00002")
    ap.add_argument("--min-kb", type=int, default=96)
    ap.add_argument("--no-bad-sync", action="store_true", help="only look for all-zero runs")
    ap.add_argument("--7z", dest="sevenz", default=shutil.which("7z") or r"C:\Program Files\7-Zip\7z.exe")
    a = ap.parse_args()
    min_units = max(1, a.min_kb * 1024 // UNIT)
    found = False
    for root in a.paths:
        for src in find_sources(root):
            is_dir = src.is_dir()
            if a.clips:
                clips = a.clips.split(",")
            else:
                clips = sorted(p.stem for p in src.glob("*.m2ts")) if is_dir else clip_names(a.sevenz, src)
            label = (src.parent.parent if is_dir else src).stem[:60]
            for clip in clips:
                if is_dir:
                    with open(src / f"{clip}.m2ts", "rb") as f:
                        total, zr, br = damage_runs(f, min_units, not a.no_bad_sync)
                    rc = 0
                else:
                    p = subprocess.Popen([a.sevenz, "e", "-so", "-bd", str(src), f"BDMV\\STREAM\\{clip}.m2ts"],
                                         stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
                    total, zr, br = damage_runs(p.stdout, min_units, not a.no_bad_sync)
                    rc = p.wait()
                found |= bool(zr) or bool(br) or rc != 0
                line = f"{label} | {clip}.m2ts {total / 1e9:.2f} GB 7z-rc={rc} | zeros>={a.min_kb}KB: {describe(zr, total)}"
                if not a.no_bad_sync:
                    line += f" | bad-sync>={a.min_kb}KB: {describe(br, total)}"
                print(line, flush=True)
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main())

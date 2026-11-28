#!/usr/bin/env python3
"""Find all-zero runs (download holes) in the m2ts clips of Blu-ray ISOs / BDMV folders BEFORE converting.

A damaged Baidu download extracts with 7z rc 0 and the right size; libbluray then logs "Skipping broken unit" and
ffmpeg ends early with exit 0. Streaming the clips and looking for zero runs finds it in minutes.

usage: scan_holes.py [--clips 00001,00002] [--min-kb 96] [--7z PATH] PATH [PATH ...]
  PATH     an .iso, a folder containing BDMV, or a folder holding several of either (searched recursively)
  --clips  only these clips (take them from the playlist `survey` chose); default = every BDMV/STREAM/*.m2ts
Output per clip: size, 7z rc, zero runs >= min-kb as "<percent of file>:<MB>(@byte offset)". Exit 1 if any hole.
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


def zero_runs(stream, min_units: int):
    """Return (total_bytes, [(start, end)]) for zero runs of at least min_units * UNIT bytes."""
    zero = bytes(UNIT)
    pos, start, runs = 0, None, []
    while True:
        chunk = stream.read(UNIT * 1024)
        if not chunk:
            break
        for o in range(0, len(chunk), UNIT):
            unit = chunk[o:o + UNIT]
            if unit == zero[:len(unit)]:
                if start is None:
                    start = pos + o
            elif start is not None:
                runs.append((start, pos + o))
                start = None
        pos += len(chunk)
    if start is not None:
        runs.append((start, pos))
    return pos, [(a, b) for a, b in runs if b - a >= UNIT * min_units]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="+", type=Path)
    ap.add_argument("--clips", help="comma list of clip names, e.g. 00001,00002")
    ap.add_argument("--min-kb", type=int, default=96)
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
                        total, runs = zero_runs(f, min_units)
                    rc = 0
                else:
                    p = subprocess.Popen([a.sevenz, "e", "-so", "-bd", str(src), f"BDMV\\STREAM\\{clip}.m2ts"],
                                         stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
                    total, runs = zero_runs(p.stdout, min_units)
                    rc = p.wait()
                found |= bool(runs) or rc != 0
                desc = ", ".join(f"{x / max(total, 1) * 100:.1f}%:{(y - x) / 1e6:.0f}MB(@{x})" for x, y in runs) or "none"
                print(f"{label} | {clip}.m2ts {total / 1e9:.2f} GB 7z-rc={rc} | zero runs>={a.min_kb}KB: {desc}", flush=True)
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main())

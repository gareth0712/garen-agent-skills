#!/usr/bin/env python3
"""Rename + file verified MP4s into a Jellyfin folder and park their finished source folders. Dry run by default.

usage: plan_moves.py --map moves.json|moves.csv --converted-dir DIR --trash-dir DIR --manifest moves.jsonl [--apply]
       plan_moves.py --undo moves.jsonl [--apply]

Mapping rows (JSON list of objects, or CSV with a header):
  mp4     path of the verified output
  name    final file name, e.g. "Batman Begins 蝙蝠俠—俠影之謎 [2005] [4K].mp4"   (must end .mp4, no  < > : " / \\ | ? *)
  folder  (optional) the source folder that holds the disc; moved to --trash-dir once every disc in it has a mapped mp4
  Several rows may share one folder (a multi-disc folder): it moves only after all of them are mapped.

Refuses (nothing is moved, exit 1): a missing mp4; an existing destination; mp4 and destination on different drives
(rename only, never copy); a folder that still holds a disc whose output is not in the mapping (an unconverted disc);
a folder that contains the destination; an unsafe name.
Every move is appended to the manifest (one JSON line each) so --undo can reverse it. Never overwrites.
"""
import argparse
import csv
import json
import os
import sys
import time
from pathlib import Path

BAD = set('<>:"/\\|?*')


def load_rows(p: Path):
    if p.suffix.lower() == ".csv":
        with open(p, encoding="utf-8-sig", newline="") as f:
            return list(csv.DictReader(f))
    return json.loads(p.read_text(encoding="utf-8"))


def discs_in(folder: Path):
    """(disc path, expected output mp4) for every ISO / BDMV / VIDEO_TS under folder."""
    for iso in folder.rglob("*.iso"):
        yield iso, iso.with_suffix(".mp4")
    for kind in ("BDMV", "VIDEO_TS"):
        for d in folder.rglob(kind):
            if d.is_dir():
                yield d, d.parent / (d.parent.name + ".mp4")


def same_drive(a: Path, b: Path) -> bool:
    if os.name == "nt":
        return os.path.splitdrive(str(a.resolve()))[0].lower() == os.path.splitdrive(str(b.resolve()))[0].lower()
    probe = b
    while not probe.exists():
        probe = probe.parent
    return os.stat(a).st_dev == os.stat(probe).st_dev


def plan(rows, converted: Path, trash: Path):
    errors, moves, folders = [], [], {}
    mapped = {Path(r["mp4"]).resolve() for r in rows}
    seen_dst = set()
    for r in rows:
        mp4, name = Path(r["mp4"]), r["name"]
        dst = converted / name
        if not mp4.is_file():
            errors.append(f"MISSING mp4: {mp4}")
            continue
        if not name.lower().endswith(".mp4") or BAD & set(name):
            errors.append(f"UNSAFE name (must end .mp4, none of < > : \" / \\ | ? *): {name!r}")
            continue
        if dst.exists() or dst in seen_dst:
            errors.append(f"DESTINATION EXISTS: {dst}")
            continue
        if not same_drive(mp4, converted):
            errors.append(f"DIFFERENT DRIVE (rename only): {mp4} -> {converted}")
            continue
        seen_dst.add(dst)
        moves.append((mp4, dst))
        if r.get("folder"):
            folders.setdefault(Path(r["folder"]), []).append(mp4)
    folder_moves = []
    for folder, _ in folders.items():
        if not folder.is_dir():
            errors.append(f"MISSING folder: {folder}")
            continue
        unconverted = [d for d, out in discs_in(folder) if out.resolve() not in mapped]
        if unconverted:
            errors.append(f"UNCONVERTED DISC still in {folder}: " + ", ".join(str(d) for d in unconverted))
            continue
        if not any(True for _ in discs_in(folder)):
            errors.append(f"NO DISC found in {folder} (refusing to trash a folder that is not a disc folder)")
            continue
        if converted.resolve().is_relative_to(folder.resolve()):
            errors.append(f"converted dir is inside {folder}")
            continue
        target = trash / folder.name
        if target.exists():
            errors.append(f"TRASH TARGET EXISTS: {target}")
            continue
        folder_moves.append((folder, target))
    return errors, moves, folder_moves


def undo(manifest: Path, apply: bool) -> int:
    lines = [json.loads(l) for l in manifest.read_text(encoding="utf-8").splitlines() if l.strip()]
    for rec in reversed(lines):
        src, dst = Path(rec["to"]), Path(rec["from"])
        if not src.exists() or dst.exists():
            print(f"SKIP (missing source or occupied target): {src} -> {dst}")
            continue
        print(f"undo: {src} -> {dst}")
        if apply:
            os.rename(src, dst)
    if not apply:
        print("dry run; add --apply")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--map", type=Path)
    ap.add_argument("--converted-dir", type=Path)
    ap.add_argument("--trash-dir", type=Path)
    ap.add_argument("--manifest", type=Path)
    ap.add_argument("--undo", type=Path)
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    if a.undo:
        return undo(a.undo, a.apply)
    if not (a.map and a.converted_dir and a.trash_dir and a.manifest):
        ap.error("--map, --converted-dir, --trash-dir and --manifest are required")
    errors, moves, folder_moves = plan(load_rows(a.map), a.converted_dir, a.trash_dir)
    for m, d in moves:
        print(f"mp4    {m}\n   -> {d}")
    for f, t in folder_moves:
        print(f"folder {f}\n   -> {t}")
    if errors:
        print("\nREFUSED:")
        for e in errors:
            print("  " + e)
        return 1
    if not a.apply:
        print(f"\ndry run: {len(moves)} mp4, {len(folder_moves)} folders; add --apply")
        return 0
    a.converted_dir.mkdir(parents=True, exist_ok=True)
    a.trash_dir.mkdir(parents=True, exist_ok=True)
    a.manifest.parent.mkdir(parents=True, exist_ok=True)
    with open(a.manifest, "a", encoding="utf-8") as log:
        for src, dst in moves + folder_moves:
            size = src.stat().st_size if src.is_file() else None
            os.rename(src, dst)
            if size is not None:
                assert dst.stat().st_size == size, dst
            log.write(json.dumps({"at": time.strftime("%Y-%m-%d %H:%M:%S"), "from": str(src), "to": str(dst),
                                  "size": size}, ensure_ascii=False) + "\n")
            log.flush()
            print("moved", dst)
    return 0


if __name__ == "__main__":
    sys.exit(main())

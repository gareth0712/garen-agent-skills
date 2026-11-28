#!/usr/bin/env python3
"""Join hole-repaired MP4 parts into one MP4 (stream copy) with playlist chapters and no timestamp collision at joins.

Why the pad: an encode that stopped at a hole ends mid-GOP, so its last displayed frame sits up to ~0.125 s after the
stream's duration; without a pad that frame shares a pts with the first frames of the next part (decoding across the join
logs `non monotonically increasing dts`). Pad per part (except the last) =
max(0.125, largest video pts in the last 10 s - video duration + 0.0834), written as `duration` in the concat list.

usage: concat_parts.py --repo <checkout containing modules/disc_convert> DISC.iso OUT.mp4
           --part PART1.mp4 0 --part PART2.mp4 3238.5 --part PART3.mp4 3264
  --part FILE FILM_START   parts in order; FILM_START = playlist time (s) at which that part's content starts
  --repo                   checkout whose modules/disc_convert supplies playlist chapters, audio plan and verify
Writes OUT.mp4.partial, verifies (module verify + clean decode of video and audio across every join), then renames to OUT.
On failure leaves the .partial and exits 1. Refuses to overwrite OUT. Prints the film seconds missing at each join.
Env: TMD_RUNTIME_ROOT may be needed by the module's context (log dir).
"""
import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--repo", required=True, type=Path)
    ap.add_argument("--part", nargs=2, action="append", metavar=("FILE", "FILM_START"), required=True)
    ap.add_argument("disc", type=Path)
    ap.add_argument("out", type=Path)
    a = ap.parse_args()
    sys.path.insert(0, str(a.repo))
    from modules.disc_convert import convert, discs, ffmpeg_cmd, runner, verify
    from modules.disc_convert.cli import _make_context

    out = a.out
    if out.exists():
        print("refusing to overwrite", out)
        return 1
    files = [Path(f) for f, _ in a.part]
    film = [float(s) for _, s in a.part]
    ctx = _make_context()
    d = discs.find_discs(a.disc)[0]
    pl = convert.best_playlist(d)
    streams = discs.probe_streams(ctx.ffprobe, d.bluray_source(), pl.number)
    audio = discs.resolve_audio_indices(discs.plan_audio(pl), streams)

    def probe(args):
        return subprocess.run([ctx.ffprobe, "-v", "error", *args], capture_output=True, text=True).stdout

    def vdur(p):
        return float(probe(["-f", "mp4", "-select_streams", "v:0", "-show_entries", "stream=duration", "-of", "csv=p=0", str(p)]).strip().strip(",").split(",")[0])

    def maxpts(p, dur):
        o = probe(["-f", "mp4", "-select_streams", "v:0", "-read_intervals", f"{max(dur - 10, 0):.3f}%", "-show_entries", "packet=pts_time", "-of", "csv=p=0", str(p)])
        return max(float(x.strip(",")) for x in o.split() if x.strip(","))

    durs = [vdur(p) for p in files]
    pads = [max(0.125, maxpts(p, dd) - dd + 0.0834) for p, dd in zip(files[:-1], durs[:-1])] + [0.0]
    span = [dd + pd for dd, pd in zip(durs, pads)]
    outstart = [sum(span[:i]) for i in range(len(files))]
    total = sum(span)
    for i in range(len(files) - 1):
        lost = film[i + 1] - (film[i] + durs[i])
        print(f"join {i + 1}: at output {outstart[i + 1]:.3f}s pad {pads[i]:.3f}s film time lost {lost:.3f}s")
    chs, valid = [], [c for c in pl.chapters if c < pl.duration]
    for c in valid:
        for k in range(len(files)):
            if film[k] <= c < film[k] + durs[k]:
                chs.append(outstart[k] + c - film[k])
                break
    print(f"chapters kept {len(chs)} of {len(valid)}; total {total:.3f}s")
    tmp = Path(tempfile.mkdtemp(prefix="concat-"))
    partial = out.with_name(out.name + ".partial")
    try:
        meta = tmp / "c.ffmeta"
        meta.write_text(ffmpeg_cmd.chapters_ffmetadata(chs, total), encoding="utf-8")
        lines = []
        for i, p in enumerate(files):
            lines.append("file '" + str(p).replace("\\", "/").replace("'", "'\''") + "'\n")
            if i < len(files) - 1:
                lines.append(f"duration {span[i]:.6f}\n")
        lst = tmp / "l.txt"
        lst.write_text("".join(lines), encoding="utf-8")
        cmd = [ctx.ffmpeg, "-hide_banner", "-nostdin", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-f", "ffmetadata", "-i", str(meta),
               "-map", "0:v:0", "-map", "0:a", "-map_chapters", "1", "-map_metadata", "-1", "-c", "copy", "-tag:v", "hvc1"]
        for i, au in enumerate(audio):
            cmd += [f"-metadata:s:a:{i}", f"language={au.lang}", f"-disposition:a:{i}", "default" if i == 0 else "0"]
        cmd += ["-movflags", "+faststart", "-f", "mp4", str(partial)]
        rc = runner.run_ffmpeg(cmd, ctx.log_dir / "disc-convert-ffmpeg-concat-parts.log")
        print("concat rc", rc)
        if rc:
            return 1
        fails = verify.verify_output(ctx.ffmpeg, ctx.ffprobe, str(partial), verify.Expect("bluray", total, tuple(x.channels for x in audio), len(chs)))
        for j in outstart[1:]:
            for k in ("0:v:0", "0:a:0"):
                e = subprocess.run([ctx.ffmpeg, "-v", "error", "-ss", f"{j - 2:.2f}", "-i", str(partial), "-map", k, "-t", "5", "-f", "null", "-"],
                                   capture_output=True, text=True, errors="replace").stderr
                e = [l for l in e.splitlines() if l.strip() and "QT chapter track" not in l]
                print(f"join {j:.2f} {k}: {'clean' if not e else e[:2]}")
                if e:
                    fails.append(f"decode errors at join {j:.2f} {k}")
        print("VERIFY FAILS:", fails)
        if fails:
            return 1
        partial.rename(out)
        print("OK", out)
        return 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())

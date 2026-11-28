#!/usr/bin/env python3
"""Hole repair helper: encode ONE part of a single-clip Blu-ray playlist with the module's exact encoder flags.

Input -ss is used, so it only works for single-clip playlists (in a multi-clip playlist it lands on undecodable data).
usage: encode_part.py --repo <checkout holding modules/disc_convert> <disc dir or iso> <tag> <partN> <ss-seconds> <t-seconds>
Writes <out stem>.<tag>-part<N>.mp4 beside the ISO. Set TMD_RUNTIME_ROOT like a normal convert run.
"""
import argparse
import shutil
import sys
import tempfile
import time
from pathlib import Path

ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
ap.add_argument("--repo", required=True, type=Path)
ap.add_argument("disc", type=Path)
ap.add_argument("tag")
ap.add_argument("n", type=int)
ap.add_argument("ss", type=float)
ap.add_argument("t", type=float)
a = ap.parse_args()
sys.path.insert(0, str(a.repo))
from modules.disc_convert import convert, discs, ffmpeg_cmd, runner  # noqa: E402
from modules.disc_convert.cli import _make_context  # noqa: E402

ctx = _make_context()
d = discs.find_discs(a.disc)[0]
pl = convert.best_playlist(d)
assert len(set(pl.clips)) == 1, "multi-clip playlist: input -ss is unsafe"
sub, _srt, note = discs.choose_subtitle(d, pl, None, convert.load_choices(ctx.choices_file).get(d.key))
streams = discs.probe_streams(ctx.ffprobe, d.bluray_source(), pl.number)
audio = discs.resolve_audio_indices(discs.plan_audio(pl), streams)
out = d.out_path()
part = out.with_name(f"{out.stem}.{a.tag}-part{a.n}.mp4")
assert not part.exists(), part
tmp = Path(tempfile.mkdtemp(prefix="holepart-"))
try:
    meta = tmp / "c.ffmeta"
    meta.write_text(";FFMETADATA1\n", encoding="utf-8")
    cmd = ffmpeg_cmd.bluray_convert_cmd(ctx.ffmpeg, d.bluray_source(), pl.number, sub, audio, str(meta),
                                        str(part) + ".partial", a.t)
    base = ffmpeg_cmd.bluray_input_args(d.bluray_source(), pl.number)
    i = cmd.index(base[0])
    assert cmd[i:i + len(base)] == base
    cmd[i:i + len(base)] = ffmpeg_cmd.bluray_input_args(d.bluray_source(), pl.number, ss=a.ss)
    ctx.log(f"HOLEFIX {a.tag} part{a.n} ss={a.ss} t={a.t} sub={note}")
    t0 = time.time()
    rc = runner.run_ffmpeg(cmd, ctx.log_dir / f"disc-convert-ffmpeg-{a.tag}-part{a.n}.log", cwd=str(tmp))
    print("rc", rc, "secs", round(time.time() - t0), flush=True)
    if rc == 0:
        Path(str(part) + ".partial").rename(part)
    sys.exit(rc)
finally:
    shutil.rmtree(tmp, ignore_errors=True)

#!/usr/bin/env python3
"""Review page for converted discs: one row per MP4 with 4 frames (20/40/60/80 %), length, size, chapters, path.

usage: gen_review.py --root <folder holding the discs> [--out <root>/_review] [--ffmpeg-dir <dir>]
                     [--reasons reasons.json] [--converted-dir converted]
  An output counts when it sits next to its ISO (<iso stem>.mp4) or inside its BDMV parent (<folder>/<folder>.mp4);
  MP4s already moved to <root>/<converted-dir> are listed too. `<name>.mp4.failed` files are listed with a reason.
  --reasons  JSON {"name substring": "why it failed"}; default text says "failed, being redone".
  HDR frames are tonemapped to SDR so the colours differ from the real picture on a TV.
Open <out>/index.html in a browser. ffmpeg/ffprobe from --ffmpeg-dir or PATH.
"""
import argparse
import html
import json
import subprocess
import sys
from pathlib import Path
from urllib.parse import quote

TONEMAP = ("zscale=t=linear:npl=100,format=gbrpf32le,tonemap=hable,"
           "zscale=p=bt709:t=bt709:m=bt709:r=tv,format=yuv420p,")


def tool(ffdir: str | None, name: str) -> str:
    return str(Path(ffdir) / name) if ffdir else name


def probe(ffprobe: str, p: Path) -> dict:
    r = subprocess.run([ffprobe, "-v", "error", "-print_format", "json", "-show_streams", "-show_format",
                        "-show_chapters", str(p)], capture_output=True)
    return json.loads(r.stdout.decode("utf-8", "replace") or "{}")


def frame(ffmpeg: str, mp4: Path, t: float, hdr: bool, dest: Path) -> bool:
    if dest.exists():
        return True
    vf = (TONEMAP if hdr else "") + "scale=640:-2"
    r = subprocess.run([ffmpeg, "-v", "error", "-nostdin", "-y", "-ss", f"{t:.1f}", "-i", str(mp4), "-frames:v", "1",
                        "-vf", vf, "-q:v", "4", str(dest)], capture_output=True)
    return r.returncode == 0 and dest.exists()


def hms(s: float) -> str:
    s = int(round(s))
    return f"{s // 3600}:{s % 3600 // 60:02d}:{s % 60:02d}"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", required=True, type=Path)
    ap.add_argument("--out", type=Path)
    ap.add_argument("--ffmpeg-dir")
    ap.add_argument("--reasons", type=Path)
    ap.add_argument("--converted-dir", default="converted")
    a = ap.parse_args()
    root = a.root
    out = a.out or root / "_review"
    img = out / "img"
    img.mkdir(parents=True, exist_ok=True)
    ffmpeg, ffprobe = tool(a.ffmpeg_dir, "ffmpeg"), tool(a.ffmpeg_dir, "ffprobe")
    reasons = json.loads(a.reasons.read_text(encoding="utf-8")) if a.reasons else {}
    srcs = [(i.with_suffix(".mp4"), i.stem) for i in root.rglob("*.iso")]
    srcs += [(b.parent / (b.parent.name + ".mp4"), b.parent.name) for b in root.rglob("BDMV") if b.is_dir()]
    srcs = [x for x in srcs if "to-be-removed" not in x[0].parts and a.converted_dir not in x[0].parts]
    srcs += [(m, m.stem) for m in (root / a.converted_dir).glob("*.mp4")]
    rows = []
    for n, (mp4, name) in enumerate(sorted(srcs, key=lambda x: str(x[0]))):
        failed = mp4.with_name(mp4.name + ".failed")
        if mp4.exists():
            info = probe(ffprobe, mp4)
            v = next((s for s in info.get("streams", []) if s.get("codec_type") == "video"), {})
            hdr = v.get("color_transfer") == "smpte2084"
            dur = float(info.get("format", {}).get("duration", 0) or 0)
            imgs = [d.name for k, fr in enumerate((0.2, 0.4, 0.6, 0.8))
                    if frame(ffmpeg, mp4, dur * fr, hdr, d := img / f"d{n:02d}_{k}.jpg")]
            rows.append(dict(name=name, ok=True, mp4=mp4, dur=dur, size=mp4.stat().st_size,
                             chapters=len(info.get("chapters", [])),
                             video=f"{v.get('width')}x{v.get('height')} {'HDR10' if hdr else 'SDR'}",
                             audio=len([s for s in info.get("streams", []) if s.get("codec_type") == "audio"]),
                             imgs=imgs))
        elif failed.exists():
            why = next((r for k, r in reasons.items() if k in name), "failed, being redone")
            rows.append(dict(name=name, ok=False, mp4=failed, why=why))
        print(("ok " if mp4.exists() else "failed ") + name, flush=True)
    ok = [r for r in rows if r["ok"]]
    parts = [f"""<!doctype html><meta charset="utf-8"><title>ISO to MP4 review</title>
<style>body{{font-family:system-ui,sans-serif;margin:24px;background:#111;color:#ddd}}
.row{{border-bottom:1px solid #333;padding:14px 0}} h2{{font-size:17px;margin:0 0 6px}}
.meta{{font-size:13px;color:#aaa;margin-bottom:8px}} .strip img{{width:24%;margin-right:.5%}}
a{{color:#6cf}} code{{font-size:12px;color:#bbb;user-select:all}} .bad{{color:#f88}}</style>
<h1>{len(ok)} converted, {len(rows) - len(ok)} not finished</h1>
<p>4 frames per film (20/40/60/80 % of the length). HDR is tonemapped, so colours differ from a real TV.
Click the name to play in the browser, or copy the path into a player.</p>"""]
    for r in rows:
        href = quote(r["mp4"].relative_to(root).as_posix())
        if r["ok"]:
            parts.append(f"""<div class="row"><h2><a href="../{href}">{html.escape(r['name'])}</a></h2>
<div class="meta">{hms(r['dur'])} · {r['size'] / 1e9:.2f} GB · {r['video']} · {r['chapters']} chapters · {r['audio']} audio</div>
<div class="strip">{''.join(f'<img src="img/{i}">' for i in r['imgs'])}</div>
<code>{html.escape(str(r['mp4']))}</code></div>""")
        else:
            parts.append(f"""<div class="row"><h2 class="bad">FAILED {html.escape(r['name'])}</h2>
<div class="meta">{html.escape(r['why'])}</div><code>{html.escape(str(r['mp4']))}</code></div>""")
    (out / "index.html").write_text("\n".join(parts), encoding="utf-8")
    print(out / "index.html")
    return 0


if __name__ == "__main__":
    sys.exit(main())

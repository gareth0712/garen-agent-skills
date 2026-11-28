---
name: iso-to-mp4
description: Convert Blu-ray / UHD / DVD ISOs (or BDMV folders) to playable MP4, then verify, review, name and file them. Use when the user has disc ISOs or BDMV folders to convert, mentions burned-in Chinese subtitles, a disc converting short or slowly, or zero-filled holes in a downloaded ISO.
---

# ISO to MP4

Runbook for `python -m modules.disc_convert survey|samples|convert` (module guide with traps 1-11: `modules/disc_convert/CLAUDE.md` in the repo that holds the module; read it before touching the module). Set `TMD_RUNTIME_ROOT` to the runtime folder. Scripts here are in `scripts/` (each prints usage with `--help`). Needs ffmpeg + ffprobe (PATH, or `$FFMPEG` / `$FFPROBE`) and 7z (PATH or `--7z`). Example paths below (`E:\...`) are only examples.

Done = every disc has a verified MP4 you have looked at, named for Jellyfin, filed, and its source parked in `to-be-removed`.

## Order of work (each step ends on its check)

1. **survey**: `python -m modules.disc_convert survey <root>`. Check: every Blu-ray lists a 45 min - 4 h playlist and its zho (Chinese) PGS PIDs; every DVD lists a VTS and cells.
2. **Pick the subtitle track per disc**: `samples <iso> --at N` (N = a second with a subtitle on screen) writes one 6-frame strip per zho track. Look at each; the owner wants the Traditional / Hong Kong track. Write the pick into the choices file (`<runtime>/data/disc-convert-choices.json`) or pass `--sub-pid 0x12ae`. A disc with more than one zho track and no choice is skipped, never guessed. Check: every such disc has a choice, written after seeing a traditional-character frame.
3. **Scan every ISO for all-zero holes BEFORE converting** (cheap, minutes per disc): `python scripts/scan_holes.py --clips <clips of the chosen playlist> <root>`. Baidu-downloaded ISOs: 3 of 13 had zero runs of 157-786 MB; 7z extracts them with rc 0 and the right size. libbluray then logs `Skipping broken unit` and ffmpeg ends EARLY with exit 0, so otherwise only a duration check catches it, after hours of encoding. Check: exit 0, or a hole list per disc. A disc with a hole goes to "Hole repair" below (or is re-downloaded), not into the batch.
4. **convert**: `convert <root>` (one run at a time; STOP flag stops between discs). Watch the per-disc ffmpeg log for `speed=` (see Traps). Check: `SUMMARY` line per disc.
5. **Verify each output** with `scripts/verify_bd.sh <exact.mp4> <iso> <playlist> <pgs-pid> <that disc's ffmpeg log> <playlist-seconds>`. It needs the explicit log path and exact mp4 path (an old version picked the second-newest log, sometimes the wrong disc, and a glob also matched `.sample.mp4`). Then LOOK at the frame it writes: Chinese subtitle present, traditional, readable. Check: `VERIFY OK` and the frame seen. DVDs: duration within 2 s, 10 seek points (module `verify`), and look at one frame.
6. **Review page**: `python scripts/gen_review.py --root <root>` (4 frames per film + path). Hand the owner the `index.html` path.
7. **Name + move** (skill `jellyfin-media-naming`, `scripts/plan_moves.py`): verified MP4 to `<root>\converted\<Jellyfin name>`; its whole source folder to `<root>\to-be-removed\` only when every disc in that folder has a verified MP4. Never move an in-progress or unconverted disc. The manifest (JSONL) is the undo record. The module's tree scan skips `to-be-removed` and `converted`.

## Settings used (2026-11-27/28, 23 discs: 13 UHD Blu-ray + 10 DVD)

- UHD: `hevc_nvenc` p7, VBR 3M (max 12M), main10, HDR10 tags, `-tag:v hvc1`, AAC 5.1 384k (stereo sources stay stereo 160k). PGS overlay dimmed to 60 % (`colorchannelmixer` 0.6): an undimmed PGS white on a PQ frame is about 10,000 nits; owner approved 0.6 (knob: `SUB_DIM` in `ffmpeg_cmd.py`).
- DVD: `bwdif` + `libx264` crf 20, 640x480. VOBs are streamed from the ISO through `7z e -so` into ffmpeg stdin (ffmpeg's `dvdvideo` demuxer failed on these discs). A 7z feed failure once killed one disc (exit 99): rerun it.
- `-t` is always the playlist length. UHD runs about 1.4-1.6x real time on an RTX 5090, 2.5-3.8 GB per film, one 4K film 70-90 min. A DVD 120 s sample takes about 9 s.

## Traps that cost hours (full list: module guide)

- **Multi-clip playlist (trap 11)**: PGS overlay + audio in one ffmpeg ran 0.16x and grew to 35 GB RAM. The module now splits video / audio / mux for multi-clip playlists. Detect: `speed=0.1x` in `<runtime>/log/disc-convert-ffmpeg-*.log`, or ffmpeg memory in the tens of GB. Stop it; do not wait. The cause is inferred from one disc.
- **Short output with exit 0**: broken units. Compare duration with the playlist length every time.
- **Subtitle language is only in the playlist table**: map PGS by PID, never by order. Two zho tracks may be simplified and traditional; only a rendered frame tells.
- **TrueHD PID is two ffmpeg streams** (truehd + ac3 core): map audio by resolved stream index, not PID.
- **Fake playlists** (100 repeats of one clip) and the same cut under several playlist numbers (lowest number wins ties).
- **PGS canvas**: ffmpeg cannot probe it; `-canvas_size 1920x1080` before `-i`.
- **Finding a check frame**: PGS packet pts include the playlist `start_time` (output time = pts - start_time). `ffprobe -read_intervals "%+400"`, packets > 2000 bytes; the first big cue can be a studio logo, probe further in (`verify_bd.sh` does the first pass).
- Windows/SMB: close file handles before moving; `.mp4.partial` needs `-f mp4`; keep names short.

## Hole repair (first run in progress 2026-11-28; update this section from its report)

Owner chose option A (keep what was encoded). Option B = re-download the ISO.

1. Keep part 1: the `<stem>.mp4.failed` (it ends at the hole). Note the duration it reaches and the hole byte range from `scan_holes.py` (percent of the clip x playlist length gives the rough time; confirm by probing).
2. Encode from just after the hole with `scripts/encode_part.py --repo <module checkout> <iso> <tag> 2 <ss> <t>` (input `-ss`, same encoder flags and subtitle pick). Single-clip playlists only: input `-ss` inside a multi-clip playlist lands on undecodable data.
3. Concatenate `-c copy`, shift the chapter marks after the join, verify across each join (seek a few seconds either side; subtitle still on, audio in sync) and the total duration = playlist length minus the cut hole.
4. A film with a hole has a gap of the hole's length; tell the owner how many seconds of film are missing.

Small test clips around a hole: `7z e -so disc.iso "BDMV\STREAM\00001.m2ts" | python scripts/cut_m2ts.py <start> <len> out.m2ts`.

## Learnings log

After EVERY disc job: append new obstacles and fixes here (dated) and to the module guide in the same task, then commit and push the skills repo. Keep entries to what the source cannot tell you.

- 2026-11-28: first 23-disc job. Added the pre-convert hole scan (3 of 13 ISOs damaged), the multi-clip 3-pass split (trap 11), explicit log/mp4 arguments for `verify_bd.sh`, and the moves rule (converted -> `converted`, finished folder -> `to-be-removed`, manifest for undo).

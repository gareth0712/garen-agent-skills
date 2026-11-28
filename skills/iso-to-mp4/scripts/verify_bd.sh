#!/bin/bash
# Verify one converted Blu-ray MP4 and grab a tonemapped frame at the first subtitle cue.
# usage: verify_bd.sh <exact.mp4> <source.iso|BDMV-parent-dir> <playlist-number> <pgs-pid|-> <ffmpeg-log> [expected-seconds] [out.jpg]
#   exact.mp4        the exact output path (never a glob: it also matches <stem>.sample.mp4)
#   ffmpeg-log       the per-disc ffmpeg log of THIS run (never "second newest log": that picked the wrong disc once)
#   pgs-pid          e.g. 0x12ad, or - to skip the subtitle frame
#   expected-seconds playlist length; if given, a duration gap > 2 s fails (libbluray skips broken units and ffmpeg
#                    then ends EARLY with exit 0, so this is the only check that catches a damaged source)
# ffmpeg/ffprobe come from $FFMPEG / $FFPROBE or PATH. Exit 0 = all checks passed, 1 = a check failed.
set -u
if [ "${1:-}" = "--help" ] || [ "${1:-}" = "-h" ]; then sed -n '2,10p' "$0"; exit 0; fi
if [ $# -lt 5 ]; then sed -n '2,10p' "$0"; exit 2; fi
F="$1"; ISO="$2"; PL="$3"; PID="$4"; LOG="$5"; EXPECT="${6:-}"; JPG="${7:-${F%.mp4}.subcheck.jpg}"
FFMPEG="${FFMPEG:-ffmpeg}"; FFPROBE="${FFPROBE:-ffprobe}"
[ -f "$F" ] || { echo "FAIL: no such file $F"; exit 1; }
[ -f "$LOG" ] || { echo "FAIL: no such ffmpeg log $LOG"; exit 1; }
rc=0
"$FFPROBE" -v error -show_entries format=duration,size,bit_rate:stream=codec_name,profile,width,height,pix_fmt,color_transfer,channels -of compact "$F" 2>&1 | grep -v QT
echo "chapters: $("$FFPROBE" -v error -show_chapters -of csv "$F" 2>/dev/null | wc -l)"
BROKEN=$(grep -c 'Skipping broken unit' "$LOG")
echo "log: $LOG broken_units=$BROKEN"
if [ "$BROKEN" -gt 0 ]; then echo "FAIL: source has broken units (zero-filled holes): output is short or has a gap"; rc=1; fi
D=$("$FFPROBE" -v error -show_entries format=duration -of csv=p=0 "$F")
if [ -n "$EXPECT" ]; then
  awk -v d="$D" -v e="$EXPECT" 'BEGIN{x=d-e; if(x<0)x=-x; print "duration " d " expected " e " diff " x; exit !(x<=2)}' || { echo "FAIL: duration differs by more than 2 s"; rc=1; }
fi
for t in $(awk -v d="$D" 'BEGIN{printf "%d %d %d", (d>900?900:d/4), d/2, d-120}'); do
  "$FFMPEG" -v error -ss "$t" -i "$F" -frames:v 1 -f null - 2>/dev/null; r=$?
  echo "seek $t rc=$r"; if [ $r -ne 0 ]; then rc=1; fi
done
if [ "$PID" != "-" ]; then
  ST=$("$FFPROBE" -v error -playlist "$PL" -show_entries format=start_time -of csv=p=0 "bluray:$ISO" 2>/dev/null)
  # output time = packet pts - playlist start_time; cues are PGS packets > 2000 bytes; the first can be a studio logo
  CUE=$("$FFPROBE" -v error -playlist "$PL" -read_intervals "%+400" -select_streams "i:$PID" -show_entries packet=pts_time,size -of csv=p=0 "bluray:$ISO" 2>/dev/null | awk -F, '$2>2000{print $1; exit}')
  if [ -n "$CUE" ] && [ -n "$ST" ]; then
    T=$(awk -v c="$CUE" -v s="$ST" 'BEGIN{printf "%.2f", c-s+1.0}')
    echo "start=$ST cue=$CUE -> output time $T"
    "$FFMPEG" -v error -ss "$T" -i "$F" -frames:v 1 -vf "zscale=t=linear:npl=100,tonemap=hable,zscale=t=bt709:m=bt709:r=tv,format=yuv420p,scale=960:-2" -y "$JPG" 2>&1 | grep -v QT
    echo "frame (look at it: Chinese subtitle present, traditional, readable?): $JPG"
  else
    echo "WARN: no subtitle cue found in the first 400 s; probe further (-read_intervals) and check by hand"
  fi
fi
if [ $rc -eq 0 ]; then echo "VERIFY OK"; else echo "VERIFY FAILED"; fi
exit $rc

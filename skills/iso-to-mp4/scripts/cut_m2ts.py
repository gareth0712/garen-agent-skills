#!/usr/bin/env python3
"""Cut a byte range out of an m2ts read from stdin (small test clips around a hole).
usage: 7z e -so disc.iso "BDMV\\STREAM\\00001.m2ts" | cut_m2ts.py <start-byte> <length-bytes> <out.m2ts>
Cut on a multiple of 6144 so the clip starts on a packet-group boundary."""
import sys

if len(sys.argv) != 4:
    print(__doc__)
    sys.exit(0 if len(sys.argv) == 2 and sys.argv[1] in ("-h", "--help") else 2)
START, LEN, OUT = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
pos = 0
with open(OUT, "wb") as o:
    while pos < START + LEN:
        c = sys.stdin.buffer.read(1 << 22)
        if not c:
            break
        a, b = max(0, START - pos), min(len(c), START + LEN - pos)
        if b > a:
            o.write(c[a:b])
        pos += len(c)

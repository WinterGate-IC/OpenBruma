#!/usr/bin/env python3
# Generate a simple OpenBruma wallpaper PNG (no PIL needed)
import struct, zlib, os

def make_png(w, h, path):
    # gradient blue
    raw = bytearray()
    for y in range(h):
        raw.append(0)  # filter
        for x in range(w):
            r = int(30 + (x/w)*40)
            g = int(60 + (y/h)*60)
            b = int(120 + (x/w)*80)
            raw += bytes([r,g,b])
    def chunk(typ, data):
        return struct.pack(">I", len(data)) + typ + data + struct.pack(">I", zlib.crc32(typ+data) & 0xffffffff)
    sig = b"\x89PNG\r\n\x1a\n"
    ihdr = struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)
    idat = zlib.compress(bytes(raw), 9)
    with open(path, "wb") as f:
        f.write(sig)
        f.write(chunk(b"IHDR", ihdr))
        f.write(chunk(b"IDAT", idat))
        f.write(chunk(b"IEND", b""))

os.makedirs(os.path.dirname(path) if False else ".", exist_ok=True)
make_png(1920, 1080, "openbruma-wallpaper.png")
print("done")

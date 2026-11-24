#!/usr/bin/env python3
"""Generate three dimmed live wallpapers (VP9 WebM) with the OpenBruma mark.

Outputs to branding/live-wallpapers/: aurora-drift.webm, data-rain.webm,
ember-pulse.webm. Each clip is 1280x720, 20 fps, 8 s, seamless-ish loop.
"""
import math
import os
import random
import subprocess
import tempfile

from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1280, 720
FPS = 20
SECONDS = 8
FRAMES = FPS * SECONDS

ROOT = "/mnt/c/Users/zerop/OpenBruma"
OUT = os.path.join(ROOT, "branding", "live-wallpapers")
FONT = os.path.join(ROOT, "branding", "fonts", "ShareTechMono-Regular.ttf")
os.makedirs(OUT, exist_ok=True)


def make_mark(size=(760, 430)):
    """Official OpenBruma logo (transparent PNG) with a soft neon glow."""
    src = Image.open(os.path.join(ROOT, "branding", "openbruma-logo.png")).convert("RGBA")
    src = src.resize((size[1], size[1]), Image.LANCZOS)

    glow = Image.new("RGBA", src.size, (0, 0, 0, 0))
    glow.paste((46, 230, 160, 130), (0, 0), src.split()[3])
    glow = glow.filter(ImageFilter.GaussianBlur(18))

    canvas = Image.new("RGBA", (src.width + 80, src.height + 80), (0, 0, 0, 0))
    canvas.alpha_composite(glow, (40, 40))
    canvas.alpha_composite(src, (40, 40))
    return canvas


MARK = make_mark()


def base_frame():
    return Image.new("RGB", (W, H), (7, 13, 11))


def aurora(t):
    img = base_frame()
    d = ImageDraw.Draw(img, "RGBA")
    # faint hex grid for structure
    for gy in range(0, H + 40, 40):
        d.line([(0, gy), (W, gy)], fill=(30, 90, 76, 18), width=1)
    for layer, (amp, speed, color) in enumerate([
            (70, 0.7, (26, 150, 112)), (110, 0.5, (18, 104, 94)), (150, 0.3, (34, 88, 138))]):
        pts = []
        for x in range(0, W + 20, 20):
            y = H * 0.55 + amp * math.sin(x / 190.0 + t * speed + layer) \
                + amp * 0.4 * math.sin(x / 90.0 - t * speed * 1.7)
            pts.append((x, y))
        d.polygon(pts + [(W, H), (0, H)], fill=color + (120,))
    return img


RAIN = []
random.seed(7)
for _ in range(110):
    RAIN.append((random.randrange(0, W), random.randrange(-H, H),
                 random.randrange(6, 16), random.choice("01ABCDEF<>/\\#$%&*"), random.uniform(0.6, 1.8)))


def data_rain(t):
    img = base_frame()
    d = ImageDraw.Draw(img, "RGBA")
    try:
        font = ImageFont.truetype(FONT, 18)
    except OSError:
        font = ImageFont.load_default()
    for x, y, speed, glyph, scale in RAIN:
        yy = (y + t * 60 * speed) % (H + 80) - 40
        fade = max(0.0, 1.0 - abs(yy - H * 0.45) / (H * 0.75))
        d.text((x, yy), glyph, font=font, fill=(46, 230, 160, int(150 * fade)))
    return img


def ember_pulse(t):
    img = base_frame()
    d = ImageDraw.Draw(img, "RGBA")
    cx, cy = W / 2, H / 2
    for i in range(10, 0, -1):
        r = 60 + i * 34 + 18 * math.sin(t * 1.2 + i * 0.5)
        alpha = int(40 + 22 * (1 - i / 10.0) + 12 * math.sin(t * 2 + i))
        d.ellipse([cx - r, cy - r * 0.75, cx + r, cy + r * 0.75],
                  outline=(46, 230, 160, max(0, alpha)), width=3)
    for k in range(26):
        ang = k * 2.4 + t * 1.1
        rr = 210 + 70 * math.sin(t * 0.9 + k)
        x = cx + rr * math.cos(ang) * 1.5
        y = cy + rr * math.sin(ang) * 0.9
        a = int(60 + 60 * math.sin(t * 2 + k))
        d.ellipse([x - 3, y - 3, x + 3, y + 3], fill=(157, 255, 217, max(0, a)))
    return img


def compose(name, painter):
    tmp = tempfile.mkdtemp(prefix="bruma-live-")
    for f in range(FRAMES):
        t = f / FPS
        img = painter(t).convert("RGBA")
        # dim so the desktop stays readable
        img = Image.blend(img, Image.new("RGBA", img.size, (4, 9, 8, 255)), 0.28)
        img.alpha_composite(MARK, ((W - MARK.width) // 2, int(H * 0.13)))
        img = Image.blend(img, Image.new("RGBA", img.size, (0, 0, 0, 255)), 0.18)
        img.convert("RGB").save(os.path.join(tmp, f"{f:04d}.png"), "PNG")

    out = os.path.join(OUT, name)
    subprocess.run([
        "ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS),
        "-i", os.path.join(tmp, "%04d.png"),
        "-c:v", "libvpx-vp9", "-b:v", "0", "-crf", "38", "-row-mt", "1",
        "-pix_fmt", "yuv420p", "-an", out,
    ], check=True)
    size = os.path.getsize(out)
    print(f"{name}: {size/1e6:.2f} MB")
    for fn in os.listdir(tmp):
        os.remove(os.path.join(tmp, fn))
    os.rmdir(tmp)


compose("aurora-drift.webm", aurora)
compose("data-rain.webm", data_rain)
compose("ember-pulse.webm", ember_pulse)
print("done")

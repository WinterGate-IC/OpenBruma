#!/usr/bin/env python3
"""Generate OpenBruma wallpapers with UmbraForge.

This uses WinterGate IC's UmbraForge renderer (MIT) to produce a set of
branded 4K wallpapers in the WIC "neo-noir" palette, plus login/GRUB variants.

Usage (inside the Debian build environment):
    UMBRAFORGE_SRC=/root/UmbraForge/src python3 branding/umbraforge_themes.py
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

UMBRA = os.environ.get("UMBRAFORGE_SRC", "/root/UmbraForge/src")
sys.path.insert(0, UMBRA)

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtGui import QGuiApplication  # noqa: E402

app = QGuiApplication.instance() or QGuiApplication(sys.argv)

from umbraforge import layers, renderer  # noqa: E402


def _darken(hex_color: str, factor: float = 0.35) -> str:
    hex_color = hex_color.lstrip("#")
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return "#%02x%02x%02x" % (int(r * factor), int(g * factor), int(b * factor))


def _effects(glow: str | None = None, blur: float = 0.0) -> dict:
    fx = layers.default_effects()
    if glow:
        fx["glow"] = {"enabled": True, "color": glow, "opacity": 0.55, "size": 0.018}
    if blur:
        fx["blur"] = {"enabled": True, "radius": blur}
    return fx


def _text(name: str, text: str, *, font: str, size: float, color: str,
          x: float, y: float, w: float, h: float, weight: int = 700,
          align: str = "center", valign: str = "middle",
          spacing: float = 0.0, glow: str | None = None,
          stroke: str = "", stroke_width: float = 0.0) -> layers.TextLayer:
    layer = layers.TextLayer(
        name=name, text=text, font=font, size=size, color=color,
        x=x, y=y, w=w, h=h, weight=weight, align=align, valign=valign,
        letter_spacing=spacing, stroke_color=stroke,
        stroke_width=stroke_width,
    )
    layer.effects = _effects(glow)
    return layer


def _shape(name: str, shape: str, *, x: float, y: float, w: float, h: float,
           fill: str = "#00000000", stroke: str = "", stroke_width: float = 0.0,
           fill2: str = "", gradient: bool = False, glow: str | None = None) -> layers.ShapeLayer:
    layer = layers.ShapeLayer(
        name=name, shape=shape, fill=fill, fill2=fill2, gradient=gradient,
        stroke=stroke, stroke_width=stroke_width, x=x, y=y, w=w, h=h,
    )
    layer.effects = _effects(glow)
    return layer


THEMES = [
    {
        "key": "neo-noir",
        "title": "Neo-Noir",
        "primary": "#00ff9d",
        "accent": "#00b8ff",
        "accent2": "#7b2eda",
        "accent3": "#ff3366",
        "bg": "#0a0c0f",
        "pattern": "hexagons",
        "pattern_color": "#00ff9d",
        "pattern_opacity": 0.055,
        "pattern_scale": 0.55,
    },
    {
        "key": "electric-blue",
        "title": "Electric Blue",
        "primary": "#00b8ff",
        "accent": "#00ff9d",
        "accent2": "#7b2eda",
        "accent3": "#ff3366",
        "bg": "#050b14",
        "pattern": "grid",
        "pattern_color": "#00b8ff",
        "pattern_opacity": 0.07,
        "pattern_scale": 0.45,
    },
    {
        "key": "violet-forge",
        "title": "Violet Forge",
        "primary": "#b06bff",
        "accent": "#00ff9d",
        "accent2": "#00b8ff",
        "accent3": "#ff3366",
        "bg": "#0b0614",
        "pattern": "rings",
        "pattern_color": "#b06bff",
        "pattern_opacity": 0.06,
        "pattern_scale": 0.55,
    },
    {
        "key": "ember",
        "title": "Ember",
        "primary": "#ff6b00",
        "accent": "#ff3366",
        "accent2": "#ffaa00",
        "accent3": "#00b8ff",
        "bg": "#0c0a0a",
        "pattern": "rays",
        "pattern_color": "#ff6b00",
        "pattern_opacity": 0.05,
        "pattern_scale": 0.6,
    },
    {
        "key": "cyber-lime",
        "title": "Cyber-Lime",
        "primary": "#00ff41",
        "accent": "#00ff9d",
        "accent2": "#00b8ff",
        "accent3": "#ff3366",
        "bg": "#000000",
        "pattern": "scanlines",
        "pattern_color": "#00ff41",
        "pattern_opacity": 0.08,
        "pattern_scale": 0.4,
    },
    {
        "key": "crimson-gate",
        "title": "Crimson Gate",
        "primary": "#ff3366",
        "accent": "#ff6b00",
        "accent2": "#7b2eda",
        "accent3": "#00ff9d",
        "bg": "#0a0508",
        "pattern": "hexagons",
        "pattern_color": "#ff3366",
        "pattern_opacity": 0.05,
        "pattern_scale": 0.5,
    },
    {
        "key": "ghost",
        "title": "Ghost Protocol",
        "primary": "#ffffff",
        "accent": "#00b8ff",
        "accent2": "#7b2eda",
        "accent3": "#00ff9d",
        "bg": "#05070a",
        "pattern": "grid",
        "pattern_color": "#ffffff",
        "pattern_opacity": 0.045,
        "pattern_scale": 0.5,
    },
    {
        "key": "aurora",
        "title": "Aurora",
        "primary": "#00ff9d",
        "accent": "#00b8ff",
        "accent2": "#7b2eda",
        "accent3": "#ff3366",
        "bg": "#040a10",
        "pattern": "waves",
        "pattern_color": "#00b8ff",
        "pattern_opacity": 0.06,
        "pattern_scale": 0.5,
    },
]


def build(theme: dict, width: int = 3840, height: int = 2160,
          compact: bool = False) -> layers.Design:
    design = layers.Design(name=f"OpenBruma {theme['title']}",
                           width=width, height=height)
    design.background = layers.merge(layers.default_background(), {
        "kind": "linear",
        "color": _darken(theme["primary"], 0.20),
        "color2": theme["bg"],
        "angle": 135.0,
        "pattern": theme["pattern"],
        "pattern_color": theme["pattern_color"],
        "pattern_opacity": theme["pattern_opacity"],
        "pattern_scale": theme["pattern_scale"],
        "vignette": 0.5,
    })

    p = theme["primary"]
    a = theme["accent"]
    a2 = theme["accent2"]
    a3 = theme["accent3"]

    # Outer gate arc
    design.add(_shape("gate", "arch_window", x=0.34, y=0.08, w=0.32, h=0.46,
                      fill="#00000000", stroke=p, stroke_width=0.0022,
                      glow=p))
    # Hex badge ring
    design.add(_shape("hex-badge", "hex_badge", x=0.40, y=0.15, w=0.20, h=0.28,
                      fill="#00000000", stroke=a, stroke_width=0.0016,
                      glow=a))
    # Inner hexagon, filled with a subtle gradient
    design.add(_shape("hex-core", "hexagon", x=0.445, y=0.205, w=0.11, h=0.17,
                      fill=_darken(p, 0.30), fill2=_darken(a2, 0.25),
                      gradient=True, stroke=p, stroke_width=0.0014,
                      glow=p))
    # Crosshair / radar accent
    design.add(_shape("radar", "radar", x=0.44, y=0.20, w=0.12, h=0.19,
                      fill="#00000000", stroke=a3, stroke_width=0.0012))

    # Wordmark
    design.add(_text("wordmark", "OPENBRUMA", font="Orbitron", size=0.105,
                     color="#ffffff", weight=900, x=0.18, y=0.55, w=0.64,
                     h=0.12, spacing=0.14, glow=p))
    design.add(_text("collective", "WINTERGATE INTELLIGENCE COLLECTIVE",
                     font="Share Tech Mono", size=0.021, color=theme["accent"],
                     weight=400, x=0.20, y=0.675, w=0.60, h=0.025,
                     spacing=0.22))
    design.add(_text("tagline", "WHERE THE SHADOWS END, AND THE PEOPLE STAND",
                     font="Share Tech Mono", size=0.016, color=p,
                     weight=400, x=0.20, y=0.715, w=0.60, h=0.02,
                     spacing=0.18, glow=p))
    design.add(_text("capabilities", "OSINT  ·  INVESTIGATION  ·  DEFENSE",
                     font="Share Tech Mono", size=0.014, color=theme["accent2"],
                     weight=400, x=0.20, y=0.80, w=0.60, h=0.02,
                     spacing=0.16))
    design.add(_text("est", "EST. 04.09.2025  ·  WINTERGATE.ORG",
                     font="Share Tech Mono", size=0.011, color="#6c7a8d",
                     weight=400, x=0.20, y=0.86, w=0.60, h=0.015,
                     spacing=0.14))

    if not compact:
        # Corner brackets for a HUD feel
        design.add(_shape("corner-tl", "frame_corner", x=0.03, y=0.04,
                          w=0.10, h=0.14, fill="#00000000", stroke=theme["accent3"],
                          stroke_width=0.0012))
        design.add(_shape("corner-br", "frame_corner", x=0.87, y=0.82,
                          w=0.10, h=0.14, fill="#00000000", stroke=theme["accent3"],
                          stroke_width=0.0012))
    return design


def main() -> int:
    here = Path(__file__).resolve().parent
    out = here / "wallpapers"
    out.mkdir(parents=True, exist_ok=True)

    for theme in THEMES:
        design = build(theme, 3840, 2160)
        target = out / f"openbruma-{theme['key']}.png"
        if renderer.save_image(design, str(target)):
            print("wrote", target)
        else:
            print("FAILED", target)

        login = build(theme, 1920, 1080, compact=True)
        login_target = out / f"login-{theme['key']}.png"
        if renderer.save_image(login, str(login_target)):
            print("wrote", login_target)
        else:
            print("FAILED", login_target)

    # A cleaner GRUB background: same art, no small print, darker vignette
    grub_theme = dict(THEMES[0])
    grub = build(grub_theme, 1920, 1080, compact=True)
    grub.background = layers.merge(grub.background, {"vignette": 0.72})
    grub_target = out / "grub-neo-noir.png"
    if renderer.save_image(grub, str(grub_target)):
        print("wrote", grub_target)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

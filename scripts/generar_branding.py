#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Genera og-image (1200x630), íconos y favicon para el dashboard Plan Perú 2050."""
import os, json
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
A = os.path.join(ROOT, "assets"); os.makedirs(A, exist_ok=True)

def font(sz, bold=True):
    cands = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/Library/Fonts/Arial.ttf",
    ]
    for c in cands:
        if os.path.exists(c):
            try: return ImageFont.truetype(c, sz)
            except Exception: pass
    return ImageFont.load_default()

meta = json.load(open(os.path.join(ROOT, "data/meta.json")))
coms = json.load(open(os.path.join(ROOT, "data/comisiones.json")))
n_ind = sum(len(c.get("indicadores", [])) for c in coms)

BG1, BG2 = (10, 14, 26), (22, 30, 53)
RED, GOLD, WHITE, MUT = (217, 16, 35), (224, 165, 46), (235, 240, 247), (138, 152, 184)

def vgrad(w, h, c1, c2):
    base = Image.new("RGB", (w, h), c1)
    top = Image.new("RGB", (w, h), c2)
    mask = Image.new("L", (w, h))
    md = mask.load()
    for y in range(h):
        v = int(255 * (1 - y / h) ** 1.5)
        for x in range(0, w, 1): md[x, y] = v
    base.paste(top, (0, 0), mask)
    return base

# ---------- OG IMAGE ----------
W, H = 1200, 630
im = vgrad(W, H, BG1, BG2)
d = ImageDraw.Draw(im)
# franja bandera izquierda
d.rectangle([0, 0, 14, H], fill=RED)
d.rectangle([14, 0, 22, H], fill=WHITE)
# glow
d.ellipse([820, -260, 1380, 300], fill=(34, 44, 80))
im = im.filter(__import__("PIL.ImageFilter", fromlist=["GaussianBlur"]).GaussianBlur(0))
d = ImageDraw.Draw(im)
d.rectangle([0, 0, 14, H], fill=RED); d.rectangle([14, 0, 22, H], fill=WHITE)
# eyebrow
d.text((70, 74), "CNPP · COLEGIO DE INGENIEROS DEL PERÚ", font=font(22), fill=MUT)
# title
d.text((68, 120), "PLAN PERÚ", font=font(96), fill=WHITE)
d.text((68, 212), "2050", font=font(120), fill=GOLD)
d.text((74, 350), "Dashboard de Comisiones Temáticas", font=font(40, False), fill=WHITE)
d.text((74, 404), "Visión · Brechas · Metas 2050 · Indicadores · Simulaciones · Mapas", font=font(24, False), fill=MUT)
# stat cards
stats = [(str(meta["totalComisiones"]), "comisiones"), (str(len(coms)), "con datos"), (str(n_ind), "indicadores")]
x = 74
for val, lab in stats:
    d.rounded_rectangle([x, 466, x+220, 576], radius=16, fill=(17, 23, 38), outline=(30, 40, 64), width=2)
    d.text((x+24, 478), val, font=font(52), fill=GOLD)
    d.text((x+24, 542), lab, font=font(19, False), fill=MUT)
    x += 244
d.text((830, 556), "unimauro.github.io/plan-peru-2050", font=font(20, False), fill=MUT)
im.save(os.path.join(A, "og-image.png"))
print("✓ assets/og-image.png", im.size)

# ---------- ICON (512) — bandera redondeada + 50 ----------
def icon(sz):
    im = Image.new("RGBA", (sz, sz), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    r = int(sz * 0.22)
    d.rounded_rectangle([0, 0, sz-1, sz-1], radius=r, fill=(10, 14, 26))
    # franjas bandera horizontales internas
    pad = int(sz*0.16); top = int(sz*0.18); h = sz - 2*top; band = h//3
    d.rounded_rectangle([pad, top, sz-pad, top+band], radius=6, fill=RED)
    d.rectangle([pad, top+band, sz-pad, top+2*band], fill=(235,240,247))
    d.rounded_rectangle([pad, top+2*band, sz-pad, top+3*band], radius=6, fill=RED)
    # "50" sobre la franja blanca
    f = font(int(sz*0.26))
    txt = "50"
    bb = d.textbbox((0,0), txt, font=f)
    tw, th = bb[2]-bb[0], bb[3]-bb[1]
    d.text(((sz-tw)/2 - bb[0], top+band + (band-th)/2 - bb[1]), txt, font=f, fill=(10,14,26))
    return im

icon(512).save(os.path.join(A, "icon-512.png"))
icon(192).save(os.path.join(A, "icon-192.png"))
icon(180).save(os.path.join(A, "apple-touch-icon.png"))
ic = icon(64)
ic.save(os.path.join(ROOT, "favicon.ico"), sizes=[(16,16),(32,32),(48,48),(64,64)])
print("✓ íconos + favicon.ico")

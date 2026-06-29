#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Genera, por comisión validada:
  - assets/og/<id>.png  (imagen OG 1200x630 con marca + eje + nombre + dato clave)
  - c/<id>.html         (página-stub con meta OG propios + redirección a /#<id>)
Permite que al compartir https://planperu2050.pe/c/<id>.html en redes salga
la tarjeta de ESA comisión."""
import os, json, unicodedata, re
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OGDIR = os.path.join(ROOT, "assets", "og"); os.makedirs(OGDIR, exist_ok=True)
CDIR = os.path.join(ROOT, "c"); os.makedirs(CDIR, exist_ok=True)
BASE = "https://planperu2050.pe"

val = json.load(open(os.path.join(ROOT, "data/comisiones.json")))

EJE_COLOR = {"Economía del Conocimiento": (224,165,46), "Sostenibilidad y Ambiente": (22,163,74),
             "Soberanía y Defensa": (217,16,35), "Infraestructura y Conectividad": (59,130,246),
             "Bienestar y Salud": (168,85,247), "Competitividad": (46,212,122)}

def font(sz, bold=True):
    for c in (["/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
               "/System/Library/Fonts/Helvetica.ttc", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"]):
        if os.path.exists(c):
            try: return ImageFont.truetype(c, sz)
            except Exception: pass
    return ImageFont.load_default()

def wrap(draw, text, fnt, maxw):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textbbox((0,0), t, font=fnt)[2] <= maxw: cur = t
        else: lines.append(cur); cur = w
    if cur: lines.append(cur)
    return lines

def esc(s): return str(s or "").replace("&","&amp;").replace("<","&lt;").replace(">","&gt;").replace('"',"&quot;")

def og_image(c):
    W,H = 1200,630
    im = Image.new("RGB",(W,H),(10,14,26)); d = ImageDraw.Draw(im)
    acc = EJE_COLOR.get(c.get("eje"), (217,16,35))
    # glow
    d.ellipse([820,-260,1420,320], fill=(acc[0]//6+18, acc[1]//6+22, acc[2]//6+40))
    # franja bandera vertical (Perú) izquierda
    d.rectangle([0,0,10,H], fill=(217,16,35)); d.rectangle([10,0,18,H], fill=(255,255,255)); d.rectangle([18,0,28,H], fill=(217,16,35))
    d.text((70,70), "PLAN PERÚ 2050 · COMISIÓN TEMÁTICA", font=font(22), fill=(138,152,184))
    # chip eje
    eje = (c.get("eje") or "").upper()
    if eje:
        ew = d.textbbox((0,0), eje, font=font(20))[2]
        d.rounded_rectangle([70,118,70+ew+34,162], radius=22, fill=acc)
        d.text((87,128), eje, font=font(20), fill=(10,14,26))
    # nombre (grande)
    lines = wrap(d, c.get("nombre",""), font(64), 1050)[:3]
    y = 210
    for ln in lines:
        d.text((70,y), ln, font=font(64), fill=(255,255,255)); y += 76
    # dato clave: nº indicadores / objetivos
    n_ind = len(c.get("indicadores",[])); n_obj = len(c.get("objetivos_estrategicos") or c.get("metas") or [])
    d.text((70,470), f"{n_ind} indicadores · {n_obj} objetivos · meta 2050", font=font(28,False), fill=acc)
    d.text((70,560), "planperu2050.pe", font=font(22,False), fill=(138,152,184))
    im.save(os.path.join(OGDIR, f"{c['id']}.png"))

def stub_html(c):
    title = f"{c['nombre']} · Plan Perú 2050"
    desc = (c.get("resumen") or c.get("vision") or f"Comisión {c['nombre']} del Plan Perú 2050.")[:200]
    og = f"{BASE}/assets/og/{c['id']}.png"
    url = f"{BASE}/c/{c['id']}.html"
    html = f"""<!doctype html>
<html lang="es"><head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}"/>
<link rel="canonical" href="{url}"/>
<meta property="og:type" content="article"/>
<meta property="og:site_name" content="Plan Perú 2050"/>
<meta property="og:locale" content="es_PE"/>
<meta property="og:url" content="{url}"/>
<meta property="og:title" content="{esc(title)}"/>
<meta property="og:description" content="{esc(desc)}"/>
<meta property="og:image" content="{og}"/>
<meta property="og:image:width" content="1200"/>
<meta property="og:image:height" content="630"/>
<meta name="twitter:card" content="summary_large_image"/>
<meta name="twitter:title" content="{esc(title)}"/>
<meta name="twitter:description" content="{esc(desc)}"/>
<meta name="twitter:image" content="{og}"/>
<link rel="icon" href="../favicon.ico"/>
<script>location.replace("../#{c['id']}");</script>
<meta http-equiv="refresh" content="0; url=../#{c['id']}"/>
</head><body style="background:#0a0e1a;color:#e8edf7;font-family:system-ui,sans-serif;text-align:center;padding:60px">
<p>Abriendo <b>{esc(c['nombre'])}</b> en el Plan Perú 2050…</p>
<p><a href="../#{c['id']}" style="color:#e0a52e">Ir al dashboard →</a></p>
</body></html>"""
    open(os.path.join(CDIR, f"{c['id']}.html"), "w", encoding="utf-8").write(html)

if __name__ == "__main__":
    for c in val:
        og_image(c); stub_html(c)
    print(f"✓ {len(val)} OG + stubs en assets/og/ y c/")
    # añadir stubs al sitemap
    sm = os.path.join(ROOT, "sitemap.xml")
    urls = "\n".join(f"  <url><loc>{BASE}/c/{c['id']}.html</loc><changefreq>monthly</changefreq><priority>0.7</priority></url>" for c in val)
    base = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>{BASE}/</loc><changefreq>weekly</changefreq><priority>1.0</priority></url>
{urls}
</urlset>"""
    open(sm, "w").write(base)
    print(f"✓ sitemap.xml con {len(val)} comisiones")

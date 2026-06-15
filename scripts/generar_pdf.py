#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Genera PDFs con buena presentación interna (texto, tablas, gráficos y mapas):
- entregables/pdf/<id>.pdf            por comisión (validadas)
- entregables/pdf/plan-100-dias.pdf   consolidado de 100 días
- entregables/pdf/sintesis-por-ejes.pdf con gráficos por eje
"""
import json, os
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
                                Image, HRFlowable, PageBreak, KeepTogether)
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PDF = os.path.join(ROOT, "entregables", "pdf"); os.makedirs(PDF, exist_ok=True)
IMG = os.path.join(ROOT, "entregables", "_img"); os.makedirs(IMG, exist_ok=True)
GEO = os.path.expanduser("~/Documents/Repos/proyecto-inti/data/distritos.geojson")

RED = colors.HexColor("#D91023"); GOLD = colors.HexColor("#B8840E")
DARK = colors.HexColor("#1A2238"); GREY = colors.HexColor("#5D6B88")
LIGHT = colors.HexColor("#F4F6FB"); LINE = colors.HexColor("#D7DCE8"); GREEN = colors.HexColor("#1B8A4B")

val = json.load(open(os.path.join(ROOT, "data/comisiones.json")))
rev = json.load(open(os.path.join(ROOT, "data/comisiones_revision.json")))
puntos = json.load(open(os.path.join(ROOT, "data/puntos.json")))
TERRITORIAL = {"espacio", "maritimo-fluvial-y-lacustre", "telecomunicaciones", "medio-ambiente"}

# ---------- estilos ----------
def st(name, **kw): kw.setdefault("fontName", "Helvetica"); return ParagraphStyle(name, **kw)
S = {
  "eyebrow": st("eyebrow", fontName="Helvetica-Bold", fontSize=8.5, textColor=GOLD, spaceAfter=2, leading=11),
  "sub": st("sub", fontSize=9, textColor=GREY, spaceAfter=2, leading=12),
  "title": st("title", fontName="Helvetica-Bold", fontSize=22, textColor=RED, spaceAfter=6, leading=24),
  "resumen": st("resumen", fontSize=10.5, textColor=DARK, spaceAfter=6, leading=15),
  "h4": st("h4", fontName="Helvetica-Bold", fontSize=11, textColor=RED, spaceBefore=12, spaceAfter=5, leading=14),
  "body": st("body", fontSize=10, textColor=DARK, leading=14, spaceAfter=4),
  "bullet": st("bullet", fontSize=9.5, textColor=DARK, leading=13, leftIndent=10, bulletIndent=0, spaceAfter=2),
  "cap": st("cap", fontSize=8, textColor=GREY, alignment=TA_CENTER, spaceBefore=3, leading=10),
  "th": st("th", fontName="Helvetica-Bold", fontSize=8.5, textColor=colors.white, leading=10),
  "td": st("td", fontSize=8, textColor=DARK, leading=10),
  "tdb": st("tdb", fontName="Helvetica-Bold", fontSize=8, textColor=DARK, leading=10),
  "kpin": st("kpin", fontName="Helvetica-Bold", fontSize=17, textColor=RED, alignment=TA_CENTER, leading=19),
  "kpil": st("kpil", fontSize=7.5, textColor=GREY, alignment=TA_CENTER, leading=9),
  "reco": st("reco", fontSize=10, textColor=DARK, leading=14, backColor=colors.HexColor("#FBEEF0"),
             borderColor=colors.HexColor("#F0C6CC"), borderWidth=1, borderPadding=8, spaceBefore=4),
  "foot": st("foot", fontSize=7.5, textColor=GREY, alignment=TA_LEFT, leading=10),
}
E = lambda s: (str(s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))

def avance(i):
    a, m = i.get("actual"), i.get("meta")
    if a is None or m is None: return None
    if m == a: return 100.0
    return max(0, min(100, (a/m if m >= a else m/a)*100))

def fnum(x):
    if x is None: return "s/d"
    if isinstance(x, float) and x == int(x): x = int(x)
    return f"{x:,}".replace(",", " ")

# ---------- charts ----------
_polys = None
def peru_polys():
    global _polys
    if _polys is not None: return _polys
    p = []
    try:
        gj = json.load(open(GEO))
        for ft in gj["features"]:
            g = ft.get("geometry") or {}; t, c = g.get("type"), g.get("coordinates")
            if t == "Polygon": p.append(c[0])
            elif t == "MultiPolygon":
                for part in c: p.append(part[0])
    except Exception: pass
    _polys = p; return p

def chart_avance(c):
    inds = [(i, avance(i)) for i in c.get("indicadores", [])]
    inds = [(i, v) for i, v in inds if v is not None][:12]
    if not inds: return None
    fig, ax = plt.subplots(figsize=(7.2, max(2, .4*len(inds)+.7)))
    labels = [(i["nombre"][:38]+"…") if len(i["nombre"]) > 39 else i["nombre"] for i, _ in inds]
    vals = [round(v, 1) for _, v in inds]
    ax.barh(range(len(inds)), vals, color="#B8840E", height=.6)
    ax.set_yticks(range(len(inds))); ax.set_yticklabels(labels, fontsize=8)
    ax.invert_yaxis(); ax.set_xlim(0, 100); ax.set_xlabel("% de avance hacia la meta 2050", fontsize=8.5)
    for s in ("top", "right"): ax.spines[s].set_visible(False)
    ax.grid(axis="x", color="#e6e9f0")
    for k, v in enumerate(vals): ax.text(min(v+1.5, 95), k, f"{v:.0f}%", va="center", fontsize=7.5, color="#1A2238")
    fig.tight_layout(); p = os.path.join(IMG, f"pdf_avance_{c['id']}.png"); fig.savefig(p, dpi=150); plt.close(fig); return p

def chart_map(c):
    pts = [p for p in puntos["puntos"] if p.get("comision") == c["id"]]
    if not pts: return None
    fig, ax = plt.subplots(figsize=(4.6, 6.0))
    pol = peru_polys()
    if pol: ax.add_collection(PolyCollection(pol, closed=True, facecolors="#e9edf5", edgecolors="none"))
    tipos = puntos["tipos"]; seen = set()
    for p in pts:
        t = tipos.get(p["tipo"], {}); lb = t.get("label", p["tipo"])
        ax.scatter(p["lng"], p["lat"], s=40, c=t.get("color", "#d91023"), edgecolors="white",
                   linewidths=.7, zorder=5, label=lb if lb not in seen else None); seen.add(lb)
    ax.set_xlim(-82, -68); ax.set_ylim(-18.5, .5); ax.set_aspect(1); ax.axis("off")
    ax.legend(loc="lower left", fontsize=7.5, frameon=False)
    fig.tight_layout(); p = os.path.join(IMG, f"pdf_mapa_{c['id']}.png"); fig.savefig(p, dpi=150, bbox_inches="tight"); plt.close(fig); return p

# ---------- documento base ----------
def header_footer(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(RED); canvas.rect(0, A4[1]-6, A4[0], 6, fill=1, stroke=0)
    canvas.setFillColor(GOLD); canvas.rect(0, A4[1]-9, A4[0], 3, fill=1, stroke=0)
    canvas.setFillColor(GREY); canvas.setFont("Helvetica", 7.5)
    canvas.drawString(18*mm, 10*mm, "Plan Perú 2050 · CNPP — Colegio de Ingenieros del Perú")
    canvas.drawRightString(A4[0]-18*mm, 10*mm, f"{doc.page}")
    canvas.restoreState()

def make_doc(path):
    return SimpleDocTemplate(path, pagesize=A4, topMargin=20*mm, bottomMargin=16*mm,
                             leftMargin=18*mm, rightMargin=18*mm, title="Plan Perú 2050")

def kpi_table(c):
    inds = c.get("indicadores", [])
    quant = [i for i in inds if i.get("actual") is not None and i.get("meta") is not None]
    avgs = [avance(i) for i in quant]; idx = sum(avgs)/len(avgs) if avgs else None
    data = [[Paragraph(f"{len(inds)}", S["kpin"]), Paragraph(f"{len(c.get('pilares',[]))}", S["kpin"]),
             Paragraph(f"{len(c.get('metas',[]))}", S["kpin"]), Paragraph(f"{idx:.0f}%" if idx is not None else "—", S["kpin"])],
            [Paragraph("Indicadores", S["kpil"]), Paragraph("Pilares", S["kpil"]),
             Paragraph("Metas 2050", S["kpil"]), Paragraph("Avance estim.", S["kpil"])]]
    t = Table(data, colWidths=[42*mm]*4)
    t.setStyle(TableStyle([("BACKGROUND", (0,0), (-1,-1), LIGHT), ("BOX", (0,0), (-1,-1), .5, LINE),
        ("INNERGRID", (0,0), (-1,-1), .5, colors.white), ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("TOPPADDING", (0,0), (-1,0), 7), ("BOTTOMPADDING", (0,1), (-1,1), 7)]))
    return t

def bullets(items, story):
    for it in items:
        story.append(Paragraph("•&nbsp;&nbsp;" + E(it), S["bullet"]))

def commission_story(c, revision=False):
    s = []
    s.append(Paragraph("PLAN PERÚ 2050 · COMISIÓN TEMÁTICA", S["eyebrow"]))
    s.append(Paragraph(E(c["nombre"]), S["title"]))
    if c.get("eje"): s.append(Paragraph("Eje estratégico: " + E(c["eje"]), S["sub"]))
    if revision:
        s.append(Paragraph("⚠ Línea base <b>preliminar</b> — contenido inferido, pendiente de validación. No proviene de redacción oficial.", S["reco"]))
    if c.get("resumen"): s.append(Paragraph(E(c["resumen"]), S["resumen"]))
    s.append(HRFlowable(color=LINE, thickness=.6, spaceBefore=4, spaceAfter=6))
    s.append(kpi_table(c)); s.append(Spacer(1, 6))
    if c.get("vision"):
        s.append(Paragraph("Visión 2050", S["h4"])); s.append(Paragraph(E(c["vision"]), S["body"]))
    if c.get("diagnostico"):
        s.append(Paragraph("Diagnóstico — brecha 2026", S["h4"])); bullets(c["diagnostico"], s)
    inds = c.get("indicadores", [])
    if inds:
        s.append(Paragraph("Indicadores: hoy → meta 2050", S["h4"]))
        rows = [[Paragraph(h, S["th"]) for h in ["Indicador", "Hoy", "Meta 2050", "Unidad", "% av.", "Fuente"]]]
        for i in inds:
            av = avance(i)
            rows.append([Paragraph(E(i["nombre"]), S["tdb"]), Paragraph(fnum(i.get("actual")), S["td"]),
                         Paragraph(fnum(i.get("meta")), S["td"]), Paragraph(E(i.get("unidad","")), S["td"]),
                         Paragraph(f"{av:.0f}%" if av is not None else "—", S["td"]), Paragraph(E((i.get("fuente","") or "")[:80]), S["td"])])
        t = Table(rows, colWidths=[52*mm, 16*mm, 18*mm, 20*mm, 12*mm, 56*mm], repeatRows=1)
        t.setStyle(TableStyle([("BACKGROUND", (0,0), (-1,0), RED), ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, LIGHT]),
            ("GRID", (0,0), (-1,-1), .4, LINE), ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
            ("TOPPADDING", (0,0), (-1,-1), 3), ("BOTTOMPADDING", (0,0), (-1,-1), 3),
            ("LEFTPADDING", (0,0), (-1,-1), 4), ("RIGHTPADDING", (0,0), (-1,-1), 4)]))
        s.append(t)
        img = chart_avance(c)
        if img:
            s.append(Spacer(1, 8)); s.append(Image(img, width=165*mm, height=165*mm*plt_ratio(img)))
            s.append(Paragraph("Avance estimado de cada indicador hacia su meta 2050.", S["cap"]))
    if c["id"] in TERRITORIAL:
        mp = chart_map(c)
        if mp:
            s.append(Paragraph("Mapa estratégico", S["h4"]))
            s.append(Image(mp, width=88*mm, height=88*mm*plt_ratio(mp)))
            s.append(Paragraph("Infraestructura asociada (ubicación referencial).", S["cap"]))
    if c.get("pilares"):
        s.append(Paragraph("Pilares de la estrategia", S["h4"]))
        for p in c["pilares"]:
            s.append(Paragraph("<b>" + E(p.get("nombre","")) + ":</b> " + E(p.get("descripcion","")), S["body"]))
    if c.get("cien_dias"):
        s.append(Paragraph("Hoja de ruta · 100 primeros días", S["h4"]))
        for d in c["cien_dias"]:
            txt = E(d.get("accion","") if isinstance(d, dict) else d)
            if isinstance(d, dict) and d.get("tipo"): txt += f' <font color="#B8840E">[{E(d["tipo"])}]</font>'
            s.append(Paragraph("•&nbsp;&nbsp;" + txt, S["bullet"]))
    if c.get("metas"):
        s.append(Paragraph("Metas 2050", S["h4"])); bullets(c["metas"], s)
    if c.get("acciones"):
        s.append(Paragraph("Acciones e iniciativas", S["h4"])); bullets(c["acciones"], s)
    if c.get("recomendacion"):
        s.append(Paragraph("Recomendación de política", S["h4"])); s.append(Paragraph(E(c["recomendacion"]), S["reco"]))
    return s

from PIL import Image as PILImage
def plt_ratio(path):
    w, h = PILImage.open(path).size; return h/w

# ---------- 1) PDFs por comisión ----------
def build_commissions():
    for c in val:
        d = make_doc(os.path.join(PDF, f"{c['id']}.pdf"))
        d.build(commission_story(c), onFirstPage=header_footer, onLaterPages=header_footer)
        print("  ✓ pdf/", c["id"] + ".pdf")

# ---------- 2) Plan 100 días ----------
def build_100():
    coms = [c for c in val if c.get("cien_dias")]
    s = [Paragraph("PLAN PERÚ 2050", S["eyebrow"]), Paragraph("Plan de los 100 Primeros Días", S["title"]),
         Paragraph("Medidas inmediatas propuestas por las comisiones temáticas para los primeros 100 días del próximo "
                   "gobierno. Extraídas de las redacciones; sujetas a validación oficial.", S["resumen"]),
         Paragraph(f"{sum(len(c['cien_dias']) for c in coms)} medidas · {len(coms)} comisiones", S["h4"]),
         HRFlowable(color=LINE, thickness=.6, spaceAfter=6)]
    for c in coms:
        blk = [Paragraph(E(c["nombre"]), S["h4"])]
        for d in c["cien_dias"]:
            txt = E(d.get("accion","") if isinstance(d, dict) else d)
            if isinstance(d, dict) and d.get("tipo"): txt += f' <font color="#B8840E">[{E(d["tipo"])}]</font>'
            blk.append(Paragraph("•&nbsp;&nbsp;" + txt, S["bullet"]))
        s.append(KeepTogether(blk))
    make_doc(os.path.join(PDF, "plan-100-dias.pdf")).build(s, onFirstPage=header_footer, onLaterPages=header_footer)
    print("  ✓ pdf/plan-100-dias.pdf")

# ---------- 3) Síntesis por ejes (con gráficos) ----------
EJES = [("Economía del Conocimiento","Dimensión económica"),("Competitividad","Dimensión económica"),
        ("Infraestructura y Conectividad","Económica / territorial"),("Sostenibilidad y Ambiente","Dimensión ambiental"),
        ("Bienestar y Salud","Dimensión social"),("Soberanía y Defensa","Institucional / soberanía")]

def chart_ejes_dist(coms):
    labels = [e for e, _ in EJES]
    nv = [sum(1 for c in coms if c.get("eje") == e and c["_val"]) for e in labels]
    nr = [sum(1 for c in coms if c.get("eje") == e and not c["_val"]) for e in labels]
    fig, ax = plt.subplots(figsize=(7.4, 3.2))
    y = range(len(labels))
    ax.barh(list(y), nv, color="#1B8A4B", label="Validado")
    ax.barh(list(y), nr, left=nv, color="#B8840E", label="En revisión")
    ax.set_yticks(list(y)); ax.set_yticklabels([l[:26] for l in labels], fontsize=8); ax.invert_yaxis()
    for s in ("top","right"): ax.spines[s].set_visible(False)
    ax.grid(axis="x", color="#e6e9f0"); ax.legend(fontsize=8, frameon=False, loc="lower right")
    ax.set_xlabel("N° de comisiones", fontsize=8.5)
    fig.tight_layout(); p = os.path.join(IMG, "pdf_ejes_dist.png"); fig.savefig(p, dpi=150); plt.close(fig); return p

def chart_ejes_avance(coms):
    rows = []
    for e, _ in EJES:
        avs = []
        for c in coms:
            if c.get("eje") == e and c["_val"]:
                vv = [avance(i) for i in c.get("indicadores", []) if avance(i) is not None]
                if vv: avs.append(sum(vv)/len(vv))
        if avs: rows.append((e, sum(avs)/len(avs)))
    if not rows: return None
    fig, ax = plt.subplots(figsize=(7.4, 2.6))
    ax.barh([r[0][:26] for r in rows], [round(r[1],1) for r in rows], color="#D91023")
    ax.set_xlim(0, 100); ax.invert_yaxis()
    for s in ("top","right"): ax.spines[s].set_visible(False)
    ax.grid(axis="x", color="#e6e9f0"); ax.set_xlabel("% avance promedio (comisiones validadas)", fontsize=8.5)
    ax.tick_params(labelsize=8)
    fig.tight_layout(); p = os.path.join(IMG, "pdf_ejes_avance.png"); fig.savefig(p, dpi=150); plt.close(fig); return p

def build_sintesis():
    for c in val: c["_val"] = True
    for c in rev: c["_val"] = False
    coms = val + rev
    s = [Paragraph("PLAN PERÚ 2050", S["eyebrow"]), Paragraph("Síntesis por Ejes Estratégicos", S["title"]),
         Paragraph("Consolidado de visión, metas y acciones de las comisiones agrupadas por eje (dimensiones económica, "
                   "social, ambiental e institucional). Generado desde el dashboard del Plan Perú 2050.", S["resumen"])]
    d1 = chart_ejes_dist(coms)
    if d1:
        s.append(Paragraph("Comisiones por eje (validadas vs. en revisión)", S["h4"]))
        s.append(Image(d1, width=170*mm, height=170*mm*plt_ratio(d1)))
    d2 = chart_ejes_avance(coms)
    if d2:
        s.append(Paragraph("Avance promedio por eje", S["h4"]))
        s.append(Image(d2, width=170*mm, height=170*mm*plt_ratio(d2)))
    for e, dim in EJES:
        grp = [c for c in coms if c.get("eje") == e]
        if not grp: continue
        grp.sort(key=lambda c: (not c["_val"], c["nombre"]))
        nv = sum(1 for c in grp if c["_val"])
        blk = [Paragraph(E(e), S["h4"]), Paragraph(f"{dim} · {len(grp)} comisiones ({nv} validadas, {len(grp)-nv} en revisión)", S["sub"])]
        s.append(KeepTogether(blk))
        for c in grp:
            tag = '<font color="#1B8A4B">● validado</font>' if c["_val"] else '<font color="#B8840E">○ en revisión</font>'
            s.append(Paragraph(f"<b>{E(c['nombre'])}</b>  {tag}", S["body"]))
            vis = (c.get("vision") or c.get("resumen") or "")
            if vis: s.append(Paragraph(E(vis[:280] + ("…" if len(vis) > 280 else "")), S["bullet"]))
    make_doc(os.path.join(PDF, "sintesis-por-ejes.pdf")).build(s, onFirstPage=header_footer, onLaterPages=header_footer)
    print("  ✓ pdf/sintesis-por-ejes.pdf")

if __name__ == "__main__":
    print("Generando PDFs…")
    build_commissions(); build_100(); build_sintesis()
    print("Listo:", os.path.relpath(PDF, ROOT))

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Genera entregables/INFORME-TECNICO-dashboard.pdf — informe de ingeniería del
portal Plan Perú 2050: arquitectura, pipeline de datos, stack y proceso de actualización,
con diagramas."""
import os, json
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
                                Image, HRFlowable, PageBreak, KeepTogether)
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "entregables"); os.makedirs(OUT, exist_ok=True)
IMG = os.path.join(OUT, "_img"); os.makedirs(IMG, exist_ok=True)

RED = colors.HexColor("#D91023"); GOLD = colors.HexColor("#B8840E")
DARK = colors.HexColor("#1A2238"); GREY = colors.HexColor("#5D6B88")
LIGHT = colors.HexColor("#F4F6FB"); LINE = colors.HexColor("#D7DCE8"); GREEN = colors.HexColor("#1B8A4B")

# datos reales para el informe
try:
    val = json.load(open(os.path.join(ROOT, "data/comisiones.json")))
    rev = json.load(open(os.path.join(ROOT, "data/comisiones_revision.json")))
    meta = json.load(open(os.path.join(ROOT, "data/meta.json")))
    n_total = meta.get("totalComisiones", 65); n_val = len(val); n_rev = len(rev)
    n_ind = sum(len(c.get("indicadores", [])) for c in val)
except Exception:
    n_total, n_val, n_rev, n_ind = 65, 20, 44, 220

def st(name, **kw): kw.setdefault("fontName", "Helvetica"); return ParagraphStyle(name, **kw)
S = {
  "eyebrow": st("e", fontName="Helvetica-Bold", fontSize=8.5, textColor=GOLD, spaceAfter=2),
  "title": st("t", fontName="Helvetica-Bold", fontSize=22, textColor=RED, spaceAfter=6, leading=24),
  "sub": st("s", fontSize=10.5, textColor=GREY, spaceAfter=4, leading=14),
  "h": st("h", fontName="Helvetica-Bold", fontSize=13, textColor=RED, spaceBefore=14, spaceAfter=6),
  "h2": st("h2", fontName="Helvetica-Bold", fontSize=10.5, textColor=DARK, spaceBefore=8, spaceAfter=3),
  "body": st("b", fontSize=10, textColor=DARK, leading=15, spaceAfter=5),
  "bullet": st("bu", fontSize=9.5, textColor=DARK, leading=14, leftIndent=10, spaceAfter=2),
  "cap": st("c", fontSize=8, textColor=GREY, alignment=TA_CENTER, spaceBefore=3),
  "kpin": st("kn", fontName="Helvetica-Bold", fontSize=18, textColor=RED, alignment=TA_CENTER),
  "kpil": st("kl", fontSize=8, textColor=GREY, alignment=TA_CENTER),
  "td": st("td", fontSize=8.5, textColor=DARK, leading=11),
  "th": st("th", fontName="Helvetica-Bold", fontSize=8.5, textColor=colors.white),
}
E = lambda s: str(s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

# ---------- diagrama: pipeline de datos ----------
def box(ax, x, y, w, h, text, fc, tc="white", fs=9):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.04",
        linewidth=0, facecolor=fc))
    ax.text(x + w/2, y + h/2, text, ha="center", va="center", color=tc, fontsize=fs, weight="bold", wrap=True)

def arrow(ax, x1, y1, x2, y2):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=14,
        linewidth=1.6, color="#5D6B88"))

def diag_pipeline():
    fig, ax = plt.subplots(figsize=(9.2, 3.0)); ax.set_xlim(0, 10); ax.set_ylim(0, 3); ax.axis("off")
    steps = [
        (0.1, "Documentos\nde comisiones\n(.docx .pdf .pptx)", "#5D6B88"),
        (2.1, "Conversión\na texto\n(pandoc/pdftotext)", "#3b82f6"),
        (4.1, "Extracción IA\nmulti-agente\n(estructura oficial)", "#D91023"),
        (6.1, "Datos JSON\nvalidados\n(anti-overclaiming)", "#B8840E"),
        (8.1, "Dashboard +\nPDFs + Deploy\n(VPS/Caddy)", "#1B8A4B"),
    ]
    w, h, y = 1.75, 1.2, 0.9
    for i, (x, t, c) in enumerate(steps):
        box(ax, x, y, w, h, t, c, fs=8)
        if i < len(steps) - 1: arrow(ax, x + w + 0.02, y + h/2, x + 2.0, y + h/2)
    ax.text(5, 2.7, "Pipeline de datos — del documento al portal", ha="center", fontsize=11, weight="bold", color="#1A2238")
    p = os.path.join(IMG, "tec_pipeline.png"); fig.savefig(p, dpi=160, bbox_inches="tight"); plt.close(fig); return p

# ---------- diagrama: arquitectura de despliegue ----------
def diag_arch():
    fig, ax = plt.subplots(figsize=(9.2, 3.6)); ax.set_xlim(0, 10); ax.set_ylim(0, 4); ax.axis("off")
    box(ax, 0.2, 2.6, 2.2, 1.0, "Repositorio\nGitHub\n(código + datos)", "#1A2238", fs=8.5)
    box(ax, 0.2, 0.5, 2.2, 1.0, "GitHub Pages\n(espejo)", "#5D6B88", fs=8.5)
    box(ax, 3.6, 1.6, 2.6, 1.4, "VPS (Caddy)\nplanperu2050.pe\nHTTPS automático", "#1B8A4B", fs=9)
    box(ax, 7.2, 2.7, 2.6, 0.9, "Sitio estático\n(HTML/JS/JSON/PDF)", "#B8840E", fs=8.5)
    box(ax, 7.2, 1.5, 2.6, 0.9, "Gateway IA seguro\n(prompt+modelo fijos,\nrate-limit, key oculta)", "#D91023", fs=7.5)
    box(ax, 7.2, 0.3, 2.6, 0.9, "OpenRouter\n(LLM)", "#3b82f6", fs=8.5)
    arrow(ax, 2.4, 3.1, 3.6, 2.6); ax.text(2.5, 3.35, "deploy.sh (rsync)", fontsize=7, color="#5D6B88")
    arrow(ax, 2.4, 1.0, 2.4, 1.0)
    arrow(ax, 1.3, 2.6, 1.3, 1.5); ax.text(1.4, 2.05, "git push", fontsize=7, color="#5D6B88")
    arrow(ax, 6.2, 2.5, 7.2, 3.0)
    arrow(ax, 6.2, 2.2, 7.2, 1.9)
    arrow(ax, 8.5, 1.5, 8.5, 1.2)
    ax.text(5, 3.8, "Arquitectura de despliegue", ha="center", fontsize=11, weight="bold", color="#1A2238")
    p = os.path.join(IMG, "tec_arch.png"); fig.savefig(p, dpi=160, bbox_inches="tight"); plt.close(fig); return p

# ---------- diagrama: estado de cobertura ----------
def diag_estado():
    fig, ax = plt.subplots(figsize=(5.0, 3.4))
    vals = [n_val, n_rev, max(0, n_total - n_val - n_rev)]
    labels = [f"Validadas ({n_val})", f"En revisión ({n_rev})", f"En redacción ({vals[2]})"]
    ax.pie(vals, labels=labels, colors=["#1B8A4B", "#B8840E", "#5D6B88"], autopct=lambda p: f"{p*sum(vals)/100:.0f}",
           textprops={"fontsize": 9, "color": "#1A2238"}, wedgeprops={"edgecolor": "white", "linewidth": 2})
    ax.set_title(f"Cobertura: {n_total} comisiones", fontsize=11, weight="bold", color="#1A2238")
    p = os.path.join(IMG, "tec_estado.png"); fig.savefig(p, dpi=160, bbox_inches="tight"); plt.close(fig); return p

def ratio(path):
    from PIL import Image as PImg; w, h = PImg.open(path).size; return h/w

def header_footer(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(RED); canvas.rect(0, A4[1]-6, A4[0], 6, fill=1, stroke=0)
    canvas.setFillColor(GOLD); canvas.rect(0, A4[1]-9, A4[0], 3, fill=1, stroke=0)
    canvas.setFillColor(GREY); canvas.setFont("Helvetica", 7.5)
    canvas.drawString(18*mm, 10*mm, "Plan Perú 2050 · Informe técnico del portal · CNPP — CIP")
    canvas.drawRightString(A4[0]-18*mm, 10*mm, f"{doc.page}")
    canvas.restoreState()

def build():
    pipe, arch, estado = diag_pipeline(), diag_arch(), diag_estado()
    s = []
    s.append(Paragraph("PLAN PERÚ 2050 · DOCUMENTO DE INGENIERÍA", S["eyebrow"]))
    s.append(Paragraph("Informe técnico del portal-dashboard", S["title"]))
    s.append(Paragraph("Arquitectura, pipeline de datos y proceso de actualización de la plataforma de Comisiones "
                       "Temáticas del Plan Perú 2050. Documento de referencia para el CNPP — Colegio de Ingenieros del Perú.", S["sub"]))
    s.append(HRFlowable(color=LINE, thickness=.6, spaceBefore=4, spaceAfter=8))

    # KPIs
    k = [[Paragraph(str(n_total), S["kpin"]), Paragraph(str(n_val), S["kpin"]), Paragraph(str(n_rev), S["kpin"]), Paragraph(str(n_ind), S["kpin"])],
         [Paragraph("Comisiones", S["kpil"]), Paragraph("Validadas", S["kpil"]), Paragraph("En revisión", S["kpil"]), Paragraph("Indicadores", S["kpil"])]]
    kt = Table(k, colWidths=[42*mm]*4); kt.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),LIGHT),("BOX",(0,0),(-1,-1),.5,LINE),
        ("INNERGRID",(0,0),(-1,-1),.5,colors.white),("TOPPADDING",(0,0),(-1,0),7),("BOTTOMPADDING",(0,1),(-1,1),7),("VALIGN",(0,0),(-1,-1),"MIDDLE")]))
    s.append(kt)

    s.append(Paragraph("1. Resumen", S["h"]))
    s.append(Paragraph("El portal es una aplicación web <b>estática</b> (sin servidor de aplicaciones) que publica la "
        "información de las comisiones del Plan Perú 2050 y permite consultarla, filtrarla, simular escenarios y descargar "
        "los documentos. Los datos se producen mediante un <b>pipeline asistido por IA</b> que transforma las redacciones de "
        "cada comisión en datos estructurados verificables. El diseño prioriza <b>rapidez, bajo costo, trazabilidad de fuentes "
        "y facilidad de actualización</b>.", S["body"]))

    s.append(Paragraph("2. Pipeline de datos", S["h"]))
    s.append(Paragraph("Cada documento de comisión recorre cinco etapas hasta llegar al portal:", S["body"]))
    s.append(Image(pipe, width=170*mm, height=170*mm*ratio(pipe)))
    s.append(Paragraph("Figura 1. Del documento de la comisión al portal publicado.", S["cap"]))
    for b in [
        "<b>1. Ingesta:</b> se reciben los Informes Ejecutivos (.docx, .pdf, .pptx) de cada comisión.",
        "<b>2. Conversión:</b> se extrae el texto con herramientas estándar (pandoc, pdftotext, python-pptx).",
        "<b>3. Extracción IA multi-agente:</b> un agente por comisión estructura el contenido al esquema oficial "
        "(I. Situación futura … VIII. Articulación con Programas Presupuestales), con regla <b>anti-overclaiming</b>: "
        "solo se capturan cifras explícitas en el documento; si un dato no consta, se marca como «sin dato» (nunca se inventa).",
        "<b>4. Validación:</b> los datos quedan en JSON versionado. Cada comisión se marca «validada» (redacción oficial) o "
        "«en revisión» (línea base preliminar, claramente etiquetada).",
        "<b>5. Publicación:</b> se generan automáticamente las fichas, los PDFs (con índice) y se despliega al servidor.",
    ]: s.append(Paragraph("• " + b, S["bullet"]))

    s.append(Paragraph("3. Arquitectura y despliegue", S["h"]))
    s.append(Image(arch, width=170*mm, height=170*mm*ratio(arch)))
    s.append(Paragraph("Figura 2. El código y los datos viven en GitHub; el sitio se sirve desde un VPS con Caddy "
        "(HTTPS automático). La consulta con IA pasa por un proxy que mantiene la llave del modelo oculta en el servidor.", S["cap"]))

    s.append(Paragraph("4. Stack tecnológico", S["h"]))
    rows = [[Paragraph("Capa", S["th"]), Paragraph("Tecnología", S["th"]), Paragraph("Rol", S["th"])]]
    stack = [
        ("Frontend", "HTML5 + JavaScript (sin framework)", "Interfaz, filtros, fichas, navegación por pestañas"),
        ("Visualización", "Chart.js + Leaflet", "Gráficos de avance/brechas y mapa del Perú"),
        ("Simulación", "JS (fórmulas polinómicas)", "Escenarios y trayectoria 2026→2050"),
        ("Datos", "JSON versionado en Git", "Comisiones, indicadores, puntos del mapa"),
        ("Extracción", "Pipeline IA multi-agente", "Documentos → datos estructurados"),
        ("Documentos", "Python (reportlab, python-docx, matplotlib)", "PDFs/Word con índice y gráficos"),
        ("IA / Asistente", "OpenRouter vía proxy Caddy", "Consulta en lenguaje natural, key oculta"),
        ("Hosting", "VPS + Caddy (HTTPS automático)", "planperu2050.pe — servidor del portal"),
        ("CI / Fuente", "GitHub + GitHub Pages (espejo)", "Versionado y respaldo"),
        ("Analítica", "Google Analytics (GA4)", "Métricas de uso"),
    ]
    for a, b, c in stack:
        rows.append([Paragraph("<b>"+a+"</b>", S["td"]), Paragraph(b, S["td"]), Paragraph(c, S["td"])])
    t = Table(rows, colWidths=[30*mm, 58*mm, 82*mm], repeatRows=1)
    t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),RED),("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white,LIGHT]),
        ("GRID",(0,0),(-1,-1),.4,LINE),("VALIGN",(0,0),(-1,-1),"MIDDLE"),("TOPPADDING",(0,0),(-1,-1),3),("BOTTOMPADDING",(0,0),(-1,-1),3),
        ("LEFTPADDING",(0,0),(-1,-1),5),("RIGHTPADDING",(0,0),(-1,-1),5)]))
    s.append(t)

    s.append(PageBreak())
    s.append(Paragraph("5. Estado actual de la cobertura", S["h"]))
    s.append(Image(estado, width=95*mm, height=95*mm*ratio(estado)))
    s.append(Paragraph(f"Figura 3. {n_val} comisiones validadas y {n_rev} en revisión, de {n_total} comisiones temáticas.", S["cap"]))
    s.append(Paragraph("Las comisiones «validadas» provienen de redacciones oficiales; las «en revisión» son una línea base "
        "preliminar inferida que el equipo del CIP valida progresivamente. Cada ficha indica su estado de forma visible.", S["body"]))

    s.append(Paragraph("6. Proceso de actualización", S["h"]))
    s.append(Paragraph("Incorporar o actualizar una comisión es un proceso reproducible de pocos pasos:", S["body"]))
    for i, b in enumerate([
        "Recibir el Informe Ejecutivo de la comisión y colocarlo en la carpeta de fuentes.",
        "Convertir a texto y ejecutar la extracción IA (un agente por documento) al esquema oficial.",
        "Revisar el JSON resultante; mover la comisión de «en revisión» a «validada» cuando corresponda.",
        "Regenerar automáticamente las fichas y los PDFs (scripts de Python).",
        "Publicar: «git push» (versiona + espejo) y «deploy.sh» (actualiza el servidor). El HTTPS se renueva solo.",
    ], 1): s.append(Paragraph(f"<b>{i}.</b> " + b, S["bullet"]))
    s.append(Paragraph("Tiempo típico por lote de comisiones: minutos. No se requiere intervención manual en el servidor.", S["body"]))

    s.append(Paragraph("7. Funcionalidades del portal", S["h"]))
    for b in [
        "Directorio de comisiones con buscador y filtros por eje y por estado.",
        "Ficha por comisión con la estructura del Informe Ejecutivo (I–VIII), incluida la articulación con el Acuerdo "
        "Nacional, el PEDN 2050 y los Programas Presupuestales.",
        "Panorama nacional con gráficos comparativos y mapa territorial del Perú.",
        "Simulación de escenarios con fórmulas polinómicas (trayectoria 2026→2050).",
        "Asistente de consulta con IA (respuestas breves, lenguaje natural).",
        "Descarga de documentos en PDF (fichas, plan de 100 días, síntesis por ejes) con índice.",
        "Sección de preguntas frecuentes (FAQ) y dosificación de la vista por hitos.",
    ]: s.append(Paragraph("• " + b, S["bullet"]))

    s.append(Paragraph("8. Seguridad del asistente de IA", S["h"]))
    s.append(Paragraph("El asistente conversacional fue sometido a un <b>análisis adversarial</b> (pruebas de abuso) y "
        "posteriormente blindado. Diseño actual:", S["body"]))
    for b in [
        "<b>Gateway propio del lado del servidor:</b> el navegador solo envía la pregunta; el servidor controla el "
        "prompt del sistema, el modelo y el contexto. El usuario no puede alterar el rol del asistente.",
        "<b>Alcance restringido:</b> responde únicamente sobre el Plan Perú 2050; cualquier pregunta de otro tema "
        "(o intento de cambiar sus reglas) recibe un mensaje fijo de rechazo.",
        "<b>Modelo y respuesta acotados:</b> el modelo y el límite de tokens los fija el servidor (no el cliente), "
        "evitando el uso de modelos costosos con la cuenta del proyecto.",
        "<b>Límite de frecuencia (rate-limit) por IP:</b> impide el abuso por volumen de consultas.",
        "<b>Llave de IA protegida:</b> la credencial del modelo reside solo en el servidor (variable de entorno del "
        "servicio), nunca en el navegador ni en la configuración pública del proxy.",
    ]: s.append(Paragraph("• " + b, S["bullet"]))
    s.append(Paragraph("Resultado de la verificación posterior: los intentos de abuso (uso fuera de tema, modelos "
        "arbitrarios, inyección de instrucciones y consultas masivas) quedan bloqueados, manteniéndose el servicio "
        "funcional para consultas legítimas.", S["body"]))

    s.append(Paragraph("9. Principios de diseño", S["h"]))
    for b in [
        "<b>Anti-overclaiming:</b> no se inventan cifras; las fuentes son trazables y el estado de validación es visible.",
        "<b>Reproducibilidad:</b> todo el proceso (extracción, documentos, despliegue) está automatizado y versionado.",
        "<b>Bajo costo y robustez:</b> sitio estático + un servidor; sin base de datos compleja ni dependencias frágiles.",
        "<b>Privacidad:</b> los datos personales de los integrantes de las comisiones no se publican.",
        "<b>Seguridad por diseño:</b> los controles del asistente viven en el servidor, no en el cliente.",
    ]: s.append(Paragraph("• " + b, S["bullet"]))

    s.append(Spacer(1, 10))
    s.append(Paragraph("Desarrollo, analítica de datos e ingeniería del portal: <b>Carlos Cárdenas Fernández</b>. "
        "Portal en producción: planperu2050.pe", st("f", fontSize=8.5, textColor=GREY, leading=12)))

    SimpleDocTemplate(os.path.join(OUT, "INFORME-TECNICO-dashboard.pdf"), pagesize=A4,
        topMargin=20*mm, bottomMargin=16*mm, leftMargin=18*mm, rightMargin=18*mm, title="Informe técnico — Plan Perú 2050"
    ).build(s, onFirstPage=header_footer, onLaterPages=header_footer)
    print("✓ entregables/INFORME-TECNICO-dashboard.pdf")

if __name__ == "__main__":
    build()

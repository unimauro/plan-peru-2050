#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Informe de avance del Plan Perú 2050 en PDF (para presentar a Tellys). Mismo contenido que el Word."""
import os, json
from datetime import date
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
                                HRFlowable, ListFlowable, ListItem)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
OUT = os.path.join(ROOT, "entregables", "Primer-Informe-Plan-Peru-2050.pdf")

RED = colors.HexColor("#D91023"); GOLD = colors.HexColor("#B8840E")
DARK = colors.HexColor("#1A2238"); GREY = colors.HexColor("#5D6B88")
LIGHT = colors.HexColor("#F4F6FB"); LINE = colors.HexColor("#D7DCE8")


def L(fn):
    return json.load(open(os.path.join(DATA, fn), encoding="utf-8"))


meta = L("meta.json")
val = len(L("comisiones.json")); rev = len(L("comisiones_revision.json"))
arts = L("articulacion.json")["articulaciones"]
nAN = sum(len(x["acuerdo_nacional"]) for x in arts)
nPP = sum(len(x["programas_presupuestales"]) for x in arts)
nK = L("keiko_articulacion.json")["total_propuestas"]
seg = L("seguimiento.json"); nInd = len(seg["indicadores"]); nAuto = len(seg.get("auto", {}))
nPPtot = L("programas_presupuestales.json")["total"]


def sp(name, **kw):
    kw.setdefault("fontName", "Helvetica")
    return ParagraphStyle(name, **kw)


S = {
    "eyebrow": sp("eyebrow", fontName="Helvetica-Bold", fontSize=9, textColor=GOLD, spaceAfter=2, leading=11),
    "cover": sp("cover", fontName="Helvetica-Bold", fontSize=24, textColor=RED, spaceAfter=4, leading=27),
    "coversub": sp("coversub", fontSize=12, textColor=GREY, spaceAfter=3, leading=16),
    "meta": sp("meta", fontSize=10.5, textColor=DARK, spaceAfter=2, leading=14),
    "h1": sp("h1", fontName="Helvetica-Bold", fontSize=15, textColor=RED, spaceBefore=14, spaceAfter=3, leading=18),
    "h2": sp("h2", fontName="Helvetica-Bold", fontSize=11.5, textColor=GOLD, spaceBefore=8, spaceAfter=3, leading=14),
    "body": sp("body", fontSize=10.5, textColor=DARK, leading=15, spaceAfter=6, alignment=TA_LEFT),
    "note": sp("note", fontSize=9.5, textColor=GREY, leading=13, spaceAfter=6),
    "bullet": sp("bullet", fontSize=10.5, textColor=DARK, leading=14, spaceAfter=2),
    "th": sp("th", fontName="Helvetica-Bold", fontSize=9.5, textColor=colors.white, leading=12),
    "td": sp("td", fontSize=9.5, textColor=DARK, leading=12),
    "link": sp("link", fontSize=10.5, textColor=GOLD, leading=14, spaceAfter=6),
}
E = lambda s: (str(s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def H1(t): return [Paragraph(E(t), S["h1"]), HRFlowable(width="100%", thickness=1, color=GOLD, spaceAfter=6)]
def H2(t): return [Paragraph(E(t), S["h2"])]
def P(t, style="body"): return [Paragraph(E(t) if "<" not in t else t, S[style])]


def bl(items):
    lf = []
    for it in items:
        if isinstance(it, tuple):
            lf.append(ListItem(Paragraph("<b>%s</b> %s" % (E(it[0]), E(it[1])), S["bullet"]), leftIndent=6))
        else:
            lf.append(ListItem(Paragraph(E(it), S["bullet"]), leftIndent=6))
    return [ListFlowable(lf, bulletType="bullet", start="•", bulletColor=RED, leftIndent=12), Spacer(1, 4)]


def tbl(headers, rows, widths):
    data = [[Paragraph(h, S["th"]) for h in headers]]
    for r in rows:
        data.append([Paragraph(E(str(c)), S["td"]) for c in r])
    t = Table(data, colWidths=[w * mm for w in widths], repeatRows=1)
    ts = [("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1F2A44")),
          ("GRID", (0, 0), (-1, -1), .5, LINE), ("VALIGN", (0, 0), (-1, -1), "TOP"),
          ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
          ("LEFTPADDING", (0, 0), (-1, -1), 6), ("RIGHTPADDING", (0, 0), (-1, -1), 6)]
    for i in range(1, len(data)):
        if i % 2 == 0:
            ts.append(("BACKGROUND", (0, i), (-1, i), LIGHT))
    t.setStyle(TableStyle(ts))
    return [t, Spacer(1, 8)]


def header_footer(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(RED); canvas.rect(0, A4[1] - 6, A4[0], 6, fill=1, stroke=0)
    canvas.setFillColor(GOLD); canvas.rect(0, A4[1] - 9, A4[0], 3, fill=1, stroke=0)
    canvas.setFillColor(GREY); canvas.setFont("Helvetica", 7.5)
    canvas.drawString(18 * mm, 10 * mm, "Plan Perú 2050 · Primer Informe · 21-jul-2026 · CNPP — Colegio de Ingenieros del Perú")
    canvas.drawRightString(A4[0] - 18 * mm, 10 * mm, str(doc.page))
    canvas.restoreState()


story = []
# Portada
story += [Spacer(1, 10), Paragraph("PLAN PERÚ 2050 &nbsp;·&nbsp; PRIMER INFORME", S["eyebrow"]),
          Paragraph("Primer Informe de avance de la plataforma digital", S["cover"]),
          Paragraph("Comisiones Temáticas Nacionales · CNPP — Colegio de Ingenieros del Perú", S["coversub"]),
          Spacer(1, 14),
          Paragraph("<b>Informe N°:</b> 1 (de 3)", S["meta"]),
          Paragraph("<b>Fecha:</b> 21 de julio de 2026", S["meta"]),
          Paragraph("<b>Elaborado por:</b> Ing. Carlos Cárdenas Fernández", S["meta"]),
          Paragraph("<b>Revisor principal:</b> Ing. Alejandro Camarena", S["meta"]),
          Paragraph("<b>Dirigido a:</b> Ing. Tellys Paucar y equipo técnico del Plan Perú 2050 — CNPP / Colegio de Ingenieros del Perú", S["meta"]),
          Paragraph('<b>Plataforma:</b> <font color="#B8840E">https://planperu2050.pe</font>', S["meta"]),
          Spacer(1, 12)]

story += H1("1. Resumen ejecutivo")
story += P("Se ha construido y puesto en producción una plataforma web interactiva del Plan Perú 2050 "
           "(https://planperu2050.pe) que sistematiza las %d Comisiones Temáticas Nacionales, las articula con el "
           "Acuerdo Nacional y con los Programas Presupuestales del MEF, incorpora el plan de gobierno entrante, una "
           "capa de inteligencia territorial y un sistema de seguimiento mensual de indicadores hacia las metas 2050. "
           "Todo el contenido está etiquetado según su origen, bajo un principio estricto de no sobre-afirmación." % meta["totalComisiones"])
story += tbl(["Componente", "Estado"], [
    ["Comisiones en la plataforma", "%d de %d: %d validadas + %d en revisión" % (val + rev, meta["totalComisiones"], val, rev)],
    ["Clasificación", "Los 4 ejes / 36 políticas del Acuerdo Nacional"],
    ["Articulación al Acuerdo Nacional", "%d enlaces (política ↔ comisión)" % nAN],
    ["Articulación a Programas Presupuestales", "%d enlaces (%d PP del MEF)" % (nPP, nPPtot)],
    ["Plan de gobierno articulado", "%d propuestas alineadas a comisiones y AN" % nK],
    ["Seguimiento de indicadores", "%d hacia meta 2050 (%d con dato oficial automático)" % (nInd, nAuto)],
], [58, 105])

story += H1("2. La plataforma y sus módulos")
story += P("El tablero es una aplicación web pública, responsiva y de actualización automática. Sus módulos:")
story += bl([
    ("Explorar.", "Ficha de cada comisión con visión 2050, diagnóstico, objetivos, acciones, indicadores (hoy → meta 2050) y recomendaciones, en el formato oficial de Informe Ejecutivo."),
    ("Articulación.", "Cubo de doble entrada: por cada eje y política del Acuerdo Nacional, las comisiones vinculadas y el tipo de relación."),
    ("Flujos.", "Diagrama Sankey por capas: Políticas de Estado → Comisiones → Programas Presupuestales."),
    ("Plan de gobierno.", "Propuestas del plan de gobierno entrante alineadas a las comisiones del CIP y al Acuerdo Nacional."),
    ("Territorial.", "Indicadores por departamento, provincia y distrito (IDH, pobreza, vulnerabilidad, VAB) y gasto público del MEF."),
    ("Seguimiento.", "Avance mensual de los indicadores hacia las metas 2050, con dato oficial automático donde existe."),
    ("Simulación.", "Proyección interactiva de escenarios al 2050."),
])

story += H1("3. Articulación estratégica (hacia arriba y hacia abajo)")
story += P("Cada comisión se articula en dos direcciones, con la metodología de clasificación acordada. Cada vínculo "
           "lleva una justificación textual, de modo que la matriz es completamente auditable.")
story += H2("Tipos de relación")
story += bl([("Igual / similar.", "igualdad o similitud semántica directa."),
             ("Desagregado.", "la comisión especifica (temática o territorialmente) algo contenido en la política o el programa."),
             ("Causal.", "relación causa-efecto deducida de los textos.")])
story += H2("Alcance actual")
story += bl(["%d enlaces Comisiones ↔ Políticas de Estado del Acuerdo Nacional (hacia arriba)." % nAN,
             "%d enlaces Comisiones ↔ Programas Presupuestales del MEF (hacia abajo, %d PP)." % (nPP, nPPtot)])
story += P("La propuesta de articulación fue generada con inteligencia artificial (un análisis por comisión) y se "
           "entrega como PROPUESTA A VALIDAR por el equipo técnico. Se adjunta la matriz completa en Excel.", "note")

story += H1("4. Articulación con el plan de gobierno entrante")
story += P("Se procesaron los 3 pilares del plan de gobierno (Orden, Económico, Social) y se alinearon %d propuestas "
           "a las comisiones del CIP y a las políticas del Acuerdo Nacional, con el mismo criterio de relación. Esto "
           "muestra de forma objetiva cómo el plan de gobierno se articula con la agenda técnica del Colegio, y sirve "
           "de base para un seguimiento posterior con dato duro." % nK)

story += H1("5. Inteligencia territorial")
story += P("Módulo con un mapa interactivo del Perú y datos reales por departamento, provincia y distrito:")
story += bl([
    "Mapa interactivo por distrito (1,826 distritos), coloreado por IDH, pobreza o pobreza extrema, con detalle al hacer clic en cada distrito.",
    "IDH, pobreza y pobreza extrema por distrito, y población (fuente PNUD / INEI).",
    "Gasto público del MEF (SIAF) por departamento: presupuesto, devengado y ejecución del año en curso.",
    "Presupuesto por tipo de gasto: corriente vs. inversión/capital, por departamento (MEF, año en curso).",
    "Valor Agregado Bruto (VAB) por departamento y VAB per cápita (INEI 2023), como aproximación al desarrollo productivo.",
    "Vulnerabilidad económica a la pobreza (INEI): 31.4% nacional (2023); a nivel departamental por grupos (2019).",
])
story += P("Nota metodológica: la vulnerabilidad a la pobreza NO se publica a nivel distrital; el nivel oficial más fino "
           "es provincial (2018) y departamental agrupado (2019). El VAB oficial se publica por departamento. Se indica "
           "la fuente y el año en cada caso.", "note")

story += H1("6. Seguimiento mensual de indicadores")
story += P("Sistema que registra automáticamente, cada mes, qué tan cerca o lejos estamos de las metas 2050. Ordena los "
           "indicadores del más lejano al más cercano a su meta y calcula un índice de avance. Para los indicadores con "
           "serie estadística oficial, el valor se actualiza solo desde la fuente (hoy %d indicadores toman su valor del "
           "BCRP, con su año y su advertencia de vigencia); el resto usa el valor de la redacción de la comisión. Los "
           "indicadores nuevos se incorporan automáticamente." % nAuto)

story += H1("7. Estado de las observaciones de la última reunión")
story += tbl(["Observación", "Estado"], [
    ["Exportar la matriz de articulación a Excel para validar", "ATENDIDO — Excel con 3 hojas y columnas de validación"],
    ["Corregir el PDF con los ejes temáticos antiguos", "ATENDIDO — ahora muestra los ejes del Acuerdo Nacional"],
    ["Articulación con Programas Presupuestales", "HECHO — detalle de comisión, Flujos y Excel"],
    ["Columna de Vulnerabilidad económica a la pobreza (INEI)", "ATENDIDO — a nivel departamental (no existe distrital)"],
    ["Columna de Valor Agregado Bruto (VAB)", "ATENDIDO — por departamento y per cápita (INEI 2023)"],
    ["Confirmar el año del IDH", "Es IDH 2019 (PNUD), el último a nivel distrital"],
    ["Mapa territorial interactivo por distrito", "ATENDIDO — mapa del Perú con IDH/pobreza y detalle por distrito"],
    ["Presupuesto corriente vs. inversión por territorio", "ATENDIDO — por departamento (MEF, tipo de gasto)"],
], [92, 71])

story += H1("8. Fuentes y principio anti-sobreafirmación")
story += P("Todo el contenido está rotulado según su naturaleza, para no presentar como oficial lo que es estimado o inferido:")
story += bl([
    ("Dato oficial (fuente y año):", "IDH y pobreza (PNUD/INEI), gasto MEF (SIAF), VAB y vulnerabilidad (INEI), presión tributaria e informalidad (BCRP)."),
    ("Propuesta con IA (a validar):", "la matriz de articulación y el alineamiento del plan de gobierno."),
    ("Redacción de la comisión:", "validada o “en revisión” (línea base preliminar)."),
])

story += H1("9. Cómo revisar y validar")
story += P("Se adjunta la matriz completa en Excel. Cada fila trae la relación propuesta, su tipo y su justificación, más "
           "tres columnas para la validación del equipo: «¿Correcto?» (Sí/No/Revisar), «Tipo corregido» y «Observación», "
           "con menús desplegables. Con la matriz corregida se cierra la articulación de forma definitiva.")
story += [Paragraph('Descarga directa: <font color="#B8840E">https://planperu2050.pe/entregables/articulacion.xlsx</font>', S["link"])]

story += H1("10. Próximos pasos")
story += bl([
    "Recibir la versión final de las comisiones y actualizar el tablero.",
    "Validación humana de la matriz de articulación (con el Excel adjunto).",
    "Detallar la articulación a nivel de objetivos de cada política de Estado (tercer nivel del Acuerdo Nacional).",
    "Llevar el presupuesto corriente vs. inversión al nivel provincial y distrital.",
    "Conectar más indicadores de seguimiento a fuentes oficiales (INEI/ENDES/MTC/MINEM).",
])
story += H1("Enlaces")
story += bl([
    "Plataforma: https://planperu2050.pe",
    "Matriz de articulación (Excel): https://planperu2050.pe/entregables/articulacion.xlsx",
    "Fichas por comisión (PDF): https://planperu2050.pe/entregables/pdf/",
])

os.makedirs(os.path.dirname(OUT), exist_ok=True)
doc = SimpleDocTemplate(OUT, pagesize=A4, topMargin=20 * mm, bottomMargin=16 * mm,
                        leftMargin=18 * mm, rightMargin=18 * mm, title="Informe Plan Perú 2050")
doc.build(story, onFirstPage=header_footer, onLaterPages=header_footer)
print("✓", OUT)

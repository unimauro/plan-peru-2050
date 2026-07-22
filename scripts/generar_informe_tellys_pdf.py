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
                                HRFlowable, ListFlowable, ListItem, Image, KeepTogether)

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
try:
    _ao = L("articulacion_objetivos.json")["articulacion"]; nObj = sum(len(v) for v in _ao.values())
except Exception:
    nObj = 0
try:
    _anj = L("acuerdo_nacional.json"); nObjAN = _anj.get("total_objetivos", 0)
except Exception:
    nObjAN = 0
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


IMG = os.path.join(ROOT, "entregables", "_img")
def shot(fn, caption, w=170):
    p = os.path.join(IMG, fn)
    if not os.path.exists(p):
        return []
    from PIL import Image as PILImage
    iw, ih = PILImage.open(p).size
    W = w * mm; H = W * ih / iw
    im = Image(p, width=W, height=H)
    im.hAlign = "CENTER"
    cap = Paragraph("<i>" + E(caption) + "</i>", ParagraphStyle("cap", fontSize=8.5, textColor=GREY, leading=11, alignment=1, spaceBefore=3, spaceAfter=10))
    box = Table([[im], [cap]], colWidths=[W])
    box.setStyle(TableStyle([("BOX", (0, 0), (-1, -1), .6, LINE), ("TOPPADDING", (0, 0), (-1, -1), 5),
                             ("BOTTOMPADDING", (0, 0), (-1, -1), 2), ("LEFTPADDING", (0, 0), (-1, -1), 5),
                             ("RIGHTPADDING", (0, 0), (-1, -1), 5), ("BACKGROUND", (0, 0), (-1, -1), colors.white)]))
    return [Spacer(1, 4), box, Spacer(1, 4)]


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

# Índice
story += H1("Índice")
_toc = [
    "1. Resumen ejecutivo", "2. La plataforma y sus módulos",
    "3. Articulación estratégica (hacia arriba y hacia abajo)", "4. Articulación con el plan de gobierno entrante",
    "5. Inteligencia territorial", "6. Seguimiento mensual de indicadores",
    "7. Estado de las observaciones de la última reunión", "8. Fuentes de datos y principio anti-sobreafirmación",
    "9. Cómo revisar y validar", "10. Próximos pasos", "Anexo. Enlaces",
]
story += [ListFlowable([ListItem(Paragraph(E(t), S["bullet"]), leftIndent=6) for t in _toc],
                       bulletType="bullet", start="•", bulletColor=GOLD, leftIndent=12), Spacer(1, 6)]

story += H1("1. Resumen ejecutivo")
story += P("El presente documento constituye el <b>Primer Informe de avance</b> de la plataforma digital del "
           "Plan Perú 2050, desarrollada para las Comisiones Temáticas Nacionales del CNPP — Colegio de Ingenieros "
           "del Perú. La plataforma, disponible en línea y de acceso público en https://planperu2050.pe, transforma "
           "el trabajo de las comisiones —hasta ahora disperso en documentos— en una herramienta interactiva, "
           "consultable y verificable, orientada a la toma de decisiones y a la incidencia técnica.")
story += P("En su estado actual, la plataforma sistematiza las %d Comisiones Temáticas Nacionales y las articula en "
           "<b>dos direcciones</b>: hacia arriba, con los cuatro ejes y las treinta y seis Políticas de Estado del "
           "Acuerdo Nacional, y hacia abajo, con los Programas Presupuestales del Ministerio de Economía y Finanzas. "
           "Incorpora, además, el alineamiento del plan de gobierno entrante, una capa de inteligencia territorial "
           "con datos oficiales a nivel de departamento, provincia y distrito, y un sistema de seguimiento mensual "
           "que mide cuán cerca o lejos se encuentra el país de las metas aspiracionales al 2050. La totalidad del "
           "contenido se encuentra rotulada según su origen —dato oficial, propuesta asistida por inteligencia "
           "artificial a validar, o redacción de la comisión— bajo un principio estricto de no sobre-afirmación." % meta["totalComisiones"])
story += tbl(["Componente", "Estado"], [
    ["Comisiones en la plataforma", "%d de %d: %d validadas + %d en revisión" % (val + rev, meta["totalComisiones"], val, rev)],
    ["Clasificación", "Los 4 ejes / 36 políticas del Acuerdo Nacional"],
    ["Articulación al Acuerdo Nacional", "%d enlaces (política ↔ comisión)" % nAN],
    ["Articulación a Programas Presupuestales", "%d enlaces (%d PP del MEF)" % (nPP, nPPtot)],
    ["Plan de gobierno articulado", "%d propuestas alineadas a comisiones y AN" % nK],
    ["Seguimiento de indicadores", "%d hacia meta 2050 (%d con dato oficial automático)" % (nInd, nAuto)],
], [58, 105])

story += H1("2. La plataforma y sus módulos")
story += P("El tablero es una aplicación web pública, responsiva (se adapta a computadora, tableta y teléfono) y de "
           "actualización automática. Ofrece una opción de tema claro u oscuro para su presentación e impresión. "
           "Se organiza en los siguientes módulos:")
story += bl([
    ("Explorar.", "Ficha de cada comisión con visión 2050, diagnóstico, objetivos, acciones, indicadores (hoy → meta 2050) y recomendaciones, en el formato oficial de Informe Ejecutivo."),
    ("Articulación.", "Cubo de doble entrada: por cada eje y política del Acuerdo Nacional, las comisiones vinculadas y el tipo de relación."),
    ("Flujos.", "Diagrama Sankey por capas: Políticas de Estado → Comisiones → Programas Presupuestales."),
    ("Plan de gobierno.", "Propuestas del plan de gobierno entrante alineadas a las comisiones del CIP y al Acuerdo Nacional."),
    ("Territorial.", "Indicadores por departamento, provincia y distrito (IDH, pobreza, vulnerabilidad, VAB) y gasto público del MEF."),
    ("Seguimiento.", "Avance mensual de los indicadores hacia las metas 2050, con dato oficial automático donde existe."),
    ("Simulación.", "Proyección interactiva de escenarios al 2050."),
])
story += shot("cap_explorar.png", "Vista principal (Explorar): las comisiones temáticas, con filtros por eje del Acuerdo Nacional y estado de validación.")

story += H1("3. Articulación estratégica (hacia arriba y hacia abajo)")
story += P("Cada comisión se articula en dos direcciones, con la metodología de clasificación acordada. Cada vínculo "
           "lleva una justificación textual, de modo que la matriz es completamente auditable.")
story += H2("Tipos de relación")
story += bl([("Igual / similar.", "igualdad o similitud semántica directa."),
             ("Desagregado.", "la comisión especifica (temática o territorialmente) algo contenido en la política o el programa."),
             ("Causal.", "relación causa-efecto deducida de los textos.")])
story += H2("Alcance actual")
story += bl(["%d enlaces Comisiones ↔ Políticas de Estado del Acuerdo Nacional (hacia arriba)." % nAN,
             "%d enlaces Comisiones ↔ Objetivos específicos del Acuerdo Nacional (tercer nivel de la jerarquía)." % nObj,
             "%d enlaces Comisiones ↔ Programas Presupuestales del MEF (hacia abajo, %d PP)." % (nPP, nPPtot)])
story += P("La jerarquía del Acuerdo Nacional se incorporó en sus <b>tres niveles</b>: 4 ejes, 36 Políticas de Estado y "
           "%d objetivos (los compromisos con letra a, b, c…, tomados de acuerdonacional.pe). La articulación de cada "
           "comisión llega ahora hasta el objetivo específico, que es el nivel más fino y el ideal para el análisis." % nObjAN)
story += P("La propuesta de articulación fue generada con inteligencia artificial (un análisis por comisión) y se "
           "entrega como PROPUESTA A VALIDAR por el equipo técnico. Se adjunta la matriz completa en Excel.", "note")
story += shot("cap_articulacion.png", "Módulo Articulación: por cada eje y política del Acuerdo Nacional se listan las comisiones vinculadas y el tipo de relación (igual/similar, desagregado o causal).")
story += P("Adicionalmente, el módulo <b>Flujos</b> representa esta articulación como un diagrama de flujos (Sankey) "
           "por capas, que permite visualizar de un vistazo cómo las Políticas de Estado se conectan con las comisiones "
           "y estas, a su vez, con los Programas Presupuestales. El grosor de cada flujo refleja el número de vínculos.")
story += shot("cap_flujos.png", "Módulo Flujos: diagrama Sankey por capas — Políticas de Estado → Comisiones del CIP → Programas Presupuestales, para el eje Democracia y Estado de Derecho.")

story += H1("4. Articulación con el plan de gobierno entrante")
story += P("Se procesaron los 3 pilares del plan de gobierno (Orden, Económico, Social) y se alinearon %d propuestas "
           "a las comisiones del CIP y a las políticas del Acuerdo Nacional, con el mismo criterio de relación. Esto "
           "muestra de forma objetiva cómo el plan de gobierno se articula con la agenda técnica del Colegio, y sirve "
           "de base para un seguimiento posterior con dato duro." % nK)

story += H1("5. Inteligencia territorial")
story += P("Módulo con un mapa interactivo del Perú y datos reales por departamento, provincia y distrito:")
story += bl([
    "Mapa interactivo por distrito (1,826 distritos), coloreado por IDH, pobreza o pobreza extrema; y por departamento según VAB per cápita, vulnerabilidad, ejecución del gasto o porcentaje de inversión. Detalle al hacer clic en cada distrito.",
    "IDH, pobreza y pobreza extrema por distrito, y población (fuente PNUD / INEI).",
    "Gasto público del MEF (SIAF) por departamento: presupuesto, devengado y ejecución del año en curso.",
    "Presupuesto por tipo de gasto: corriente vs. inversión/capital, por departamento (MEF, año en curso).",
    "Valor Agregado Bruto (VAB) por departamento y VAB per cápita (INEI 2023), como aproximación al desarrollo productivo.",
    "Vulnerabilidad económica a la pobreza (INEI): 31.4% nacional (2023); a nivel departamental por grupos (2019).",
])
story += P("Nota metodológica: la vulnerabilidad a la pobreza NO se publica a nivel distrital; el nivel oficial más fino "
           "es provincial (2018) y departamental agrupado (2019). El VAB oficial se publica por departamento. Se indica "
           "la fuente y el año en cada caso.", "note")
story += shot("cap_territorial.png", "Módulo Territorial: mapa interactivo del Perú coloreado por IDH a nivel distrital, con el detalle presupuestal y socioeconómico por departamento.")

story += H1("6. Seguimiento mensual de indicadores")
story += P("Sistema que registra automáticamente, cada mes, qué tan cerca o lejos estamos de las metas 2050. Ordena los "
           "indicadores del más lejano al más cercano a su meta y calcula un índice de avance. Para los indicadores con "
           "serie estadística oficial, el valor se actualiza solo desde la fuente (hoy %d indicadores toman su valor del "
           "BCRP, con su año y su advertencia de vigencia); el resto usa el valor de la redacción de la comisión. Los "
           "indicadores nuevos se incorporan automáticamente." % nAuto)
story += shot("cap_seguimiento.png", "Módulo Seguimiento: los indicadores ordenados del más lejano al más cercano a su meta 2050, con el valor actual, la meta y el porcentaje de avance.")

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

story += H1("8. Fuentes de datos y principio anti-sobreafirmación")
story += P("Cada dato del tablero indica su fuente y su año. Detalle de las fuentes oficiales utilizadas:")
story += tbl(["Información", "Fuente · Año"], [
    ["Comisiones Temáticas (visión, diagnóstico, objetivos, metas)", "Redacciones del CNPP — Colegio de Ingenieros del Perú"],
    ["Ejes y Políticas de Estado", "Acuerdo Nacional — acuerdonacional.pe"],
    ["Programas Presupuestales", "MEF — Consulta Amigable / SIAF"],
    ["Gasto público y corriente vs. inversión por departamento", "MEF — Consulta Amigable / SIAF (año en curso)"],
    ["IDH, pobreza, pobreza extrema y población por distrito", "PNUD e INEI (IDH 2019)"],
    ["Valor Agregado Bruto (VAB) por departamento", "INEI — PBI por Departamentos 2007–2023 (2023E)"],
    ["Vulnerabilidad económica a la pobreza", "INEI (nacional 31,4% 2023; departamental por grupos 2019)"],
    ["Presión tributaria e informalidad laboral", "BCRP — BCRPData"],
    ["Geometría del mapa (distritos)", "GeoJSON de distritos del Perú (INEI/MINAM)"],
], [80, 83])
story += P("Además, todo el contenido está rotulado según su naturaleza, para no presentar como oficial lo que es estimado o inferido:")
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

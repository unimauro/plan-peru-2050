# Roadmap — Plan Perú 2050 Dashboard

Estado: 🟢 hecho · 🟡 en curso · ⚪ pendiente

## Fase 0 — Base (🟢 hecho)
- 🟢 Directorio de las 64 comisiones (sin PII) + buscador + filtros por eje.
- 🟢 Fichas con visión, brecha 2026, pilares, indicadores hoy→meta 2050, metas, acciones, recomendación.
- 🟢 Extracción estructurada de 8 comisiones (88 indicadores) con criterio anti-overclaiming.
- 🟢 Simulador de metas + índice de avance nacional.
- 🟢 Consulta IA (local / OpenRouter opcional).
- 🟢 Deploy GitHub Pages.

## Fase 1 — Visualización y territorio (🟡 en curso)
- 🟡 **Panorama nacional**: comparativa entre comisiones (avance, # indicadores, brechas) + distribución por eje.
- 🟡 **Mapa del Perú** (Leaflet): puntos estratégicos por comisión territorial (puertos, aeropuertos, hubs telecom, estaciones espaciales).
- 🟡 **Gráfico por comisión** en la ficha (Chart.js: avance de cada indicador).
- ⚪ Comparador de comisiones lado a lado.
- ⚪ Exportar ficha de comisión a PDF / compartir enlace directo (`#comision`).

## Fase 2 — Datos y profundidad (⚪ pendiente)
- ⚪ Incorporar las comisiones restantes a medida que lleguen sus redacciones (solo agregar al JSON).
- ⚪ Choropleth departamental (indicadores con desagregación territorial).
- ⚪ Línea de tiempo de hitos 2030 / 2040 / 2050 por indicador (las matrices traen valores intermedios).
- ⚪ Fuentes citadas y enlaces a los documentos oficiales por comisión.

## Fase 3 — Auditoría de alineamiento (⚪ pendiente — encargo aparte)
> Requiere los anexos/PDFs base (matrices de articulación) de Tellys/CIP.
- ⚪ Motor de *matching semántico*: objetivos de políticas vs Plan Estratégico (PSEN/PCN/PDRC).
- ⚪ Clasificación en 6 categorías: igual/similar · desagregado · agregado · causal con evidencia · causal sin evidencia · desarticulado.
- ⚪ Matriz navegable + tabulación de porcentajes por tipo de articulación.
- ⚪ Exportable a Word/Excel como anexo.

## Fase 4 — Difusión (⚪ pendiente)
- ⚪ Dominio propio / SEO + OG por comisión.
- ⚪ Proxy de IA en Vercel (key no expuesta) para la consulta inteligente.
- ⚪ Versión imprimible / informe ejecutivo.

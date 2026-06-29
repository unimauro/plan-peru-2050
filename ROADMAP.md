# Roadmap — Plan Perú 2050 Dashboard

Estado: 🟢 hecho · 🟡 en curso · ⚪ pendiente · 🔵 depende de terceros

Producción: **https://planperu2050.pe** (oficial) y **https://plan2050.tunky.net** (respaldo) — VPS + Caddy/HTTPS.
Fuente/espejo: repo `unimauro/plan-peru-2050` + GitHub Pages.

## Fase 0 — Base (🟢 hecho)
- 🟢 Directorio de las 65 comisiones (sin PII) + buscador + filtros por eje y por estado.
- 🟢 Fichas por comisión + simulador de metas + índice de avance nacional.
- 🟢 Extracción estructurada anti-overclaiming (cifras reales con fuente o `null`).
- 🟢 Consulta IA (OpenRouter vía proxy en Caddy, key oculta) + fallback de búsqueda local.

## Fase 1 — Visualización y territorio (🟢 hecho)
- 🟢 Panorama nacional con **4 gráficos**: avance por comisión, comisiones por eje, cobertura por eje, mayores brechas.
- 🟢 Mapa del Perú (Leaflet) con puntos estratégicos por comisión territorial (silueta real del geojson).
- 🟢 Gráfico de avance por comisión en la ficha.
- 🟢 Enlace directo por comisión (`#id`) + cerrar con ESC.
- 🟢 **Pestaña dedicada de Simulación** (tabs Explorar/Simulación) con escenarios predefinidos (Hoy/25/50/75/100%), índice nacional y gráfico de avance por indicador. Deep-link `?tab=simular`.
- 🟢 **Navegación por pestañas** en header sticky (Explorar / Simulación / FAQ), mobile-friendly + botón volver arriba.
- 🟢 **Simulación con fórmulas polinómicas** (ritmo lineal/cuadrático/curva-S/raíz) + **trayectoria temporal 2026→2050**.
- 🟢 **FAQ** (acordeón).
- ⚪ Comparador de comisiones lado a lado.

## Fase 2 — Datos y cobertura (🟢 mayormente hecho)
- 🟢 **65 comisiones con contenido**: 19 validadas (redacción oficial) + 45 «en revisión» (línea base inferida, etiquetada).
- 🟢 Etiquetas/estado: Validado / En revisión / En redacción, con filtros y banner.
- 🟢 **Editor `editar.html`** para agregar/editar indicadores «en revisión» y descargar el JSON.
- 🟢 Dosificación por hito (`?v=all/validado/h1/h2/h3`).
- 🔵 Validar las 45 «en revisión» con el equipo del CIP (proceso, no técnico).
- 🔵 Incorporar más comisiones a medida que lleguen redacciones (pipeline listo).
- ⚪ Línea de tiempo 2030 / 2040 / 2050 por indicador (las matrices traen valores intermedios).
- ⚪ Choropleth departamental para indicadores con desagregación territorial.

## Fase 3 — Estructura oficial e Informe Ejecutivo (🟢 hecho)
- 🟢 Ficha y descargables reordenados al **Informe Ejecutivo oficial (I–VIII)**.
- 🟢 **PDFs y Word con índice (Contenido)** + estructura: Situación Futura/Actual · Objetivos · Acciones · Matriz Resumen · Hitos 100 días · **Articulación con Acuerdo Nacional/PEDN 2050** · **Articulación con Programas Presupuestales**.
- 🟢 Entregables descargables: ficha por comisión, plan de 100 días, síntesis por ejes (PDF + Word).

## Fase 4 — Difusión y marca (🟢 hecho)
- 🟢 Dominio propio `planperu2050.pe` con HTTPS · SEO (robots/sitemap/meta) · miniatura OG.
- 🟢 Google Analytics (G-P4XP2W8XFE).
- 🟢 Autoría al pie (Carlos Cárdenas Fernández).
- 🟢 **Bandera del Perú vertical** (corregido logo Austria→Perú).
- 🟢 **Informe técnico del portal** (ingeniería/pipeline/arquitectura con diagramas) descargable.
- ⚪ OG dinámica por comisión (imagen de compartir por ficha).
- ⚪ Reponer video de presentación cuando llegue el nuevo (`data/meta.json` → `video`).

## Fase 5 — Auditoría de alineamiento (🟡 listo para empezar — Actividad 4 del TDR)
> La articulación POR COMISIÓN (VII y VIII) ya está en las fichas. Falta la **matriz transversal** del encargo pagado.
> 🟢 Metodología recibida (PPTX «ARTICULACIONES PP2050»): Acuerdo Nacional (4 dimensiones + políticas), PEDN, lista de ~80 Programas Presupuestales del MEF, y las categorías de clasificación.
> 🔵 Falta que el CIP formalice el contrato (en trámite) y/o pasar los anexos/listados completos.
- ⚪ Motor de *matching semántico*: objetivos de comisiones vs Acuerdo Nacional / PEDN 2050 / Programas Presupuestales.
- ⚪ Clasificación en 6 categorías: igual/similar · desagregado · agregado · causal con evidencia · causal sin evidencia · desarticulado.
- ⚪ Matriz navegable + tabulación de porcentajes + export Word/Excel.

## Pendientes menores (opcionales / mejoras)
- ⚪ Comparador de comisiones lado a lado.
- ⚪ Línea de tiempo 2030/2040/2050 por indicador · choropleth departamental.
- ⚪ OG dinámica por comisión.
- ⚪ Reponer video cuando llegue el nuevo.
- ⚪ (Seguridad) rotar la OpenRouter key (se compartió por chat).

## Operación
- 🟢 Deploy: `git push` (versiona + Pages) + `bash deploy/deploy.sh` (VPS).
- 🟢 Pipeline de actualización: documento → conversión → extracción IA → JSON → regenerar PDFs → deploy.

# Plan Perú 2050 — Dashboard de Comisiones

Dashboard interactivo de las **Comisiones Temáticas del Plan Perú 2050** (CNPP — Colegio de Ingenieros del Perú): visión 2050, brechas al 2026, metas e **indicadores cuantitativos** con **simulaciones** y consulta asistida por IA.

> Herramienta de consulta y proyección. Las cifras se extraen de las redacciones de cada comisión y están **sujetas a validación oficial**. No difunde datos personales de los integrantes de las comisiones.

## ✨ Qué hace

- **Directorio de las 64 comisiones temáticas** con buscador y filtros por eje estratégico.
- **Ficha por comisión** (las que ya tienen redacción): visión, diagnóstico/brecha 2026, pilares, **indicadores hoy → meta 2050**, metas, acciones y recomendación de política.
- **Simulador de metas**: mueve los indicadores cuantitativos y proyecta el *“índice de avance nacional”* hacia 2050.
- **Consulta IA** (opcional): pregunta en lenguaje natural sobre el plan. Sin IA configurada, usa búsqueda local sobre los datos.

## 🗂️ Estructura

```
index.html          # UI (single page, sin build)
js/app.js           # Motor: carga datos, render, simulador, IA
config.js           # Config opcional del asistente IA (OpenRouter / proxy)
data/meta.json      # Directorio de las 64 comisiones (sin PII)
data/comisiones.json# Detalle estructurado de las comisiones redactadas
fuentes/            # Documentos originales (NO versionados — contienen contacto/PII)
```

## 📊 Datos

`data/comisiones.json` se generó extrayendo, de cada redacción de comisión, los campos: `vision`, `diagnostico`, `pilares`, `indicadores` (con `actual`/`meta`/`unidad`/`fuente`/`anioMeta`), `metas`, `acciones`, `recomendacion` y `eje`. Solo se incluyen cifras **explícitas** en los documentos fuente (sin inventar valores).

Comisiones con datos en esta versión: **Aeroespacial, Marítimo-Fluvial-Lacustre, Capital del Conocimiento, Perú en la Era Digital, Ciencia y Tecnología, Medio Ambiente, Salud (Gemelos Digitales) y Telecomunicaciones.**

## 🚀 Uso local

Sirve la carpeta con cualquier servidor estático:

```bash
python3 -m http.server 8080
# abrir http://localhost:8080
```

## 🌐 Despliegue (GitHub Pages)

1. Settings → Pages → *Deploy from a branch* → `main` / root.
2. La URL pública quedará en `https://<usuario>.github.io/plan-peru-2050/`.

## 🤖 IA opcional

Edita `config.js`: pon una API key de OpenRouter (demo) o la URL de un proxy (recomendado, para no exponer la key). Si lo dejas vacío, el asistente responde con búsqueda local sobre los datos.

---

Fuente: redacciones de las Comisiones Temáticas del Plan Perú 2050 (CNPP — CIP). Construido como herramienta de consulta ciudadana e institucional.

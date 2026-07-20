#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Seguimiento de indicadores del Plan Perú 2050 — snapshot mensual.

Idea: mes a mes registrar el valor "actual" de cada indicador rastreable (los que
tienen actual + meta) para trackear qué tan cerca/lejos estamos de la meta 2050.
Al agregar las comisiones nuevos indicadores, se suman solos (se leen del data/).

- Refresca las DEFINICIONES (meta, unidad, comisión) desde comisiones*.json.
- Agrega UN snapshot por mes (YYYY-MM). Idempotente: si ya hay snapshot del mes, lo actualiza.
- La HISTORIA se acumula en data/seguimiento.json (no se borra en deploys; ver rsync exclude).

Uso:  python3 scripts/seguimiento_snapshot.py [DATA_DIR]
Cron (VPS, mensual):  0 6 1 * * python3 /opt/pp2050/repo/scripts/seguimiento_snapshot.py /var/www/plan-peru-2050/data
"""
import os, sys, json, re, unicodedata
from datetime import datetime, timezone

DATA = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), "..", "data")
OUT = os.path.join(DATA, "seguimiento.json")


def slug(s):
    s = unicodedata.normalize("NFD", str(s or "")).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")[:48]


def load(fn):
    try:
        return json.load(open(os.path.join(DATA, fn), encoding="utf-8"))
    except Exception:
        return []


def main():
    coms = load("comisiones.json") + load("comisiones_revision.json")
    defs, valores = [], {}
    seen = set()
    for c in coms:
        for i in c.get("indicadores", []):
            if i.get("actual") is None or i.get("meta") is None:
                continue
            key = c.get("id", "") + "__" + slug(i.get("nombre"))
            if key in seen:
                continue
            seen.add(key)
            defs.append({
                "key": key, "comision_id": c.get("id"), "comision": c.get("nombre"),
                "nombre": i.get("nombre"), "meta": i.get("meta"), "anioMeta": i.get("anioMeta"),
                "unidad": i.get("unidad", ""), "fuente": i.get("fuente", ""),
            })
            valores[key] = i.get("actual")

    prev = {}
    if os.path.exists(OUT):
        try:
            prev = json.load(open(OUT, encoding="utf-8"))
        except Exception:
            prev = {}
    snaps = prev.get("snapshots", [])
    mes = datetime.now(timezone.utc).strftime("%Y-%m")
    snap = {"fecha": mes, "valores": valores}
    snaps = [s for s in snaps if s.get("fecha") != mes] + [snap]
    snaps.sort(key=lambda s: s["fecha"])

    out = {
        "fuente": "Indicadores del Plan Perú 2050 (comisiones). Snapshot mensual de avance hacia la meta 2050.",
        "actualizado": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "indicadores": defs,
        "snapshots": snaps,
    }
    json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"✓ {OUT} — {len(defs)} indicadores rastreables · {len(snaps)} snapshots (último: {mes})")


if __name__ == "__main__":
    main()

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
import os, sys, json, re, unicodedata, urllib.request
from datetime import datetime, timezone

BCRP = "https://estadisticas.bcrp.gob.pe/estadisticas/series/api"


def _num(v):
    try:
        return float(str(v).replace(",", ""))
    except Exception:
        return None


def fetch_bcrp(code, modo="anual", factor=1):
    """Jala el valor vigente de una serie de BCRPData. Ver reference_bcrp_data_api.
    modo: 'anual' (último anual) · 'ultimo' (último valor no vacío) · 'mensual_suma' (suma 12 meses del último año completo).
    Devuelve {valor, periodo} o None si falla (fallback al valor manual)."""
    try:
        rng = "/2015/2026" if modo == "anual" else "/2018-1/2026-12"
        j = json.loads(urllib.request.urlopen(BCRP + "/" + code + "/json" + rng, timeout=25).read())
        vals = [(p.get("name", ""), _num(p["values"][0])) for p in j.get("periods", []) if p.get("values")]
        vals = [(n, v) for n, v in vals if v is not None]
        if not vals:
            return None
        if modo == "mensual_suma":
            byyear = {}
            for n, v in vals:
                m = re.search(r"(20\d{2})", n)
                if m:
                    byyear.setdefault(m.group(1), []).append(v)
            comp = [(y, vs) for y, vs in byyear.items() if len(vs) >= 12]
            if not comp:
                return None  # sin año completo: NO usar suma parcial (ensuciaría el % de avance)
            y, vs = max(comp)
            return {"valor": round(sum(vs) * factor, 1), "periodo": y}
        n, v = vals[-1]
        m = re.search(r"(20\d{2})", n)
        return {"valor": round(v * factor, 2), "periodo": (m.group(1) if m else n)}
    except Exception as e:
        sys.stderr.write("BCRP %s: %s\n" % (code, e))
        return None

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
    # Catálogo traductor: si un indicador se renombró (key = comision_id+slug(nombre) cambió),
    # migra su historial de la key vieja a la nueva. Ver data/indicador_alias.json.
    alias = {}
    ap = os.path.join(DATA, "indicador_alias.json")
    if os.path.exists(ap):
        try:
            alias = json.load(open(ap, encoding="utf-8")).get("alias", {})
        except Exception:
            alias = {}

    def canon(k):
        seen = set()
        while k in alias and k not in seen:
            seen.add(k)
            k = alias[k]
        return k

    for s in prev.get("snapshots", []):  # migrar historial a las keys canónicas
        s["valores"] = {canon(k): v for k, v in s.get("valores", {}).items()}
    prev_auto = {canon(k): v for k, v in prev.get("auto", {}).items()}
    prev_last = {canon(k): v for k, v in (prev.get("snapshots") or [{}])[-1].get("valores", {}).items()}

    # Detectar posibles renombres SIN alias (keys en el historial que ya no existen) → avisar
    curkeys = set(valores)
    orphans = set()
    for s in prev.get("snapshots", []):
        orphans |= (set(s["valores"]) - curkeys)
    if orphans:
        sys.stderr.write("⚠ keys en el historial que ya no están en los indicadores actuales "
                         "(¿renombradas? agrégalas a indicador_alias.json vieja→nueva): "
                         + ", ".join(sorted(orphans)) + "\n")

    # Auto-jalado de valores REALES (BCRPData) para los indicadores mapeados y verificados.
    auto = {}
    fuentes = os.path.join(DATA, "indicador_fuentes.json")
    if os.path.exists(fuentes) and not os.environ.get("PP2050_NO_FETCH"):
        try:
            mapeos = json.load(open(fuentes, encoding="utf-8")).get("mapeos", {})
        except Exception:
            mapeos = {}
        cache = {}
        for key, m in mapeos.items():
            if key not in valores:
                continue
            ck = (m.get("codigo"), m.get("modo", "anual"), m.get("factor", 1))
            if ck not in cache:
                cache[ck] = fetch_bcrp(*ck)
            r = cache[ck]
            if r and r.get("valor") is not None:
                valores[key] = r["valor"]
                auto[key] = {"fuente": m.get("fuente", "BCRP"), "codigo": m.get("codigo"),
                             "periodo": r["periodo"], "confianza": m.get("confianza", "media"),
                             "caveat": m.get("caveat")}
            elif key in prev_auto and key in prev_last:
                # BCRP falló/no disponible: conservar el último valor oficial ya capturado (no degradar a manual)
                valores[key] = prev_last[key]
                auto[key] = dict(prev_auto[key])
        if auto:
            print("  auto (BCRP): " + ", ".join("%s=%s(%s)" % (k.split("__")[0], valores[k], auto[k]["periodo"]) for k in auto))

    snaps = prev.get("snapshots", [])
    mes = datetime.now(timezone.utc).strftime("%Y-%m")
    snap = {"fecha": mes, "valores": valores}
    snaps = [s for s in snaps if s.get("fecha") != mes] + [snap]
    snaps.sort(key=lambda s: s["fecha"])

    out = {
        "fuente": "Indicadores del Plan Perú 2050 (comisiones). Snapshot mensual de avance hacia la meta 2050.",
        "actualizado": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "indicadores": defs,
        "auto": auto,   # indicadores con valor jalado de fuente oficial (BCRP) este mes
        "snapshots": snaps,
    }
    json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"✓ {OUT} — {len(defs)} indicadores rastreables · {len(snaps)} snapshots (último: {mes})")


if __name__ == "__main__":
    main()

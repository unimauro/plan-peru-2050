#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""MEF Consulta Amigable — gasto por Departamento × Genérica, clasificado en
CORRIENTE vs INVERSIÓN (genérica 6 'Adquisición de Activos No Financieros' = inversión).
Corre LOCAL (IP residencial; el VPS es bloqueado por el WAF). Ver reference_mef_api_gasto.

Uso:  python3 scripts/scraper_gasto_tipo.py [AÑO] [--test]
Salida: data/gasto_tipo_departamento.json
"""
import requests, re, json, os, sys, time
from bs4 import BeautifulSoup

BASE = "https://apps5.mineco.gob.pe/transparencia/Navegador/"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"
OUT = os.path.join(os.path.dirname(__file__), "..", "data", "gasto_tipo_departamento.json")
YEAR = int([a for a in sys.argv[1:] if a.isdigit()][0]) if any(a.isdigit() for a in sys.argv[1:]) else 2026
TEST = "--test" in sys.argv


def new_session():
    s = requests.Session(); s.headers.update({"User-Agent": UA})
    s.get(BASE + "default.aspx", timeout=40)
    return s


def num(s):
    s = (s or "").replace(",", "").strip()
    try:
        return round(float(s), 2)
    except ValueError:
        return 0.0


def fields(soup, click_name=None, click_val=None):
    d = {}
    for inp in soup.select("input"):
        n = inp.get("name"); t = (inp.get("type") or "text").lower()
        if not n or t in ("submit", "button", "image", "reset"):
            continue
        if t in ("radio", "checkbox"):
            if inp.has_attr("checked"):
                d[n] = inp.get("value", "on")
        else:
            d[n] = inp.get("value", "")
    for sel in soup.select("select"):
        n = sel.get("name")
        if n:
            o = sel.select_one("option[selected]") or sel.select_one("option")
            d[n] = o.get("value", "") if o else ""
    if click_name:
        d[click_name] = click_val
    return d


def parse_grp_rows(soup, code_len=2):
    """Filas 'NN: NOMBRE' capturando el value del radio grp1 de esa fila + montos."""
    out = []
    pat = re.compile(r"^(\d{%d}):\s*(.+)$" % code_len) if code_len else re.compile(r"^([\d\-]+):\s*(.+)$")
    for tr in soup.find_all("tr"):
        radio = tr.select_one("input[name=grp1]")
        tds = tr.find_all("td")
        txt = [t.get_text(" ", strip=True) for t in tds]
        idx = next((i for i, c in enumerate(txt) if pat.match(c)), None)
        if idx is None or not radio:
            continue
        m = pat.match(txt[idx])
        nums = [num(c) for c in txt[idx + 1:] if re.match(r"^[\d,]+(\.\d+)?$", c.replace(",", ""))]
        if len(nums) < 6:
            continue
        out.append({"radio": radio.get("value"), "code": m.group(1), "nombre": m.group(2).strip(),
                    "pim": nums[1], "devengado": nums[5]})
    return out


def get_departamentos(s):
    s.get(f"{BASE}default.aspx?y={YEAR}&ap=ActProy", timeout=40)
    html = s.get(f"{BASE}Navegar.aspx?y={YEAR}&ap=ActProy", timeout=40).text
    soup = BeautifulSoup(html, "lxml")
    d = fields(soup, "ctl00$CPH1$BtnDepartamentoMeta", "Departamento")
    g = soup.select_one("input[name=grp1]")
    if g:
        d["grp1"] = g.get("value")
    action = soup.find("form").get("action")
    resp = s.post(BASE + action, data=d,
                  headers={"Referer": f"{BASE}Navegar.aspx?y={YEAR}&ap=ActProy"}, timeout=50)
    return BeautifulSoup(resp.text, "lxml"), resp.url


def drill_generica(s, dep_soup, referer, dep_radio):
    """Selecciona el depto (grp1=dep_radio) y clic Genérica → filas por genérica."""
    d = fields(dep_soup, "ctl00$CPH1$BtnGenerica", "Genérica")
    d["grp1"] = dep_radio
    action = dep_soup.find("form").get("action")
    resp = s.post(BASE + action, data=d, headers={"Referer": referer}, timeout=50)
    return parse_grp_rows(BeautifulSoup(resp.text, "lxml"), code_len=0)


def main():
    s = new_session()
    dep_soup, dep_url = get_departamentos(s)
    deps = parse_grp_rows(dep_soup, code_len=2)
    print(f"departamentos: {len(deps)}", flush=True)
    if TEST:
        deps = deps[:2]
    result = {}
    for dp in deps:
        name = dp["nombre"]
        for attempt in range(3):
            try:
                gens = drill_generica(s, dep_soup, dep_url, dp["radio"])
                # Tipo de gasto por 1er dígito del código: 5=Corriente, 6=Capital/Inversión, 7=Deuda
                acc = {"corriente_pim": 0.0, "corriente_dev": 0.0, "inversion_pim": 0.0,
                       "inversion_dev": 0.0, "deuda_pim": 0.0, "deuda_dev": 0.0}
                for g in gens:
                    t = g["code"].split("-")[0]
                    k = "corriente" if t == "5" else "inversion" if t == "6" else "deuda" if t == "7" else None
                    if k:
                        acc[k + "_pim"] += g["pim"]; acc[k + "_dev"] += g["devengado"]
                result[name] = {kk: round(vv) for kk, vv in acc.items()}
                print(f"  {name}: corriente S/{acc['corriente_pim']/1e6:.0f}M · inversión S/{acc['inversion_pim']/1e6:.0f}M · deuda S/{acc['deuda_pim']/1e6:.0f}M ({len(gens)} filas)", flush=True)
                break
            except Exception as e:
                print(f"  {name}: error {repr(e)[:60]} (reintento {attempt})", flush=True)
                time.sleep(6); s = new_session(); dep_soup, dep_url = get_departamentos(s)
        time.sleep(2)
    if not TEST:
        out = {"fuente": f"MEF Consulta Amigable {YEAR} — gasto por departamento (destino META) clasificado en corriente vs inversión (genérica 6 = Adquisición de Activos No Financieros).",
               "anio": YEAR, "departamentos": result}
        json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print(f"✓ {OUT} — {len(result)} departamentos", flush=True)
    else:
        print("TEST OK — no se escribió archivo")


if __name__ == "__main__":
    main()

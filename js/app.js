/* ============================================================
   Plan Perú 2050 — Dashboard de Comisiones
   Carga meta.json (directorio) + comisiones.json (detalle) y
   renderiza KPIs, filtros, fichas, detalle, simulador y consulta IA.
   ============================================================ */
"use strict";

const S = { meta: null, detail: {}, list: [], filterEje: "todas", q: "" };

const $ = (s, r = document) => r.querySelector(s);
const el = (t, c, h) => { const n = document.createElement(t); if (c) n.className = c; if (h != null) n.innerHTML = h; return n; };
const num = (n) => (n == null ? "—" : new Intl.NumberFormat("es-PE", { maximumFractionDigits: 2 }).format(n));
const clamp = (n, a = 0, b = 100) => Math.max(a, Math.min(b, n));
const esc = (s) => String(s ?? "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));

async function boot() {
  try {
    const [meta, det] = await Promise.all([
      fetch("data/meta.json").then((r) => r.json()),
      fetch("data/comisiones.json").then((r) => (r.ok ? r.json() : [])).catch(() => []),
    ]);
    S.meta = meta;
    (Array.isArray(det) ? det : det.comisiones || []).forEach((d) => (S.detail[d.id] = d));
    // Merge directory with detail
    S.list = meta.comisiones.map((c) => ({ ...c, ...(S.detail[c.id] || {}) }));
    $("#pill-updated").textContent = "Actualizado " + (meta.actualizado || "");
    renderKPIs();
    renderChips();
    renderGrid();
    buildSimulator();
    renderOverview();
    renderMap();
    wireAI();
    wireSearch();
    openFromHash();
  } catch (e) {
    $("#grid").innerHTML = '<div class="skeleton">No se pudieron cargar los datos.</div>';
    console.error(e);
  }
}

function detailed() { return S.list.filter((c) => S.detail[c.id]); }
function allIndicators() {
  const out = [];
  detailed().forEach((c) => (c.indicadores || []).forEach((i) => {
    if (i.actual != null && i.meta != null && i.actual !== i.meta) out.push({ ...i, com: c.nombre, comId: c.id });
  }));
  return out;
}

function renderKPIs() {
  const inds = allIndicators();
  const ejes = new Set(detailed().map((c) => c.eje).filter(Boolean));
  const kpis = [
    { n: S.meta.totalComisiones, l: "Comisiones temáticas", a: false },
    { n: detailed().length, l: "Con redacción y datos", a: true },
    { n: inds.length, l: "Indicadores cuantificados", a: false },
    { n: ejes.size || "—", l: "Ejes estratégicos", a: false },
  ];
  $("#kpis").innerHTML = "";
  kpis.forEach((k) => $("#kpis").append(el("div", "kpi" + (k.a ? " accent" : ""), `<div class="n">${num(k.n)}</div><div class="l">${k.l}</div>`)));
}

function renderChips() {
  const ejes = [...new Set(detailed().map((c) => c.eje).filter(Boolean))].sort();
  const box = $("#chips"); box.innerHTML = "";
  const mk = (id, label) => {
    const c = el("button", "chip" + (S.filterEje === id ? " on" : ""), esc(label));
    c.onclick = () => { S.filterEje = id; renderChips(); renderGrid(); };
    return c;
  };
  box.append(mk("todas", "Todas"));
  box.append(mk("redactadas", "✓ Con datos"));
  ejes.forEach((e) => box.append(mk(e, e)));
}

function matchFilter(c) {
  if (S.q) {
    const hay = (c.nombre + " " + (c.resumen || "") + " " + (c.eje || "")).toLowerCase();
    if (!hay.includes(S.q.toLowerCase())) return false;
  }
  if (S.filterEje === "todas") return true;
  if (S.filterEje === "redactadas") return !!S.detail[c.id];
  return c.eje === S.filterEje;
}

function renderGrid() {
  const g = $("#grid"); g.innerHTML = "";
  const items = S.list.filter(matchFilter);
  if (!items.length) { g.innerHTML = '<div class="skeleton">Sin resultados.</div>'; return; }
  // detailed first
  items.sort((a, b) => (S.detail[b.id] ? 1 : 0) - (S.detail[a.id] ? 1 : 0));
  items.forEach((c) => {
    const has = !!S.detail[c.id];
    const card = el("div", "card" + (has ? "" : " lock"));
    const nInd = (c.indicadores || []).length;
    card.innerHTML = `
      <span class="badge ${has ? "ok" : "pend"}">${has ? "Con datos" : "En redacción"}</span>
      ${c.eje ? `<div class="eje">${esc(c.eje)}</div>` : `<div class="eje">Comisión temática</div>`}
      <h3>${esc(c.nombre)}</h3>
      <p>${esc(c.resumen || "Comisión del Plan Perú 2050. Redacción en proceso.")}</p>
      ${has ? `<div class="mini"><span><b>${(c.pilares || []).length}</b> pilares</span><span><b>${nInd}</b> indicadores</span><span><b>${(c.metas || []).length}</b> metas</span></div>` : ""}`;
    if (has) card.onclick = () => openDetail(c.id);
    g.append(card);
  });
}

function indicatorRow(i) {
  let pct = 0, label = "";
  if (i.actual != null && i.meta != null) {
    if (i.meta >= i.actual) { pct = i.meta ? clamp((i.actual / i.meta) * 100) : 0; label = `avance ${pct.toFixed(0)}%`; }
    else { pct = i.actual ? clamp((i.meta / i.actual) * 100) : 0; label = "meta de reducción"; }
  }
  return `<div class="ind">
    <div class="h"><b>${esc(i.nombre)}</b>
      <span class="vals">${i.actual != null ? `<span class="a">${num(i.actual)}${esc(i.unidad || "")}</span> → ` : ""}${i.meta != null ? `<span class="m">${num(i.meta)}${esc(i.unidad || "")}</span>` : ""}</span></div>
    ${i.actual != null && i.meta != null ? `<div class="bar"><i style="width:${pct}%"></i></div><div class="src">${esc(label)}${i.anioMeta ? " · meta " + i.anioMeta : ""}${i.fuente ? " · " + esc(i.fuente) : ""}</div>` : (i.fuente ? `<div class="src">${esc(i.fuente)}</div>` : "")}
  </div>`;
}

function openDetail(id) {
  const c = S.list.find((x) => x.id === id); if (!c) return;
  const s = $("#sheet");
  s.innerHTML = `
    <button class="close" onclick="closeDetail()">×</button>
    ${c.eje ? `<div class="eje" style="color:var(--mut2);font-size:.72rem;text-transform:uppercase;letter-spacing:.06em;font-weight:600">${esc(c.eje)}</div>` : ""}
    <h2 class="serif">${esc(c.nombre)}</h2>
    ${c.resumen ? `<p style="color:var(--mut);font-size:1.02rem;margin:6px 0 0">${esc(c.resumen)}</p>` : ""}
    ${c.vision ? `<div class="block"><h4>Visión 2050</h4><p>${esc(c.vision)}</p></div>` : ""}
    ${(c.diagnostico || []).length ? `<div class="block"><h4>Diagnóstico — brecha 2026</h4><ul class="ul">${c.diagnostico.map((d) => `<li>${esc(d)}</li>`).join("")}</ul></div>` : ""}
    ${(c.indicadores || []).length ? `<div class="block"><h4>Indicadores: hoy → meta 2050</h4><div class="detchart"><canvas id="detCanvas"></canvas></div>${c.indicadores.map(indicatorRow).join("")}</div>` : ""}
    ${(c.pilares || []).length ? `<div class="block"><h4>Pilares de la estrategia</h4>${c.pilares.map((p) => `<div class="pilar"><b>${esc(p.nombre)}</b><span>${esc(p.descripcion)}</span></div>`).join("")}</div>` : ""}
    ${(c.metas || []).length ? `<div class="block"><h4>Metas 2050</h4><ul class="ul">${c.metas.map((m) => `<li>${esc(m)}</li>`).join("")}</ul></div>` : ""}
    ${(c.acciones || []).length ? `<div class="block"><h4>Acciones e iniciativas</h4><ul class="ul">${c.acciones.map((a) => `<li>${esc(a)}</li>`).join("")}</ul></div>` : ""}
    ${c.recomendacion ? `<div class="block"><h4>Recomendación de política</h4><div class="reco">${esc(c.recomendacion)}</div></div>` : ""}`;
  $("#modal").classList.add("open");
  document.body.style.overflow = "hidden";
  if (location.hash !== "#" + id) history.replaceState(null, "", "#" + id);
  setTimeout(() => detailChart(c), 30);
}
function closeDetail() {
  $("#modal").classList.remove("open"); document.body.style.overflow = "";
  if (location.hash) history.replaceState(null, "", location.pathname + location.search);
}
$("#modal").addEventListener("click", (e) => { if (e.target.id === "modal") closeDetail(); });
document.addEventListener("keydown", (e) => { if (e.key === "Escape") closeDetail(); });
window.closeDetail = closeDetail;
function openFromHash() {
  const id = decodeURIComponent((location.hash || "").replace(/^#/, ""));
  if (id && S.detail[id]) setTimeout(() => openDetail(id), 200);
}
window.addEventListener("hashchange", openFromHash);

/* ---------- Simulador ---------- */
function buildSimulator() {
  const inds = allIndicators().slice(0, 8);
  const box = $("#sim");
  if (!inds.length) { box.innerHTML = '<div class="skeleton">Aún no hay indicadores cuantitativos cargados.</div>'; return; }
  box.innerHTML = `<div class="gaugewrap" style="margin-bottom:8px"><div><div style="font-size:.8rem;color:var(--mut)">Índice de avance nacional simulado</div><div class="big serif" id="simIndex" style="font-size:2.2rem;color:var(--gold)">0%</div></div><div style="flex:1;min-width:200px;color:var(--mut);font-size:.85rem">Mueve los controles para proyectar cuánto avanzaría cada indicador hacia su meta 2050. El índice promedia el avance de los indicadores.</div></div>`;
  inds.forEach((i, k) => {
    const lo = Math.min(i.actual, i.meta), hi = Math.max(i.actual, i.meta);
    const row = el("div", "sim-row");
    row.innerHTML = `
      <div><div style="font-weight:600">${esc(i.nombre)}</div><div class="sim-meta">${esc(i.com)} · hoy ${num(i.actual)}${esc(i.unidad || "")} → meta ${num(i.meta)}${esc(i.unidad || "")}</div>
        <input type="range" min="${lo}" max="${hi}" step="${(hi - lo) / 100 || 1}" value="${i.actual}" data-k="${k}" />
      </div>
      <div class="sim-out"><div class="big" id="so${k}">${num(i.actual)}<span style="font-size:.9rem;color:var(--mut)">${esc(i.unidad || "")}</span></div><div class="sim-meta" id="sp${k}">0% de avance</div></div>`;
    box.append(row);
    const range = $("input", row);
    range.oninput = () => updateSim(inds);
  });
  updateSim(inds);
}
function updateSim(inds) {
  let sum = 0;
  inds.forEach((i, k) => {
    const range = document.querySelector(`input[data-k="${k}"]`); if (!range) return;
    const v = parseFloat(range.value);
    const lo = Math.min(i.actual, i.meta), hi = Math.max(i.actual, i.meta);
    const adv = hi === lo ? 100 : clamp(((v - i.actual) / (i.meta - i.actual)) * 100);
    sum += adv;
    const so = $("#so" + k), sp = $("#sp" + k);
    if (so) so.innerHTML = `${num(v)}<span style="font-size:.9rem;color:var(--mut)">${esc(i.unidad || "")}</span>`;
    if (sp) sp.textContent = `${adv.toFixed(0)}% de avance`;
  });
  const idx = $("#simIndex"); if (idx) idx.textContent = (sum / inds.length).toFixed(0) + "%";
}

/* ---------- Avance helpers ---------- */
function indAvance(i) {
  if (i.actual == null || i.meta == null) return null;
  if (i.meta === i.actual) return 100;
  if (i.meta >= i.actual) return clamp((i.actual / i.meta) * 100);
  return clamp((i.meta / i.actual) * 100); // meta de reducción
}
function comAvance(c) {
  const v = (c.indicadores || []).map(indAvance).filter((x) => x != null);
  return v.length ? v.reduce((a, b) => a + b, 0) / v.length : null;
}
const CHARTS = {};
const EJE_COLORS = { "Economía del Conocimiento": "#e0a52e", "Sostenibilidad y Ambiente": "#16a34a", "Soberanía y Defensa": "#d91023", "Infraestructura y Conectividad": "#3b82f6", "Bienestar y Salud": "#a855f7", "Competitividad": "#2ed47a" };
const ejeColor = (e) => EJE_COLORS[e] || "#8a98b8";
const chartFont = () => { try { Chart.defaults.color = "#8a98b8"; Chart.defaults.font.family = "Inter, sans-serif"; } catch (e) {} };

/* ---------- Panorama (Chart.js) ---------- */
function renderOverview() {
  if (typeof Chart === "undefined") return;
  chartFont();
  const det = detailed().map((c) => ({ c, av: comAvance(c) })).filter((x) => x.av != null).sort((a, b) => b.av - a.av);
  // Bar: avance por comisión
  const a = document.getElementById("chartAvance");
  if (a && det.length) {
    CHARTS.avance && CHARTS.avance.destroy();
    CHARTS.avance = new Chart(a, {
      type: "bar",
      data: { labels: det.map((x) => x.c.nombre.length > 22 ? x.c.nombre.slice(0, 20) + "…" : x.c.nombre),
        datasets: [{ data: det.map((x) => +x.av.toFixed(1)), backgroundColor: det.map((x) => ejeColor(x.c.eje)), borderRadius: 6 }] },
      options: { indexAxis: "y", plugins: { legend: { display: false }, tooltip: { callbacks: { label: (i) => ` ${i.raw}% de avance hacia 2050` } } },
        scales: { x: { max: 100, grid: { color: "#1e2840" }, ticks: { callback: (v) => v + "%" } }, y: { grid: { display: false } } },
        onClick: (e, els) => { if (els[0]) openDetail(det[els[0].index].c.id); } },
    });
  }
  // Doughnut: comisiones por eje
  const e = document.getElementById("chartEjes");
  if (e) {
    const byEje = {};
    detailed().forEach((c) => { if (c.eje) byEje[c.eje] = (byEje[c.eje] || 0) + 1; });
    const labels = Object.keys(byEje);
    CHARTS.ejes && CHARTS.ejes.destroy();
    CHARTS.ejes = new Chart(e, {
      type: "doughnut",
      data: { labels, datasets: [{ data: labels.map((l) => byEje[l]), backgroundColor: labels.map(ejeColor), borderColor: "#0a0e1a", borderWidth: 2 }] },
      options: { cutout: "62%", plugins: { legend: { position: "bottom", labels: { boxWidth: 12, padding: 10, font: { size: 11 } } } } },
    });
  }
}

/* ---------- Mapa estratégico (Leaflet) ---------- */
async function renderMap() {
  const elMap = document.getElementById("map");
  if (!elMap || typeof L === "undefined") return;
  let data;
  try { data = await fetch("data/puntos.json").then((r) => r.json()); } catch (e) { elMap.innerHTML = '<div class="skeleton">No se pudo cargar el mapa.</div>'; return; }
  const map = L.map("map", { scrollWheelZoom: false, attributionControl: true }).setView([-9.2, -75], 5);
  L.tileLayer("https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png", {
    attribution: "© OpenStreetMap, © CARTO", maxZoom: 12, subdomains: "abcd",
  }).addTo(map);
  const tipos = data.tipos || {};
  (data.puntos || []).forEach((p) => {
    const color = (tipos[p.tipo] || {}).color || "#fff";
    const m = L.circleMarker([p.lat, p.lng], { radius: 6, color, fillColor: color, fillOpacity: 0.85, weight: 1.5 }).addTo(map);
    const com = S.list.find((c) => c.id === p.comision);
    m.bindPopup(`<b>${esc(p.nombre)}</b><br>${esc((tipos[p.tipo] || {}).label || p.tipo)}${p.nota ? "<br><span style='color:#8a98b8'>" + esc(p.nota) + "</span>" : ""}${com && S.detail[com.id] ? `<br><a href="#" onclick="closeMapTo('${com.id}');return false" style="color:#e0a52e">Ver comisión →</a>` : ""}`);
  });
  // Legend
  const leg = document.getElementById("maplegend");
  if (leg) leg.innerHTML = Object.values(tipos).map((t) => `<span><i style="background:${t.color}"></i>${esc(t.label)}</span>`).join("") + `<span style="color:var(--mut2)">${esc(data.nota || "")}</span>`;
}
window.closeMapTo = (id) => openDetail(id);

/* ---------- Detail chart ---------- */
function detailChart(c) {
  const cv = document.getElementById("detCanvas");
  if (!cv || typeof Chart === "undefined") return;
  const inds = (c.indicadores || []).map((i) => ({ i, av: indAvance(i) })).filter((x) => x.av != null);
  if (!inds.length) { cv.parentElement.style.display = "none"; return; }
  chartFont();
  CHARTS.detail && CHARTS.detail.destroy();
  CHARTS.detail = new Chart(cv, {
    type: "bar",
    data: { labels: inds.map((x) => x.i.nombre.length > 26 ? x.i.nombre.slice(0, 24) + "…" : x.i.nombre),
      datasets: [{ label: "% avance", data: inds.map((x) => +x.av.toFixed(1)), backgroundColor: "#e0a52e", borderRadius: 5 }] },
    options: { indexAxis: "y", plugins: { legend: { display: false }, tooltip: { callbacks: { label: (t) => ` ${t.raw}% de avance` } } },
      scales: { x: { max: 100, grid: { color: "#1e2840" }, ticks: { callback: (v) => v + "%" } }, y: { grid: { display: false }, ticks: { font: { size: 10 } } } } },
  });
}

/* ---------- Búsqueda ---------- */
function wireSearch() {
  let t;
  $("#q").addEventListener("input", (e) => { clearTimeout(t); t = setTimeout(() => { S.q = e.target.value.trim(); renderGrid(); }, 120); });
}

/* ---------- Consulta IA ---------- */
function wireAI() {
  const panel = $("#aiPanel"), log = $("#aiLog");
  $("#aiBtn").onclick = () => { panel.classList.toggle("open"); if (panel.classList.contains("open") && !log.children.length) addMsg("a", "Hola 👋 Pregúntame sobre las comisiones del Plan Perú 2050: visión, brechas, metas o indicadores."); };
  $("#aiClose").onclick = () => panel.classList.remove("open");
  const send = () => {
    const inp = $("#aiInput"), q = inp.value.trim(); if (!q) return;
    addMsg("u", q); inp.value = "";
    answer(q);
  };
  $("#aiSend").onclick = send;
  $("#aiInput").addEventListener("keydown", (e) => { if (e.key === "Enter") send(); });
}
function addMsg(role, html) { const m = el("div", "msg " + role, esc(html)); $("#aiLog").append(m); $("#aiLog").scrollTop = 1e9; return m; }

async function answer(q) {
  const cfg = window.PP2050_IA || {};
  const ctx = detailed().map((c) => `### ${c.nombre} (${c.eje || ""})\nVisión: ${c.vision || ""}\nBrechas: ${(c.diagnostico || []).join("; ")}\nMetas: ${(c.metas || []).join("; ")}\nIndicadores: ${(c.indicadores || []).map((i) => `${i.nombre} ${i.actual}→${i.meta}${i.unidad || ""}`).join("; ")}\nRecomendación: ${c.recomendacion || ""}`).join("\n\n");
  if (cfg.apiKey || cfg.proxy) {
    const wait = addMsg("a", "Pensando…");
    try {
      const url = cfg.proxy || cfg.endpoint;
      const headers = { "Content-Type": "application/json" };
      if (!cfg.proxy && cfg.apiKey) headers.Authorization = "Bearer " + cfg.apiKey;
      const body = { model: cfg.model, messages: [
        { role: "system", content: "Eres analista del Plan Perú 2050. Responde en español, conciso y fiel a estos datos de comisiones. Si no está en los datos, dilo.\n\n" + ctx },
        { role: "user", content: q },
      ] };
      const r = await fetch(url, { method: "POST", headers, body: JSON.stringify(body) });
      const j = await r.json();
      wait.textContent = j.choices?.[0]?.message?.content || "No obtuve respuesta del modelo.";
    } catch (e) { wait.textContent = "Error al consultar el modelo. Revisa config.js."; }
    $("#aiLog").scrollTop = 1e9;
    return;
  }
  // Fallback local: búsqueda por términos
  const terms = q.toLowerCase().split(/\s+/).filter((w) => w.length > 3);
  const scored = detailed().map((c) => {
    const hay = JSON.stringify(c).toLowerCase();
    return { c, score: terms.reduce((a, w) => a + (hay.includes(w) ? 1 : 0), 0) };
  }).filter((x) => x.score > 0).sort((a, b) => b.score - a.score).slice(0, 3);
  if (!scored.length) { addMsg("a", "No encontré comisiones relacionadas. Prueba con: energía, salud, marítimo, conocimiento, digital, ambiente…"); return; }
  scored.forEach(({ c }) => {
    addMsg("a", `${c.nombre} — ${c.resumen || c.vision || ""} ${(c.metas || [])[0] ? "Meta: " + c.metas[0] : ""}`);
  });
  addMsg("a", "💡 Para respuestas más ricas con IA, configura una API key en config.js.");
}

boot();

/* ============================================================
   Plan Perú 2050 — Dashboard de Comisiones
   Carga meta.json (directorio) + comisiones.json (detalle) y
   renderiza KPIs, filtros, fichas, detalle, simulador y consulta IA.
   ============================================================ */
"use strict";

const S = { meta: null, detail: {}, list: [], filterEje: "todas", q: "", stage: "all", showRevision: true, view: "explorar", simInds: [], simChart: null, simProj: null, ritmo: "linear" };

// Dosificación por hito (feature stage)
const STAGES = {
  all: { secs: null, revision: true },
  validado: { secs: null, revision: false },
  h1: { secs: ["grid", "mapa", "sim", "panorama"], revision: true },
  h2: { secs: ["grid", "mapa", "sim", "panorama", "cien"], revision: true },
  h3: { secs: null, revision: true },
};
function applyVisibility() {
  const stage = STAGES[S.stage] || STAGES.all;
  // Solo secciones dentro de <main> (NO las pestañas del header, que también usan data-view)
  document.querySelectorAll("main [data-view], main [data-sec]").forEach((el) => {
    const secOk = !el.dataset.sec || !stage.secs || stage.secs.includes(el.dataset.sec);
    const viewOk = !el.dataset.view || el.dataset.view === S.view;
    el.style.display = secOk && viewOk ? "" : "none";
  });
}
function applyStage() {
  const cfg = window.PP2050_STAGE || {};
  let v = new URLSearchParams(location.search).get("v");
  if (!v || v === "null") v = cfg.default || "all";
  S.stage = v in STAGES ? v : "all";
  S.showRevision = (STAGES[S.stage] || STAGES.all).revision;
  applyVisibility();
  const pill = document.getElementById("pill-updated");
  if (pill && S.stage !== "all") pill.textContent = "Vista: " + (S.stage === "validado" ? "solo validadas" : S.stage.toUpperCase());
}
function setView(view) {
  S.view = view;
  document.querySelectorAll("#tabs .tab").forEach((t) => t.classList.toggle("on", t.dataset.view === view));
  applyVisibility();
  if (view === "simular") setTimeout(() => { try { S.simChart && S.simChart.resize(); S.simProj && S.simProj.resize(); } catch (e) {} }, 50);
  window.scrollTo({ top: 0, behavior: "smooth" });
}
function wireTabs() { document.querySelectorAll("#tabs .tab").forEach((t) => { t.onclick = () => setView(t.dataset.view); }); }
window.setView = setView;
window.scrollToSec = (name) => {
  const go = () => { const el = document.querySelector('section[data-sec="' + name + '"]'); if (el) el.scrollIntoView({ behavior: "smooth", block: "start" }); };
  if (S.view !== "explorar") { setView("explorar"); setTimeout(go, 90); } else go();
};
function wireToTop() {
  const btn = document.getElementById("totop"); if (!btn) return;
  btn.onclick = () => window.scrollTo({ top: 0, behavior: "smooth" });
  window.addEventListener("scroll", () => btn.classList.toggle("show", window.scrollY > 500), { passive: true });
}

const $ = (s, r = document) => r.querySelector(s);
const el = (t, c, h) => { const n = document.createElement(t); if (c) n.className = c; if (h != null) n.innerHTML = h; return n; };
const num = (n) => (n == null ? "—" : new Intl.NumberFormat("es-PE", { maximumFractionDigits: 2 }).format(n));
const clamp = (n, a = 0, b = 100) => Math.max(a, Math.min(b, n));
const esc = (s) => String(s ?? "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));

async function boot() {
  try {
    const [meta, det, rev] = await Promise.all([
      fetch("data/meta.json").then((r) => r.json()),
      fetch("data/comisiones.json").then((r) => (r.ok ? r.json() : [])).catch(() => []),
      fetch("data/comisiones_revision.json").then((r) => (r.ok ? r.json() : [])).catch(() => []),
    ]);
    S.meta = meta;
    (Array.isArray(det) ? det : det.comisiones || []).forEach((d) => (S.detail[d.id] = d));
    // Comisiones inferidas (a revisión) — no sobrescriben las validadas
    (Array.isArray(rev) ? rev : rev.comisiones || []).forEach((d) => { if (!S.detail[d.id]) S.detail[d.id] = { ...d, revision: true }; });
    // Merge directory with detail
    S.list = meta.comisiones.map((c) => ({ ...c, ...(S.detail[c.id] || {}) }));
    $("#pill-updated").textContent = "Actualizado " + (meta.actualizado || "");
    applyStage();
    renderVideo();
    renderKPIs();
    renderChips();
    renderGrid();
    buildSimulator();
    renderOverview();
    renderMap();
    render100();
    wireAI();
    wireSearch();
    wireTabs();
    wireToTop();
    openFromHash();
    const t0 = new URLSearchParams(location.search).get("tab");
    if (t0 === "simular" || t0 === "faq") setView(t0);
  } catch (e) {
    $("#grid").innerHTML = '<div class="skeleton">No se pudieron cargar los datos.</div>';
    console.error(e);
  }
}

function detailed() { return S.list.filter((c) => S.detail[c.id]); }
function validated() { return detailed().filter((c) => !S.detail[c.id].revision); }
function reviewed() { return detailed().filter((c) => S.detail[c.id].revision); }
function allIndicators() {
  // Solo indicadores de comisiones VALIDADAS (datos reales) para simulador/panorama.
  const out = [];
  validated().forEach((c) => (c.indicadores || []).forEach((i) => {
    if (i.actual != null && i.meta != null && i.actual !== i.meta) out.push({ ...i, com: c.nombre, comId: c.id });
  }));
  return out;
}

function ytId(url) {
  const m = String(url || "").match(/(?:v=|youtu\.be\/|embed\/)([A-Za-z0-9_-]{11})/);
  return m ? m[1] : null;
}
function renderVideo() {
  const box = document.getElementById("video"); if (!box) return;
  const id = ytId(S.meta && S.meta.video);
  if (!id) { box.innerHTML = ""; return; }
  box.innerHTML = `<div class="videocard"><div class="vt">▶ Presentación</div>
    <div class="videobox"><iframe src="https://www.youtube-nocookie.com/embed/${id}" title="Presentación Plan Perú 2050" loading="lazy" allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe></div></div>`;
}
function renderKPIs() {
  const inds = allIndicators();
  const ejes = new Set(detailed().map((c) => c.eje).filter(Boolean));
  const kpis = [
    { n: S.meta.totalComisiones, l: "Comisiones temáticas", a: false },
    { n: validated().length, l: "Validadas", a: true },
    ...(S.showRevision ? [{ n: reviewed().length, l: "En revisión", a: false }] : []),
    { n: inds.length, l: "Indicadores cuantificados", a: false },
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
  box.append(mk("validadas", "✓ Validado"));
  if (S.showRevision) box.append(mk("revision", "⚠ En revisión"));
  ejes.forEach((e) => box.append(mk(e, e)));
}

function matchFilter(c) {
  if (S.q) {
    const hay = (c.nombre + " " + (c.resumen || "") + " " + (c.eje || "")).toLowerCase();
    if (!hay.includes(S.q.toLowerCase())) return false;
  }
  const d = S.detail[c.id];
  if (!S.showRevision && d && d.revision) return false;
  if (S.filterEje === "todas") return true;
  if (S.filterEje === "validadas") return !!d && !d.revision;
  if (S.filterEje === "revision") return !!d && !!d.revision;
  return c.eje === S.filterEje;
}

function renderGrid() {
  const g = $("#grid"); g.innerHTML = "";
  const items = S.list.filter(matchFilter);
  if (!items.length) { g.innerHTML = '<div class="skeleton">Sin resultados.</div>'; return; }
  // detailed first
  items.sort((a, b) => (S.detail[b.id] ? 1 : 0) - (S.detail[a.id] ? 1 : 0));
  items.forEach((c) => {
    const d = S.detail[c.id];
    const has = !!d, rev = !!(d && d.revision);
    const card = el("div", "card" + (has ? "" : " lock"));
    const nInd = (c.indicadores || []).length;
    const badge = !has ? `<span class="badge pend">En redacción</span>`
      : rev ? `<span class="badge rev" title="Línea base preliminar inferida, pendiente de validación">En revisión</span>`
      : `<span class="badge ok">Validado</span>`;
    card.innerHTML = `
      ${badge}
      ${c.eje ? `<div class="eje">${esc(c.eje)}</div>` : `<div class="eje">Comisión temática</div>`}
      <h3>${esc(c.nombre)}</h3>
      <p>${esc(c.resumen || "Comisión del Plan Perú 2050. Redacción en proceso.")}</p>
      ${has ? `<div class="mini"><span><b>${((c.objetivos_estrategicos || c.metas) || []).length}</b> objetivos</span><span><b>${nInd}</b> indicadores</span><span><b>${(c.cien_dias || []).length}</b> hitos 100d</span></div>` : ""}`;
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
    ${c.revision ? `<div class="revbanner">⚠ Línea base <b>preliminar</b> — contenido inferido a partir del tema de la comisión y datos públicos, <b>pendiente de validación</b> por el equipo. No proviene de una redacción oficial.${c.nivel_confianza ? ` (confianza: ${esc(c.nivel_confianza)})` : ""}</div>` : ""}
    ${c.resumen ? `<p style="color:var(--mut);font-size:1.02rem;margin:6px 0 0">${esc(c.resumen)}</p>` : ""}
    <button class="dlbtn" style="margin-top:12px" onclick="openPdf('entregables/pdf/${c.id}.pdf')">⬇ Descargar ficha (PDF)${c.revision ? " · preliminar" : ""}</button>
    ${c.vision ? `<div class="block"><h4>I · Síntesis de la situación futura</h4><p>${esc(c.vision)}</p></div>` : ""}
    ${(c.diagnostico || []).length ? `<div class="block"><h4>II · Síntesis de la situación actual</h4><ul class="ul">${c.diagnostico.map((d) => `<li>${esc(d)}</li>`).join("")}</ul></div>` : ""}
    ${(c.objetivos_estrategicos || c.metas || []).length ? `<div class="block"><h4>III · Objetivos estratégicos</h4><ul class="ul">${(c.objetivos_estrategicos || c.metas).map((o) => `<li>${esc(o)}</li>`).join("")}</ul></div>` : ""}
    ${(c.acciones || []).length ? `<div class="block"><h4>IV · Acciones estratégicas</h4><ul class="ul">${c.acciones.map((a) => `<li>${esc(a)}</li>`).join("")}</ul></div>` : ""}
    ${(c.indicadores || []).length ? `<div class="block"><h4>V · Matriz resumen — indicadores hoy → meta 2050</h4><div class="detchart"><canvas id="detCanvas"></canvas></div>${c.indicadores.map(indicatorRow).join("")}</div>` : ""}
    ${(c.cien_dias || []).length ? `<div class="block"><h4>VI · Hitos de los primeros 100 días</h4><ul class="ul ul100">${c.cien_dias.map((d) => `<li>${esc(d.accion || d)}${d.tipo ? ` <span class="tag100">${esc(d.tipo)}</span>` : ""}</li>`).join("")}</ul></div>` : ""}
    ${(c.articulacion_acuerdo_pedn || []).length ? `<div class="block"><h4>VII · Articulación con el Acuerdo Nacional y el PEDN al 2050</h4><ul class="ul">${c.articulacion_acuerdo_pedn.map((x) => `<li>${esc(x)}</li>`).join("")}</ul></div>` : ""}
    ${(c.articulacion_programas || []).length ? `<div class="block"><h4>VIII · Articulación con los Programas Presupuestales</h4><ul class="ul">${c.articulacion_programas.map((x) => `<li>${esc(x)}</li>`).join("")}</ul></div>` : ""}
    ${(c.pilares || []).length ? `<div class="block"><h4>Pilares de la estrategia</h4>${c.pilares.map((p) => `<div class="pilar"><b>${esc(p.nombre)}</b><span>${esc(p.descripcion)}</span></div>`).join("")}</div>` : ""}
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

/* ---------- Simulador de escenarios ---------- */
function buildSimulator() {
  const inds = allIndicators().slice(0, 10);
  S.simInds = inds;
  const box = $("#sim");
  if (!inds.length) { box.innerHTML = '<div class="skeleton">Aún no hay indicadores cuantitativos cargados.</div>'; return; }
  box.innerHTML = `<div class="gaugewrap" style="margin-bottom:8px"><div><div style="font-size:.8rem;color:var(--mut)">Índice de avance nacional</div><div class="big serif" id="simIndex" style="font-size:2.4rem;color:var(--gold)">0%</div></div><div style="flex:1;min-width:200px;color:var(--mut);font-size:.85rem">Promedio del avance de ${inds.length} indicadores cuantitativos validados desde su línea base de hoy hacia su meta 2050.</div></div>`;
  inds.forEach((i, k) => {
    const lo = Math.min(i.actual, i.meta), hi = Math.max(i.actual, i.meta);
    const row = el("div", "sim-row");
    row.innerHTML = `
      <div><div style="font-weight:600">${esc(i.nombre)}</div><div class="sim-meta">${esc(i.com)} · hoy ${num(i.actual)}${esc(i.unidad || "")} → meta ${num(i.meta)}${esc(i.unidad || "")}</div>
        <input type="range" min="${lo}" max="${hi}" step="${(hi - lo) / 100 || 1}" value="${i.actual}" data-k="${k}" />
      </div>
      <div class="sim-out"><div class="big" id="so${k}">${num(i.actual)}<span style="font-size:.9rem;color:var(--mut)">${esc(i.unidad || "")}</span></div><div class="sim-meta" id="sp${k}">0% de avance</div></div>`;
    box.append(row);
    $("input", row).oninput = () => { document.querySelectorAll("#scenarios .scbtn").forEach((b) => b.classList.remove("on")); updateSim(); };
  });
  document.querySelectorAll("#scenarios .scbtn").forEach((b) => { b.onclick = () => setScenario(+b.dataset.pct, b); });
  const cv = document.getElementById("simChart");
  if (cv && typeof Chart !== "undefined") {
    chartFont();
    S.simChart && S.simChart.destroy();
    S.simChart = new Chart(cv, {
      type: "bar",
      data: { labels: inds.map((i) => (i.nombre.length > 26 ? i.nombre.slice(0, 24) + "…" : i.nombre)),
        datasets: [{ label: "% avance", data: inds.map(() => 0), backgroundColor: "#e0a52e", borderRadius: 5 }] },
      options: { indexAxis: "y", plugins: { legend: { display: false }, tooltip: { callbacks: { label: (t) => ` ${t.raw}% de avance hacia la meta` } } },
        scales: { x: { max: 100, grid: { color: "#1e2840" }, ticks: { callback: (v) => v + "%" } }, y: { grid: { display: false }, ticks: { font: { size: 10 } } } } },
    });
  }
  // Gráfico de proyección temporal (polinómica)
  const pj = document.getElementById("simProj");
  if (pj && typeof Chart !== "undefined") {
    chartFont();
    S.simProj && S.simProj.destroy();
    S.simProj = new Chart(pj, {
      type: "line",
      data: { labels: PROJ_YEARS.map(String),
        datasets: [{ label: "Índice nacional", data: PROJ_YEARS.map(() => 0), borderColor: "#e0a52e", backgroundColor: "rgba(224,165,46,.15)", fill: true, tension: 0.35, pointRadius: 4, pointBackgroundColor: "#e0a52e" }] },
      options: { plugins: { legend: { display: false }, tooltip: { callbacks: { label: (t) => ` Índice ${t.raw}% en ${t.label}` } } },
        scales: { y: { min: 0, max: 100, grid: { color: "#1e2840" }, ticks: { callback: (v) => v + "%" } }, x: { grid: { display: false } } } },
    });
  }
  document.querySelectorAll("#ritmo .scbtn").forEach((b) => { b.onclick = () => setRitmo(b.dataset.shape, b); });
  updateSim();
}
function updateSim() {
  const inds = S.simInds; let sum = 0; const advs = [];
  inds.forEach((i, k) => {
    const range = document.querySelector(`input[data-k="${k}"]`); if (!range) { advs.push(0); return; }
    const v = parseFloat(range.value);
    const adv = i.meta === i.actual ? 100 : clamp(((v - i.actual) / (i.meta - i.actual)) * 100);
    sum += adv; advs.push(+adv.toFixed(1));
    const so = $("#so" + k), sp = $("#sp" + k);
    if (so) so.innerHTML = `${num(v)}<span style="font-size:.9rem;color:var(--mut)">${esc(i.unidad || "")}</span>`;
    if (sp) sp.textContent = `${adv.toFixed(0)}% de avance`;
  });
  const T = inds.length ? sum / inds.length : 0;
  const idx = $("#simIndex"); if (idx) idx.textContent = T.toFixed(0) + "%";
  if (S.simChart) { S.simChart.data.datasets[0].data = advs; S.simChart.update("none"); }
  if (S.simProj) {
    S.simProj.data.datasets[0].data = PROJ_YEARS.map((y) => +(T * shapeFn((y - 2026) / 24)).toFixed(1));
    S.simProj.update("none");
  }
}
function setScenario(pct, btn) {
  S.simInds.forEach((i, k) => {
    const range = document.querySelector(`input[data-k="${k}"]`); if (!range) return;
    range.value = i.actual + (pct / 100) * (i.meta - i.actual);
  });
  document.querySelectorAll("#scenarios .scbtn").forEach((b) => b.classList.toggle("on", b === btn));
  updateSim();
}
window.setScenario = setScenario;

/* Proyección temporal con fórmula polinómica (ritmo de avance) */
const PROJ_YEARS = [2026, 2030, 2035, 2040, 2045, 2050];
function shapeFn(x) {
  switch (S.ritmo) {
    case "accel": return x * x;               // cuadrática: arranque lento, cierre rápido
    case "scurve": return x * x * (3 - 2 * x); // cúbica smoothstep (curva S)
    case "early": return Math.sqrt(x);        // raíz: arranque rápido
    default: return x;                         // lineal
  }
}
function setRitmo(shape, btn) {
  S.ritmo = shape;
  document.querySelectorAll("#ritmo .scbtn").forEach((b) => b.classList.toggle("on", b === btn));
  updateSim();
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
  const det = validated().map((c) => ({ c, av: comAvance(c) })).filter((x) => x.av != null).sort((a, b) => b.av - a.av);
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
  // Cobertura por eje (validadas vs en revisión, apilado)
  const cv = document.getElementById("chartCobertura");
  if (cv) {
    const ejesAll = [...new Set(detailed().map((c) => c.eje).filter(Boolean))].sort();
    CHARTS.cobertura && CHARTS.cobertura.destroy();
    CHARTS.cobertura = new Chart(cv, {
      type: "bar",
      data: { labels: ejesAll.map((e) => (e.length > 20 ? e.slice(0, 18) + "…" : e)),
        datasets: [
          { label: "Validadas", data: ejesAll.map((e) => validated().filter((c) => c.eje === e).length), backgroundColor: "#2ed47a", borderRadius: 4 },
          { label: "En revisión", data: ejesAll.map((e) => reviewed().filter((c) => c.eje === e).length), backgroundColor: "#e0a52e", borderRadius: 4 },
        ] },
      options: { indexAxis: "y", plugins: { legend: { position: "bottom", labels: { boxWidth: 12, font: { size: 11 } } } },
        scales: { x: { stacked: true, grid: { color: "#1e2840" } }, y: { stacked: true, grid: { display: false } } } },
    });
  }
  // Mayores brechas — indicadores con menor avance
  const bv = document.getElementById("chartBrechas");
  if (bv) {
    const gaps = allIndicators().map((i) => ({ i, av: indAvance(i) })).filter((x) => x.av != null)
      .sort((a, b) => a.av - b.av).slice(0, 12);
    CHARTS.brechas && CHARTS.brechas.destroy();
    CHARTS.brechas = new Chart(bv, {
      type: "bar",
      data: { labels: gaps.map((x) => (x.i.nombre.length > 30 ? x.i.nombre.slice(0, 28) + "…" : x.i.nombre)),
        datasets: [{ data: gaps.map((x) => +x.av.toFixed(1)), backgroundColor: "#d91023", borderRadius: 4 }] },
      options: { indexAxis: "y",
        plugins: { legend: { display: false }, tooltip: { callbacks: { label: (t) => ` ${t.raw}% de avance · ${gaps[t.dataIndex].i.com}` } } },
        scales: { x: { max: 100, grid: { color: "#1e2840" }, ticks: { callback: (v) => v + "%" } }, y: { grid: { display: false }, ticks: { font: { size: 9 } } } } },
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

/* ---------- Plan 100 días ---------- */
function with100() { return S.list.filter((c) => (S.detail[c.id]?.cien_dias || []).length); }
function render100() {
  const box = document.getElementById("cien"); if (!box) return;
  const list = with100();
  if (!list.length) { box.innerHTML = '<div class="skeleton">Sin medidas de 100 días cargadas.</div>'; return; }
  const total = list.reduce((a, c) => a + S.detail[c.id].cien_dias.length, 0);
  box.innerHTML = `
    <div class="sub" style="font-size:.85rem;color:var(--mut);margin-bottom:12px">${total} medidas inmediatas en ${list.length} comisiones, extraídas de las redacciones. Útiles como insumo para los primeros 100 días del próximo gobierno.</div>
    <div style="display:grid;gap:8px">${list.map((c) => `<div style="display:flex;justify-content:space-between;align-items:center;gap:10px;border-bottom:1px solid var(--line);padding:8px 0"><button onclick="openDetail('${c.id}')" style="background:none;border:none;color:var(--txt);font:inherit;text-align:left;cursor:pointer;flex:1">${esc(c.nombre)}</button><span style="color:var(--gold);font-size:.82rem;white-space:nowrap">${S.detail[c.id].cien_dias.length} medidas</span></div>`).join("")}</div>
    <button class="dlbtn" style="margin-top:14px" onclick="dl100All()">⬇ Descargar plan consolidado de 100 días</button>`;
}
function md100(c) {
  const d = S.detail[c.id]; if (!d?.cien_dias?.length) return "";
  return `## ${c.nombre}\n` + d.cien_dias.map((x) => `- ${x.accion || x}${x.tipo ? ` _(${x.tipo})_` : ""}`).join("\n") + "\n\n";
}
function downloadText(name, text) {
  const b = new Blob([text], { type: "text/markdown;charset=utf-8" });
  const a = document.createElement("a"); a.href = URL.createObjectURL(b); a.download = name; a.click();
  setTimeout(() => URL.revokeObjectURL(a.href), 1000);
}
window.openPdf = (path) => window.open(path, "_blank", "noopener");
window.dl100All = () => window.openPdf("entregables/pdf/plan-100-dias.pdf");

window.dlEjes = () => window.openPdf("entregables/pdf/sintesis-por-ejes.pdf");

/* ---------- Búsqueda ---------- */
function wireSearch() {
  let t;
  $("#q").addEventListener("input", (e) => { clearTimeout(t); t = setTimeout(() => { S.q = e.target.value.trim(); renderGrid(); }, 120); });
}

/* ---------- Consulta IA ---------- */
function wireAI() {
  const panel = $("#aiPanel"), log = $("#aiLog");
  const ask = (q) => { addMsg("u", q); answer(q); };
  const send = () => {
    const inp = $("#aiInput"), q = inp.value.trim(); if (!q) return;
    inp.value = ""; ask(q);
  };
  $("#aiBtn").onclick = () => {
    panel.classList.toggle("open");
    if (panel.classList.contains("open") && !log.children.length) {
      addMsg("a", "Hola 👋 Soy el asistente del Plan Perú 2050. Pregúntame algo, o prueba:");
      const sugs = ["¿Qué propone la comisión de Salud?", "¿Cuál es la meta de Minería al 2050?", "Resume Educación en una frase", "¿Qué dice sobre energía nuclear?"];
      const box = el("div", "ai-sugs");
      sugs.forEach((s) => { const b = el("button", "ai-sug", esc(s)); b.onclick = () => ask(s); box.append(b); });
      log.append(box); log.scrollTop = 1e9;
    }
  };
  $("#aiClose").onclick = () => panel.classList.remove("open");
  $("#aiSend").onclick = send;
  $("#aiInput").addEventListener("keydown", (e) => { if (e.key === "Enter") send(); });
}
function addMsg(role, html) { const m = el("div", "msg " + role, esc(html)); $("#aiLog").append(m); $("#aiLog").scrollTop = 1e9; return m; }

async function answer(q) {
  const cfg = window.PP2050_IA || {};
  // Recuperación: solo las comisiones relevantes a la pregunta (prompt corto = respuesta rápida)
  const terms = q.toLowerCase().split(/\s+/).filter((w) => w.length > 3);
  const scored = detailed().map((c) => {
    const hay = (c.nombre + " " + (c.resumen || "") + " " + (c.eje || "") + " " + (c.vision || "") + " " + (c.diagnostico || []).join(" ")).toLowerCase();
    return { c, score: terms.reduce((a, w) => a + (hay.includes(w) ? 1 : 0), 0) };
  }).sort((a, b) => b.score - a.score);
  const picks = scored[0] && scored[0].score > 0 ? scored.filter((x) => x.score > 0).slice(0, 3) : scored.slice(0, 2);
  const ctx = picks.map(({ c }) => `### ${c.nombre} (${c.eje || ""})\n${(c.resumen || c.vision || "").slice(0, 320)}\nObjetivos: ${(c.objetivos_estrategicos || c.metas || []).slice(0, 3).join("; ")}\nIndicadores: ${(c.indicadores || []).slice(0, 4).map((i) => `${i.nombre} ${i.actual ?? "s/d"}→${i.meta ?? "s/d"}${i.unidad || ""}`).join("; ")}`).join("\n\n");
  if (cfg.apiKey || cfg.proxy) {
    const wait = addMsg("a", "…");
    try {
      const url = cfg.proxy || cfg.endpoint;
      const headers = { "Content-Type": "application/json" };
      if (!cfg.proxy && cfg.apiKey) headers.Authorization = "Bearer " + cfg.apiKey;
      const body = { model: cfg.model, max_tokens: 220, temperature: 0.6, messages: [
        { role: "system", content: "Eres un asesor cercano del Plan Perú 2050. Responde MUY breve (1 a 3 frases), en español cálido y humano, como hablándole a una persona, sin tecnicismos. Usa solo estos datos; si algo no está, dilo en una frase corta. No inventes cifras.\n\nDATOS:\n" + ctx },
        { role: "user", content: q },
      ] };
      const r = await fetch(url, { method: "POST", headers, body: JSON.stringify(body) });
      if (!r.ok) throw new Error("proxy " + r.status);
      const j = await r.json();
      const txt = j.choices?.[0]?.message?.content;
      if (!txt) throw new Error("empty");
      wait.textContent = txt;
      $("#aiLog").scrollTop = 1e9;
      return;
    } catch (e) {
      wait.remove(); // sin LLM disponible → cae a búsqueda local
    }
  }
  // Fallback local: usa las comisiones ya recuperadas (picks)
  if (!picks.length || !picks.some((x) => x.score > 0)) { addMsg("a", "No encontré comisiones relacionadas. Prueba con: energía, salud, minería, conocimiento, digital, ambiente…"); return; }
  picks.forEach(({ c }) => {
    addMsg("a", `${c.nombre} — ${(c.resumen || c.vision || "").slice(0, 180)} ${((c.objetivos_estrategicos || c.metas) || [])[0] ? "Objetivo: " + (c.objetivos_estrategicos || c.metas)[0] : ""}`);
  });
}

boot();

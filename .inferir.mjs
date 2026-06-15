export const meta = {
  name: 'pp2050-inferir',
  description: 'Inferir línea base preliminar (a revisión) de las comisiones sin redacción',
  phases: [{ title: 'Inferir', detail: 'un agente por lote de comisiones' }],
};

const COM = {
  type: 'object', additionalProperties: false,
  required: ['id', 'nombre', 'eje', 'resumen', 'vision', 'diagnostico', 'pilares', 'indicadores', 'metas', 'recomendacion', 'revision', 'nivel_confianza'],
  properties: {
    id: { type: 'string' }, nombre: { type: 'string' }, eje: { type: 'string' },
    resumen: { type: 'string' }, vision: { type: 'string' },
    diagnostico: { type: 'array', items: { type: 'string' } },
    pilares: { type: 'array', items: { type: 'object', additionalProperties: false, required: ['nombre', 'descripcion'], properties: { nombre: { type: 'string' }, descripcion: { type: 'string' } } } },
    indicadores: { type: 'array', items: { type: 'object', additionalProperties: false, required: ['nombre', 'actual', 'meta', 'unidad', 'fuente'], properties: { nombre: { type: 'string' }, actual: { type: ['number', 'null'] }, meta: { type: ['number', 'null'] }, unidad: { type: 'string' }, fuente: { type: 'string' }, anioMeta: { type: 'number' } } } },
    metas: { type: 'array', items: { type: 'string' } },
    acciones: { type: 'array', items: { type: 'string' } },
    recomendacion: { type: 'string' },
    revision: { type: 'boolean' },
    nivel_confianza: { type: 'string', enum: ['medio', 'preliminar'] },
  },
};
const SCHEMA = { type: 'object', additionalProperties: false, required: ['comisiones'], properties: { comisiones: { type: 'array', items: COM } } };

const RULES = `Estás construyendo una LÍNEA BASE PRELIMINAR ("a revisión") para comisiones del Plan Perú 2050 (CNPP — Colegio de Ingenieros del Perú) que AÚN NO TIENEN redacción oficial. El contenido es inferido para que el equipo lo revise y valide; NO es oficial.

REGLAS ESTRICTAS (anti-overclaiming):
- visión, diagnóstico, pilares, metas, acciones y recomendación: redáctalos en español, realistas y específicos a la situación de ese sector EN EL PERÚ (usa conocimiento general del sector y del país, horizonte 2050). Tono técnico, sobrio.
- indicadores: incluye 3 a 6. Para "actual" usa SOLO una cifra pública que conozcas con razonable certeza (INEI, ministerios, Banco Mundial, OCDE, OMS, etc.) y entonces pon en "fuente" algo como "referencial — <fuente>". Si NO estás seguro del valor, pon actual=null. Para "meta" puedes proponer una meta 2050 (anioMeta 2050) y marca en "fuente" "meta propuesta — a validar". NUNCA inventes una cifra y la presentes como dato real.
- nivel_confianza: "medio" si tiene varios indicadores con cifras públicas reales; "preliminar" si es mayormente cualitativo.
- revision: true SIEMPRE.
- eje: uno de: "Economía del Conocimiento", "Sostenibilidad y Ambiente", "Soberanía y Defensa", "Infraestructura y Conectividad", "Bienestar y Salud", "Competitividad".
- Respeta EXACTAMENTE el id y nombre que se te dan por comisión.
Devuelve { comisiones: [...] } con un objeto por cada comisión del lote.`;

phase('Inferir');

const lotes = [[{"id":"capital-social","nombre":"Capital Social"},{"id":"desarrollo-rural","nombre":"Desarrollo Rural"},{"id":"etica","nombre":"Ética"},{"id":"innovacion","nombre":"Innovación"}],[{"id":"mipymes","nombre":"Mipymes"},{"id":"quimica","nombre":"Química"},{"id":"vivienda","nombre":"Vivienda"},{"id":"ciber-seguridad","nombre":"Ciber Seguridad"},{"id":"desarrollo-urbano","nombre":"Desarrollo Urbano"}],[{"id":"forestal","nombre":"Forestal"},{"id":"inteligencia-artificial","nombre":"Inteligencia Artificial"},{"id":"orden-publico-y-seguridad","nombre":"Orden Público y Seguridad"},{"id":"reforma-del-estado","nombre":"Reforma Del Estado"}]];
const results = await parallel(
  lotes.map((lote, i) => () =>
    agent(`${RULES}\n\nLOTE ${i + 1} — genera una comisión por cada una de estas:\n${lote.map((c) => `- id="${c.id}" nombre="${c.nombre}"`).join('\n')}`,
      { label: `lote-${i + 1}`, phase: 'Inferir', schema: SCHEMA })
  )
);
const all = results.filter(Boolean).flatMap((r) => r.comisiones || []);
log(`Inferidas ${all.length} comisiones`);
return { comisiones: all };

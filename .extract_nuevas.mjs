export const meta = {
  name: 'pp2050-extract-nuevas',
  description: 'Extraer datos de las nuevas redacciones oficiales (→ validado)',
  phases: [{ title: 'Extract', detail: 'un agente por comisión nueva' }],
};
const DIR = '/Users/unimauro/Documents/Repos/plan-peru-2050/fuentes/nuevas';

const SCHEMA = {
  type: 'object', additionalProperties: false,
  required: ['id', 'nombre', 'resumen', 'vision', 'diagnostico', 'pilares', 'indicadores', 'metas', 'recomendacion', 'eje'],
  properties: {
    id: { type: 'string' }, nombre: { type: 'string' }, eje: { type: 'string' },
    resumen: { type: 'string' }, vision: { type: 'string' },
    diagnostico: { type: 'array', items: { type: 'string' } },
    pilares: { type: 'array', items: { type: 'object', additionalProperties: false, required: ['nombre', 'descripcion'], properties: { nombre: { type: 'string' }, descripcion: { type: 'string' } } } },
    indicadores: { type: 'array', description: 'Indicadores cuantitativos. SOLO cifras EXPLÍCITAS en el texto; null si no consta. No inventar.',
      items: { type: 'object', additionalProperties: false, required: ['nombre', 'actual', 'meta', 'unidad'],
        properties: { nombre: { type: 'string' }, actual: { type: ['number', 'null'] }, meta: { type: ['number', 'null'] }, unidad: { type: 'string' }, fuente: { type: 'string' }, anioMeta: { type: 'number' } } } },
    metas: { type: 'array', items: { type: 'string' } },
    acciones: { type: 'array', items: { type: 'string' } },
    recomendacion: { type: 'string' },
    cien_dias: { type: 'array', items: { type: 'object', additionalProperties: false, required: ['accion'], properties: { accion: { type: 'string' }, tipo: { type: 'string' } } },
      description: 'Medidas de los primeros 100 días si el documento las trae; vacío si no.' },
  },
};

const P = (file, id, nombre) => `Eres analista de políticas públicas. Lee COMPLETO el archivo:
${DIR}/${file}
Es la redacción oficial de la Comisión Temática "${nombre}" del Plan Perú 2050 (CNPP / Colegio de Ingenieros del Perú).
Algunos documentos dicen "Plan Perú 2040" — respeta el año de meta que indique cada indicador (anioMeta).

Extrae a datos estructurados, fiel al documento, SIN inventar cifras:
- id EXACTO: "${id}"  ·  nombre: "${nombre}"
- indicadores: captura los CUANTITATIVOS con actual (hoy/brecha) y meta SOLO si el número está en el texto; si no, null.
  Pon la fuente/año en "fuente"/"anioMeta". Prefiere null antes que un número inventado.
- diagnostico (brechas), pilares (con descripción), metas (texto), acciones (iniciativas), recomendacion (la principal).
- cien_dias: medidas de los primeros 100 días si las trae (acción + tipo); vacío si no.
- eje: uno de "Economía del Conocimiento" / "Sostenibilidad y Ambiente" / "Soberanía y Defensa" /
  "Infraestructura y Conectividad" / "Bienestar y Salud" / "Competitividad".
Devuelve el objeto estructurado.`;

phase('Extract');
const T = [
  ['ComisionDesarrolloHumanoIndustria.txt', 'industria', 'Industria (Desarrollo Humano)'],
  ['ComercioExterior.txt', 'comercio-exterior-e-insercion-en-el-merc', 'Comercio Exterior e Inserción en el Mercado Externo'],
  ['ComisionAcuicultura.txt', 'acuicultura-y-pesca', 'Acuicultura y Pesca'],
  ['ComisionEducacion.txt', 'educacion-tres-niveles', 'Educación (Tres Niveles)'],
  ['ComisionEnergiaNuclear.txt', 'energia-nuclear', 'Energía Nuclear'],
  ['ComisionInfraestructura.txt', 'infraestructura-y-construccion', 'Infraestructura y Construcción'],
  ['ComisionReformaEstado.txt', 'reforma-del-estado', 'Reforma del Estado'],
  ['ComisionMineria.txt', 'mineria', 'Minería'],
  ['ComisionMYPE.txt', 'mipymes', 'MYPE / MIPYMES'],
  ['ComisionPesca.txt', 'pesca', 'Pesca'],
];
const r = await parallel(T.map(([f, id, n]) => () => agent(P(f, id, n), { label: id, phase: 'Extract', schema: SCHEMA })));
return { comisiones: r.filter(Boolean) };

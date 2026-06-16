export const meta = {
  name: 'pp2050-extract-oficial',
  description: 'Re-extraer docs de formato oficial al esquema del Informe Ejecutivo (con articulaciones)',
  phases: [{ title: 'Extract', detail: 'un agente por comisión (estructura oficial)' }],
};
const DIR = '/Users/unimauro/Documents/Repos/plan-peru-2050/fuentes/nuevas';

const IND = { type: 'object', additionalProperties: false, required: ['nombre', 'actual', 'meta', 'unidad'],
  properties: { nombre: { type: 'string' }, actual: { type: ['number', 'null'] }, meta: { type: ['number', 'null'] }, unidad: { type: 'string' }, fuente: { type: 'string' }, anioMeta: { type: 'number' } } };

const SCHEMA = {
  type: 'object', additionalProperties: false,
  required: ['id', 'nombre', 'eje', 'resumen', 'vision', 'diagnostico', 'objetivos_estrategicos', 'acciones', 'indicadores', 'cien_dias', 'articulacion_acuerdo_pedn', 'articulacion_programas'],
  properties: {
    id: { type: 'string' }, nombre: { type: 'string' }, eje: { type: 'string' },
    resumen: { type: 'string', description: 'Introducción / resumen ejecutivo en 1-3 frases.' },
    vision: { type: 'string', description: 'I. Síntesis de la Situación Futura (visión 2050).' },
    diagnostico: { type: 'array', items: { type: 'string' }, description: 'II. Síntesis de la Situación Actual (brechas/bullets, con cifras si las hay).' },
    objetivos_estrategicos: { type: 'array', items: { type: 'string' }, description: 'III. Objetivos Estratégicos.' },
    acciones: { type: 'array', items: { type: 'string' }, description: 'IV. Acciones Estratégicas.' },
    indicadores: { type: 'array', items: IND, description: 'V. Matriz Resumen — indicadores cuantitativos. SOLO cifras EXPLÍCITAS; null si no consta. No inventar.' },
    cien_dias: { type: 'array', items: { type: 'object', additionalProperties: false, required: ['accion'], properties: { accion: { type: 'string' }, tipo: { type: 'string' } } }, description: 'VI. Hitos de los primeros 100 días de Gobierno.' },
    articulacion_acuerdo_pedn: { type: 'array', items: { type: 'string' }, description: 'VII. Articulación con Políticas de Estado del Acuerdo Nacional y el PEDN al 2050 (lista los alineamientos, ej. "PEDN ON 1: …", "Política de Estado N°…").' },
    articulacion_programas: { type: 'array', items: { type: 'string' }, description: 'VIII. Articulación con Programas Presupuestales (lista los PP, ej. "PP 0091: …").' },
    pilares: { type: 'array', items: { type: 'object', additionalProperties: false, required: ['nombre', 'descripcion'], properties: { nombre: { type: 'string' }, descripcion: { type: 'string' } } } },
    recomendacion: { type: 'string' },
  },
};

const P = (file, id, nombre) => `Eres analista de políticas públicas. Lee COMPLETO el archivo:
${DIR}/${file}
Es el "Informe Ejecutivo" de la Comisión "${nombre}" del Plan Perú 2050 (CNPP / Colegio de Ingenieros del Perú).
Tiene la estructura oficial: I. Síntesis de la Situación Futura · II. Síntesis de la Situación Actual ·
III. Objetivos Estratégicos · IV. Acciones Estratégicas · V. Matriz Resumen · VI. Hitos de los primeros 100 días ·
VII. Articulación con las Políticas de Estado y el PEDN al 2050 · VIII. Articulación con los Programas Presupuestales ·
IX. Integrantes (NO la extraigas — son datos personales).

Extrae a datos estructurados, fiel al documento, SIN inventar cifras (null si un número no está explícito):
- id EXACTO: "${id}" · nombre: "${nombre}"
- vision = I (situación futura) · diagnostico = II (situación actual, bullets) · objetivos_estrategicos = III ·
  acciones = IV (acciones estratégicas) · indicadores = V (Matriz Resumen, cuantitativos con actual/meta/unidad/fuente/anioMeta) ·
  cien_dias = VI (acción + tipo) · articulacion_acuerdo_pedn = VII (lista los alineamientos al Acuerdo Nacional / PEDN, ej. "PEDN ON 1: …") ·
  articulacion_programas = VIII (lista los Programas Presupuestales, ej. "PP 00XX: …").
- eje: uno de "Economía del Conocimiento" / "Sostenibilidad y Ambiente" / "Soberanía y Defensa" /
  "Infraestructura y Conectividad" / "Bienestar y Salud" / "Competitividad".
- recomendacion: si el doc trae una recomendación de política, inclúyela; si no, frase breve. pilares: opcional.
Devuelve el objeto estructurado.`;

phase('Extract');
const T = [
  ['DH_Industrializacion_V1606.txt', 'industria', 'Desarrollo Humano e Industrialización'],
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

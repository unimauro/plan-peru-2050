export const meta = {
  name: 'pp2050-100dias',
  description: 'Extraer la hoja de ruta de 100 primeros días de cada redacción',
  phases: [{ title: '100días', detail: 'un agente por comisión redactada' }],
};
const DIR = '/Users/unimauro/Documents/Repos/plan-peru-2050/fuentes';
const SCHEMA = {
  type: 'object', additionalProperties: false,
  required: ['id', 'cien_dias'],
  properties: {
    id: { type: 'string' },
    cien_dias: {
      type: 'array',
      description: 'Medidas concretas para los primeros 100 días del próximo gobierno que el documento propone. Vacío si el documento no las trae.',
      items: { type: 'object', additionalProperties: false, required: ['accion'], properties: {
        accion: { type: 'string', description: 'Medida concreta (verbo + objeto).' },
        tipo: { type: 'string', description: 'ley/decreto, institucional, inversión, programa, regulación, etc.' },
      } },
    },
  },
};
const P = (file, id, nombre) => `Lee el archivo:\n${DIR}/${file}\nEs la redacción de la Comisión "${nombre}" del Plan Perú 2050.
Extrae ÚNICAMENTE las medidas que el documento propone para los PRIMEROS 100 DÍAS del próximo gobierno
(busca secciones como "100 días", "primeros 100 días", "hoja de ruta", "hitos 100 días", "acciones inmediatas").
Devuelve cada medida como una acción concreta y su tipo. Si el documento NO trae medidas de 100 días, devuelve cien_dias vacío.
NO inventes medidas que no estén en el texto. id EXACTO: "${id}".`;

phase('100días');
const T = [
  ['REDACCIÓN_-_COMISIÓN_AEROESPACIAL_Final.txt','espacio','Aeroespacial'],
  ['REDACCIÓN_-_COMISIÓN_MARÍTIMO_VFINAL_.txt','maritimo-fluvial-y-lacustre','Marítimo'],
  ['CNPP_2050_-Mayo_2026.txt','capital-del-conocimiento','Capital del Conocimiento'],
  ['COMISIÓN_PERÚ_EN_LA_ERA_DIGITAL_AL_2050_v4.txt','peru-en-la-era-digital','Perú en la Era Digital'],
  ['REDACCIÓN_-_COMISIÓN_CYT.txt','ciencia-y-tecnologia','Ciencia y Tecnología'],
  ['COMISION_AMBIENTAL_rev.txt','medio-ambiente','Medio Ambiente'],
  ['Propuesta_Politica_Publica_Gemelos_Digitales_Salud_Peru_2026_v20.txt','salud','Salud'],
  ['PPLANPERU2050 TELECOMUNICACIONES (1).txt','telecomunicaciones','Telecomunicaciones'],
];
const r = await parallel(T.map(([f,id,n]) => () => agent(P(f,id,n), { label: id, phase: '100días', schema: SCHEMA })));
return { items: r.filter(Boolean) };

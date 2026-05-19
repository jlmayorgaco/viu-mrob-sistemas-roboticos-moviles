const path = require('path');
const fs = require('fs');
const { createRequire } = require('module');

function loadPptxGen() {
  try {
    return require('pptxgenjs');
  } catch (err) {
    const tempRuntime = path.join(process.env.TEMP || process.env.TMP || '', 'actividad1_pptxgenjs_runtime', 'node_modules', 'pptxgenjs', 'package.json');
    if (fs.existsSync(tempRuntime)) {
      return createRequire(tempRuntime)('pptxgenjs');
    }
    const bundled = path.join(
      process.env.USERPROFILE || '',
      '.cache',
      'codex-runtimes',
      'codex-primary-runtime',
      'dependencies',
      'node',
      'node_modules',
      'pptxgenjs',
      'package.json'
    );
    if (fs.existsSync(bundled)) {
      return createRequire(bundled)('pptxgenjs');
    }
    throw new Error('pptxgenjs is required. Run `npm install pptxgenjs` or set NODE_PATH to a node_modules folder that contains it.');
  }
}

const pptxgen = loadPptxGen();

const out = path.join(__dirname, 'Actividad2_Pioneer_CoppeliaSim.pptx');
const pptx = new pptxgen();
pptx.layout = 'LAYOUT_WIDE';
pptx.author = 'Jorge Luis Mayorga Taborda';
pptx.company = 'Universidad Internacional de Valencia';
pptx.subject = 'Actividad 2 - CoppeliaSim/Lua';
pptx.title = 'Programacion y control de un robot Pioneer';
pptx.lang = 'es-ES';
pptx.theme = {
  headFontFace: 'Aptos Display',
  bodyFontFace: 'Aptos',
  lang: 'es-ES',
};
pptx.defineLayout({ name: 'WIDE', width: 13.333, height: 7.5 });
pptx.layout = 'WIDE';

const C = {
  primary: 'C44624',
  accent: 'E8552D',
  ink: '191919',
  muted: '5E6670',
  pale: 'F6F7F9',
  rule: 'D9DEE5',
  green: '2D8A4E',
};

function addHeader(slide, title, n) {
  slide.background = { color: 'FFFFFF' };
  slide.addShape(pptx.ShapeType.rect, {
    x: 0,
    y: 0,
    w: 13.333,
    h: 0.78,
    fill: { color: C.primary },
    line: { color: C.primary },
  });
  slide.addText(title, {
    x: 0.55,
    y: 0.18,
    w: 10.8,
    h: 0.36,
    fontFace: 'Aptos Display',
    fontSize: 19,
    bold: true,
    color: 'FFFFFF',
    margin: 0,
    fit: 'shrink',
  });
  slide.addText(String(n), {
    x: 12.45,
    y: 0.18,
    w: 0.35,
    h: 0.32,
    fontSize: 12,
    color: 'FFFFFF',
    align: 'right',
    margin: 0,
  });
}

function addBullets(slide, items, x = 0.85, y = 1.35, w = 11.5, fontSize = 17, gap = 0.48) {
  items.forEach((item, i) => {
    slide.addText('-', { x, y: y + i * gap + 0.03, w: 0.18, h: 0.2, fontSize, color: C.ink, margin: 0 });
    slide.addText(item, {
      x: x + 0.32,
      y: y + i * gap,
      w,
      h: gap * 0.88,
      fontSize,
      color: C.ink,
      margin: 0,
      fit: 'shrink',
    });
  });
}

function addBodyText(slide, text, x, y, w, h, fontSize = 18, opts = {}) {
  slide.addText(text, {
    x,
    y,
    w,
    h,
    fontSize,
    color: opts.color || C.ink,
    bold: opts.bold || false,
    align: opts.align || 'left',
    valign: opts.valign || 'mid',
    margin: 0.02,
    fit: 'shrink',
  });
}

function addMetric(slide, value, label, x, y, w) {
  slide.addText(value, {
    x,
    y,
    w,
    h: 0.52,
    fontFace: 'Aptos Display',
    fontSize: 30,
    bold: true,
    color: C.primary,
    margin: 0,
    fit: 'shrink',
  });
  slide.addText(label, {
    x,
    y: y + 0.54,
    w,
    h: 0.42,
    fontSize: 12,
    color: C.muted,
    margin: 0,
    fit: 'shrink',
  });
}

function addEquation(slide, eq, x, y, w) {
  slide.addShape(pptx.ShapeType.rect, {
    x,
    y,
    w,
    h: 0.72,
    fill: { color: C.pale },
    line: { color: C.rule, width: 1 },
    radius: 0.08,
  });
  slide.addText(eq, {
    x: x + 0.18,
    y: y + 0.18,
    w: w - 0.36,
    h: 0.34,
    fontFace: 'Cambria Math',
    fontSize: 19,
    color: C.ink,
    margin: 0,
    align: 'center',
    fit: 'shrink',
  });
}

function slide1() {
  const s = pptx.addSlide();
  s.background = { color: 'FFFFFF' };
  s.addShape(pptx.ShapeType.rect, { x: 0, y: 0, w: 13.333, h: 7.5, fill: { color: 'FFFFFF' }, line: { color: 'FFFFFF' } });
  s.addShape(pptx.ShapeType.rect, { x: 0, y: 0, w: 0.22, h: 7.5, fill: { color: C.primary }, line: { color: C.primary } });
  s.addText('Programacion y control de un robot Pioneer', {
    x: 0.72,
    y: 1.25,
    w: 11.4,
    h: 0.92,
    fontFace: 'Aptos Display',
    fontSize: 35,
    bold: true,
    color: C.ink,
    margin: 0,
    fit: 'shrink',
  });
  s.addText('Actividad 2 - CoppeliaSim/Lua', { x: 0.75, y: 2.35, w: 7.2, h: 0.38, fontSize: 19, color: C.primary, bold: true, margin: 0 });
  s.addText('Universidad Internacional de Valencia\\nAutor: Jorge Luis Mayorga Taborda\\nProfesor: Jose I. Iniguez\\nEntrega: 26 de mayo de 2026', {
    x: 0.76,
    y: 3.18,
    w: 7.5,
    h: 1.35,
    fontSize: 15,
    color: C.ink,
    breakLine: false,
    margin: 0,
    fit: 'shrink',
  });
  addMetric(s, '22', 'sensores activos', 9.05, 3.05, 2.1);
  addMetric(s, '8', 'escenarios de prueba', 9.05, 4.05, 2.1);
  addMetric(s, '3 AMR', 'flota A* auxiliar', 9.05, 5.05, 2.45);
}

function slide2() {
  const s = pptx.addSlide();
  addHeader(s, 'Objetivo', 2);
  addBullets(s, [
    'Programar un Pioneer P3DX en CoppeliaSim.',
    'Parte 1: desplazamiento hacia un objetivo mediante campos potenciales.',
    'Parte 2: evitacion reactiva de obstaculos.',
    'Integracion del robot en una celda robotizada.',
  ]);
}

function slideTraceability() {
  const s = pptx.addSlide();
  addHeader(s, 'Trazabilidad 5/5', 3);
  const rows = [
    [{ text: 'Guia y temas', options: { bold: true } }, { text: 'Implementacion final', options: { bold: true } }],
    ['Pioneer en CoppeliaSim/Lua', 'Script Lua embebido en PioneerP3DX.'],
    ['Campos potenciales', 'Atraccion a mannequin con saturacion de velocidad.'],
    ['Anticolision', '16 ultrasonidos + 6 sensores virtuales.'],
    ['Celda robotizada', 'Docking/carga, HMI, transportadores, palets, vallas y eventos.'],
    ['Bateria y robustez', 'Zonas de velocidad, sensor degradado y telemetria industrial.'],
    ['A* cooperativo', '3 AMR auxiliares con reservas temporales, bateria y recarga.'],
    ['PPTs de clase', 'Modelo diferencial, sensores, FSM, navegacion y validacion.'],
  ];
  s.addTable(rows, {
    x: 0.75,
    y: 1.25,
    w: 11.8,
    h: 4.45,
    colW: [5.2, 6.6],
    border: { type: 'solid', color: '222222', pt: 0.6 },
    fontSize: 13.5,
    color: C.ink,
    margin: 0.08,
    valign: 'mid',
  });
}

function slide3() {
  const s = pptx.addSlide();
  addHeader(s, 'Entorno de simulacion', 4);
  addBullets(s, [
    'CoppeliaSim con scripts Lua embebidos.',
    'Escenas base: Actividad2_1_Pioneer.ttt y Actividad2_2_Pioneer.ttt.',
    'Escena final: Actividad2_Pioneer_Profesional_10_10.ttt.',
    'Objetivos posibles: mannequin, Bill o dummy de estacion.',
    '16 ultrasonidos + 6 sensores virtuales de seguridad.',
    'Escenarios: pallet movil, parada, objetivo dinamico, pasillo estrecho, sensor degradado y bateria baja.',
  ], 0.85, 1.18, 11.8, 16, 0.52);
}

function slide4() {
  const s = pptx.addSlide();
  addHeader(s, 'Modelo Pioneer P3DX', 5);
  addEquation(s, 'v_L = v - (L/2) omega     |     v_R = v + (L/2) omega', 1.15, 1.55, 11.0);
  addEquation(s, 'omega_L = v_L / r     |     omega_R = v_R / r', 1.15, 2.65, 11.0);
  addBodyText(s, 'Robot diferencial con control por velocidad de ruedas y sensores de proximidad.', 1.4, 4.25, 10.4, 0.5, 18, { align: 'center' });
}

function slide5() {
  const s = pptx.addSlide();
  addHeader(s, 'Parte 1: campos potenciales', 6);
  addEquation(s, 'F_att = k_att [ x_g - x_r ,  y_g - y_r ]', 1.25, 1.25, 10.8);
  addBullets(s, [
    'Calcular vector robot-objetivo.',
    'Obtener rumbo deseado con atan2.',
    'Regular avance y giro con saturacion.',
    'Detener al entrar en tolerancia.',
  ], 1.35, 2.55, 9.4, 17, 0.55);
}

function slide6() {
  const s = pptx.addSlide();
  addHeader(s, 'Parte 2: anticolisiones', 7);
  addBullets(s, [
    'Cada sensor cercano genera fuerza repulsiva.',
    'La direccion final combina atraccion y repulsion.',
    'El robot reduce velocidad cuando hay obstaculos cerca.',
    'Se prueban obstaculos frontales, laterales, objetivo movil, ruido y fallo intermitente de sensor.',
  ], 0.95, 1.35, 11.5, 17, 0.62);
  addMetric(s, '0,191 m', 'distancia minima validada', 1.25, 5.2, 3.4);
  addMetric(s, '0,540', 'riesgo final de obstaculo', 5.0, 5.2, 3.4);
  addMetric(s, '22', 'sensores leidos por el controlador', 8.65, 5.2, 3.4);
}

function slide7() {
  const s = pptx.addSlide();
  addHeader(s, 'Flujo de control', 8);
  const boxes = [
    ['Leer objetivo, ruta y sensores', 0.9, 1.65],
    ['FSM + campos potenciales', 4.25, 1.65],
    ['Saturar v, omega', 7.6, 1.65],
    ['Enviar velocidades de rueda', 4.25, 3.65],
  ];
  boxes.forEach(([txt, x, y]) => {
    s.addShape(pptx.ShapeType.roundRect, { x, y, w: 2.7, h: 0.75, rectRadius: 0.08, fill: { color: C.pale }, line: { color: C.primary, width: 1.2 } });
    addBodyText(s, txt, x + 0.12, y + 0.15, 2.46, 0.42, 12, { align: 'center' });
  });
  s.addShape(pptx.ShapeType.line, { x: 3.68, y: 2.02, w: 0.48, h: 0, line: { color: C.primary, width: 1.5, endArrowType: 'triangle' } });
  s.addShape(pptx.ShapeType.line, { x: 7.03, y: 2.02, w: 0.48, h: 0, line: { color: C.primary, width: 1.5, endArrowType: 'triangle' } });
  s.addShape(pptx.ShapeType.line, { x: 8.95, y: 2.45, w: -2.6, h: 1.05, line: { color: C.primary, width: 1.5, endArrowType: 'triangle' } });
  s.addShape(pptx.ShapeType.line, { x: 4.2, y: 4.05, w: -2.2, h: -1.25, line: { color: C.primary, width: 1.2, dash: 'dash', endArrowType: 'triangle' } });
}

function slide8() {
  const s = pptx.addSlide();
  addHeader(s, 'Integracion en celda', 9);
  addBullets(s, [
    'Zona segura de espera.',
    'Mision hacia Bill, mannequin o punto de estacion.',
    'Evitacion de obstaculos de la celda.',
    'Senales internas: missionReady, pioneerArrived, pioneerState y pioneerScenario.',
    'Celda con transportadores, palets, vallas, eventos, estacion objetivo y estacion de carga.',
  ], 0.9, 1.25, 11.5, 16, 0.55);
}

function slideRobustness() {
  const s = pptx.addSlide();
  addHeader(s, 'Extensiones robustas', 10);
  addBullets(s, [
    'Bateria simulada con modos NORMAL, LOW y CHARGING.',
    'Zonas de velocidad: docking, carril de aproximacion y zona por defecto.',
    'Filtro de ruido y fallo intermitente en sensores fronto-laterales.',
    'HMI visual con bateria, estado, zona activa, carga y fallo sensorial.',
    'Flota auxiliar de 3 AMR con A* cooperativo y retorno a estaciones de carga.',
  ], 0.9, 1.25, 11.5, 16.5, 0.58);
  addMetric(s, '68%', 'bateria final', 1.05, 5.15, 2.6);
  addMetric(s, 'LOW', 'politica vista', 4.0, 5.15, 2.6);
  addMetric(s, '3', 'zonas vistas', 6.95, 5.15, 2.6);
  addMetric(s, 'S6-S7', 'sensores y bateria', 9.9, 5.15, 2.6);
}

function slideFleet() {
  const s = pptx.addSlide();
  addHeader(s, 'Flota A* cooperativa', 11);
  addBullets(s, [
    '3 robots AMR auxiliares sobre una grilla de celda.',
    'A* con reservas celda-tiempo y arista-tiempo para evitar ocupaciones simultaneas y cruces opuestos.',
    'Bateria con descarga, retorno autonomo a estacion de carga y recarga hasta READY.',
    'La flota complementa al Pioneer principal sin cambiar la solucion exigida por la guia.',
  ], 0.9, 1.18, 11.5, 16.2, 0.58);
  addMetric(s, '16', 'planes A* generados', 1.05, 5.15, 2.6);
  addMetric(s, '8', 'conflictos evitados', 4.0, 5.15, 2.6);
  addMetric(s, '4', 'eventos de carga', 6.95, 5.15, 2.6);
  addMetric(s, '3/3', 'robots READY', 9.9, 5.15, 2.6);
}

function slide9() {
  const s = pptx.addSlide();
  addHeader(s, 'Validacion', 12);
  const rows = [
    [{ text: 'Prueba', options: { bold: true } }, { text: 'Criterio', options: { bold: true } }],
    ['Atraccion', 'Distancia al objetivo decrece.'],
    ['Llegada', 'Parada dentro de tolerancia.'],
    ['Obstaculo frontal', 'Rodeo sin colision.'],
    ['Objetivo movil', 'Seguimiento estable.'],
    ['Celda', 'No invadir zonas de otros equipos.'],
    ['Flota A*', '3 robots completan mision y recarga.'],
  ];
  s.addTable(rows, {
    x: 0.65,
    y: 1.05,
    w: 12.0,
    h: 2.45,
    colW: [5.9, 6.1],
    border: { type: 'solid', color: '222222', pt: 0.7 },
    fontSize: 14,
    color: C.ink,
    margin: 0.08,
    valign: 'mid',
  });
  addBodyText(s, 'Validacion headless final: 4,328 m -> 0,739 m, estado ARRIVED, 22 sensores activos, 8 escenarios observados y distancia minima a obstaculo 0,191 m. Flota: 16 planes A*, 8 conflictos evitados, 4 cargas y 3/3 robots READY.', 0.75, 4.25, 11.8, 1.05, 14.5);
}

function slide10() {
  const s = pptx.addSlide();
  addHeader(s, 'Conclusiones', 13);
  addBullets(s, [
    'Campos potenciales: solucion sencilla y didactica.',
    'La evitacion reactiva mejora seguridad de navegacion.',
    'La flota A* demuestra coordinacion multi-robot y gestion de bateria.',
    'CoppeliaSim permite ajustar parametros antes de la demostracion.',
    'Limitacion: posibles minimos locales y oscilaciones.',
  ], 0.95, 1.45, 11.1, 17, 0.62);
}

[slide1, slide2, slideTraceability, slide3, slide4, slide5, slide6, slide7, slide8, slideRobustness, slideFleet, slide9, slide10].forEach((fn) => fn());

pptx.writeFile({ fileName: out });

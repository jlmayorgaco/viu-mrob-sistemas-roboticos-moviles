const path = require('path');
const fs = require('fs');
const { createRequire } = require('module');

function loadPptxGen() {
  try {
    return require('pptxgenjs');
  } catch (err) {
    const tempRuntime = path.join(process.env.TEMP || process.env.TMP || '', 'actividad1_pptxgenjs_runtime', 'node_modules', 'pptxgenjs', 'package.json');
    if (fs.existsSync(tempRuntime)) return createRequire(tempRuntime)('pptxgenjs');

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
    if (fs.existsSync(bundled)) return createRequire(bundled)('pptxgenjs');

    throw new Error('pptxgenjs is required. Run `npm install pptxgenjs` or set NODE_PATH to a node_modules folder that contains it.');
  }
}

const pptxgen = loadPptxGen();
const pptx = new pptxgen();
const out = path.join(__dirname, 'Actividad2_Pioneer_CoppeliaSim.pptx');

pptx.defineLayout({ name: 'WIDE', width: 13.333, height: 7.5 });
pptx.layout = 'WIDE';
pptx.author = 'Jorge Luis Mayorga Taborda';
pptx.company = 'Universidad Internacional de Valencia';
pptx.subject = 'Actividad 2 - CoppeliaSim/Lua';
pptx.title = 'Programacion y control de un robot Pioneer P3DX';
pptx.lang = 'es-ES';
pptx.theme = {
  headFontFace: 'Aptos Display',
  bodyFontFace: 'Aptos',
  lang: 'es-ES',
};

const C = {
  deep: '0B1F33',
  ink: '17202A',
  muted: '65717F',
  paper: 'F7F8FA',
  rule: 'D8DEE6',
  copper: 'C44624',
  orange: 'E8552D',
  teal: '168B8F',
  blue: '2B6CB0',
  green: '2D8A4E',
  amber: 'B7791F',
  red: 'B83232',
  white: 'FFFFFF',
};

let slideNo = 0;

function addText(slide, text, x, y, w, h, opts = {}) {
  slide.addText(text, {
    x,
    y,
    w,
    h,
    margin: opts.margin ?? 0,
    fontFace: opts.fontFace || 'Aptos',
    fontSize: opts.fontSize || 14,
    bold: opts.bold || false,
    color: opts.color || C.ink,
    align: opts.align || 'left',
    valign: opts.valign || 'top',
    breakLine: false,
    fit: 'shrink',
  });
}

function addSlide(title, kicker) {
  slideNo += 1;
  const s = pptx.addSlide();
  s.background = { color: C.white };
  s.addShape(pptx.ShapeType.rect, { x: 0, y: 0, w: 13.333, h: 0.55, fill: { color: C.paper }, line: { color: C.paper } });
  s.addShape(pptx.ShapeType.line, { x: 0, y: 0.55, w: 13.333, h: 0, line: { color: C.rule, width: 0.6 } });
  addText(s, kicker, 0.45, 0.13, 5.2, 0.18, { fontSize: 7, bold: true, color: C.copper });
  addText(s, title, 0.45, 0.62, 11.0, 0.42, { fontFace: 'Aptos Display', fontSize: 20, bold: true, color: C.deep });
  addText(s, `Actividad 2  ·  Sistemas Roboticos Moviles  ·  CoppeliaSim/Lua`, 0.45, 7.22, 4.5, 0.12, { fontSize: 6, color: C.muted });
  addText(s, `${slideNo}/15`, 12.42, 7.20, 0.45, 0.15, { fontSize: 6, color: C.muted, align: 'right' });
  return s;
}

function rect(slide, x, y, w, h, color, lineColor = color, transparency = 0) {
  slide.addShape(pptx.ShapeType.rect, {
    x, y, w, h,
    fill: { color, transparency },
    line: { color: lineColor, width: 0.7 },
  });
}

function circle(slide, x, y, d, color, lineColor = color, transparency = 0) {
  slide.addShape(pptx.ShapeType.ellipse, {
    x, y, w: d, h: d,
    fill: { color, transparency },
    line: { color: lineColor, width: 0.7 },
  });
}

function line(slide, x1, y1, x2, y2, color = C.deep, width = 1, arrow = false) {
  slide.addShape(pptx.ShapeType.line, {
    x: x1,
    y: y1,
    w: x2 - x1,
    h: y2 - y1,
    line: {
      color,
      width,
      endArrowType: arrow ? 'triangle' : 'none',
    },
  });
}

function metric(slide, value, label, x, y, color) {
  addText(slide, value, x, y, 1.8, 0.38, { fontFace: 'Aptos Display', fontSize: 24, bold: true, color });
  addText(slide, label, x, y + 0.42, 1.8, 0.28, { fontSize: 7, color: C.muted });
}

function metric2(slide, value, label, x, y, color) {
  addText(slide, value, x, y, 2.0, 0.42, { fontFace: 'Aptos Display', fontSize: 26, bold: true, color });
  addText(slide, label, x, y + 0.44, 2.0, 0.26, { fontSize: 8, color: C.muted });
}

function tag(slide, text, x, y, color, w = 1.65) {
  rect(slide, x, y, w, 0.32, tint(color), color);
  addText(slide, text, x + 0.08, y + 0.08, w - 0.16, 0.12, { fontSize: 6.2, bold: true, color, align: 'center' });
}

function tint(color) {
  const map = {
    [C.teal]: 'E6F4F4',
    [C.orange]: 'FDEDE8',
    [C.green]: 'EAF5EE',
    [C.blue]: 'EAF1FA',
    [C.red]: 'FBEAEA',
    [C.amber]: 'FBF2DF',
    [C.copper]: 'F9ECE8',
    [C.muted]: 'EEF1F4',
  };
  return map[color] || C.paper;
}

function bullet(slide, text, x, y, color = C.copper, w = 4.8) {
  circle(slide, x, y + 0.04, 0.07, color, color);
  addText(slide, text, x + 0.18, y, w, 0.28, { fontSize: 9, color: C.ink });
}

function grid(slide, x, y, w, h, cols = 10, rows = 8) {
  rect(slide, x, y, w, h, C.paper, C.rule);
  for (let i = 1; i < cols; i++) line(slide, x + (w * i) / cols, y + 0.15, x + (w * i) / cols, y + h - 0.15, C.rule, 0.25);
  for (let j = 1; j < rows; j++) line(slide, x + 0.15, y + (h * j) / rows, x + w - 0.15, y + (h * j) / rows, C.rule, 0.25);
}

function robot(slide, x, y, scale = 1, color = C.teal) {
  rect(slide, x - 0.23 * scale, y - 0.14 * scale, 0.46 * scale, 0.28 * scale, tint(color), color);
  rect(slide, x - 0.12 * scale, y - 0.06 * scale, 0.24 * scale, 0.12 * scale, 'FFFFFF', color);
  line(slide, x + 0.23 * scale, y, x + 0.42 * scale, y, color, 1.1, true);
  circle(slide, x - 0.40 * scale, y - 0.40 * scale, 0.80 * scale, 'FFFFFF', color);
  circle(slide, x - 0.63 * scale, y - 0.63 * scale, 1.26 * scale, 'FFFFFF', color);
}

function card(slide, x, y, w, h, title, body, color) {
  rect(slide, x, y, w, h, tint(color), color);
  addText(slide, title, x + 0.20, y + 0.20, w - 0.40, 0.32, { fontSize: 11, bold: true, color });
  addText(slide, body, x + 0.20, y + 0.72, w - 0.40, h - 0.88, { fontSize: 8.4, color: C.ink });
}

function cover() {
  const s = pptx.addSlide();
  slideNo += 1;
  s.background = { color: C.deep };
  rect(s, 0, 0, 13.333, 7.5, C.deep, C.deep);
  for (let x = 0; x <= 13.3; x += 0.45) line(s, x, 0, x, 7.5, '17324C', 0.25);
  for (let y = 0; y <= 7.5; y += 0.45) line(s, 0, y, 13.333, y, '17324C', 0.25);
  addText(s, 'UNIVERSIDAD INTERNACIONAL DE VALENCIA', 0.62, 0.55, 4.0, 0.18, { fontSize: 7, bold: true, color: C.orange });
  addText(s, 'Pioneer P3DX en\nCoppeliaSim/Lua', 0.62, 1.44, 5.8, 1.25, { fontFace: 'Aptos Display', fontSize: 34, bold: true, color: C.white });
  addText(s, 'Campos potenciales, anticolision, integracion en celda, bateria simulada y extension multi-robot con A* cooperativo.', 0.65, 3.02, 5.35, 0.62, { fontSize: 12, color: 'D9E2EA' });
  addText(s, 'Autor: Jorge Luis Mayorga Taborda\nProfesor: Jose I. Iniguez\nEntrega: 26 de mayo de 2026', 0.65, 5.55, 4.3, 0.58, { fontSize: 8, color: 'C7D3DF' });
  grid(s, 7.05, 1.28, 5.1, 4.86, 8, 7);
  rect(s, 7.55, 4.52, 1.10, 0.82, 'EAF1FA', C.rule);
  rect(s, 10.06, 4.55, 1.50, 0.88, 'FBF2DF', C.rule);
  rect(s, 10.30, 1.72, 1.25, 0.62, 'EAF5EE', C.rule);
  robot(s, 7.72, 2.18, 0.86, C.teal);
  line(s, 7.72, 2.18, 8.85, 2.18, C.orange, 2, true);
  line(s, 8.85, 2.18, 8.85, 3.65, C.orange, 2, true);
  line(s, 8.85, 3.65, 11.20, 3.65, C.orange, 2, true);
  line(s, 11.20, 3.65, 11.20, 5.05, C.orange, 2, true);
  addText(s, 'celda robotizada', 7.90, 4.08, 1.20, 0.18, { fontSize: 6, bold: true, color: C.deep });
  addText(s, 'objetivo', 10.72, 4.18, 0.70, 0.16, { fontSize: 6, color: C.muted });
}

function slideGuide() {
  const s = addSlide('Que tiene que demostrar la entrega', 'lectura de la guia');
  addText(s, 'La presentacion separa lo obligatorio de la mejora profesional para que la defensa sea facil de corregir.', 0.58, 1.25, 10.8, 0.26, { fontSize: 10, color: C.muted });
  card(s, 0.85, 2.25, 3.45, 3.05, '1  Pioneer programado', 'Script Lua embebido, lectura de objetivo, velocidad de ruedas y telemetria.', C.teal);
  card(s, 4.95, 2.25, 3.45, 3.05, '2  Campos potenciales', 'Atraccion a mannequin, repulsion de obstaculos y saturaciones para evitar oscilacion.', C.orange);
  card(s, 9.05, 2.25, 3.45, 3.05, '3  Celda y validacion', 'Integracion industrial, escenarios S1-S8, bateria y evidencia JSON reproducible.', C.green);
  addText(s, 'No se vende como robot industrial real: se defiende como simulacion rigurosa y trazable del temario.', 0.85, 6.28, 11.6, 0.24, { fontSize: 9, bold: true, color: C.copper });
}

function slidePipeline() {
  const s = addSlide('De dos escenas base a una demo defendible', 'pipeline de trabajo');
  const items = [
    ['Escenas base', 'Actividad2_1 y Actividad2_2', C.blue],
    ['Generador Python', 'celda, rutas y overlays', C.teal],
    ['Scripts Lua', 'Pioneer, eventos y flota A*', C.orange],
    ['Evidencia final', 'PDF, PPTX, JSON y .ttt', C.green],
  ];
  items.forEach(([t, b, c], i) => {
    const x = 0.85 + i * 3.05;
    card(s, x, 1.65, 2.25, 1.20, t, b, c);
    if (i < 3) line(s, x + 2.35, 2.24, x + 2.78, 2.24, C.copper, 1.2, true);
  });
  addText(s, 'Criterios de calidad', 0.85, 3.85, 3.5, 0.30, { fontSize: 12, bold: true, color: C.deep });
  bullet(s, 'El robot llega a objetivo y publica estado ARRIVED.', 0.90, 4.45, C.green, 7.5);
  bullet(s, 'Los obstaculos activan reduccion de velocidad y recuperacion.', 0.90, 4.90, C.orange, 7.5);
  bullet(s, 'La celda tiene HMI, estacion de carga, carriles y zonas de seguridad.', 0.90, 5.35, C.teal, 7.5);
  bullet(s, 'La flota auxiliar resuelve rutas A* y recarga.', 0.90, 5.80, C.blue, 7.5);
  metric2(s, '22', 'sensores activos', 10.80, 4.15, C.teal);
  metric2(s, '8', 'escenarios S1-S8', 10.80, 5.05, C.orange);
  metric2(s, '3/3', 'AMR recargados', 10.80, 5.95, C.green);
}

function slideCell() {
  const s = addSlide('Celda CoppeliaSim: geometria y mision', 'plano de operacion');
  grid(s, 0.70, 1.35, 7.05, 5.25, 11, 8);
  rect(s, 1.12, 4.85, 1.18, 0.74, 'EAF1FA', C.rule);
  addText(s, 'transportador', 1.12, 4.55, 1.30, 0.14, { fontSize: 6, bold: true, color: C.blue });
  rect(s, 3.70, 4.70, 1.80, 0.84, 'FBF2DF', C.rule);
  addText(s, 'zona robotizada', 3.95, 4.40, 1.4, 0.14, { fontSize: 6, bold: true, color: C.amber });
  rect(s, 6.05, 1.78, 1.10, 0.56, 'EAF5EE', C.rule);
  addText(s, 'carga', 6.35, 1.50, 0.6, 0.14, { fontSize: 6, bold: true, color: C.green });
  rect(s, 3.00, 3.18, 0.70, 0.55, 'FBEAEA', C.rule);
  rect(s, 4.95, 3.10, 0.65, 0.56, 'FBEAEA', C.rule);
  robot(s, 1.05, 2.08, 0.75, C.teal);
  line(s, 1.05, 2.08, 2.35, 2.08, C.orange, 2, true);
  line(s, 2.35, 2.08, 2.35, 3.70, C.orange, 2, true);
  line(s, 2.35, 3.70, 4.55, 3.70, C.orange, 2, true);
  line(s, 4.55, 3.70, 4.55, 5.05, C.orange, 2, true);
  line(s, 4.55, 5.05, 6.65, 5.05, C.orange, 1.2, true);
  line(s, 6.65, 5.05, 6.65, 2.05, C.orange, 1.2, true);
  addText(s, 'Que ve el profesor', 8.45, 1.50, 3.2, 0.26, { fontSize: 12, bold: true, color: C.deep });
  bullet(s, 'Ruta nominal y retorno a carga.', 8.50, 2.13, C.teal, 4.2);
  bullet(s, 'Zonas de seguridad y carriles.', 8.50, 2.60, C.orange, 4.2);
  bullet(s, 'Obstaculos moviles y pasillo estrecho.', 8.50, 3.07, C.red, 4.2);
  bullet(s, 'HMI con estado, bateria y fallo sensorial.', 8.50, 3.54, C.blue, 4.2);
  bullet(s, 'Camaras nombradas para inspeccion rapida.', 8.50, 4.01, C.green, 4.2);
}

function slideModel() {
  const s = addSlide('Modelo cinematico: Pioneer diferencial', 'cinematica');
  rect(s, 0.85, 1.60, 5.35, 4.65, C.paper, C.rule);
  rect(s, 2.55, 3.30, 1.20, 0.72, 'FFFFFF', C.deep);
  rect(s, 2.84, 3.47, 0.62, 0.32, 'EAF1FA', C.deep);
  line(s, 2.39, 3.30, 2.39, 4.02, C.deep, 1.3);
  line(s, 3.91, 3.30, 3.91, 4.02, C.deep, 1.3);
  line(s, 3.15, 3.66, 4.42, 3.66, C.teal, 1.4, true);
  line(s, 3.15, 3.66, 3.82, 3.03, C.orange, 1.1, true);
  addText(s, 'base diferencial', 1.25, 2.05, 1.6, 0.18, { fontSize: 8, bold: true, color: C.deep });
  addText(s, 'distancia entre ruedas L', 2.35, 4.35, 2.0, 0.18, { fontSize: 7, color: C.muted, align: 'center' });
  addText(s, 'v_L = v - L/2 omega', 7.35, 2.25, 3.6, 0.42, { fontFace: 'Cambria Math', fontSize: 20, bold: true, color: C.deep });
  addText(s, 'v_R = v + L/2 omega', 7.35, 3.20, 3.6, 0.42, { fontFace: 'Cambria Math', fontSize: 20, bold: true, color: C.deep });
  addText(s, 'Implicacion de control', 7.35, 4.35, 3.0, 0.22, { fontSize: 12, bold: true, color: C.copper });
  addText(s, 'El controlador calcula velocidad lineal y angular, limita ambas magnitudes y las traduce a comandos de rueda para evitar giros bruscos en la celda.', 7.35, 4.85, 4.7, 0.72, { fontSize: 9, color: C.ink });
}

function slidePotential() {
  const s = addSlide('Campos potenciales: atraccion y repulsion', 'navegacion local');
  grid(s, 0.85, 1.22, 7.10, 5.45, 11, 9);
  robot(s, 1.65, 5.55, 0.75, C.teal);
  circle(s, 6.35, 2.10, 0.18, C.green, C.green);
  addText(s, 'objetivo', 6.08, 1.72, 0.8, 0.12, { fontSize: 6, bold: true, color: C.green });
  circle(s, 3.20, 4.35, 0.52, 'FBEAEA', C.red);
  circle(s, 4.55, 3.15, 0.46, 'FBEAEA', C.red);
  line(s, 1.65, 5.55, 6.20, 2.22, C.green, 1.5, true);
  line(s, 3.20, 4.35, 2.35, 4.85, C.red, 1.2, true);
  line(s, 4.55, 3.15, 3.75, 3.65, C.red, 1.2, true);
  line(s, 1.65, 5.55, 2.55, 4.62, C.orange, 1.8, true);
  line(s, 2.55, 4.62, 4.65, 3.85, C.orange, 1.8, true);
  line(s, 4.65, 3.85, 6.20, 2.22, C.orange, 1.8, true);
  addText(s, 'Ley usada', 8.72, 1.50, 2.0, 0.24, { fontSize: 12, bold: true, color: C.deep });
  addText(s, 'F = F_att + Σ F_rep,i', 8.72, 2.10, 3.2, 0.35, { fontFace: 'Cambria Math', fontSize: 16, bold: true, color: C.deep });
  addText(s, 'Cada ciclo recalcula rumbo desde objetivo, sensores y saturacion de v, omega. No es un camino dibujado a mano.', 8.72, 2.78, 3.7, 0.68, { fontSize: 9, color: C.ink });
  tag(s, 'saturacion', 8.72, 4.25, C.orange, 1.55);
  tag(s, 'tolerancia', 8.72, 4.75, C.green, 1.55);
  tag(s, 'recuperacion', 8.72, 5.25, C.red, 1.55);
}

function slideCollision() {
  const s = addSlide('Anticolision: sensores y zonas de velocidad', 'seguridad reactiva');
  rect(s, 0.85, 1.28, 6.55, 5.45, C.paper, C.rule);
  robot(s, 3.72, 4.10, 0.78, C.teal);
  [0, 25, 50, -25, -50, 90, -90, 180].forEach((deg) => {
    const r = 2.0;
    const rad = (Math.PI * deg) / 180;
    const x2 = 3.72 + Math.cos(rad) * r;
    const y2 = 4.10 - Math.sin(rad) * r;
    line(s, 3.72, 4.10, x2, y2, deg === 0 ? C.red : deg < 0 ? C.orange : C.blue, 0.9, true);
  });
  circle(s, 3.72 - 0.74, 4.10 - 0.74, 1.48, 'FFFFFF', C.red);
  circle(s, 3.72 - 1.18, 4.10 - 1.18, 2.36, 'FFFFFF', C.orange);
  circle(s, 3.72 - 1.62, 4.10 - 1.62, 3.24, 'FFFFFF', C.green);
  rect(s, 5.50, 3.78, 0.58, 0.56, 'FBEAEA', C.rule);
  addText(s, 'Implementado', 8.10, 1.52, 2.8, 0.24, { fontSize: 12, bold: true, color: C.deep });
  bullet(s, '16 ultrasonidos Pioneer + 6 sensores virtuales.', 8.15, 2.12, C.teal, 4.2);
  bullet(s, 'Ruido determinista y fallo intermitente.', 8.15, 2.62, C.orange, 4.2);
  bullet(s, 'Distancia minima validada: 0,191 m.', 8.15, 3.12, C.red, 4.2);
  bullet(s, 'Estado RECOVERY si el riesgo permanece alto.', 8.15, 3.62, C.blue, 4.2);
  addText(s, 'La seguridad se demuestra como comportamiento de simulacion: reduccion de velocidad, evasion local y parada controlada.', 8.15, 5.10, 4.2, 0.58, { fontSize: 8.6, color: C.muted });
}

function slideFSM() {
  const s = addSlide('Maquina de estados del Pioneer', 'arquitectura de control');
  const states = [
    [1.10, 2.35, 'ROUTE', C.teal],
    [3.78, 2.35, 'AVOIDING', C.orange],
    [6.72, 2.35, 'RECOVERY', C.red],
    [3.78, 4.32, 'HOLD', C.blue],
    [9.72, 2.35, 'ARRIVED', C.green],
  ];
  states.forEach(([x, y, t, c]) => card(s, x, y, 1.82, 0.82, t, '', c));
  line(s, 2.92, 2.76, 3.74, 2.76, C.deep, 1.0, true);
  line(s, 5.60, 2.76, 6.68, 2.76, C.deep, 1.0, true);
  line(s, 8.54, 2.76, 9.68, 2.76, C.deep, 1.0, true);
  line(s, 4.69, 3.17, 4.69, 4.28, C.blue, 1.0, true);
  line(s, 4.69, 4.32, 4.69, 5.22, C.green, 1.0, true);
  line(s, 4.69, 5.22, 10.63, 5.22, C.green, 1.0, true);
  line(s, 10.63, 5.22, 10.63, 3.17, C.green, 1.0, true);
  addText(s, 'La FSM evita una demo opaca: cada transicion puede defenderse con estados internos, telemetria y eventos visibles en CoppeliaSim.', 1.10, 6.12, 10.8, 0.32, { fontSize: 9, color: C.ink });
}

function slideIntegration() {
  const s = addSlide('Integracion en celda: modulos y senales', 'sistema completo');
  const mods = [
    ['Pioneer Controller', 'FSM, campos, ruedas y bateria', C.teal],
    ['Scenario Manager', 'S1-S8, obstaculos y parada', C.orange],
    ['MultiRobot A* Manager', 'rutas, reservas y carga', C.blue],
    ['Demo Overlay', 'labels, camaras y lectura rapida', C.green],
  ];
  mods.forEach(([t, b, c], i) => {
    const x = 0.78 + i * 3.10;
    card(s, x, 2.20, 2.45, 1.25, t, b, c);
    if (i < 3) line(s, x + 2.52, 2.82, x + 2.94, 2.82, C.copper, 1.0, true);
  });
  addText(s, 'Senales de coordinacion', 0.82, 4.48, 3.2, 0.24, { fontSize: 12, bold: true, color: C.deep });
  tag(s, 'missionReady', 0.82, 5.12, C.teal, 1.55);
  tag(s, 'pioneerState', 2.72, 5.12, C.orange, 1.55);
  tag(s, 'pioneerBatteryLevel', 4.62, 5.12, C.blue, 1.92);
  tag(s, 'fleetAllComplete', 6.90, 5.12, C.green, 1.75);
  tag(s, 'demoOverlayLabels', 9.02, 5.12, C.copper, 1.85);
  addText(s, 'La defensa no depende de "mirar si se mueve": los modulos publican estados, eventos y metricas que quedan registrados en JSON.', 0.82, 6.22, 11.4, 0.28, { fontSize: 9, color: C.ink });
}

function slideScenarios() {
  const s = addSlide('Escenarios S1-S8: pruebas con degradacion', 'validacion secuencial');
  line(s, 0.98, 3.28, 12.45, 3.28, C.rule, 1.0);
  const sc = [
    ['S1', 'ruta nominal', C.teal],
    ['S2', 'pallet movil', C.orange],
    ['S3', 'parada', C.blue],
    ['S4', 'objetivo movil', C.green],
    ['S5', 'pasillo estrecho', C.amber],
    ['S6', 'fallo sensor', C.red],
    ['S7', 'bateria baja', C.blue],
    ['S8', 'llegada', C.green],
  ];
  sc.forEach(([n, t, c], i) => {
    const x = 0.98 + i * 1.64;
    circle(s, x - 0.15, 3.13, 0.30, tint(c), c);
    addText(s, n, x - 0.08, 3.22, 0.18, 0.08, { fontSize: 5.5, bold: true, color: c, align: 'center' });
    addText(s, t, x - 0.55, 3.82, 1.05, 0.26, { fontSize: 7, color: C.ink, align: 'center' });
  });
  addText(s, 'La demo cubre condiciones normales, interaccion con celda y fallos.', 0.98, 1.55, 8.0, 0.22, { fontSize: 11, bold: true, color: C.deep });
  addText(s, 'El profesor puede pulsar Play y observar una secuencia ordenada, no un recorrido idealizado.', 0.98, 1.97, 9.5, 0.22, { fontSize: 8.8, color: C.muted });
  metric2(s, '4,328 m', 'distancia inicial', 1.02, 5.52, C.teal);
  metric2(s, '0,739 m', 'distancia final', 3.92, 5.52, C.green);
  metric2(s, 'ARRIVED', 'estado final', 6.82, 5.52, C.orange);
  metric2(s, '0,191 m', 'min. obstaculo', 9.72, 5.52, C.red);
}

function slideFleet() {
  const s = addSlide('Extension multi-robot: A* cooperativo', 'flota auxiliar');
  grid(s, 0.85, 1.32, 7.05, 5.15, 10, 8);
  robot(s, 1.45, 5.55, 0.42, C.teal);
  robot(s, 1.45, 2.02, 0.42, C.orange);
  robot(s, 6.95, 5.55, 0.42, C.blue);
  line(s, 1.45, 5.55, 3.05, 5.55, C.teal, 1.5, true);
  line(s, 3.05, 5.55, 3.05, 3.66, C.teal, 1.5, true);
  line(s, 3.05, 3.66, 6.60, 3.66, C.teal, 1.5, true);
  line(s, 1.45, 2.02, 3.65, 2.02, C.orange, 1.5, true);
  line(s, 3.65, 2.02, 3.65, 3.02, C.orange, 1.5, true);
  line(s, 3.65, 3.02, 6.60, 3.02, C.orange, 1.5, true);
  line(s, 6.95, 5.55, 5.32, 5.55, C.blue, 1.5, true);
  line(s, 5.32, 5.55, 5.32, 4.52, C.blue, 1.5, true);
  line(s, 5.32, 4.52, 2.50, 4.52, C.blue, 1.5, true);
  rect(s, 3.10, 3.16, 0.50, 0.45, 'FBEAEA', C.rule);
  rect(s, 5.02, 3.78, 0.50, 0.45, 'FBEAEA', C.rule);
  addText(s, 'Resultado validado', 8.70, 1.60, 2.8, 0.24, { fontSize: 12, bold: true, color: C.deep });
  metric2(s, '16', 'planes A* generados', 8.70, 2.18, C.blue);
  metric2(s, '8', 'conflictos evitados', 8.70, 3.08, C.orange);
  metric2(s, '4', 'eventos de carga', 8.70, 3.98, C.teal);
  metric2(s, '3/3', 'robots READY', 8.70, 4.88, C.green);
}

function slideValidation() {
  const s = addSlide('Validacion: indicadores que sostienen la defensa', 'evidencia cuantitativa');
  rect(s, 0.90, 1.35, 11.55, 4.92, C.paper, C.rule);
  const metrics = [
    ['4.328', 'inicial', C.muted],
    ['0.739', 'final', C.green],
    ['22', 'sensores', C.teal],
    ['8', 'escenarios', C.orange],
    ['3', 'AMR READY', C.blue],
    ['0.191', 'min. obstaculo', C.red],
  ];
  metrics.forEach(([v, l, c], i) => metric2(s, v, l, 1.25 + i * 1.82, 2.05, c));
  line(s, 1.20, 3.55, 11.80, 3.55, C.rule, 0.8);
  bullet(s, 'Pioneer reduce distancia y termina en ARRIVED.', 1.25, 4.12, C.green, 8.8);
  bullet(s, 'Sensores cubren proximidad, ruido y fallo intermitente.', 1.25, 4.62, C.teal, 8.8);
  bullet(s, 'La flota auxiliar completa rutas y recarga.', 1.25, 5.12, C.blue, 8.8);
  bullet(s, 'El JSON permite reproducir la evidencia sin depender de una captura.', 1.25, 5.62, C.orange, 8.8);
}

function slideDeliverables() {
  const s = addSlide('Entregables y como defenderlos en 3 minutos', 'guion de presentacion');
  addText(s, 'Archivos principales', 0.85, 1.70, 3.0, 0.22, { fontSize: 12, bold: true, color: C.deep });
  const files = [
    ['Actividad2_Pioneer_Profesional_10_10.ttt', 'escena final para abrir y ejecutar en CoppeliaSim', C.teal],
    ['Actividad2_Pioneer_Profesional_10_10_validation.json', 'evidencia reproducible de resultados', C.orange],
    ['main.pdf', 'informe tecnico con trazabilidad y validacion', C.blue],
    ['Actividad2_Pioneer_CoppeliaSim.pptx', 'presentacion editable profesional', C.green],
  ];
  files.forEach(([name, desc, c], i) => {
    const y = 2.32 + i * 0.68;
    rect(s, 0.85, y, 5.95, 0.46, tint(c), tint(c));
    addText(s, name, 1.05, y + 0.08, 5.4, 0.13, { fontSize: 6.7, bold: true, color: c });
    addText(s, desc, 1.05, y + 0.25, 5.4, 0.10, { fontSize: 5.4, color: C.muted });
  });
  addText(s, 'Orden recomendado', 8.05, 1.70, 3.0, 0.22, { fontSize: 12, bold: true, color: C.deep });
  const order = [
    'Explicar guia: Pioneer, campos potenciales, anticolision.',
    'Mostrar celda: ruta, sensores, HMI y bateria.',
    'Ejecutar o ensenar validacion: S1-S8 y ARRIVED.',
    'Cerrar con extension A*: flota, reservas y carga.',
  ];
  order.forEach((txt, i) => {
    const y = 2.34 + i * 0.75;
    circle(s, 8.05, y + 0.02, 0.20, C.copper, C.copper);
    addText(s, String(i + 1), 8.10, y + 0.08, 0.06, 0.06, { fontSize: 5.2, bold: true, color: C.white, align: 'center' });
    addText(s, txt, 8.42, y - 0.04, 4.0, 0.22, { fontSize: 8.2, color: C.ink });
  });
}

function slideLimits() {
  const s = addSlide('Limitaciones reconocidas y mitigacion', 'criterio tecnico');
  card(s, 0.88, 2.18, 3.35, 3.45, 'Minimos locales', 'Riesgo: campo potencial puede oscilar o bloquearse.\n\nMitigacion: FSM RECOVERY y ruta por waypoints.', C.orange);
  card(s, 4.98, 2.18, 3.35, 3.45, 'Sensor imperfecto', 'Riesgo: ruido o fallo intermitente en proximidad.\n\nMitigacion: filtro, degradacion simulada y margen de seguridad.', C.red);
  card(s, 9.08, 2.18, 3.35, 3.45, 'Simulacion vs planta', 'Riesgo: la escena no equivale a certificacion industrial.\n\nMitigacion: validar primero en CoppeliaSim y documentar supuestos.', C.blue);
}

function slideConclusion() {
  const s = addSlide('Conclusion: una entrega defendible, no decorativa', 'cierre');
  addText(s, 'La mejora visual sirve a la evaluacion: cada diagrama apunta a un requisito, un modulo o una prueba.', 0.75, 1.30, 6.4, 1.02, { fontFace: 'Aptos Display', fontSize: 25, bold: true, color: C.deep });
  addText(s, 'La escena final muestra el Pioneer moviendose con campos potenciales, evitando obstaculos, publicando estado, operando dentro de una celda y extendiendose a una flota auxiliar con A* cooperativo.', 0.78, 3.10, 6.2, 0.68, { fontSize: 10, color: C.ink });
  line(s, 0.78, 5.85, 6.65, 5.85, C.copper, 1.2);
  addText(s, 'Mensaje de defensa: obligatorio resuelto, mejora profesional justificada y evidencia reproducible.', 0.80, 6.12, 6.8, 0.18, { fontSize: 8.5, bold: true, color: C.copper });
  rect(s, 8.58, 1.78, 3.75, 4.05, C.paper, C.rule);
  tag(s, 'JSON passed', 9.05, 2.22, C.green, 1.62);
  tag(s, '22 sensores', 9.05, 2.72, C.teal, 1.62);
  tag(s, 'S1-S8', 9.05, 3.22, C.orange, 1.62);
  robot(s, 9.35, 5.10, 0.64, C.teal);
  line(s, 9.35, 5.10, 10.52, 5.10, C.orange, 1.6, true);
  line(s, 10.52, 5.10, 10.52, 3.70, C.orange, 1.6, true);
  line(s, 10.52, 3.70, 11.55, 3.70, C.orange, 1.6, true);
  circle(s, 11.47, 3.62, 0.16, C.green, C.green);
  addText(s, 'ARRIVED', 11.18, 3.35, 0.7, 0.12, { fontSize: 6, bold: true, color: C.green });
}

cover();
slideGuide();
slidePipeline();
slideCell();
slideModel();
slidePotential();
slideCollision();
slideFSM();
slideIntegration();
slideScenarios();
slideFleet();
slideValidation();
slideDeliverables();
slideLimits();
slideConclusion();

pptx.writeFile({ fileName: out });

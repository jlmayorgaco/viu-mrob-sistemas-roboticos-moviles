const fs = require("fs");
const path = require("path");
const { createRequire } = require("module");

function loadPptxGen() {
  try {
    return require("pptxgenjs");
  } catch (err) {
    const bundled = path.join(
      process.env.USERPROFILE || "",
      ".cache",
      "codex-runtimes",
      "codex-primary-runtime",
      "dependencies",
      "node",
      "node_modules",
      "pptxgenjs",
      "package.json"
    );
    if (!fs.existsSync(bundled)) {
      throw new Error("pptxgenjs is required. Run `npm install pptxgenjs` or set NODE_PATH to a node_modules folder that contains it.");
    }
    try {
      return createRequire(bundled)("pptxgenjs");
    } catch (bundledErr) {
      throw new Error("pptxgenjs is present but its dependencies are unavailable. Run `npm install pptxgenjs` or set NODE_PATH to a complete node_modules folder.");
    }
  }
}

const pptxgen = loadPptxGen();
const pptx = new pptxgen();

pptx.author = "Jorge Luis Mayorga Taborda";
pptx.company = "Lunabotics";
pptx.subject = "Sistemas Robóticos Móviles";
pptx.title = "Actividad 1 - Sistema AMR-FOD-Kitting";
pptx.lang = "es-ES";
pptx.theme = {
  headFontFace: "Aptos Display",
  bodyFontFace: "Aptos",
  lang: "es-ES",
};
pptx.layout = "LAYOUT_WIDE";
pptx.defineLayout({ name: "LUNABOTICS_WIDE", width: 13.333, height: 7.5 });
pptx.layout = "LUNABOTICS_WIDE";

const C = {
  navy: "102033",
  ink: "1B2430",
  muted: "5D6B7A",
  pale: "F4F8FB",
  line: "D6DEE8",
  teal: "1F7A8C",
  cyan: "2DB7E5",
  green: "2A9D8F",
  amber: "F4A261",
  red: "B91C1C",
  violet: "6D5BD0",
  white: "FFFFFF",
};

const TEXT_FIXES = [
  [/\bRoboticos\b/g, "Robóticos"],
  [/\broboticos\b/g, "robóticos"],
  [/\bMoviles\b/g, "Móviles"],
  [/\bmoviles\b/g, "móviles"],
  [/\bTecnica\b/g, "Técnica"],
  [/\bTECNICA\b/g, "TÉCNICA"],
  [/\btecnica\b/g, "técnica"],
  [/\btecnico\b/g, "técnico"],
  [/\btecnicos\b/g, "técnicos"],
  [/\bAutomatizacion\b/g, "Automatización"],
  [/\bautomatizacion\b/g, "automatización"],
  [/\bintralogistica\b/g, "intralogística"],
  [/\blogistica\b/g, "logística"],
  [/\blogistico\b/g, "logístico"],
  [/\blinea\b/g, "línea"],
  [/\bseccion\b/g, "sección"],
  [/\bSeccion\b/g, "Sección"],
  [/\bsolucion\b/g, "solución"],
  [/\bSolucion\b/g, "Solución"],
  [/\bconfirmacion\b/g, "confirmación"],
  [/\baeronautico\b/g, "aeronáutico"],
  [/\bfabricacion\b/g, "fabricación"],
  [/\bperdidas\b/g, "pérdidas"],
  [/\bperdida\b/g, "pérdida"],
  [/\bestacion\b/g, "estación"],
  [/\butiles\b/g, "útiles"],
  [/\binspeccion\b/g, "inspección"],
  [/\bdocumentacion\b/g, "documentación"],
  [/\bmision\b/g, "misión"],
  [/\bconversacion\b/g, "conversación"],
  [/\bsimulacion\b/g, "simulación"],
  [/\baceptacion\b/g, "aceptación"],
  [/\bconfiguracion\b/g, "configuración"],
  [/\bdecision\b/g, "decisión"],
  [/\breduccion\b/g, "reducción"],
  [/\bano\b/g, "año"],
  [/\banos\b/g, "años"],
  [/\bMas\b/g, "Más"],
  [/\bQue\b/g, "Qué"],
  [/\binformacion\b/g, "información"],
  [/\bexpansion\b/g, "expansión"],
  [/\boperacion\b/g, "operación"],
  [/\bvalidacion\b/g, "validación"],
  [/\bnavegacion\b/g, "navegación"],
  [/\bpercepcion\b/g, "percepción"],
  [/\blocalizacion\b/g, "localización"],
  [/\bplanificacion\b/g, "planificación"],
  [/\bintegracion\b/g, "integración"],
  [/\belectrico\b/g, "eléctrico"],
  [/\bmedicion\b/g, "medición"],
  [/\bcamara\b/g, "cámara"],
  [/\bimagenes\b/g, "imágenes"],
  [/\bautonomia\b/g, "autonomía"],
  [/\bmecanica\b/g, "mecánica"],
  [/\btecnologia\b/g, "tecnología"],
  [/\bdinamico\b/g, "dinámico"],
  [/\bteorica\b/g, "teórica"],
  [/\bpractico\b/g, "práctico"],
  [/\bacademica\b/g, "académica"],
  [/\bpublico\b/g, "público"],
  [/\bfisico\b/g, "físico"],
  [/\bfisicamente\b/g, "físicamente"],
  [/\bgarantia\b/g, "garantía"],
  [/\bCadiz\b/g, "Cádiz"],
  [/\bPerez\b/g, "Pérez"],
  [/\bdiseno\b/g, "diseño"],
  [/\bDiseno\b/g, "Diseño"],
  [/\bdano\b/g, "daño"],
];

function txt(value) {
  let out = String(value);
  for (const [pattern, replacement] of TEXT_FIXES) out = out.replace(pattern, replacement);
  return out;
}

function addFooter(slide, n) {
  slide.addText(txt("Actividad 1  •  Sistemas Roboticos Moviles"), {
    x: 0.55, y: 7.14, w: 4.8, h: 0.18, fontFace: "Aptos", fontSize: 6.2, color: C.muted,
  });
  slide.addText(txt("Lunabotics  •  Alestis Puerto Real  •  HTP A320"), {
    x: 8.35, y: 7.14, w: 4.35, h: 0.18, fontFace: "Aptos", fontSize: 6.2, color: C.muted, align: "right",
  });
  slide.addText(txt(`${n}/16`), {
    x: 12.45, y: 0.22, w: 0.35, h: 0.16, fontFace: "Aptos", fontSize: 6.2, color: C.muted, align: "right",
  });
}

function slideBase(title, subtitle, n, accent = C.teal) {
  const slide = pptx.addSlide();
  slide.background = { color: "F7F9FC" };
  slide.addShape(pptx.ShapeType.rect, { x: 0, y: 0, w: 13.333, h: 0.08, fill: { color: accent }, line: { color: accent } });
  slide.addText(txt(subtitle), { x: 0.55, y: 0.24, w: 5.8, h: 0.18, fontFace: "Aptos", fontSize: 6.7, bold: true, color: accent });
  slide.addText(txt(title), { x: 0.55, y: 0.47, w: 10.6, h: 0.42, fontFace: "Aptos Display", fontSize: 20, bold: true, color: C.ink, margin: 0 });
  addFooter(slide, n);
  return slide;
}

function card(slide, x, y, w, h, opts = {}) {
  slide.addShape(pptx.ShapeType.roundRect, {
    x, y, w, h,
    rectRadius: 0.08,
    fill: { color: opts.fill || C.white, transparency: opts.transparency || 0 },
    line: { color: opts.line || C.line, width: opts.width || 1 },
  });
}

function label(slide, text, x, y, w, h, opts = {}) {
  slide.addText(txt(text), {
    x, y, w, h,
    fontFace: opts.face || "Aptos",
    fontSize: opts.size || 9,
    bold: opts.bold || false,
    color: opts.color || C.ink,
    align: opts.align || "left",
    valign: opts.valign || "mid",
    margin: opts.margin ?? 0.03,
    breakLine: false,
    fit: "shrink",
  });
}

function metric(slide, value, caption, x, y, color = C.teal) {
  label(slide, value, x, y, 1.35, 0.36, { size: 17, bold: true, color });
  label(slide, caption, x, y + 0.42, 1.65, 0.45, { size: 6.5, color: C.muted });
}

function pill(slide, text, x, y, w, color) {
  card(slide, x, y, w, 0.42, { fill: "FFFFFF", line: color });
  label(slide, text, x + 0.08, y + 0.08, w - 0.16, 0.25, { size: 7.2, bold: true, color, align: "center" });
}

function arrow(slide, x1, y1, x2, y2, color = C.teal) {
  slide.addShape(pptx.ShapeType.line, {
    x: x1, y: y1, w: x2 - x1, h: y2 - y1,
    line: { color, width: 1.3, endArrowType: "triangle" },
  });
}

function drawAmr(slide, x, y, s = 1, accent = C.cyan) {
  card(slide, x, y, 1.42 * s, 0.92 * s, { fill: "E9F5FA", line: C.navy });
  slide.addShape(pptx.ShapeType.rect, { x: x + 0.12 * s, y: y + 0.13 * s, w: 0.14 * s, h: 0.66 * s, fill: { color: C.ink }, line: { color: C.ink } });
  slide.addShape(pptx.ShapeType.rect, { x: x + 1.16 * s, y: y + 0.13 * s, w: 0.14 * s, h: 0.66 * s, fill: { color: C.ink }, line: { color: C.ink } });
  slide.addShape(pptx.ShapeType.ellipse, { x: x + 0.48 * s, y: y + 0.22 * s, w: 0.48 * s, h: 0.48 * s, fill: { color: "BDEAF6" }, line: { color: accent, width: 1.1 } });
  slide.addShape(pptx.ShapeType.ellipse, { x: x + 0.63 * s, y: y + 0.37 * s, w: 0.18 * s, h: 0.18 * s, fill: { color: accent }, line: { color: accent } });
}

// 1
{
  const s = pptx.addSlide();
  s.background = { color: C.navy };
  s.addShape(pptx.ShapeType.rect, { x: 0, y: 0, w: 13.333, h: 7.5, fill: { color: C.navy }, line: { color: C.navy } });
  for (let i = 0; i < 12; i++) {
    s.addShape(pptx.ShapeType.line, { x: 4.4 + i * 0.55, y: 0, w: -1.9, h: 7.5, line: { color: "244761", transparency: 20, width: 0.6 } });
  }
  label(s, "LUNABOTICS  •  OFERTA TECNICA Y COMERCIAL", 0.55, 0.44, 4.4, 0.2, { size: 6.5, bold: true, color: C.cyan });
  label(s, "Sistema\nAMR-FOD-Kitting", 0.55, 0.8, 5.4, 0.92, { face: "Aptos Display", size: 26, bold: true, color: C.white });
  label(s, "Automatizacion intralogistica para la linea HTP A320 y seccion 19.1", 0.58, 2.05, 5.6, 0.5, { size: 12.5, bold: true, color: "DCEBFF" });
  label(s, "Actividad 1 • Sistemas Roboticos Moviles\nUniversidad Internacional de Valencia\nProfesor: Jose I. Iñiguez\nAutor: Jorge Luis Mayorga Taborda\nEntrega: 26 de mayo de 2026", 0.6, 2.82, 4.6, 1.1, { size: 7.1, color: "CFE1F3" });
  drawAmr(s, 7.3, 1.0, 1.75, C.cyan);
  s.addShape(pptx.ShapeType.rect, { x: 9.02, y: 4.62, w: 0.55, h: 0.82, fill: { color: C.amber }, line: { color: C.amber } });
  label(s, "19.1", 9.06, 4.91, 0.45, 0.18, { size: 6, bold: true, color: C.white, align: "center" });
}

// 2
{
  const s = slideBase("La propuesta no robotiza el HTP: ordena el flujo que lo rodea", "Tesis", 2, C.teal);
  label(s, "Menos espera.\nMas trazabilidad.\nMenos riesgo FOD.", 0.78, 1.48, 4.5, 1.3, { face: "Aptos Display", size: 20, bold: true, color: C.navy });
  label(s, "Automatiza transporte, confirmacion y evidencia.", 0.84, 3.02, 4.2, 0.28, { size: 9, color: C.muted });
  label(s, "No invade montaje aeronautico certificado.", 0.84, 3.38, 4.2, 0.28, { size: 9, bold: true, color: C.navy });
  s.addShape(pptx.ShapeType.line, { x: 7.15, y: 1.25, w: 0, h: 4.4, line: { color: C.teal, width: 1.2 } });
  metric(s, "40", "HTP/mes actuales aproximados", 7.85, 1.45, C.teal);
  metric(s, "80+", "HTP/mes como objetivo futuro", 7.85, 3.08, C.amber);
  metric(s, "0", "promesas de fabricacion robotizada directa", 7.85, 4.72, C.red);
}

// 3
{
  const s = slideBase("Las perdidas aparecen como microesperas, no como grandes paradas", "Problema", 3, C.amber);
  card(s, 1.05, 1.35, 5.0, 3.7, { fill: "EEF5F8", line: "E2EAF0" });
  s.addShape(pptx.ShapeType.line, { x: 1.75, y: 4.45, w: 0, h: -2.25, line: { color: C.red, width: 1.1, dash: "dash" } });
  s.addShape(pptx.ShapeType.line, { x: 1.75, y: 2.2, w: 2.4, h: 0, line: { color: C.red, width: 1.1, dash: "dash" } });
  s.addShape(pptx.ShapeType.line, { x: 4.15, y: 2.2, w: 0, h: 2.0, line: { color: C.red, width: 1.1, dash: "dash" } });
  s.addShape(pptx.ShapeType.line, { x: 4.15, y: 4.2, w: -1.8, h: 0, line: { color: C.red, width: 1.1, dash: "dash" } });
  drawAmr(s, 4.45, 1.5, 0.8, C.cyan);
  const issues = [
    ["Operarios abandonan estacion para buscar utiles o consumibles.", C.amber],
    ["Kits incompletos bloquean trabajo sin quedar siempre visibles como parada.", C.red],
    ["FOD exige inspeccion, disciplina y evidencia documentada.", C.violet],
    ["La trazabilidad fina se pierde si la entrega no queda ligada a mision.", C.teal],
  ];
  issues.forEach(([t, c], i) => {
    s.addShape(pptx.ShapeType.rect, { x: 7.05, y: 1.35 + i * 0.92, w: 0.13, h: 0.42, fill: { color: c }, line: { color: c } });
    label(s, t, 7.32, 1.28 + i * 0.92, 4.2, 0.48, { size: 8.4, color: C.ink });
  });
  label(s, "ruta manual repetida", 1.66, 5.26, 2.4, 0.18, { size: 6.4, color: C.red, bold: true });
}

// 4
{
  const s = slideBase("Flujo auxiliar en HTP A320 y seccion 19.1", "Contexto", 4, C.cyan);
  card(s, 0.85, 1.35, 11.75, 4.75, { fill: "EAF7FB", line: "9DDDEF" });
  label(s, "Estructura grande;\nsoporte logistico fino.", 1.2, 1.65, 4.3, 0.82, { face: "Aptos Display", size: 20, bold: true, color: C.navy });
  label(s, "El AMR no toca montaje certificado.", 1.22, 2.66, 4.25, 0.24, { size: 8.4, bold: true, color: C.navy });
  label(s, "Estabiliza entregas, retornos, FOD y trazabilidad.", 1.22, 2.98, 4.25, 0.24, { size: 8.1, color: C.muted });
  s.addShape(pptx.ShapeType.arc, { x: 1.1, y: 3.55, w: 5.5, h: 1.1, line: { color: C.navy, width: 1.5 }, adjustPoint: 0.3 });
  s.addShape(pptx.ShapeType.triangle, { x: 2.2, y: 3.15, w: 1.15, h: 0.85, rotate: 20, fill: { color: "6FB7C6" }, line: { color: "6FB7C6" } });
  s.addShape(pptx.ShapeType.rect, { x: 4.22, y: 3.46, w: 0.72, h: 1.05, fill: { color: "F3B37A" }, line: { color: "F3B37A" } });
  label(s, "19.1", 4.36, 3.88, 0.42, 0.14, { size: 6.1, bold: true, color: C.white, align: "center" });
  label(s, "Kit -> entrega -> registro -> retorno", 6.7, 1.85, 4.6, 0.34, { size: 14.5, bold: true, color: C.navy });
  pill(s, "Kit validado\nRFID/QR", 6.82, 3.35, 1.58, C.teal);
  arrow(s, 8.45, 3.56, 8.95, 3.56, C.cyan);
  pill(s, "Estacion HTP\nentrega trazada", 9.0, 3.35, 1.65, C.amber);
  arrow(s, 10.7, 3.56, 11.18, 3.56, C.cyan);
  pill(s, "Retorno + FOD\nevidencia digital", 11.22, 3.35, 1.25, C.green);
  label(s, "Lectura clave para la propuesta", 6.76, 4.58, 3.2, 0.2, { size: 7.4, bold: true, color: C.navy });
  label(s, "La seccion 19.1 depende de kits, herramientas y disciplina FOD.", 6.76, 4.88, 5.0, 0.24, { size: 6.9, color: C.ink });
  label(s, "El AMR reduce esperas y deja trazas; no fabrica el HTP.", 6.76, 5.16, 5.0, 0.24, { size: 6.9, color: C.ink });
}

// 5
{
  const s = slideBase("De conversacion simulada a requisitos trazables", "Entrevista", 5, C.violet);
  label(s, "ACTA TECNICA\nCarlos Perez\n+10 anos de experiencia en Alestis Puerto Real.", 0.75, 1.45, 1.85, 0.92, { size: 8.2, bold: true, color: C.violet });
  label(s, "El alcance correcto no es fabricar: es asegurar flujo, FOD y trazabilidad.", 0.78, 2.7, 2.15, 1.1, { face: "Aptos Display", size: 17.5, bold: true, color: C.navy });
  const rows = [
    ["01", "No fabricar ni montar el HTP.", "Automatizar solo flujo auxiliar certificado.", "Kitting, retorno de utiles y entregas trazadas.", C.violet],
    ["02", "Prioridades y pasillos cambian durante el turno.", "Evitar rutas rigidas y paradas manuales.", "AMR omnidireccional con SLAM y gestor de misiones.", C.teal],
    ["03", "FOD requiere evidencia revisable.", "Registrar rondas, imagenes y excepciones.", "RGB-D, RFID/QR y base de datos de eventos.", C.amber],
    ["04", "La expansion debe depender de datos del piloto.", "Medir seguridad, entrega y disponibilidad.", "KPIs antes de pasar de 1 a 7 y 17 robots.", C.green],
  ];
  label(s, "HALLAZGO DE PLANTA", 3.3, 1.28, 2.1, 0.2, { size: 6.8, bold: true, color: C.muted });
  label(s, "REQUISITO", 6.45, 1.28, 1.5, 0.2, { size: 6.8, bold: true, color: C.muted });
  label(s, "DISENO AMR-FOD-KITTING", 9.05, 1.28, 2.4, 0.2, { size: 6.8, bold: true, color: C.muted });
  rows.forEach(([n, h, r, d, col], i) => {
    const y = 1.65 + i * 0.85;
    card(s, 3.18, y, 9.1, 0.58, { fill: "FFFFFF", line: col });
    label(s, n, 3.35, y + 0.18, 0.28, 0.16, { size: 6.2, bold: true, color: col, align: "center" });
    label(s, h, 3.82, y + 0.11, 2.35, 0.34, { size: 6.4, bold: true, color: C.ink });
    label(s, r, 6.38, y + 0.10, 2.05, 0.36, { size: 6.2, color: C.ink });
    label(s, d, 8.85, y + 0.10, 3.0, 0.36, { size: 6.2, color: C.ink });
  });
}

// 6
{
  const s = slideBase("Criterios de aceptacion conectados con el temario", "Requisitos", 6, C.teal);
  metric(s, ">= 95 %", "misiones completadas", 0.88, 1.5, C.teal);
  metric(s, ">= 98 %", "registro completo", 3.05, 1.5, C.green);
  metric(s, ">= 90 %", "disponibilidad AMR", 5.25, 1.5, C.cyan);
  metric(s, "0", "incidentes con dano", 7.45, 1.5, C.red);
  s.addShape(pptx.ShapeType.line, { x: 0.85, y: 2.92, w: 10.9, h: 0, line: { color: C.line, width: 1 } });
  const blocks = [
    ["Locomocion", "base mecanum/sueca con movimiento lateral"],
    ["Percepcion", "LiDAR RGB-D RFID-QR y seguridad separada"],
    ["Navegacion", "SLAM A* Dijkstra y evitacion local"],
    ["Control", "motores electricos limites de velocidad y E-stop"],
  ];
  blocks.forEach(([a, b], i) => {
    label(s, a, 0.95 + i * 2.65, 3.55, 2.25, 0.22, { size: 8.4, bold: true, color: [C.teal, C.violet, C.cyan, C.red][i] });
    label(s, b, 0.95 + i * 2.65, 4.02, 2.2, 0.55, { size: 7.3, color: C.muted });
  });
}

// 7
{
  const s = slideBase("Matriz de decision, no seleccion por intuicion", "Alternativas", 7, C.cyan);
  label(s, "PUNTUACION PONDERADA SOBRE 5", 0.85, 1.10, 2.7, 0.17, { size: 6.5, bold: true, color: C.muted });
  label(s, "4,25", 0.85, 1.42, 1.25, 0.36, { size: 23, bold: true, color: C.green });
  label(s, "AMR omnidireccional\nRB-KAIROS/AGILOX-class", 2.55, 1.38, 3.7, 0.50, { size: 8.7, bold: true, color: C.navy });
  label(s, "Gana por maniobra en estacion y representabilidad en CoppeliaSim; no por ser la opcion mas barata.", 0.88, 2.08, 5.1, 0.42, { size: 6.4, color: C.muted });
  const rows = [
    ["AMR omnidireccional", "4,25", 3.85, C.green],
    ["AMR diferencial MiR/Omron", "3,85", 3.50, C.teal],
    ["AGV", "3,05", 2.78, C.amber],
    ["robot con patas", "1,85", 1.66, C.violet],
    ["dron", "1,75", 1.58, C.red],
    ["orugas", "1,45", 1.30, C.muted],
  ];
  rows.forEach(([name, score, w, col], i) => {
    const y = 2.88 + i * 0.46;
    label(s, name, 0.90, y, 2.55, 0.18, { size: 6.6, bold: true, color: C.ink });
    s.addShape(pptx.ShapeType.rect, { x: 3.82, y: y + 0.04, w: 4.1, h: 0.14, fill: { color: "E8EEF4" }, line: { color: "E8EEF4" } });
    s.addShape(pptx.ShapeType.rect, { x: 3.82, y: y + 0.04, w, h: 0.14, fill: { color: col }, line: { color: col } });
    label(s, score, 8.15, y - 0.01, 0.42, 0.18, { size: 6.6, bold: true, color: col });
  });
  label(s, "criterios con peso", 9.15, 1.35, 2.4, 0.25, { size: 9.5, bold: true, color: C.navy });
  [
    ["25 %", "maniobra en estacion", C.green],
    ["20 %", "seguridad con operarios", C.red],
    ["15 %", "trazabilidad e integracion", C.violet],
    ["15 %", "madurez comercial", C.teal],
    ["15 %", "coste/riesgo de integracion", C.amber],
  ].forEach(([pct, txtv, col], i) => {
    const y = 1.90 + i * 0.66;
    s.addShape(pptx.ShapeType.ellipse, { x: 9.20, y: y + 0.04, w: 0.12, h: 0.12, fill: { color: col }, line: { color: col } });
    label(s, `${pct} ${txtv}`, 9.45, y - 0.02, 2.8, 0.20, { size: 7.1, bold: true, color: C.ink });
  });
}

// 8
{
  const s = slideBase("Modelo elegido y opciones reales de compra", "Robot", 8, C.green);
  drawAmr(s, 1.0, 1.55, 1.85, C.cyan);
  label(s, "LiDAR", 1.0, 1.18, 0.8, 0.18, { size: 6.5, color: C.teal, bold: true });
  label(s, "RGB-D", 3.05, 1.18, 0.8, 0.18, { size: 6.5, color: C.amber, bold: true });
  label(s, "E-stop + bumpers", 1.0, 3.75, 1.45, 0.18, { size: 6.5, color: C.red, bold: true });
  label(s, "IMU + encoders", 3.15, 3.75, 1.4, 0.18, { size: 6.5, color: C.cyan, bold: true });
  label(s, "shortlist defendible", 7.0, 1.35, 4.0, 0.35, { size: 15.0, bold: true, color: C.navy });
  const levels = [
    ["Recomendado", "RB-KAIROS-class: 250 kg, 1,5 m/s, ROS 2, omni."],
    ["Alternativa", "AGILOX ODM: 300 kg, 1,4 m/s, intralogistica."],
    ["Benchmark", "MiR250 y LD-250 solo para coste/carga AMR 250 kg."],
    ["Descartado", "KUKA omniMove: XXL y caro para kits."],
  ];
  levels.forEach(([a, b], i) => {
    const col = [C.green, C.teal, C.amber, C.red][i];
    s.addShape(pptx.ShapeType.ellipse, { x: 7.05, y: 2.05 + i * 0.62, w: 0.14, h: 0.14, fill: { color: col }, line: { color: col } });
    label(s, `${a}: ${b}`, 7.35, 1.91 + i * 0.62, 4.9, 0.32, { size: 7.5, color: C.ink });
  });
  label(s, "La licitacion exige base holonomica, safety pack, portakits, vx/vy/w, trazabilidad y pruebas FAT/SAT.", 7.02, 4.92, 5.1, 0.48, { size: 6.5, color: C.muted });
}

// 9
{
  const s = slideBase("Control por capas: navegar, actuar y dejar evidencia", "Arquitectura", 9, C.teal);
  const layers = [
    ["Percepcion", "LiDAR RGB-D RFID"],
    ["Localizacion", "SLAM IMU encoders"],
    ["Planificacion", "A* Dijkstra DWA"],
    ["Control", "vx vy w ruedas"],
    ["Integracion", "HMI BD MES"],
  ];
  layers.forEach(([a, b], i) => {
    card(s, 0.75 + i * 2.35, 1.85, 1.65, 0.78, { fill: ["E8F7FA", "EAF4FF", "FFF3E5", "EAF7F1", "F0EDFF"][i], line: [C.teal, C.cyan, C.amber, C.green, C.violet][i] });
    label(s, a, 0.85 + i * 2.35, 2.02, 1.45, 0.16, { size: 7, bold: true, color: [C.teal, C.cyan, C.amber, C.green, C.violet][i], align: "center" });
    label(s, b, 0.87 + i * 2.35, 2.28, 1.4, 0.16, { size: 5.8, color: C.muted, align: "center" });
    if (i < 4) arrow(s, 2.44 + i * 2.35, 2.24, 2.82 + i * 2.35, 2.24, C.line);
  });
  s.addShape(pptx.ShapeType.line, { x: 0.75, y: 3.52, w: 11.3, h: 0, line: { color: C.red, width: 1 } });
  label(s, "Interrupcion de seguridad: escaner, bumper o E-stop detienen cualquier mision", 0.82, 3.78, 7.6, 0.2, { size: 7.2, bold: true, color: C.red });
  label(s, "registro minimo por mision", 0.82, 4.50, 2.2, 0.2, { size: 8.2, bold: true, color: C.navy });
  label(s, "Robot, kit, origen, destino y estacion.", 0.82, 4.88, 3.2, 0.22, { size: 7.1, color: C.ink });
  label(s, "Ruta prevista y ruta ejecutada.", 4.25, 4.88, 2.7, 0.22, { size: 7.1, color: C.ink });
  label(s, "RFID/QR, seguridad, confirmacion e incidencia FOD.", 7.1, 4.88, 4.2, 0.22, { size: 7.1, color: C.ink });
}

// 10
{
  const s = slideBase("Un ciclo cerrado: pedir, mover, confirmar, registrar", "Operacion", 10, C.cyan);
  const steps = [
    ["1", "plan", C.teal], ["2", "carga", C.green], ["3", "lectura", C.violet],
    ["4", "ruta", C.cyan], ["5", "entrega", C.amber], ["6", "FOD", C.red], ["7", "retorno", C.green],
  ];
  steps.forEach(([n, t, c], i) => {
    const x = 0.95 + i * 1.65;
    s.addShape(pptx.ShapeType.ellipse, { x, y: 3.2 + (i % 2) * 0.55, w: 0.32, h: 0.32, fill: { color: c }, line: { color: c } });
    label(s, n, x + 0.08, 3.27 + (i % 2) * 0.55, 0.16, 0.1, { size: 5.5, bold: true, color: C.white, align: "center" });
    label(s, t, x - 0.2, 3.82 + (i % 2) * 0.55, 0.72, 0.14, { size: 6.5, color: c, bold: true, align: "center" });
    if (i < steps.length - 1) arrow(s, x + 0.36, 3.36 + (i % 2) * 0.55, x + 1.18, 3.36 + ((i + 1) % 2) * 0.55, C.cyan);
  });
  label(s, "La mision termina con evidencia:", 2.5, 5.52, 3.0, 0.22, { size: 8, bold: true, color: C.navy, align: "center" });
  label(s, "entrega confirmada + ruta registrada + excepcion documentada.", 5.35, 5.52, 5.4, 0.22, { size: 8, color: C.muted, align: "center" });
}

// 11
{
  const s = slideBase("La simulacion reduce riesgo antes del piloto fisico", "CoppeliaSim", 11, C.violet);
  card(s, 0.95, 1.45, 5.1, 3.4, { fill: "EEF5F8", line: "E2EAF0" });
  drawAmr(s, 4.65, 1.7, 0.75, C.cyan);
  s.addShape(pptx.ShapeType.line, { x: 1.45, y: 4.25, w: 3.6, h: 0, line: { color: C.violet, width: 1.2 } });
  s.addShape(pptx.ShapeType.line, { x: 5.05, y: 4.25, w: 0, h: -2.0, line: { color: C.violet, width: 1.2 } });
  label(s, "cuatro pruebas antes de planta", 7.0, 1.52, 4.1, 0.38, { size: 15, bold: true, color: C.navy });
  ["SLAM + fusion: llegada nominal a estacion HTP.", "A* / Dijkstra: ruta alterna con pasillo bloqueado.", "DWA / campos: cruce con operario y parada segura.", "RGB-D: ronda FOD con captura de evidencia."].forEach((t, i) => {
    s.addShape(pptx.ShapeType.rect, { x: 7.05, y: 2.18 + i * 0.62, w: 0.11, h: 0.11, fill: { color: [C.violet, C.cyan, C.red, C.amber][i] }, line: { color: [C.violet, C.cyan, C.red, C.amber][i] } });
    label(s, t, 7.35, 2.05 + i * 0.62, 4.6, 0.28, { size: 7.7, color: C.ink });
  });
  label(s, "Gate minimo antes de planta:", 7.05, 5.10, 2.6, 0.20, { size: 7.2, bold: true, color: C.navy });
  label(s, "95 % misiones entregan; cero contactos.", 7.05, 5.42, 3.8, 0.20, { size: 6.7, color: C.muted });
  label(s, "100 % misiones cerradas y bateria validada.", 7.05, 5.68, 3.9, 0.20, { size: 6.7, color: C.muted });
}

// 12
{
  const s = slideBase("Tres fases con entregables y criterio de paso", "Despliegue", 12, C.teal);
  const phases = [
    ["1", "Piloto controlado", "219.856 € CAPEX", "Zona acotada y 1-2 estaciones.", "Rutas, RFID-QR y ronda FOD.", "Riesgo: aceptacion y falsas alarmas.", "Pasa: 95 % misiones; 98 % trazas.", C.teal],
    ["7", "Expansion", "1.018.752 € CAPEX", "Varias estaciones y gestor de flota.", "Retorno de utiles y tablero de incidencias.", "Riesgo: pasillos y baterias.", "Pasa: disponibilidad >= 90 %.", C.amber],
    ["17", "Cobertura extendida", "2.310.896 € CAPEX", "Flujo auxiliar amplio e integracion.", "KPIs por turno y reservas de flota.", "Riesgo: comprar antes de medir.", "Pasa: beneficio cerca de VAN cero.", C.green],
  ];
  phases.forEach(([n, name, cost, scope1, scope2, risk, gate, col], i) => {
    const x = 0.85 + i * 4.15;
    card(s, x, 1.35, 3.65, 4.55, { fill: "FFFFFF", line: col });
    label(s, n, x + 0.25, 1.72, 0.55, 0.38, { size: 20, bold: true, color: col });
    label(s, name, x + 0.95, 1.82, 2.25, 0.22, { size: 8.2, bold: true, color: C.ink });
    label(s, cost, x + 0.28, 2.42, 1.85, 0.22, { size: 8.3, bold: true, color: col });
    label(s, scope1, x + 0.28, 3.05, 2.85, 0.22, { size: 6.4, color: C.ink });
    label(s, scope2, x + 0.28, 3.35, 2.9, 0.22, { size: 6.4, color: C.ink });
    label(s, risk, x + 0.28, 4.15, 2.9, 0.22, { size: 6.2, bold: true, color: C.red });
    label(s, gate, x + 0.28, 4.62, 2.85, 0.30, { size: 6.2, color: C.muted });
  });
  label(s, "Regla comercial: no se escala por intuicion.", 1.0, 6.10, 4.0, 0.20, { size: 7.1, bold: true, color: C.navy });
  label(s, "Se escala con trazas, seguridad, disponibilidad y uso real de flota.", 5.1, 6.10, 5.9, 0.20, { size: 7.1, bold: true, color: C.navy });
}

// 13
{
  const s = slideBase("Partidas por escenario, sin caja negra", "Presupuesto", 13, C.amber);
  label(s, "CAPEX estimado sin IVA", 0.85, 1.14, 2.2, 0.18, { size: 6.4, bold: true, color: C.muted });
  [["219.856 €", "1 robot", C.teal], ["1.018.752 €", "7 robots", C.amber], ["2.310.896 €", "17 robots", C.green]].forEach(([v, t, col], i) => {
    label(s, v, 0.85 + i * 3.55, 1.48, 2.25, 0.3, { size: 13.8, bold: true, color: col });
    label(s, t, 0.88 + i * 3.55, 1.86, 1.1, 0.16, { size: 6.3, bold: true, color: C.muted });
  });
  card(s, 0.85, 2.35, 11.65, 3.35, { fill: "FFFFFF", line: C.line });
  label(s, "Partida", 1.03, 2.55, 2.5, 0.16, { size: 6.3, bold: true, color: C.ink });
  label(s, "1 robot", 6.0, 2.55, 0.9, 0.16, { size: 6.3, bold: true, color: C.ink, align: "right" });
  label(s, "7 robots", 8.42, 2.55, 0.95, 0.16, { size: 6.3, bold: true, color: C.ink, align: "right" });
  label(s, "17 robots", 11.1, 2.55, 1.0, 0.16, { size: 6.3, bold: true, color: C.ink, align: "right" });
  const rows = [
    ["AMR omni + sensores + portakits", "78.500", "549.500", "1.334.500", C.teal],
    ["Software flota + trazabilidad", "24.000", "65.000", "120.000", C.violet],
    ["Ingenieria + CoppeliaSim", "46.000", "126.000", "245.000", C.cyan],
    ["Instalacion + mapeo + SAT", "20.000", "60.000", "135.000", C.green],
    ["Formacion + cambio operativo", "9.500", "27.000", "46.000", C.amber],
    ["Mantenimiento ano 1", "6.300", "44.100", "106.800", C.teal],
    ["Logistica + ciber + docs", "12.000", "38.000", "76.000", C.violet],
    ["Contingencia + margen 12 %", "23.556", "109.152", "247.596", C.red],
  ];
  rows.forEach(([part, one, seven, seventeen, col], i) => {
    const y = 2.95 + i * 0.31;
    s.addShape(pptx.ShapeType.rect, { x: 1.03, y: y + 0.03, w: 0.06, h: 0.06, fill: { color: col }, line: { color: col } });
    label(s, part, 1.18, y, 3.6, 0.16, { size: 5.8, bold: true, color: C.ink });
    label(s, one, 5.7, y, 1.2, 0.16, { size: 5.8, color: C.ink, align: "right" });
    label(s, seven, 8.08, y, 1.3, 0.16, { size: 5.8, color: C.ink, align: "right" });
    label(s, seventeen, 10.72, y, 1.4, 0.16, { size: 5.8, color: C.ink, align: "right" });
  });
  label(s, "Referencias publicas: RB-KAIROS/AGILOX, MiR250/LD-250, Hokuyo, Intel, Zebra y SICK.", 0.88, 6.05, 7.2, 0.18, { size: 6.4, color: C.muted });
  label(s, "No es cotizacion vinculante.", 8.2, 6.05, 2.3, 0.18, { size: 6.4, bold: true, color: C.muted });
}

// 14
{
  const s = slideBase("Tiempo recuperado frente a umbral financiero", "ROI", 14, C.teal);
  card(s, 0.85, 1.28, 3.75, 4.7, { fill: "EAF7F6", line: C.teal });
  label(s, "Supuesto de\ncalculo", 1.05, 1.48, 2.2, 0.52, { size: 13.0, bold: true, color: C.navy });
  label(s, "Salario guia: 20.000-28.000 €/ano.", 1.06, 2.30, 2.8, 0.20, { size: 7.0, color: C.ink });
  label(s, "Caso central: 24.000 €.", 1.06, 2.62, 2.4, 0.20, { size: 7.0, color: C.ink });
  label(s, "Coste empresa 1,35; 1.760 h/ano.", 1.06, 2.94, 2.9, 0.20, { size: 7.0, color: C.ink });
  label(s, "18,4 €/h", 1.05, 3.55, 2.3, 0.34, { size: 18, bold: true, color: C.teal });
  label(s, "Se monetiza tiempo improductivo; no reduccion de plantilla.", 1.08, 4.28, 2.8, 0.32, { size: 6.7, bold: true, color: C.red });

  label(s, "Beneficio anual: recuperado vs VAN cero", 5.05, 1.42, 4.4, 0.22, { size: 8, bold: true, color: C.muted });
  label(s, "horas recuperadas", 5.05, 1.78, 1.6, 0.16, { size: 5.7, color: C.teal });
  label(s, "umbral VAN cero", 7.05, 1.78, 1.5, 0.16, { size: 5.7, color: C.amber });
  const roiRows = [
    ["1 robot", "825 h/ano", "15.180 €", "80.260 €", 0.32, 1.16, C.amber],
    ["7 robots", "5.940 h/ano", "109.296 €", "359.263 €", 2.02, 3.30, C.teal],
    ["17 robots", "14.000 h/ano", "257.600 €", "814.017 €", 3.35, 4.80, C.green],
  ];
  roiRows.forEach(([esc, hrs, val, req, vw, rw, col], i) => {
    const y = 2.45 + i * 1.05;
    label(s, esc, 5.05, y, 1.0, 0.18, { size: 7, bold: true, color: col });
    label(s, hrs, 6.05, y, 1.15, 0.18, { size: 5.8, color: C.muted });
    s.addShape(pptx.ShapeType.rect, { x: 7.45, y: y - 0.05, w: vw, h: 0.12, fill: { color: C.teal }, line: { color: C.teal } });
    s.addShape(pptx.ShapeType.rect, { x: 7.45, y: y + 0.18, w: rw, h: 0.12, fill: { color: C.amber }, line: { color: C.amber } });
    label(s, val, 7.5 + vw, y - 0.1, 0.95, 0.16, { size: 5.5, color: C.ink });
    label(s, req, 7.5 + rw, y + 0.13, 0.95, 0.16, { size: 5.5, color: C.ink });
  });
  label(s, "Lectura: con solo horas recuperadas el VAN central sigue exigente.", 5.05, 5.72, 5.3, 0.18, { size: 6.3, bold: true, color: C.navy });
  label(s, "7 o 17 robots requieren menos esperas, continuidad de flujo y menor riesgo FOD.", 5.05, 5.98, 6.4, 0.18, { size: 6.3, bold: true, color: C.navy });
  label(s, "La decision final debe usar datos reales hacia 80 HTP/mes.", 5.05, 6.24, 5.3, 0.18, { size: 6.3, bold: true, color: C.navy });
}

// 15
{
  const s = slideBase("Entregables y condiciones de aceptacion", "Oferta comercial", 15, C.amber);
  label(s, "Entregables de la fase piloto", 0.88, 1.35, 3.3, 0.26, { size: 12.8, bold: true, color: C.navy });
  const deliverables = [
    ["Mapa operativo", "rutas, zonas lentas, carga y entrega", C.teal],
    ["Configuracion AMR", "misiones, prioridades y reglas de bateria", C.green],
    ["Trazabilidad", "BD, RFID-QR, HMI y excepciones", C.violet],
    ["FOD preventivo", "rondas con imagen y validacion humana", C.red],
    ["Validacion CoppeliaSim", "SLAM, ruta bloqueada, cruce y FOD", C.cyan],
    ["Formacion", "operarios, supervisores y mantenimiento", C.amber],
  ];
  deliverables.forEach(([a, b, c], i) => {
    const y = 2.05 + i * 0.52;
    s.addShape(pptx.ShapeType.rect, { x: 0.95, y: y + 0.05, w: 0.08, h: 0.08, fill: { color: c }, line: { color: c } });
    label(s, a, 1.16, y - 0.04, 2.25, 0.18, { size: 6.6, bold: true, color: c });
    label(s, b, 1.16, y + 0.20, 5.6, 0.18, { size: 5.8, color: C.ink });
  });
  card(s, 8.0, 1.35, 4.55, 4.75, { fill: "FFF7EF", line: C.amber });
  label(s, "Gate de aceptacion", 8.28, 1.72, 2.0, 0.2, { size: 8, bold: true, color: C.muted });
  const gates = [
    ["Seguridad", "0 contactos o incidentes con dano", C.red],
    ["Misiones", ">= 95 % completadas", C.teal],
    ["Trazabilidad", ">= 98 % con registro completo", C.violet],
    ["Disponibilidad", ">= 90 % en turno piloto", C.green],
    ["FOD", "100 % eventos revisables", C.amber],
    ["Escalado", "solo con VAN y datos de flujo", C.cyan],
  ];
  gates.forEach(([a, b, c], i) => {
    const y = 2.35 + i * 0.50;
    label(s, a, 8.32, y, 1.25, 0.16, { size: 6.0, bold: true, color: c });
    label(s, b, 9.78, y, 2.05, 0.16, { size: 5.9, color: C.ink });
    s.addShape(pptx.ShapeType.line, { x: 8.28, y: y + 0.28, w: 3.75, h: 0, line: { color: C.line, width: 0.6 } });
  });
  label(s, "Exclusion explicita: no se certifica montaje HTP.", 8.28, 5.52, 3.7, 0.18, { size: 6.0, bold: true, color: C.red });
  label(s, "Tampoco sustituye inspeccion aeronautica obligatoria.", 8.28, 5.76, 3.7, 0.18, { size: 6.0, bold: true, color: C.red });
}

// 16
{
  const s = slideBase("Recomendacion: medir antes de escalar", "Cierre", 16, C.green);
  label(s, "1 robot primero", 0.9, 1.45, 3.8, 0.42, { face: "Aptos Display", size: 22, bold: true, color: C.teal });
  label(s, "Validar rutas, seguridad y entregas.", 0.95, 2.16, 3.3, 0.24, { size: 9, color: C.ink });
  label(s, "Medir trazabilidad, FOD y aceptacion.", 0.95, 2.50, 3.3, 0.24, { size: 9, color: C.ink });
  label(s, "Escalar solo con datos.", 0.95, 2.84, 2.4, 0.24, { size: 9, bold: true, color: C.navy });
  drawAmr(s, 7.2, 2.0, 1.15, C.cyan);
  arrow(s, 8.85, 2.45, 10.3, 2.45, C.cyan);
  s.addShape(pptx.ShapeType.rect, { x: 10.7, y: 2.2, w: 0.55, h: 0.78, fill: { color: C.amber }, line: { color: C.amber } });
  s.addShape(pptx.ShapeType.triangle, { x: 11.05, y: 1.85, w: 0.95, h: 0.65, rotate: 18, fill: { color: "6FB7C6" }, line: { color: "6FB7C6" } });
  label(s, "rutas verificadas", 1.0, 5.75, 1.6, 0.18, { size: 6.8, bold: true, color: C.teal });
  label(s, "sin tocar montaje", 4.05, 5.75, 1.8, 0.18, { size: 6.8, bold: true, color: C.amber });
  label(s, "costes por partida", 7.1, 5.75, 1.8, 0.18, { size: 6.8, bold: true, color: C.green });
  label(s, "temario aplicado", 10.0, 5.75, 1.8, 0.18, { size: 6.8, bold: true, color: C.violet });
}

pptx.writeFile({ fileName: path.join(__dirname, "Actividad1_AMR_FOD_Kitting_editable.pptx") });

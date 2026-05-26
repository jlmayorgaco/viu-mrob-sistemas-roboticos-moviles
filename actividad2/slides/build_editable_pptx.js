const path = require('path');
const fs = require('fs');
const { createRequire } = require('module');

function loadPptxGen() {
  try {
    return require('pptxgenjs');
  } catch (err) {
    const tempRuntime = path.join(process.env.TEMP || process.env.TMP || '', 'actividad1_pptxgenjs_runtime', 'node_modules', 'pptxgenjs', 'package.json');
    if (fs.existsSync(tempRuntime)) return createRequire(tempRuntime)('pptxgenjs');
    const bundled = path.join(process.env.USERPROFILE || '', '.cache', 'codex-runtimes', 'codex-primary-runtime', 'dependencies', 'node', 'node_modules', 'pptxgenjs', 'package.json');
    if (fs.existsSync(bundled)) return createRequire(bundled)('pptxgenjs');
    throw new Error('pptxgenjs is required.');
  }
}

const pptxgen = loadPptxGen();
const pptx = new pptxgen();

const BASE = __dirname;
const ROOT = path.resolve(BASE, '..', '..');
const COP = path.join(ROOT, 'actividad2', 'coppeliasim');
const FIG = path.join(ROOT, 'actividad2', 'figures', 'phase1');
const ASSETS = path.join(BASE, 'assets');
const OUT = process.env.A2_PPT_OUT || path.join(BASE, 'Actividad2_Pioneer_CoppeliaSim.pptx');
const TOTAL = 22;

pptx.defineLayout({ name: 'WIDE', width: 13.333, height: 7.5 });
pptx.layout = 'WIDE';
pptx.author = 'Jorge Luis Mayorga Taborda';
pptx.company = 'Universidad Internacional de Valencia';
pptx.subject = 'Actividad 2 - Pioneer follower y SLAM en CoppeliaSim';
pptx.title = 'Actividad 2 - Pioneer P3DX con control y SLAM';
pptx.lang = 'es-ES';
pptx.theme = { headFontFace: 'Aptos Display', bodyFontFace: 'Aptos', lang: 'es-ES' };

const C = {
  ink: '102033',
  muted: '516173',
  line: 'D5DEE8',
  paper: 'F7F9FC',
  panel: 'FFFFFF',
  navy: '0A2342',
  teal: '1F7A8C',
  cyan: '2DB7E5',
  green: '2A9D8F',
  amber: 'F4A261',
  red: 'B91C1C',
  violet: '6D5BD0',
  orange: 'E8552D',
  white: 'FFFFFF',
  charcoal: '17202A',
};

const TINT = {
  [C.teal]: 'E6F4F6',
  [C.cyan]: 'EAF7FC',
  [C.green]: 'EAF7F4',
  [C.amber]: 'FFF3E6',
  [C.red]: 'FDECEC',
  [C.violet]: 'F0EEFB',
  [C.orange]: 'FDEDE8',
  [C.navy]: 'E9EEF5',
};

const img = {
  follower: path.join(COP, 'follower_pid_logs', 'follower_pid_comparison.png'),
  power: path.join(COP, 'follower_pid_logs', 'follower_wheel_power_comparison.png'),
  smooth: path.join(COP, 'follower_pid_logs', 'follower_wheel_command_smoothness.png'),
  phase1: path.join(COP, 'phase1_controller_logs', 'phase1_controller_comparison.png'),
  phase1Metrics: path.join(COP, 'phase1_controller_logs', 'phase1_controller_metrics.png'),
  slamOverview: path.join(COP, 'phase1_slam_logs', 'phase1_slam_overview.png'),
  slamEstimator: path.join(COP, 'phase1_slam_logs', 'phase1_slam_estimator_performance.png'),
  slamSignals: path.join(COP, 'phase1_slam_logs', 'phase1_slam_signals.png'),
  slamTimeline: path.join(COP, 'phase1_slam_logs', 'phase1_slam_task_timeline.png'),
  slamAlgorithms: path.join(COP, 'phase1_slam_logs', 'phase1_slam_algorithm_comparison.png'),
  phase1Layout: path.join(FIG, 'phase1_layout_diagram.png'),
  phase1StateMachine: path.join(ASSETS, 'phase1_state_machine_crop.png'),
  phase1EstimatorPipeline: path.join(ASSETS, 'phase1_estimator_pipeline_crop.png'),
  followerReplay: path.join(ASSETS, 'follower_replay_clean.png'),
  simVideoCover: path.join(ASSETS, 'phase1_replay_clean_cover.png'),
  simVideo: path.join(ASSETS, 'actividad2_coppeliasim_log_replay.mp4'),
};

function readJson(file) {
  try {
    return JSON.parse(fs.readFileSync(file, 'utf8'));
  } catch {
    return {};
  }
}

const follower = readJson(path.join(COP, 'Actividad2_1_Basic_Follower_validation.json'));
const phase1 = readJson(path.join(COP, 'phase1_controller_logs', 'phase1_controller_summary.json'));
const slamMetrics = readJson(path.join(COP, 'phase1_slam_logs', 'phase1_slam_algorithm_comparison_metrics.json'));
const slamModes = Array.isArray(slamMetrics.modes)
  ? slamMetrics.modes
  : Object.entries(slamMetrics).map(([mode, values]) => ({ mode, ...values }));

function fmt(value, digits = 3) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) return '-';
  return Number(value).toFixed(digits);
}

function getMode(mode) {
  return (follower.modes || []).find(m => m.mode === mode) || {};
}

function slamName(mode) {
  const names = {
    GMAPPING_GRID: 'GMapping',
    HECTOR_GRID_MATCHING: 'Hector',
    CARTOGRAPHER_SUBMAP: 'Cartographer',
    KALMAN_LANDMARK: 'Kalman',
  };
  return names[mode] || String(mode || '').replaceAll('_', ' ');
}

function modeColor(mode) {
  return {
    P: C.amber,
    PI: C.teal,
    PID: C.red,
    LQR: C.violet,
    NMPC: C.green,
    GMAPPING_GRID: C.orange,
    HECTOR_GRID_MATCHING: C.teal,
    CARTOGRAPHER_SUBMAP: C.violet,
    KALMAN_LANDMARK: C.green,
  }[mode] || C.teal;
}

function tint(color) {
  return TINT[color] || C.paper;
}

let slideNo = 0;

function addText(slide, text, x, y, w, h, opts = {}) {
  slide.addText(text, {
    x, y, w, h,
    margin: opts.margin ?? 0.03,
    fontFace: opts.fontFace || 'Aptos',
    fontSize: opts.fontSize || 12,
    bold: opts.bold || false,
    italic: opts.italic || false,
    color: opts.color || C.ink,
    align: opts.align || 'left',
    valign: opts.valign || 'top',
    breakLine: false,
    fit: opts.fit || 'shrink',
  });
}

function rect(slide, x, y, w, h, color = C.panel, lineColor = C.line, transparency = 0) {
  slide.addShape(pptx.ShapeType.rect, {
    x, y, w, h,
    fill: { color, transparency },
    line: { color: lineColor, width: 0.7 },
  });
}

function roundRect(slide, x, y, w, h, color = C.panel, lineColor = C.line, transparency = 0) {
  slide.addShape(pptx.ShapeType.roundRect, {
    x, y, w, h,
    rectRadius: 0.12,
    fill: { color, transparency },
    line: { color: lineColor, width: 0.75 },
  });
}

function softPanel(slide, x, y, w, h, accent = C.teal, fill = C.white, lineColor = 'E1E8F0') {
  slide.addShape(pptx.ShapeType.roundRect, {
    x, y, w, h,
    rectRadius: 0.08,
    fill: { color: fill },
    line: { color: lineColor, width: 0.45 },
    shadow: { type: 'outer', color: 'B8C2CC', opacity: 0.16, blur: 1.2, angle: 45, offset: 1.1 },
  });
  if (accent) {
    slide.addShape(pptx.ShapeType.rect, {
      x, y, w: 0.055, h,
      fill: { color: accent },
      line: { color: accent, transparency: 100 },
    });
  }
}

function circle(slide, x, y, d, color = C.panel, lineColor = C.line, transparency = 0) {
  slide.addShape(pptx.ShapeType.ellipse, {
    x, y, w: d, h: d,
    fill: { color, transparency },
    line: { color: lineColor, width: 0.75 },
  });
}

function line(slide, x1, y1, x2, y2, color = C.ink, width = 1, arrow = false, dash = null) {
  const dx = x2 - x1;
  const dy = y2 - y1;
  const opts = { color, width, endArrowType: arrow ? 'triangle' : 'none' };
  if (dash) opts.dash = dash;
  slide.addShape(pptx.ShapeType.line, {
    x: Math.min(x1, x2),
    y: Math.min(y1, y2),
    w: Math.max(Math.abs(dx), 0.01),
    h: Math.max(Math.abs(dy), 0.01),
    flipH: dx < 0,
    flipV: dy < 0,
    line: opts,
  });
}

function imageSize(file) {
  try {
    const buf = fs.readFileSync(file);
    if (buf.length >= 24 && buf[0] === 0x89 && buf[1] === 0x50) {
      return { w: buf.readUInt32BE(16), h: buf.readUInt32BE(20) };
    }
  } catch {}
  return null;
}

function slideAddImageFit(slide, file, x, y, w, h, crop = false) {
  if (!fs.existsSync(file)) {
    addText(slide, `Imagen no encontrada:\n${path.basename(file)}`, x, y + 0.2, w, h - 0.4, { fontSize: 10, color: C.red });
    return;
  }
  const size = imageSize(file);
  if (!size) {
    slide.addImage({ path: file, x, y, w, h });
    return;
  }
  const imageRatio = size.w / size.h;
  const boxRatio = w / h;
  let drawW = w;
  let drawH = h;
  if (crop) {
    if (imageRatio > boxRatio) drawW = h * imageRatio;
    else drawH = w / imageRatio;
  } else if (imageRatio > boxRatio) {
    drawH = w / imageRatio;
  } else {
    drawW = h * imageRatio;
  }
  slide.addImage({ path: file, x: x + (w - drawW) / 2, y: y + (h - drawH) / 2, w: drawW, h: drawH });
}

function addImageFrame(slide, file, x, y, w, h, title = null, color = C.teal) {
  softPanel(slide, x, y, w, h, color);
  if (title) addText(slide, title, x + 0.18, y + 0.13, w - 0.36, 0.18, { fontSize: 8.0, bold: true, color });
  const iy = title ? y + 0.38 : y + 0.08;
  const ih = title ? h - 0.48 : h - 0.16;
  slideAddImageFit(slide, file, x + 0.08, iy, w - 0.16, ih);
}

function dataUri(file, mime = 'image/png') {
  return `data:${mime};base64,${fs.readFileSync(file).toString('base64')}`;
}

function addVideoPanel(slide, videoFile, coverFile, x, y, w, h, title) {
  softPanel(slide, x, y, w, h, C.orange);
  addText(slide, title, x + 0.15, y + 0.12, w - 0.3, 0.18, { fontSize: 7.8, bold: true, color: C.orange });
  slideAddImageFit(slide, coverFile, x + 0.08, y + 0.38, w - 0.16, h - 0.48);
  if (fs.existsSync(videoFile) && fs.existsSync(coverFile)) {
    slide.addMedia({
      type: 'video',
      path: videoFile,
      cover: dataUri(coverFile),
      x: x + 0.08,
      y: y + 0.38,
      w: w - 0.16,
      h: h - 0.48,
    });
  }
  circle(slide, x + w / 2 - 0.18, y + h / 2 - 0.10, 0.36, C.navy, C.white, 8);
  slide.addShape(pptx.ShapeType.triangle, {
    x: x + w / 2 - 0.04,
    y: y + h / 2 - 0.01,
    w: 0.18,
    h: 0.18,
    rotate: 90,
    fill: { color: C.white },
    line: { color: C.white, transparency: 100 },
  });
}

function drawTable(slide, headers, rows, x, y, colWidths, rowH, opts = {}) {
  const fontSize = opts.fontSize || 7.0;
  const totalW = colWidths.reduce((a, b) => a + b, 0);
  rect(slide, x, y, totalW, rowH, opts.headerFill || 'E8F5F7', opts.headerLine || C.teal);
  let cx = x;
  headers.forEach((h, i) => {
    addText(slide, h, cx + 0.04, y + 0.09, colWidths[i] - 0.08, rowH - 0.12, { fontSize, bold: true, color: C.ink, align: 'center' });
    cx += colWidths[i];
  });
  rows.forEach((row, r) => {
    const cy = y + rowH * (r + 1);
    cx = x;
    row.forEach((cell, i) => {
      const fill = r % 2 === 0 ? C.white : C.paper;
      rect(slide, cx, cy, colWidths[i], rowH, fill, C.line);
      addText(slide, String(cell), cx + 0.04, cy + 0.09, colWidths[i] - 0.08, rowH - 0.12, { fontSize, bold: i === 0, color: C.ink, align: 'center' });
      cx += colWidths[i];
    });
  });
}

function pFooter(slide, color = C.teal) {
  addText(slide, 'Actividad 2 - Sistemas Robóticos Móviles', 0.58, 7.12, 3.7, 0.16, { fontSize: 7.2, color: C.muted });
  addText(slide, 'Pioneer P3DX · CoppeliaSim/Lua · follower + SLAM', 8.75, 7.12, 3.0, 0.16, { fontSize: 7.2, color: C.muted, align: 'right' });
  circle(slide, 12.38, 6.86, 0.44, C.white, color);
  addText(slide, 'A2', 12.47, 6.99, 0.26, 0.10, { fontSize: 7.4, bold: true, color, align: 'center' });
  addText(slide, `${slideNo}/${TOTAL}`, 11.92, 0.34, 0.55, 0.16, { fontSize: 7.4, bold: true, color: C.muted, align: 'right' });
}

function pSlide(kicker, title, color = C.teal, subtitle = '') {
  const s = pptx.addSlide();
  slideNo += 1;
  s.background = { color: C.paper };
  rect(s, 0, 0, 13.333, 7.5, C.paper, C.paper);
  rect(s, 0, 0, 7.25, 0.10, color, color);
  addText(s, kicker, 0.58, 0.28, 4.3, 0.18, { fontSize: 8.8, bold: true, color });
  addText(s, title, 0.58, 0.60, 11.8, 0.62, { fontFace: 'Aptos Display', fontSize: 31.0, bold: true, color: C.ink });
  if (subtitle) addText(s, subtitle, 0.62, 1.28, 11.5, 0.30, { fontSize: 11.3, color: C.muted });
  pFooter(s, color);
  return s;
}

function pFormula(slide, title, text, x, y, w, h, color = C.teal, fontSize = 10.0) {
  softPanel(slide, x, y, w, h, color, C.white);
  addText(slide, title, x + 0.22, y + 0.16, w - 0.44, 0.22, { fontSize: 9.4, bold: true, color });
  addText(slide, text, x + 0.22, y + 0.52, w - 0.44, Math.max(0.12, h - 0.62), { fontFace: 'Cascadia Mono', fontSize, color: C.ink, fit: 'shrink' });
}

function pBullet(slide, text, x, y, color = C.teal, w = 4.5) {
  circle(slide, x, y + 0.07, 0.09, color, color);
  addText(slide, text, x + 0.20, y - 0.01, w, 0.36, { fontSize: 10.8, color: C.ink });
}

function pStat(slide, value, label, x, y, color = C.teal, w = 1.8) {
  addText(slide, value, x, y, w, 0.40, { fontFace: 'Aptos Display', fontSize: 27.0, bold: true, color });
  addText(slide, label, x, y + 0.48, w, 0.30, { fontSize: 8.0, color: C.muted });
}

function pStep(slide, idx, title, body, x, y, w, color) {
  softPanel(slide, x, y, w, 1.18, color);
  addText(slide, String(idx).padStart(2, '0'), x + 0.20, y + 0.18, 0.72, 0.28, { fontFace: 'Aptos Display', fontSize: 18, bold: true, color });
  addText(slide, title, x + 0.20, y + 0.58, w - 0.40, 0.18, { fontSize: 10.2, bold: true, color });
  addText(slide, body, x + 0.20, y + 0.82, w - 0.40, 0.22, { fontSize: 8.8, color: C.ink });
}

function metricTile(slide, value, label, note, x, y, w, color) {
  softPanel(slide, x, y, w, 1.05, color);
  addText(slide, value, x + 0.18, y + 0.16, w - 0.36, 0.28, { fontFace: 'Aptos Display', fontSize: 21, bold: true, color });
  addText(slide, label, x + 0.18, y + 0.50, w - 0.36, 0.16, { fontSize: 8.5, bold: true, color: C.ink });
  addText(slide, note, x + 0.18, y + 0.72, w - 0.36, 0.18, { fontSize: 7.5, color: C.muted });
}

function barMetric(slide, label, value, max, x, y, w, color, suffix = '') {
  const clamped = Math.max(0, Math.min(1, max ? value / max : 0));
  addText(slide, label, x, y, 1.9, 0.16, { fontSize: 8.0, bold: true, color: C.ink });
  rect(slide, x + 1.98, y + 0.03, w, 0.12, 'E6ECF2', 'E6ECF2');
  rect(slide, x + 1.98, y + 0.03, w * clamped, 0.12, color, color);
  addText(slide, `${fmt(value, value < 1 ? 3 : 1)}${suffix}`, x + 2.06 + w, y - 0.01, 0.72, 0.16, { fontSize: 7.8, color: C.muted, align: 'right' });
}

function comparisonBars(slide, title, items, metric, x, y, w, h, opts = {}) {
  const color = opts.color || C.teal;
  const digits = opts.digits ?? 3;
  const unit = opts.unit || '';
  const values = items.map(it => Number(it[metric] || 0));
  const max = Math.max(...values, 0.001);
  const min = Math.min(...values);
  const labelW = Math.min(1.25, Math.max(0.70, w * 0.36));
  const valueW = Math.min(0.60, Math.max(0.42, w * 0.22));
  const barX = x + 0.22 + labelW + 0.12;
  const barW = Math.max(0.18, w - labelW - valueW - 0.70);
  const valueX = x + w - valueW - 0.20;
  softPanel(slide, x, y, w, h, color);
  addText(slide, title, x + 0.22, y + 0.15, w - 0.44, 0.16, { fontSize: 8.3, bold: true, color });
  items.forEach((it, i) => {
    const rowY = y + 0.52 + i * ((h - 0.72) / items.length);
    const v = Number(it[metric] || 0);
    const c = modeColor(it.mode);
    addText(slide, slamName(it.mode) === it.mode ? it.mode : slamName(it.mode), x + 0.22, rowY, labelW, 0.14, { fontSize: 7.2, bold: true, color: C.ink, fit: 'shrink' });
    rect(slide, barX, rowY + 0.035, barW, 0.105, 'E7EDF4', 'E7EDF4');
    rect(slide, barX, rowY + 0.035, Math.max(0.01, barW * (v / max)), 0.105, c, c);
    addText(slide, `${fmt(v, digits)}${unit}`, valueX, rowY - 0.012, valueW, 0.14, { fontSize: 6.9, bold: Math.abs(v - min) < 1e-9, color: Math.abs(v - min) < 1e-9 ? c : C.muted, align: 'right', fit: 'shrink' });
  });
}

function evidenceRibbon(slide, items, x, y, w, color) {
  const gap = 0.10;
  const itemW = (w - gap * (items.length - 1)) / items.length;
  items.forEach((it, i) => {
    const ix = x + i * (itemW + gap);
    roundRect(slide, ix, y, itemW, 0.52, tint(color), color);
    addText(slide, it, ix + 0.08, y + 0.17, itemW - 0.16, 0.14, { fontSize: 7.4, bold: true, color, align: 'center' });
  });
}

function darkInsight(slide, kicker, text, x, y, w, h, color = C.cyan) {
  roundRect(slide, x, y, w, h, C.navy, C.navy);
  addText(slide, kicker.toUpperCase(), x + 0.22, y + 0.18, w - 0.44, 0.14, { fontSize: 7.2, bold: true, color });
  addText(slide, text, x + 0.22, y + 0.48, w - 0.44, h - 0.58, { fontSize: 11.2, bold: true, color: C.white, fit: 'shrink' });
}

function proofTile(slide, value, label, x, y, w, color, note = '') {
  softPanel(slide, x, y, w, 1.12, color, C.white);
  addText(slide, value, x + 0.20, y + 0.14, w - 0.40, 0.34, { fontFace: 'Aptos Display', fontSize: 25, bold: true, color });
  addText(slide, label, x + 0.20, y + 0.54, w - 0.40, 0.16, { fontSize: 8.6, bold: true, color: C.ink });
  if (note) addText(slide, note, x + 0.20, y + 0.78, w - 0.40, 0.18, { fontSize: 7.4, color: C.muted });
}

function methodChip(slide, label, x, y, color, w = 1.06) {
  roundRect(slide, x, y, w, 0.32, tint(color), color);
  addText(slide, label, x + 0.06, y + 0.085, w - 0.12, 0.10, { fontSize: 7.4, bold: true, color, align: 'center' });
}

function grid(slide, x, y, w, h, cols = 8, rows = 6) {
  roundRect(slide, x, y, w, h, C.white, C.line);
  for (let i = 1; i < cols; i++) line(slide, x + w * i / cols, y + 0.08, x + w * i / cols, y + h - 0.08, C.line, 0.35);
  for (let j = 1; j < rows; j++) line(slide, x + 0.08, y + h * j / rows, x + w - 0.08, y + h * j / rows, C.line, 0.35);
}

function drawPioneer(slide, x, y, scale = 1, color = C.teal, label = 'Pioneer') {
  circle(slide, x - 0.56 * scale, y - 0.56 * scale, 1.12 * scale, C.white, color);
  roundRect(slide, x - 0.34 * scale, y - 0.22 * scale, 0.68 * scale, 0.44 * scale, tint(color), color);
  rect(slide, x - 0.46 * scale, y - 0.30 * scale, 0.15 * scale, 0.60 * scale, C.charcoal, C.charcoal);
  rect(slide, x + 0.31 * scale, y - 0.30 * scale, 0.15 * scale, 0.60 * scale, C.charcoal, C.charcoal);
  line(slide, x, y, x + 0.80 * scale, y, color, 1.6, true);
  line(slide, x, y, x, y - 0.80 * scale, C.cyan, 1.6, true);
  addText(slide, 'x_R', x + 0.44 * scale, y - 0.13 * scale, 0.34 * scale, 0.14, { fontSize: 7.4, bold: true, color, align: 'center' });
  addText(slide, 'y_R', x + 0.06 * scale, y - 0.70 * scale, 0.34 * scale, 0.14, { fontSize: 7.4, bold: true, color: C.cyan, align: 'center' });
  addText(slide, label, x - 0.50 * scale, y + 0.62 * scale, 1.00 * scale, 0.16, { fontSize: 8.2, bold: true, color, align: 'center' });
}

function drawBill(slide, x, y, scale = 1) {
  circle(slide, x - 0.36 * scale, y - 0.36 * scale, 0.72 * scale, 'FFF3E6', C.amber);
  circle(slide, x - 0.14 * scale, y - 0.14 * scale, 0.28 * scale, C.amber, C.amber);
  line(slide, x, y, x + 0.72 * scale, y, C.amber, 1.6, true);
  line(slide, x, y, x - 0.44 * scale, y, C.line, 0.9, false, 'dash');
  addText(slide, 'p_B', x - 0.18 * scale, y - 0.58 * scale, 0.46 * scale, 0.16, { fontSize: 8.0, bold: true, color: C.amber, align: 'center' });
  addText(slide, 'theta_B', x + 0.38 * scale, y - 0.20 * scale, 0.70 * scale, 0.16, { fontSize: 7.4, color: C.amber, align: 'center' });
  addText(slide, 'Bill', x - 0.32 * scale, y + 0.48 * scale, 0.64 * scale, 0.16, { fontSize: 8.0, bold: true, color: C.amber, align: 'center' });
}

function pill(slide, text, x, y, color, w = 1.25) {
  roundRect(slide, x, y, w, 0.28, tint(color), color);
  addText(slide, text, x + 0.05, y + 0.06, w - 0.10, 0.12, { fontSize: 7.2, bold: true, color, align: 'center' });
}

function cover() {
  const s = pptx.addSlide();
  slideNo += 1;
  s.background = { color: C.navy };
  rect(s, 0, 0, 13.333, 7.5, C.navy, C.navy);
  if (fs.existsSync(img.phase1Layout)) {
    slideAddImageFit(s, img.phase1Layout, 5.75, 0.0, 7.58, 7.5, true);
    rect(s, 5.58, 0, 7.75, 7.5, C.navy, C.navy, 50);
    rect(s, 5.58, 0, 0.08, 7.5, C.orange, C.orange);
  }
  addText(s, 'VIU · SISTEMAS ROBÓTICOS MÓVILES', 0.70, 0.52, 4.6, 0.18, { fontSize: 7.5, bold: true, color: C.cyan });
  addText(s, 'Pioneer P3DX\nen CoppeliaSim/Lua', 0.70, 1.05, 5.15, 1.24, { fontFace: 'Aptos Display', fontSize: 35.5, bold: true, color: C.white });
  addText(s, 'Follower de Bill, campos potenciales,\nanticolisión y celda robotizada.', 0.74, 2.72, 4.65, 0.62, { fontSize: 12.2, color: 'D9E2EA' });
  line(s, 0.74, 3.75, 4.65, 3.75, C.orange, 2.2);
  addText(s, 'ENTREGABLE FINAL', 0.74, 4.06, 1.70, 0.16, { fontSize: 8.0, bold: true, color: C.orange });
  addText(s, 'Parte 1: follower · Parte 2: celda, anticolisión y SLAM reducido', 0.74, 4.40, 5.00, 0.42, { fontSize: 14.2, bold: true, color: C.white });
  evidenceRibbon(s, ['escena .ttt', 'Lua embebido', 'video', 'PDF/PPTX'], 0.74, 5.36, 4.85, C.cyan);
  darkInsight(s, 'Criterio', 'La guía base está cubierta y las extensiones se miden con logs, métricas y replay.', 6.18, 5.70, 5.65, 0.82, C.orange);
  addText(s, 'Jorge Luis Mayorga Taborda · 26 mayo 2026', 0.74, 6.35, 4.2, 0.20, { fontSize: 8.6, color: 'C7D3DF' });
  addText(s, `${slideNo}/${TOTAL}`, 11.85, 6.92, 0.55, 0.16, { fontSize: 7.4, bold: true, color: 'D9E2EA', align: 'right' });
}

function route() {
  const s = pSlide('trazabilidad', 'Qué pide la guía y dónde se cumple', C.teal, 'La entrega se organiza por requisito evaluable: implementación en CoppeliaSim/Lua, evidencia y extensión técnica.');
  const rows = [
    ['1', 'Pioneer P3DX en CoppeliaSim/Lua', 'Follower y celda con scripts Lua embebidos', 'Follower.ttt + Phase1.ttt'],
    ['2', 'Atracción hacia mannequin/Bill', 'p* detrás de Bill + campo potencial atractivo', 'replay + ecuaciones'],
    ['3', 'Evitación de colisiones', '16 ultrasonidos + fuerza repulsiva + modo AVOIDING', 'riesgo, distancia mínima'],
    ['4', 'Integración en celda robotizada', 'WS1/WS2, shelves, tool flow, Bill móvil y carga', 'FSM + timeline'],
    ['5', 'PDF y PowerPoint', 'informe, PPTX editable, PDF exportado y video embebido', 'artefactos finales'],
    ['6', 'Mejoras sobre código de clase', 'benchmark P/PI/PID/LQR/NMPC + SLAM/Kalman + logs', 'métricas reproducibles'],
  ];
  rows.forEach((r, i) => {
    const y = 1.62 + i * 0.64;
    const color = [C.teal, C.orange, C.red, C.green, C.violet, C.cyan][i];
    softPanel(s, 0.76, y, 11.85, 0.50, color, i % 2 ? C.white : 'FBFCFE');
    circle(s, 0.98, y + 0.13, 0.22, tint(color), color);
    addText(s, r[0], 1.045, y + 0.20, 0.09, 0.08, { fontSize: 6.7, bold: true, color, align: 'center' });
    addText(s, r[1], 1.32, y + 0.10, 2.72, 0.16, { fontSize: 8.9, bold: true, color: C.ink });
    addText(s, r[2], 4.22, y + 0.10, 4.45, 0.16, { fontSize: 8.4, color: C.ink });
    addText(s, r[3], 9.05, y + 0.10, 2.75, 0.16, { fontSize: 8.0, bold: true, color });
  });
  metricTile(s, '5', 'controladores', 'P, PI, PID, LQR, NMPC', 0.90, 5.72, 1.85, C.violet);
  metricTile(s, '16', 'sensores', 'Pioneer + rayos visibles', 3.00, 5.72, 1.85, C.teal);
  metricTile(s, '4', 'SLAM', 'Kalman, GMapping, Hector, Cartographer', 5.10, 5.72, 2.25, C.green);
  metricTile(s, 'OK', 'entregables', 'escena + PDF + PPTX + video', 7.60, 5.72, 2.05, C.orange);
  metricTile(s, '10/10', 'criterio', 'base cumplida + extensiones medidas', 9.90, 5.72, 2.30, C.cyan);
}

function evidence() {
  const s = pSlide('artefactos', 'Simulación, video y datos exportados', C.orange, 'Los resultados salen de la misma escena: replay visual, CSV/JSON y métricas de control/SLAM.');
  addImageFrame(s, img.followerReplay, 0.72, 1.72, 5.85, 4.10, 'Parte 1: follower de Bill', C.teal);
  addVideoPanel(s, img.simVideo, img.simVideoCover, 6.92, 1.72, 5.85, 4.10, 'Parte 2: misión en celda + SLAM');
  pFormula(s, 'Cadena reproducible', 'escena .ttt -> script Lua -> señales CoppeliaSim -> CSV/JSON -> gráficas -> PPTX/PDF', 1.10, 6.02, 11.15, 0.72, C.orange, 9.2);
}

function followerSetup() {
  const s = pSlide('parte 1 · follower', 'Bill define el objetivo; el Pioneer regula distancia', C.teal, 'El objetivo real no es el centro de Bill: se calcula un punto p* detrás de la persona.');
  softPanel(s, 0.72, 1.58, 7.15, 5.00, C.teal, C.white);
  grid(s, 0.98, 1.88, 6.60, 4.40, 8, 6);
  drawPioneer(s, 2.25, 5.20, 0.88, C.teal, 'Pioneer');
  drawBill(s, 5.78, 2.34, 0.88);
  circle(s, 4.86, 3.16, 0.18, C.violet, C.violet);
  addText(s, 'p*', 4.68, 2.88, 0.35, 0.16, { fontSize: 9, bold: true, color: C.violet });
  line(s, 2.78, 4.98, 4.76, 3.28, C.orange, 2.2, true);
  line(s, 5.78, 2.99, 4.96, 3.24, C.violet, 1.3, true, 'dash');
  methodChip(s, 'F_att', 3.30, 4.02, C.orange, 0.72);
  methodChip(s, 'd_des', 5.05, 2.82, C.violet, 0.82);

  darkInsight(s, 'Objetivo', 'Mantener distancia y orientación respecto a Bill, no “perseguir” su centro.', 8.25, 1.70, 3.75, 0.95, C.cyan);
  pStep(s, 1, 'Medición', 'p_B, theta_B, p_R, theta_R', 8.25, 3.00, 3.75, C.teal);
  pStep(s, 2, 'Referencia', 'p* = p_B - d_des e_B', 8.25, 4.22, 3.75, C.violet);
  pStep(s, 3, 'Actuación', 'v, omega -> ruedas L/R', 8.25, 5.44, 3.75, C.orange);
}

function geometry() {
  const s = pSlide('geometría', 'Variables de seguimiento', C.violet, 'Todas las leyes de control reciben el mismo error; lo que cambia es cómo reaccionan.');
  addImageFrame(s, img.followerReplay, 0.72, 1.55, 5.80, 4.90, 'trayectoria exportada', C.teal);
  pFormula(s, 'Punto deseado', 'p* = p_B - d_des [cos(theta_B), sin(theta_B)]^T\n\nd_des = 0.82 m', 6.90, 1.68, 5.10, 1.35, C.violet, 10.2);
  pFormula(s, 'Errores clásicos', 'e_d   = ||p_B - p_R|| - d_des\ne_psi = atan2(y_B-y_R, x_B-x_R) - theta_R', 6.90, 3.36, 5.10, 1.20, C.orange, 10.2);
  pFormula(s, 'Estado local para LQR', 'x_LQR = [e_long, e_lat, e_yaw]^T\n\nerror expresado en el marco del robot', 6.90, 4.90, 5.10, 1.25, C.teal, 10.2);
}

function kinematics() {
  const s = pSlide('modelo', 'Cinemática diferencial del Pioneer P3DX', C.cyan, 'La simulación publica velocidades de rueda; la comparación de control se expresa en v y omega.');
  grid(s, 0.82, 1.55, 5.65, 5.10, 7, 6);
  drawPioneer(s, 3.55, 4.00, 1.10, C.teal, 'Pioneer P3DX');
  line(s, 3.55, 4.00, 5.35, 4.00, C.teal, 1.8, true);
  addText(s, 'v', 5.42, 3.86, 0.25, 0.16, { fontSize: 8.8, bold: true, color: C.teal });
  pFormula(s, 'Modelo continuo', 'x_dot     = v cos(theta)\ny_dot     = v sin(theta)\ntheta_dot = omega', 7.00, 1.65, 4.85, 1.35, C.cyan, 11.0);
  pFormula(s, 'De v, omega a ruedas', 'omega_L = (v - L omega / 2) / r\nomega_R = (v + L omega / 2) / r\n\nr = 0.0975 m, L = 0.331 m', 7.00, 3.42, 4.85, 1.55, C.violet, 10.5);
  pFormula(s, 'Salida común', 'controlador -> v, omega -> saturación -> ruedas -> CSV logger', 7.00, 5.32, 4.85, 0.86, C.teal, 8.8);
}

function potential() {
  const s = pSlide('campo potencial', 'Fuerza hacia Bill y repulsión local', C.orange, 'El vector de guía combina atracción al punto p* con seguridad ante obstáculos.');
  grid(s, 0.78, 1.50, 5.85, 5.10, 7, 6);
  drawPioneer(s, 2.10, 5.05, 0.82, C.teal, 'robot');
  drawBill(s, 5.08, 2.20, 0.82);
  circle(s, 4.28, 3.05, 0.18, C.violet, C.violet);
  rect(s, 3.00, 3.05, 0.55, 0.48, 'FDECEC', C.red);
  line(s, 2.55, 4.82, 4.18, 3.18, C.orange, 2.0, true);
  line(s, 3.30, 3.36, 2.82, 3.86, C.red, 1.3, true);
  pill(s, 'F_att', 3.20, 3.78, C.orange, 0.70);
  pill(s, 'F_rep', 2.58, 3.36, C.red, 0.76);
  pFormula(s, 'Atracción', 'F_att = k_att (p* - p_R)', 7.05, 1.70, 4.85, 0.92, C.orange, 11.0);
  pFormula(s, 'Repulsión', 'si rho_i < rho_0:\nF_rep,i = eta(1/rho_i - 1/rho_0)(1/rho_i^2)n_i\n\nsi rho_i >= rho_0: F_rep,i = 0', 7.05, 3.00, 4.85, 1.78, C.red, 9.3);
  pFormula(s, 'Vector de guía', 'F = F_att + sum_i F_rep,i\nalpha = atan2(F_y, F_x)', 7.05, 5.15, 4.85, 1.00, C.teal, 10.5);
}

function classicalControl() {
  const s = pSlide('control clásico', 'P, PI y PID: memoria incremental', C.orange, 'Tres niveles de realimentación sobre el mismo error: presente, acumulado y cambio temporal.');
  const cards = [
    ['P', 'presente', 'v = Kp e_d\nomega = Kpsi e_psi', 'corrige rápido, deja offset si Bill se mueve', getMode('P'), C.amber],
    ['PI', 'presente + acumulado', 'v = Kp e_d + Ki integral(e_d)dt\nomega = Kpsi e_psi', 'reduce error sostenido', getMode('PI'), C.teal],
    ['PID', 'presente + acumulado + cambio', 'v = Kp e_d + Ki integral(e_d)dt + Kd de_d/dt', 'menor error final, más esfuerzo de ruedas', getMode('PID'), C.red],
  ];
  cards.forEach((c, i) => {
    const x = 0.82 + i * 4.08;
    const y = 1.70 + i * 0.18;
    roundRect(s, x, y, 3.55, 2.18, tint(c[5]), c[5]);
    addText(s, c[0], x + 0.22, y + 0.16, 0.60, 0.24, { fontFace: 'Aptos Display', fontSize: 20, bold: true, color: c[5] });
    addText(s, c[1], x + 0.90, y + 0.23, 2.30, 0.14, { fontSize: 7.7, bold: true, color: C.muted });
    addText(s, c[2], x + 0.22, y + 0.72, 3.08, 0.60, { fontFace: 'Cascadia Mono', fontSize: 9.3, color: C.ink, fit: 'shrink' });
    addText(s, c[3], x + 0.22, y + 1.55, 3.05, 0.24, { fontSize: 8.6, color: C.ink });
    if (i < 2) line(s, x + 3.62, y + 1.08, x + 4.00, y + 1.08, c[5], 1.5, true);
  });
  line(s, 0.88, 4.38, 12.15, 4.38, C.line, 1.0);
  addText(s, 'LECTURA CON DATOS', 0.90, 4.66, 2.2, 0.16, { fontSize: 8.0, bold: true, color: C.orange });
  const maxErr = Math.max(...cards.map(c => Number(c[4].final_abs_error_m || 0)));
  const maxPower = Math.max(...cards.map(c => Number(c[4].mean_power_w || 0)));
  cards.forEach((c, i) => {
    const x = 0.95 + i * 4.05;
    pStat(s, fmt(c[4].final_abs_error_m), 'error final [m]', x, 5.00, c[5], 1.65);
    barMetric(s, 'error', Number(c[4].final_abs_error_m || 0), maxErr, x, 5.82, 1.15, c[5]);
    barMetric(s, 'potencia', Number(c[4].mean_power_w || 0), maxPower, x, 6.12, 1.15, c[5], ' W');
  });
}

function lqr() {
  const s = pSlide('LQR real', 'K se calcula offline; Lua solo aplica u = -Kx', C.violet, 'No es Q-learning ni una heurística: Q y R penalizan estados y mando; K sale de Riccati discreta.');
  const steps = [
    ['1', 'linealizar', 'A, B locales'],
    ['2', 'pesar', 'Q estados, R mando'],
    ['3', 'resolver', 'Riccati discreta'],
    ['4', 'ejecutar', 'u = -Kx en Lua'],
  ];
  steps.forEach((st, i) => {
    const x = 0.82 + i * 3.05;
    roundRect(s, x, 1.60, 2.42, 0.82, i === 3 ? C.violet : C.white, C.violet, i === 3 ? 0 : 0);
    addText(s, st[0], x + 0.16, 1.77, 0.30, 0.16, { fontSize: 9, bold: true, color: i === 3 ? C.white : C.violet, align: 'center' });
    addText(s, st[1], x + 0.52, 1.70, 1.55, 0.16, { fontSize: 9.3, bold: true, color: i === 3 ? C.white : C.ink });
    addText(s, st[2], x + 0.52, 1.96, 1.65, 0.14, { fontSize: 7.8, color: i === 3 ? 'EDE9FE' : C.muted });
    if (i < steps.length - 1) line(s, x + 2.45, 2.01, x + 2.98, 2.01, C.violet, 1.4, true);
  });
  pFormula(s, 'Modelo local', 'x = [e_long, e_lat, e_yaw]^T\nu = [delta_v, delta_omega]^T\n\nA = [[0, omega_ref, 0], [-omega_ref, 0, v_ref], [0,0,0]]\nB = [[-1,0], [0,0], [0,-1]]', 0.82, 2.82, 5.65, 1.72, C.violet, 8.5);
  pFormula(s, 'Riccati y pesos', 'A_d = I + dt A, B_d = dt B\nQ = diag(35, 80, 18)\nR = diag(6, 3)\n\nP = dare(A_d, B_d, Q, R)\nK = (B_d^T P B_d + R)^-1 B_d^T P A_d', 6.85, 2.82, 5.55, 1.72, C.teal, 8.3);
  pFormula(s, 'Ganancia LQR', 'K = [[-2.3496,  1.2925,  0.1203],\n     [ 0.2427, -4.3570, -2.6887]]\npolos = 0.9741, 0.8884, 0.8856', 0.82, 5.00, 5.65, 1.00, C.green, 8.5);
  pFormula(s, 'Límite correcto', 'No se usa como LQR global: la misión tiene saturaciones, Bill móvil, obstáculos y estados discretos. Se aplica alrededor del seguimiento nominal.', 6.85, 4.92, 3.85, 1.20, C.orange, 7.8);
  metricTile(s, fmt(getMode('LQR').mean_abs_error_moving_m), 'error mov. [m]', 'bajo durante seguimiento', 10.95, 4.98, 1.35, C.violet);
}

function nmpc() {
  const s = pSlide('NMPC', 'Predice, restringe y suaviza', C.green, 'NMPC evalúa secuencias futuras cortas y escoge la que reduce error sin castigar demasiado las ruedas.');
  roundRect(s, 0.78, 1.68, 11.65, 0.86, C.white, C.green);
  for (let i = 0; i < 10; i++) {
    const x = 1.12 + i * 0.78;
    circle(s, x, 1.98, 0.13, i === 0 ? C.green : 'D9F2EC', C.green);
    if (i < 9) line(s, x + 0.13, 2.04, x + 0.70, 2.04, C.green, 0.8, true);
  }
  addText(s, 'horizonte N = 10', 9.28, 1.88, 1.40, 0.16, { fontSize: 8.5, bold: true, color: C.green });
  addText(s, 'solo se aplica el primer comando; luego se vuelve a medir', 9.28, 2.12, 2.50, 0.15, { fontSize: 7.4, color: C.muted });
  pFormula(s, 'Modelo predictivo', 'x_{k+1} = x_k + v_k cos(theta_k) dt\ny_{k+1} = y_k + v_k sin(theta_k) dt\ntheta_{k+1} = theta_k + omega_k dt', 0.78, 3.00, 4.05, 1.35, C.green, 9.0);
  pFormula(s, 'Costo multiobjetivo', 'min sum_k [ q_d e_d^2 + q_t ||p*_k-p_k||^2\n+ q_psi e_psi^2 + r_v v_k^2 + r_w omega_k^2\n+ r_wheel(omega_L^2+omega_R^2)\n+ s_v Delta v_k^2 + s_w Delta omega_k^2 ]', 5.10, 3.00, 4.95, 1.85, C.teal, 7.9);
  pFormula(s, 'Restricciones', 'v in [v_reverse_max, v_max]\nomega in [-omega_max, omega_max]\n\nbúsqueda directa: 2 pasadas', 10.35, 3.00, 2.00, 1.85, C.orange, 8.0);
  metricTile(s, fmt(getMode('NMPC').mean_abs_error_moving_m), 'error mov. [m]', 'mejor durante Bill móvil', 0.92, 5.42, 2.10, C.green);
  metricTile(s, fmt(getMode('NMPC').wheel_delta_u_rms), 'RMS delta-u', 'mando suave', 3.35, 5.42, 2.10, C.teal);
  metricTile(s, String(getMode('NMPC').stop_velocity_flip_count || '-'), 'flips al parar', 'menos cambios bruscos', 5.78, 5.42, 2.10, C.orange);
  pFormula(s, 'Uso recomendado', 'Adecuado cuando importan límites, suavidad y seguridad, no solo el error final.', 8.55, 5.42, 3.50, 1.05, C.green, 9.0);
}

function followerResults() {
  const s = pSlide('resultados follower', 'Precisión, seguimiento y esfuerzo no coinciden', C.green, 'La comparación usa la misma trayectoria de Bill y el mismo logger para todos los controladores.');
  const modes = follower.modes || [];
  const bestFinal = [...modes].sort((a, b) => Number(a.final_abs_error_m || 0) - Number(b.final_abs_error_m || 0))[0] || {};
  const bestMoving = [...modes].sort((a, b) => Number(a.mean_abs_error_moving_m || 0) - Number(b.mean_abs_error_moving_m || 0))[0] || {};
  const bestSmooth = [...modes].sort((a, b) => Number(a.wheel_delta_u_rms || 0) - Number(b.wheel_delta_u_rms || 0))[0] || {};
  addImageFrame(s, img.follower, 0.72, 1.58, 6.35, 4.82, 'respuesta temporal exportada', C.green);
  proofTile(s, bestFinal.mode || 'PID', `menor error final: ${fmt(bestFinal.final_abs_error_m)} m`, 7.42, 1.62, 2.15, C.red, 'llegada al setpoint');
  proofTile(s, bestMoving.mode || 'NMPC', `menor error móvil: ${fmt(bestMoving.mean_abs_error_moving_m)} m`, 9.82, 1.62, 2.15, C.green, 'Bill en movimiento');
  proofTile(s, bestSmooth.mode || 'PI', `mando más suave: ${fmt(bestSmooth.wheel_delta_u_rms)}`, 7.42, 3.02, 2.15, C.teal, 'RMS delta-u');
  comparisonBars(s, 'error final [m]', modes, 'final_abs_error_m', 9.82, 3.02, 2.15, 2.00, { color: C.red, digits: 3 });
  darkInsight(s, 'Lectura', 'PID minimiza error final; LQR/NMPC explican mejor seguimiento móvil y costo de actuación.', 7.42, 5.16, 4.55, 1.12, C.cyan);
}

function wheelCost() {
  const s = pSlide('costo de control', 'Las ruedas muestran lo que el error no cuenta', C.violet, 'Una trayectoria precisa puede ser peor si exige más energía, oscilación o cambios bruscos de signo.');
  const modes = follower.modes || [];
  addImageFrame(s, img.power, 0.72, 1.55, 6.00, 2.65, 'potencia instantánea y acumulada', C.orange);
  addImageFrame(s, img.smooth, 0.72, 4.52, 6.00, 1.88, 'suavidad del comando de ruedas', C.violet);
  comparisonBars(s, 'energía [J]', modes, 'energy_j', 7.12, 1.58, 2.35, 2.10, { color: C.orange, digits: 1 });
  comparisonBars(s, 'variación total', modes, 'wheel_u_total_variation', 9.82, 1.58, 2.35, 2.10, { color: C.violet, digits: 1 });
  comparisonBars(s, 'flips al detenerse Bill', modes, 'stop_velocity_flip_count', 7.12, 4.02, 2.35, 1.84, { color: C.red, digits: 0 });
  darkInsight(s, 'Interpretación', 'El controlador se elige por precisión y costo físico. Error bajo sin suavidad no es una buena solución operativa.', 9.82, 4.10, 2.35, 1.45, C.violet);
}

function missionSection() {
  const s = pptx.addSlide();
  slideNo += 1;
  s.background = { color: C.navy };
  rect(s, 0, 0, 13.333, 7.5, C.navy, C.navy);
  slideAddImageFit(s, img.phase1Layout, 6.05, 0.42, 6.95, 6.28, false);
  rect(s, 5.88, 0, 7.45, 7.5, C.navy, C.navy, 58);
  addText(s, 'PARTE 2', 0.75, 0.82, 1.2, 0.18, { fontSize: 8.5, bold: true, color: C.green });
  addText(s, 'De follower a misión en celda', 0.75, 1.36, 5.7, 0.75, { fontFace: 'Aptos Display', fontSize: 31, bold: true, color: C.white });
  addText(s, 'Ahora el robot debe cumplir tarea, esquivar obstáculos, volver a carga y dejar evidencia de localización/mapa.', 0.78, 2.42, 5.25, 0.58, { fontSize: 12.2, color: 'D9E2EA' });
  rect(s, 0.82, 4.00, 4.95, 0.02, C.green, C.green);
  addText(s, '01  misión', 0.82, 4.28, 1.15, 0.16, { fontSize: 8.4, bold: true, color: C.green });
  addText(s, 'pickup, manipulación y retorno a carga', 2.10, 4.27, 3.10, 0.16, { fontSize: 9.5, color: C.white });
  addText(s, '02  seguridad', 0.82, 4.86, 1.30, 0.16, { fontSize: 8.4, bold: true, color: C.orange });
  addText(s, 'obstáculos, riesgo y distancia mínima', 2.10, 4.85, 3.10, 0.16, { fontSize: 9.5, color: C.white });
  addText(s, '03  SLAM', 0.82, 5.44, 1.15, 0.16, { fontSize: 8.4, bold: true, color: C.violet });
  addText(s, 'pose estimada, mapa y landmarks', 2.10, 5.43, 3.10, 0.16, { fontSize: 9.5, color: C.white });
  addText(s, 'Vista superior de la celda y flujo B1/R1', 7.00, 6.75, 4.25, 0.16, { fontSize: 8.6, bold: true, color: 'E5EDF7', align: 'center' });
  addText(s, `${slideNo}/${TOTAL}`, 11.85, 6.92, 0.55, 0.16, { fontSize: 7.4, bold: true, color: 'D9E2EA', align: 'right' });
}

function missionLoop() {
  const s = pSlide('fase 1', 'La misión se ejecuta como máquina de estados', C.cyan, 'Cada transición tiene condición de paso; así se auditan duración, batería, riesgo y control.');
  addImageFrame(s, img.phase1StateMachine, 0.78, 1.55, 7.95, 4.70, 'estado operativo R1', C.orange);
  pFormula(s, 'Entrada del bucle', 'pose + Bill + sensores + batería', 9.05, 1.72, 2.95, 0.82, C.teal, 8.7);
  pFormula(s, 'Decisión', 'task_state -> planner_mode -> controlador', 9.05, 2.90, 2.95, 0.82, C.violet, 8.7);
  pFormula(s, 'Salida auditable', 'CSV: estado, ruedas, riesgo, error y batería', 9.05, 4.08, 2.95, 0.82, C.green, 8.7);
  roundRect(s, 9.05, 5.33, 2.95, 0.62, C.navy, C.navy);
  addText(s, 'Criterio: completar misión y terminar en CHARGING.', 9.30, 5.52, 2.45, 0.14, { fontSize: 8.2, bold: true, color: C.white, align: 'center' });
}

function phase1Results() {
  const s = pSlide('fase 1', 'PI gana el score operativo de la tarea completa', C.green, 'En la celda ya no basta seguir bien: importan tiempo activo, batería, riesgo y estabilidad.');
  const modes = [...(phase1.modes || [])].sort((a, b) => Number(a.score || 0) - Number(b.score || 0));
  const best = modes[0] || {};
  roundRect(s, 0.78, 1.58, 3.55, 4.82, C.navy, C.navy);
  addText(s, 'CONTROL SELECCIONADO', 1.06, 1.92, 2.25, 0.16, { fontSize: 7.8, bold: true, color: C.cyan });
  addText(s, best.mode || 'PI', 1.03, 2.28, 1.42, 0.62, { fontFace: 'Aptos Display', fontSize: 48, bold: true, color: C.white });
  addText(s, 'mejor balance operativo', 1.08, 3.05, 2.55, 0.24, { fontSize: 12.0, bold: true, color: C.white });
  addText(s, `score ${fmt(best.score, 3)}\nduración ${fmt(best.duration_s, 1)} s\nbatería ${fmt(best.battery_used_pct, 1)} %`, 1.08, 3.62, 2.60, 0.72, { fontSize: 10.8, color: 'DFF7F2' });
  line(s, 1.08, 4.72, 3.66, 4.72, C.green, 1.4);
  addText(s, 'Todos los modos completan la misión y terminan en CHARGING; PI reduce tiempo activo y variación sin sacrificar pose.', 1.08, 5.02, 2.70, 0.62, { fontSize: 9.1, bold: true, color: C.white, fit: 'shrink' });
  const maxScore = Math.max(...modes.map(m => Number(m.score || 0))) || 1;
  modes.forEach((m, i) => {
    barMetric(s, m.mode, Number(m.score || 0), maxScore, 4.72, 1.72 + i * 0.36, 2.45, i === 0 ? C.green : C.line);
  });
  addImageFrame(s, img.phase1Metrics, 7.72, 1.55, 4.55, 2.52, 'métricas por modo', C.green);
  softPanel(s, 4.72, 3.58, 2.78, 0.55, C.green, C.white);
  addText(s, 'CRITERIOS DE SCORE', 4.92, 3.70, 1.30, 0.10, { fontSize: 6.8, bold: true, color: C.green });
  addText(s, 'tiempo · batería · riesgo · pose · suavidad', 4.92, 3.90, 2.25, 0.10, { fontSize: 6.8, color: C.ink, fit: 'shrink' });
  addImageFrame(s, img.phase1, 4.62, 4.35, 4.05, 1.90, 'trayectoria y señales', C.teal);
  pFormula(s, 'Criterio de score', `score = combinación normalizada de duración, batería, riesgo, pose y suavidad`, 8.92, 4.38, 3.10, 1.45, C.green, 8.8);
}

function slamPipeline() {
  const s = pSlide('SLAM', 'Estimación, mapa, planificación y control en ciclo cerrado', C.teal, 'La estimación alimenta el planner local y el planner vuelve al control diferencial de ruedas.');
  addImageFrame(s, img.phase1EstimatorPipeline, 0.70, 1.58, 8.10, 4.85, 'pipeline de estimación y control', C.teal);
  pFormula(s, 'Predicción', 'x_k^- = f(x_{k-1}, u_k)\nP_k^- = F_k P_{k-1} F_k^T + Q_k', 9.15, 1.78, 2.82, 0.95, C.teal, 8.2);
  pFormula(s, 'Corrección', 'K_k = P_k^- H_k^T (H_k P_k^- H_k^T + R_k)^-1\nx_k = x_k^- + K_k(z_k - h(x_k^-))', 9.15, 3.05, 2.82, 1.20, C.violet, 7.0);
  pFormula(s, 'Mapa', 'landmark/celda -> planner -> waypoint local', 9.15, 4.62, 2.82, 0.90, C.green, 8.2);
}

function lidarMethods() {
  const s = pSlide('SLAM LiDAR', 'GMapping, Hector y Cartographer', C.violet, 'Tres formas de usar lecturas tipo LiDAR simuladas sobre el mismo recorrido.');
  pFormula(s, 'Lectura LiDAR', 'z_i = [rho_i, phi_i]\np_i^W = R(theta)p_i^R + p_R', 0.75, 1.65, 3.55, 1.25, C.teal, 10.0);
  pFormula(s, 'GMapping', 'l_t(m)=l_{t-1}(m)+logit(P(m|z_t,x_t))-l_0\n\nactualiza grilla de ocupación.', 4.90, 1.65, 3.55, 1.25, C.orange, 8.7);
  pFormula(s, 'Hector', 'x* = argmin_x sum_i [1 - M(T(x)p_i)]^2\n\nscan matching contra grilla.', 9.05, 1.65, 3.55, 1.25, C.cyan, 8.7);
  pFormula(s, 'Cartographer', 'scans locales -> submap\nscan-to-submap constraints\nloop closure si error < umbral', 0.75, 3.42, 3.55, 1.35, C.violet, 9.2);
  addImageFrame(s, img.slamOverview, 4.90, 3.28, 3.55, 2.10, 'resumen visual', C.green);
  addImageFrame(s, img.slamTimeline, 9.05, 3.28, 3.55, 2.10, 'línea de tiempo', C.orange);
  pFormula(s, 'Salida comparable', 'RMSE + P95 + max + celdas/landmarks/submaps + batería.', 1.05, 6.05, 11.15, 0.72, C.green, 8.4);
}

function kalman() {
  const s = pSlide('Kalman landmarks', 'Predicción, asociación y corrección', C.green, 'El modo Kalman landmark mantiene landmarks puntuales y corrige la pose cuando la medición se asocia con un punto conocido.');
  pFormula(s, '1 · Predicción', 'x_k^- = f(x_{k-1}, u_k)\nP_k^- = F_k P_{k-1} F_k^T + Q_k', 0.75, 1.65, 3.65, 1.28, C.teal, 9.8);
  pFormula(s, '2 · Asociación', 'si ||z_i - l_j|| < umbral: usar j\nsi no: crear nuevo landmark', 4.85, 1.65, 3.65, 1.28, C.orange, 9.8);
  pFormula(s, '3 · Corrección', 'K_k = P_k^-H_k^T(H_kP_k^-H_k^T+R_k)^-1\nx_k = x_k^- + K_k(z_k-h(x_k^-))', 8.95, 1.65, 3.65, 1.28, C.violet, 8.7);
  addImageFrame(s, img.slamEstimator, 0.92, 3.52, 5.65, 2.42, 'desempeño del estimador', C.green);
  pFormula(s, 'Lectura', 'Kalman landmarks obtiene el menor RMSE en esta celda compacta. Cartographer representa mejor estructura de mapa por submaps y cierre de ciclo.', 7.05, 3.72, 4.85, 1.58, C.green, 9.2);
  pStat(s, '0.0316', 'mejor RMSE [m]', 7.25, 5.70, C.green, 1.8);
  pStat(s, '16', 'landmarks finales', 9.35, 5.70, C.green, 1.8);
}

function slamResults() {
  const s = pSlide('benchmark SLAM', 'Cuatro modos en la misma celda', C.green, 'Implementaciones reducidas en CoppeliaSim, comparadas con las mismas señales y recorrido.');
  const modes = [...slamModes].sort((a, b) => Number(a.rmse_position_m || 0) - Number(b.rmse_position_m || 0));
  const palette = [C.green, C.violet, C.teal, C.orange];
  const best = modes[0] || {};
  roundRect(s, 0.78, 1.58, 3.05, 2.42, C.navy, C.navy);
  addText(s, 'MEJOR RMSE', 1.02, 1.88, 1.20, 0.14, { fontSize: 7.6, bold: true, color: C.cyan });
  addText(s, slamName(best.mode), 1.02, 2.22, 2.10, 0.30, { fontFace: 'Aptos Display', fontSize: 21, bold: true, color: C.white });
  addText(s, fmt(best.rmse_position_m, 4), 1.02, 2.78, 1.32, 0.42, { fontFace: 'Aptos Display', fontSize: 32, bold: true, color: C.green });
  addText(s, 'm RMSE', 2.36, 2.98, 0.80, 0.14, { fontSize: 8.0, color: 'DFF7F2' });
  addText(s, `P95 ${fmt(best.p95_position_error_m, 4)} · max ${fmt(best.max_position_error_m, 4)}`, 1.02, 3.42, 1.95, 0.14, { fontSize: 7.7, color: 'DFF7F2' });
  modes.forEach((m, i) => {
    const x = 4.20 + i * 2.02;
    const color = palette[i] || C.teal;
    roundRect(s, x, 1.62, 1.72, 2.28, i === 0 ? tint(color) : C.white, color);
    addText(s, `#${i + 1}`, x + 0.14, 1.84, 0.36, 0.13, { fontSize: 8.0, bold: true, color });
    addText(s, slamName(m.mode), x + 0.14, 2.10, 1.32, 0.22, { fontFace: 'Aptos Display', fontSize: 14.8, bold: true, color: C.ink });
    addText(s, fmt(m.rmse_position_m, 4), x + 0.14, 2.62, 0.94, 0.28, { fontFace: 'Aptos Display', fontSize: 21, bold: true, color });
    addText(s, 'RMSE [m]', x + 1.02, 2.73, 0.52, 0.11, { fontSize: 6.7, color: C.muted });
    addText(s, `P95 ${fmt(m.p95_position_error_m, 4)}`, x + 0.14, 3.10, 1.20, 0.12, { fontSize: 7.0, color: C.muted });
    const featureText = m.cartographer_submaps_final
      ? `${m.cartographer_submaps_final} submaps · ${m.loop_closures_final || 0} cierre`
      : `${m.map_features_final ?? '-'} features`;
    addText(s, featureText, x + 0.14, 3.38, 1.32, 0.14, { fontSize: 7.0, bold: true, color });
  });
  addImageFrame(s, img.slamAlgorithms, 0.78, 4.28, 6.10, 1.95, 'trayectoria, error y mapa', C.green);
  const maxRmse = Math.max(...modes.map(m => Number(m.rmse_position_m || 0))) || 1;
  addText(s, 'RANKING POR RMSE', 6.55, 4.22, 2.2, 0.16, { fontSize: 8.0, bold: true, color: C.green });
  modes.forEach((m, i) => {
    barMetric(s, slamName(m.mode), Number(m.rmse_position_m || 0), maxRmse, 6.55, 4.58 + i * 0.36, 0.62, palette[i] || C.teal, ' m');
  });
  darkInsight(s, 'Lectura técnica', 'Kalman minimiza error de pose; Cartographer aporta estructura de mapa por submaps y cierre de ciclo.', 10.30, 4.22, 2.10, 1.45, C.green);
}

function slamVisual() {
  const s = pSlide('evidencia SLAM', 'Trayectoria, error, mapa y métricas en una vista', C.green, 'Todos los modos se ejecutan sobre la misma escena, recorrido y señales exportadas.');
  addImageFrame(s, img.slamAlgorithms, 0.70, 1.55, 7.30, 4.90, 'benchmark visual', C.green);
  pBullet(s, 'Todos los modos completan la misión.', 8.45, 1.95, C.green, 3.7);
  pBullet(s, 'El error queda en escala de centímetros.', 8.45, 2.90, C.teal, 3.7);
  pBullet(s, 'Cartographer muestra submaps y cierre de ciclo simplificado.', 8.45, 3.85, C.violet, 3.7);
  pBullet(s, 'Kalman landmark da menor RMSE en esta celda.', 8.45, 4.80, C.orange, 3.7);
}

function finalDecision() {
  const s = pSlide('cumplimiento', 'Checklist final contra la guía', C.navy, 'Cada requisito queda conectado con implementación, ecuaciones y evidencia exportada.');
  const spine = [
    ['1', 'Pioneer/Lua', 'Follower y celda programados con cinemática diferencial y ruedas.', C.teal],
    ['2', 'Campos potenciales', 'F_att hacia p* detrás de Bill y F_rep para obstáculos.', C.orange],
    ['3', 'Anticolisión', '16 sensores, riesgo publicado y modo AVOIDING observado.', C.red],
    ['4', 'Celda robotizada', 'Tareas con Bill, estaciones, shelves, carga y FSM auditada.', C.green],
    ['5', 'Extensión técnica', 'P/PI/PID/LQR/NMPC, SLAM reducido, Kalman, logs y métricas.', C.violet],
  ];
  spine.forEach((it, i) => {
    const y = 1.60 + i * 0.70;
    roundRect(s, 0.92, y, 10.92, 0.50, C.white, it[3]);
    circle(s, 1.15, y + 0.16, 0.26, tint(it[3]), it[3]);
    addText(s, it[0], 1.21, y + 0.23, 0.14, 0.08, { fontSize: 7.4, bold: true, color: it[3], align: 'center' });
    addText(s, it[1], 1.62, y + 0.10, 1.62, 0.17, { fontSize: 9.6, bold: true, color: it[3] });
    addText(s, it[2], 3.40, y + 0.10, 7.55, 0.18, { fontSize: 9.4, color: C.ink });
  });
  roundRect(s, 1.00, 5.42, 10.75, 0.92, C.navy, C.navy);
  addText(s, 'CIERRE TÉCNICO', 1.30, 5.66, 1.55, 0.14, { fontSize: 7.8, bold: true, color: C.cyan });
  addText(s, 'La base de la guía está cubierta; las mejoras añaden trazabilidad, comparaciones cuantitativas y límites explícitos.', 3.00, 5.56, 7.90, 0.26, { fontSize: 11.2, bold: true, color: C.white });
}

function thanks() {
  const s = pptx.addSlide();
  slideNo += 1;
  s.background = { color: C.paper };
  rect(s, 0, 0, 13.333, 7.5, C.paper, C.paper);
  rect(s, 0, 0, 13.333, 0.08, C.violet, C.violet);
  addText(s, 'Actividad 2', 0.82, 1.28, 2.2, 0.20, { fontSize: 9.5, bold: true, color: C.violet });
  addText(s, 'Preguntas', 0.82, 2.15, 5.4, 0.74, { fontFace: 'Aptos Display', fontSize: 42, bold: true, color: C.ink });
  addText(s, 'Escena, informe, presentación, video y métricas provienen de la misma simulación.', 0.86, 3.12, 6.1, 0.34, { fontSize: 12, color: C.muted });
  addImageFrame(s, img.simVideoCover, 7.05, 1.20, 4.90, 4.45, 'replay de cierre', C.violet);
  addText(s, `${slideNo}/${TOTAL}`, 11.85, 6.92, 0.55, 0.16, { fontSize: 7.4, bold: true, color: C.muted, align: 'right' });
}

const slideFns = [
  cover,
  route,
  evidence,
  followerSetup,
  geometry,
  kinematics,
  potential,
  classicalControl,
  lqr,
  nmpc,
  followerResults,
  wheelCost,
  missionSection,
  missionLoop,
  phase1Results,
  slamPipeline,
  lidarMethods,
  kalman,
  slamResults,
  slamVisual,
  finalDecision,
  thanks,
];

const maxSlides = Number(process.env.A2_PPT_MAX_SLIDES || slideFns.length);
slideFns.slice(0, Math.max(0, Math.min(maxSlides, slideFns.length))).forEach((fn) => fn());

(async () => {
  await pptx.writeFile({ fileName: OUT });
  console.log(`Wrote ${OUT}`);
})().catch((err) => {
  console.error(err);
  process.exitCode = 1;
});

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
const TOTAL = 39;

pptx.defineLayout({ name: 'WIDE', width: 13.333, height: 7.5 });
pptx.layout = 'WIDE';
pptx.author = 'Jorge Luis Mayorga Taborda';
pptx.company = 'Universidad Internacional de Valencia';
pptx.subject = 'Actividad 2 - Pioneer seguimiento y SLAM en CoppeliaSim';
pptx.title = 'Actividad 2 - Pioneer P3DX con control y SLAM';
pptx.lang = 'es-ES';
pptx.theme = { headFontFace: 'Aptos Display', bodyFontFace: 'Aptos', lang: 'es-ES' };

const C = {
  ink: '0F1A2A',
  muted: '5E6C7A',
  line: 'C9D5E0',
  paper: 'F3F6F8',
  warmPaper: 'FAF7F3',
  panel: 'FCFDFE',
  panelEdge: 'D7E0E8',
  navy: '071826',
  steel: '24364A',
  teal: '1F7A8C',
  cyan: '2DB7E5',
  blue: '2B6CB0',
  green: '2A9D8F',
  amber: 'F4A261',
  red: 'B91C1C',
  violet: '6D5BD0',
  orange: 'C97A5C',
  orangeDark: '7F422F',
  orangeSoft: 'F3CBB9',
  white: 'FFFFFF',
  charcoal: '0F1A2A',
};

const TINT = {
  [C.teal]: 'E6F4F6',
  [C.cyan]: 'EAF7FC',
  [C.blue]: 'EAF1FB',
  [C.green]: 'EAF7F4',
  [C.amber]: 'FFF3E6',
  [C.red]: 'FDECEC',
  [C.violet]: 'F0EEFB',
  [C.orange]: 'FBE8DF',
  [C.navy]: 'E9EEF5',
};

const img = {
  cover: path.join(ROOT, 'actividad2', 'figures', 'cover.png'),
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
  phase2Algorithms: path.join(COP, 'phase2_slam_logs', 'phase2_slam_unknown_algorithm_comparison.png'),
  phase2Snapshots: path.join(COP, 'phase2_slam_logs', 'phase2_slam_mapping_snapshots.png'),
  phase2Overview: path.join(COP, 'phase2_slam_logs', 'phase2_slam_unknown_overview.png'),
  phase2Signals: path.join(COP, 'phase2_slam_logs', 'phase2_slam_unknown_signals.png'),
  phase2TrajectoryCrop: path.join(ASSETS, 'phase2_unknown_trajectory_crop.png'),
  phase2EvidenceCrop: path.join(ASSETS, 'phase2_unknown_evidence_crop.png'),
  phase2ErrorCrop: path.join(ASSETS, 'phase2_unknown_error_crop.png'),
  phase1Layout: path.join(FIG, 'phase1_layout_diagram.png'),
  phase1Overview3d: path.join(FIG, 'coppeliasim_phase1_overview_oriented.png'),
  phase1SensorRays3d: path.join(FIG, 'coppeliasim_phase1_sensor_rays_avoidance_oriented.png'),
  phase1BillWorking3d: path.join(FIG, 'coppeliasim_phase1_bill_working_oriented.png'),
  phase1Handoff3d: path.join(FIG, 'coppeliasim_phase1_handoff_t1_oriented.png'),
  phase2Initial3d: path.join(FIG, 'coppeliasim_phase2_initial_unknown_oriented.png'),
  phase2Replan3d: path.join(FIG, 'coppeliasim_phase2_replan_dynamic_oriented.png'),
  phase2Reconstruction: path.join(COP, 'phase2_slam_logs', 'phase2_slam_unknown_reconstruction_t60.png'),
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
const phase2Metrics = readJson(path.join(COP, 'phase2_slam_logs', 'phase2_slam_unknown_algorithm_metrics.json'));
const phase2Modes = Array.isArray(phase2Metrics.modes)
  ? phase2Metrics.modes
  : Object.entries(phase2Metrics).map(([mode, values]) => ({ mode, ...values }));

function fmt(value, digits = 3) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) return '-';
  return Number(value).toFixed(digits);
}

function getMode(mode) {
  return (follower.modes || []).find(m => m.mode === mode) || {};
}

function slamName(mode) {
  const names = {
    GMAPPING_GRID: 'Log-odds',
    HECTOR_GRID_MATCHING: 'Scan-to-map',
    CARTOGRAPHER_SUBMAP: 'Submapas',
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
    rectRadius: 0.07,
    fill: { color: fill },
    line: { color: lineColor, width: 0.42 },
    shadow: { type: 'outer', color: '9BA8B4', opacity: 0.08, blur: 1.3, angle: 45, offset: 0.7 },
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
  rect(slide, 0, 7.04, 13.333, 0.46, C.panel, C.panel, 4);
  line(slide, 0.58, 7.05, 12.20, 7.05, C.line, 0.55);
  rect(slide, 0.58, 7.21, 0.28, 0.05, C.orange, C.orange);
  addText(slide, 'Actividad 2 - Sistemas Robóticos Móviles', 0.58, 7.14, 3.7, 0.16, { fontSize: 7.0, color: C.muted });
  addText(slide, 'Pioneer P3DX · CoppeliaSim y Lua · seguimiento + SLAM', 8.48, 7.14, 3.28, 0.16, { fontSize: 7.0, color: C.muted, align: 'right' });
  roundRect(slide, 12.25, 7.06, 0.50, 0.22, C.orangeSoft, C.orangeSoft, 0);
  addText(slide, `${slideNo}/${TOTAL}`, 12.30, 7.09, 0.40, 0.10, { fontSize: 6.9, bold: true, color: C.ink, align: 'center' });
}

function sectionRail(slide) {
  const sections = [
    { label: 'Escena', color: C.teal, active: slideNo <= 10 },
    { label: 'Control', color: C.orange, active: slideNo >= 11 && slideNo <= 21 },
    { label: 'SLAM', color: C.violet, active: slideNo >= 22 && slideNo <= 28 },
    { label: 'Fase 2', color: C.green, active: slideNo >= 29 && slideNo <= 37 },
    { label: 'Cierre', color: C.orange, active: slideNo >= 38 },
  ];
  sections.forEach((sec, i) => {
    const x = 6.52 + i * 1.05;
    const color = sec.active ? sec.color : C.muted;
    roundRect(slide, x, 0.93, 0.92, 0.18, sec.active ? tint(sec.color) : 'EEF2F5', sec.active ? sec.color : C.line);
    addText(slide, sec.label, x + 0.04, 0.965, 0.84, 0.07, {
      fontSize: 4.6,
      bold: true,
      color,
      align: 'center',
      fit: 'shrink',
    });
  });
}

function pSlide(kicker, title, color = C.teal, subtitle = '') {
  const s = pptx.addSlide();
  slideNo += 1;
  s.background = { color: C.warmPaper };
  rect(s, 0, 0, 13.333, 7.5, C.warmPaper, C.warmPaper);
  // Clean single-tone header band (no transparent overlay: the previous 90%-transparent
  // navy box rendered as a muddy box that looked out of frame in some viewers).
  rect(s, 0, 0, 13.333, 0.92, C.orangeSoft, C.orangeSoft);
  rect(s, 0, 0.895, 13.333, 0.03, C.orange, C.orange);
  rect(s, 0, 0, 0.18, 7.5, C.white, C.white);
  roundRect(s, 0.50, 1.18, 12.56, 5.88, C.steel, C.steel, 88);
  roundRect(s, 0.38, 1.10, 12.56, 5.88, C.panel, C.panelEdge, 0);
  rect(s, 0.38, 1.10, 0.08, 5.88, C.orange, C.orange);
  rect(s, 0.46, 1.10, 0.22, 5.88, 'F7E1D6', 'F7E1D6', 0);
  addText(s, kicker, 0.58, 0.14, 4.3, 0.16, { fontSize: 7.7, bold: true, color: C.ink });
  addText(s, title, 0.58, 0.41, 9.9, 0.38, { fontFace: 'Aptos Display', fontSize: 22.5, bold: true, color: C.ink, fit: 'shrink' });
  roundRect(s, 10.20, 0.33, 2.18, 0.25, C.panel, C.panel, 62);
  addText(s, 'Pioneer P3DX · CoppeliaSim · SLAM', 10.15, 0.39, 2.06, 0.11, { fontSize: 6.6, bold: true, color: C.ink, align: 'right' });
  sectionRail(s);
  if (subtitle) addText(s, subtitle, 0.62, 1.20, 11.6, 0.26, { fontSize: 10.6, color: C.muted, fit: 'shrink' });
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
  softPanel(slide, x, y, w, 1.05, color, tint(color), color);
  rect(slide, x, y, 0.08, 1.05, color, color);
  addText(slide, value, x + 0.18, y + 0.13, w - 0.36, 0.28, { fontFace: 'Aptos Display', fontSize: 18.5, bold: true, color, fit: 'shrink' });
  addText(slide, label, x + 0.18, y + 0.49, w - 0.36, 0.16, { fontSize: 8.7, bold: true, color: C.ink, fit: 'shrink' });
  addText(slide, note, x + 0.18, y + 0.71, w - 0.36, 0.20, { fontSize: 7.7, color: C.muted, fit: 'shrink' });
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
  s.background = { color: C.warmPaper };
  rect(s, 0, 0, 13.333, 7.5, C.warmPaper, C.warmPaper);
  slideAddImageFit(s, img.phase1Overview3d, -0.83, 0, 15.00, 7.50, false);
  rect(s, 0, 0, 5.85, 7.50, C.navy, C.navy, 18);
  rect(s, 5.85, 0, 7.48, 7.50, C.navy, C.navy, 84);
  rect(s, 0, 0, 0.18, 7.50, C.orange, C.orange);
  addText(s, 'UNIVERSIDAD INTERNACIONAL DE VALENCIA', 0.70, 0.62, 4.30, 0.18, { fontSize: 7.1, bold: true, color: C.white });
  addText(s, 'Pioneer P3DX\nen CoppeliaSim y Lua', 0.70, 1.34, 4.82, 1.02, { fontFace: 'Aptos Display', fontSize: 28.5, bold: true, color: C.white });
  addText(s, 'Celda de almacén con R1, Bill, herramientas T1/T2, evitación reactiva, control y SLAM.', 0.74, 2.92, 4.72, 0.52, { fontSize: 10.8, color: C.white });
  line(s, 0.74, 3.70, 4.90, 3.70, C.orangeSoft, 1.2);
  methodChip(s, 'Fase 1', 0.74, 4.04, C.teal, 1.05);
  methodChip(s, 'Fase 2', 2.02, 4.04, C.violet, 1.05);
  methodChip(s, 'SLAM', 3.30, 4.04, C.green, 0.92);
  addText(s, 'Autor: Jorge Luis Mayorga Taborda\nProfesor: Jose I. Iñiguez\n26 de mayo de 2026', 0.74, 5.36, 4.30, 0.52, { fontSize: 9.0, color: C.white });
  addText(s, 'Fondo: captura real de CoppeliaSim', 8.82, 6.60, 3.10, 0.14, { fontSize: 7.2, bold: true, color: C.white, align: 'right' });
  addText(s, `${slideNo}/${TOTAL}`, 11.85, 6.92, 0.55, 0.16, { fontSize: 7.4, bold: true, color: C.white, align: 'right' });
}

function agendaSlide() {
  const s = pSlide('ruta técnica', 'Ruta del trabajo', C.orange, 'Ordenada para conectar especificación, implementación, métricas y conclusiones.');
  const items = [
    ['01', 'Problema y escena', 'mannequin/Bill, almacén, R1, T1/T2 y métricas', C.teal],
    ['02', 'Arquitectura y código', 'funciones Lua, FSM, sensores, planner y logger', C.orange],
    ['03', 'Control de seguimiento', 'P, PI, PID, LQR y NMPC con coste y pesos definidos', C.blue],
    ['04', 'SLAM y Fase 2', 'Kalman, grids log-odds, scan-to-map y submapas simplificados', C.violet],
    ['05', 'Resultados', 'limitaciones, elección técnica y trabajo futuro', C.green],
  ];
  items.forEach((it, i) => {
    const x = 0.82 + i * 2.48;
    softPanel(s, x, 2.18, 2.12, 3.46, it[3], tint(it[3]));
    addText(s, it[0], x + 0.20, 2.56, 1.30, 0.30, { fontFace: 'Aptos Display', fontSize: 22, bold: true, color: it[3] });
    addText(s, it[1], x + 0.20, 3.38, 1.58, 0.34, { fontSize: 11.2, bold: true, color: C.ink, fit: 'shrink' });
    addText(s, it[2], x + 0.20, 4.36, 1.64, 0.52, { fontSize: 8.0, color: C.ink, fit: 'shrink' });
  });
  darkInsight(s, 'Orden', 'Cada bloque separa implementación, medición y limitaciones técnicas.', 0.92, 6.18, 11.75, 0.56, C.orange);
}

function missionMapSlide() {
  const s = pSlide('ruta B1/R1 y puntos de misión', 'Mapa operativo de la celda', C.teal, 'La escena se organiza alrededor del rack T1/T2, mesas WS1/WS2, Bill, R1 y la estación de carga.');
  line(s, 0.72, 1.42, 9.15, 1.42, C.teal, 0.9);
  addText(s, 'vista superior de la celda y flujo B1/R1', 0.76, 1.22, 4.20, 0.14, { fontSize: 8.0, bold: true, color: C.teal });
  slideAddImageFit(s, img.phase1Layout, 0.72, 1.48, 8.72, 4.85, false);
  addText(s, 'Secuencia', 9.66, 1.68, 2.20, 0.22, { fontSize: 15.0, bold: true, color: C.ink });
  [
    ['R1 parte de carga y toma T1 en el rack.', C.teal],
    ['Bill trabaja en WS1 y después se atiende WS2.', C.green],
    ['La ruta evita pallet, pilar y caja durante el ciclo.', C.orange],
    ['Los estados exportados conectan misión, control y SLAM.', C.violet],
  ].forEach((row, i) => {
    const y = 2.26 + i * 0.58;
    circle(s, 9.72, y + 0.08, 0.10, row[1], row[1]);
    addText(s, row[0], 9.98, y, 2.85, 0.27, { fontSize: 8.8, color: C.ink, fit: 'shrink' });
  });
  line(s, 9.72, 5.34, 10.86, 5.34, C.orange, 1.0);
  addText(s, 'T1/T2', 9.72, 5.50, 1.10, 0.22, { fontFace: 'Aptos Display', fontSize: 19.0, bold: true, color: C.orange });
  addText(s, 'cola de herramientas', 9.72, 5.96, 1.48, 0.14, { fontSize: 8.0, color: C.ink });
  line(s, 11.42, 5.34, 12.58, 5.34, C.teal, 1.0);
  addText(s, 'R1/B1', 11.42, 5.50, 1.12, 0.22, { fontFace: 'Aptos Display', fontSize: 19.0, bold: true, color: C.teal });
  addText(s, 'robot y persona', 11.42, 5.96, 1.48, 0.14, { fontSize: 8.0, color: C.ink });
}

function route() {
  const s = pSlide('escenarios', 'Celda de almacén y mapa desconocido', C.teal, 'La misión principal se evalúa en una celda de almacén; Fase 2 valida el caso de mapa desconocido.');
  const rows = [
    ['1', 'Sim_T2_Phase1_Basic.ttt', 'R1, Bill, T1 y T2, batería, sensores y Kalman', 'escena principal'],
    ['2', 'Sim_T2_Phase2_SLAM_Unknown.ttt', 'mapa desconocido, obstáculos no modelados y replanificación', 'Fase 2'],
    ['3', 'Actividad2_1_Basic_Follower.ttt', 'seguimiento de Bill y controladores P, PI, PID, LQR y NMPC', 'seguimiento'],
    ['4', 'Resultados generados', 'mismo orden técnico: seguimiento, Fase 1 y Fase 2', 'análisis'],
    ['5', 'CSV y JSON de logs', 'métricas de control, SLAM, batería, riesgo y reconstrucción', 'datos'],
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
  metricTile(s, '4/4', 'tareas', 'ciclo T1 y T2 completo', 0.90, 5.72, 1.85, C.violet);
  metricTile(s, '16', 'sensores', 'Pioneer + rayos visibles', 3.00, 5.72, 1.85, C.teal);
  metricTile(s, '4', 'SLAM', 'Kalman, log-odds, scan-to-map, submapas', 5.10, 5.72, 2.25, C.green);
  metricTile(s, 'OK', 'métricas', 'datos, gráficas y replay', 7.60, 5.72, 2.05, C.orange);
  metricTile(s, 'P2', 'mapa desconocido', 'obstáculos y recuperación', 9.90, 5.72, 2.30, C.cyan);
}

function evidence() {
  const s = pSlide('experimento', 'Simulación y datos exportados', C.orange, 'Los resultados se separan por escenario para no mezclar seguimiento, Fase 1 y Fase 2.');
  addImageFrame(s, img.followerReplay, 0.72, 1.72, 5.85, 4.10, 'Parte 1: seguimiento de Bill', C.teal);
  addVideoPanel(s, img.simVideo, img.simVideoCover, 6.92, 1.72, 5.85, 4.10, 'Parte 2: misión en celda + SLAM');
  pFormula(s, 'Exportación', 'escena .ttt -> script Lua -> señales CoppeliaSim -> CSV y JSON -> gráficas', 1.10, 6.02, 11.15, 0.72, C.orange, 9.2);
}

function problemSlide() {
  const s = pSlide('problema', 'Navegación autónoma en una celda de almacén', C.teal, 'El Pioneer sigue al mannequin de la especificación, implementado como Bill/B1 en la escena.');
  const cards = [
    ['Problema', 'Coordinar seguimiento, cinemática diferencial, seguridad local y tareas T1/T2 en una escena con persona móvil.', C.teal],
    ['Implementación', 'Campos potenciales, FSM de misión, sensores de proximidad, estimación Kalman y control de ruedas.', C.green],
    ['Mapa', 'Comparación de P/PI/PID/LQR/NMPC y métodos SLAM con mapa conocido y desconocido.', C.violet],
  ];
  cards.forEach((it, i) => {
    const x = 0.82 + i * 4.05;
    line(s, x, 1.86, x, 2.92, it[2], 1.2);
    addText(s, it[0], x + 0.22, 1.98, 3.0, 0.20, { fontSize: 12.0, bold: true, color: it[2] });
    addText(s, it[1], x + 0.22, 2.40, 3.05, 0.48, { fontSize: 9.3, color: C.ink });
  });
  pFormula(s, 'Nomenclatura', 'mannequin de la especificación = Bill/B1 en CoppeliaSim; el requisito de seguimiento no cambia.', 0.92, 3.18, 11.60, 0.46, C.blue, 8.5);
  addText(s, 'Objetivos evaluados', 0.92, 4.00, 3.0, 0.22, { fontSize: 13.0, bold: true, color: C.ink });
  [
    ['Regular distancia y orientación respecto a Bill mediante un punto p*.', C.teal],
    ['Ejecutar entregas T1/T2 con una máquina de estados reproducible.', C.green],
    ['Evitar obstáculos con sensores, reducción de velocidad y recuperación.', C.orange],
    ['Comparar controladores y SLAM con métricas comunes.', C.violet],
  ].forEach((it, i) => {
    const y = 4.55 + i * 0.48;
    circle(s, 1.22, y + 0.08, 0.11, it[1], it[1]);
    addText(s, it[0], 1.48, y + 0.09, 9.9, 0.12, { fontSize: 8.5, color: C.ink });
  });
}

function experimentalSetupSlide() {
  const s = pSlide('método experimental', 'Escenarios, señales y métricas', C.orange, 'La geometría, sensores y tareas se mantienen constantes; cambia la ley de control o el método de mapeo.');
  const blocks = [
    ['Seguimiento', 'Bill define la referencia móvil p*. Se comparan P, PI, PID, LQR y NMPC.', C.teal],
    ['Misión T1/T2', 'R1 entrega herramientas, espera trabajo de Bill y finaliza en carga.', C.green],
    ['Mapa desconocido', 'R1 reconstruye obstáculos a partir de rayos de proximidad durante la ejecución.', C.violet],
  ];
  blocks.forEach((it, i) => {
    const x = 0.82 + i * 4.05;
    softPanel(s, x, 1.72, 3.55, 1.48, it[2], tint(it[2]));
    addText(s, it[0], x + 0.22, 1.98, 3.0, 0.20, { fontSize: 11.2, bold: true, color: it[2] });
    addText(s, it[1], x + 0.22, 2.40, 3.05, 0.44, { fontSize: 9.0, color: C.ink });
  });
  addText(s, 'Variables medidas', 0.92, 4.00, 3.0, 0.22, { fontSize: 13.0, bold: true, color: C.ink });
  metricTile(s, 'error', 'seguimiento y pose', 'distancia, rumbo, RMSE y P95', 1.00, 4.55, 2.30, C.teal);
  metricTile(s, 'control', 'esfuerzo', 'energía, suavidad y saturaciones', 3.85, 4.55, 2.30, C.blue);
  metricTile(s, 'seguridad', 'obstáculos', 'distancia mínima y riesgo', 6.70, 4.55, 2.30, C.orange);
  metricTile(s, 'mapa', 'SLAM', 'landmarks, celdas, submapas y updates', 9.55, 4.55, 2.60, C.violet);
}

function codeBox(slide, title, code, x, y, w, h, color) {
  softPanel(slide, x, y, w, h, color, tint(color));
  addText(slide, title, x + 0.18, y + 0.18, w - 0.36, 0.16, { fontSize: 8.2, bold: true, color });
  addText(slide, code, x + 0.18, y + 0.48, w - 0.36, h - 0.60, { fontFace: 'Cascadia Mono', fontSize: 6.8, color: C.ink, fit: 'shrink' });
}

function integratedArchitecture() {
  const s = pSlide('arquitectura', 'Sensores, estimación, mapa y control en ciclo cerrado', C.teal, 'La misma arquitectura alimenta seguimiento, misión T1/T2, evitación y SLAM.');
  [['sensores','16 ultrasonidos + rayos',C.teal],['estimador','odometría + corrección',C.green],['mapa','landmarks, grid o submapas',C.violet],['planner','ruta directa o SLAM_WAYPOINT',C.orange],['control','P/PI/PID, LQR o NMPC',C.blue]].forEach((st,i)=>{
    const x=0.68+i*2.52; line(s,x,1.80,x,2.47,st[2],1.1);
    addText(s,st[0],x+0.16,1.77,1.70,0.16,{fontSize:8.8,bold:true,color:st[2]});
    addText(s,st[1],x+0.16,2.03,1.62,0.22,{fontSize:7.1,color:C.ink});
    if(i<4) line(s,x+2.10,2.02,x+2.42,2.02,C.ink,1.0,true);
  });
  for (let i = 0; i <= 12; i++) line(s, 0.96 + i * 0.96, 3.42, 0.96 + i * 0.96, 5.62, C.line, 0.25);
  for (let i = 0; i <= 4; i++) line(s, 0.96, 3.42 + i * 0.55, 12.56, 3.42 + i * 0.55, C.line, 0.25);
  drawPioneer(s,2.05,4.58,0.78,C.teal,'R1'); drawBill(s,11.10,4.90,0.70); rect(s,5.92,4.32,0.70,0.52,'FDECEC',C.red);
  line(s,2.42,4.70,4.55,5.16,C.orange,1.3,true); line(s,4.55,5.16,6.80,4.98,C.orange,1.3,true); line(s,6.80,4.98,10.60,4.96,C.orange,1.3,true);
  line(s,2.42,4.40,4.30,3.90,C.violet,1.0,true,'dash'); line(s,4.30,3.90,7.62,3.96,C.violet,1.0,true,'dash');
  addText(s,'ruta nominal',6.60,5.18,1.05,0.12,{fontSize:7.2,bold:true,color:C.orange});
  addText(s,'SLAM_WAYPOINT',5.32,3.72,1.40,0.12,{fontSize:7.0,bold:true,color:C.violet});
  [
    ['readObstacleField', 'riesgo, giro y distancia mínima', C.teal, 0.92],
    ['registerSlamDetection', 'impacto sensor a mundo y mapa', C.violet, 3.78],
    ['plannedWaypointTo', 'ruta directa o punto intermedio', C.orange, 6.92],
    ['publishTelemetry', 'CSV/JSON de estado y mapa', C.green, 9.88],
  ].forEach(([title, body, color, x]) => {
    line(s, x, 6.18, x + 1.10, 6.18, color, 1.0);
    addText(s, title, x, 6.34, 2.15, 0.18, { fontSize: 8.2, bold: true, color, fit: 'shrink' });
    addText(s, body, x, 6.66, 2.20, 0.16, { fontSize: 7.0, color: C.ink, fit: 'shrink' });
  });
}

function coppeliaEvidence() {
  const s = pSlide('escena', 'CoppeliaSim: celda, sensores y trabajo humano', C.orange, 'Las capturas registran el comportamiento operativo de la escena.');
  addImageFrame(s,img.phase1Overview3d,0.70,1.44,5.95,2.28,'vista general de la celda',C.teal);
  addImageFrame(s,img.phase1SensorRays3d,6.88,1.44,5.95,2.28,'rayos de sensor y evitación',C.orange);
  addImageFrame(s,img.phase1BillWorking3d,0.70,4.12,5.95,2.28,'Bill trabajando frente a la mesa',C.green);
  addImageFrame(s,img.phase1Handoff3d,6.88,4.12,5.95,2.28,'interacción R1-Bill con T1',C.violet);
}

function scenarioScreenshots() {
  const s = pSlide('capturas', 'Escenarios visibles en CoppeliaSim', C.teal, 'Seguimiento, entrega, evitación, replanificación y mapa quedan registrados en capturas reales.');
  const shots = [
    [img.followerReplay, 'Seguimiento de Bill', C.teal],
    [img.phase1Overview3d, 'Fase 1: almacén', C.green],
    [img.phase1SensorRays3d, 'Evitación con rayos', C.orange],
    [img.phase1BillWorking3d, 'Bill en mesa', C.violet],
    [img.phase1Handoff3d, 'Entrega T1', C.blue],
    [img.phase2Initial3d, 'Fase 2 inicial', C.teal],
    [img.phase2Replan3d, 'Replanificación dinámica', C.orange],
    [img.phase2Overview, 'Mapa desconocido', C.green],
  ];
  shots.forEach((shot, i) => {
    const x = 0.62 + (i % 4) * 3.18;
    const y = i < 4 ? 1.36 : 4.06;
    addImageFrame(s, shot[0], x, y, 2.82, 2.22, shot[1], shot[2]);
  });
}

function videoPlaceholderFollower() {
  const s = pSlide('seguimiento y entrega', 'Video de ejecución I', C.teal, '');
  softPanel(s, 0.76, 1.32, 11.82, 5.20, C.teal, tint(C.teal), C.teal);
  slideAddImageFit(s, img.followerReplay, 1.08, 1.62, 11.18, 3.90);
  roundRect(s, 1.08, 5.62, 11.18, 0.58, 'F5FBFC', C.teal, 0);
  addText(s, 'Seguimiento de Bill, entrega T1/T2 y retorno a carga · figures/Video_Follower.mp4', 1.38, 5.76, 10.58, 0.28, { fontSize: 8.0, bold: true, color: C.teal, align: 'center' });
}

function videoPlaceholderPhase2() {
  const s = pSlide('Fase 2 y mapa desconocido', 'Video de ejecución II', C.violet, '');
  softPanel(s, 0.76, 1.32, 11.82, 5.20, C.violet, tint(C.violet), C.violet);
  slideAddImageFit(s, img.simVideoCover, 1.08, 1.62, 11.18, 3.90);
  roundRect(s, 1.08, 5.62, 11.18, 0.58, 'F8F6FF', C.violet, 0);
  addText(s, 'Exploración, obstáculos dinámicos, replanificación y SLAM · figures/Video_Task_And_Avoid_Obstacle.mp4', 1.38, 5.76, 10.58, 0.28, { fontSize: 8.0, bold: true, color: C.violet, align: 'center' });
}

function simulationReplaySlide() {
  const s = pSlide('replay', 'Replay de misión', C.violet, 'Secuencia de la misión: Bill, T1/T2, evitación, SLAM y cierre.');
  addVideoPanel(s, img.simVideo, img.simVideoCover, 0.78, 1.38, 7.55, 5.05, 'Replay de la misión de almacén');
  addText(s, 'Contenido visible', 8.78, 1.62, 2.80, 0.18, { fontSize: 14.0, bold: true, color: C.ink });
  [
    ['seguimiento de Bill con orientación frontal', C.teal],
    ['entregas T1/T2 dentro del almacén', C.green],
    ['evitación local con rayos de proximidad', C.orange],
    ['mapeo SLAM y cierre en estación de carga', C.violet],
  ].forEach((row, i) => {
    const y = 2.18 + i * 0.52;
    circle(s, 8.88, y + 0.09, 0.10, row[1], row[1]);
    addText(s, row[0], 9.12, y, 3.25, 0.20, { fontSize: 8.7, color: C.ink });
  });
  metricTile(s, 'MP4', 'replay', 'ejecución principal', 8.78, 4.62, 2.55, C.violet);
  metricTile(s, 'replay', 'secuencia', 'misión con logs exportados', 8.78, 5.76, 2.55, C.teal);
}

function codeChanges() {
  const s=pSlide('implementación','Funciones Lua integradas',C.green,'Cada función mantiene entrada, salida y responsabilidad definida.');
  const cards = [
    ['readObstacleField()', 'Lee 16 sensores, calcula risk, minObstacle, giro repulsivo y reducción de velocidad.', C.teal],
    ['registerSlamDetection(sensor,d,pt)', 'Transforma el impacto al marco global y actualiza landmark, celda log-odds o submapa.', C.violet],
    ['plannedWaypointTo(goal)', 'Comprueba si la ruta directa está bloqueada y devuelve SLAM_WAYPOINT o el objetivo final.', C.orange],
    ['deliverToolToBill(tool,ws,next)', 'Ejecuta la transición FSM: aproxima R1, entrega T1/T2, espera a Bill y registra estado.', C.green],
  ];
  cards.forEach((c, i) => {
    const x = i % 2 === 0 ? 0.92 : 6.96;
    const y = i < 2 ? 1.88 : 4.28;
    softPanel(s, x, y, 5.56, 1.62, c[2], tint(c[2]));
    addText(s, c[0], x + 0.22, y + 0.28, 5.05, 0.22, { fontFace: 'Cascadia Mono', fontSize: 10.0, bold: true, color: c[2], fit: 'shrink' });
    addText(s, c[1], x + 0.22, y + 0.78, 5.05, 0.46, { fontSize: 9.0, color: C.ink, fit: 'shrink' });
  });
  darkInsight(s, 'Salida', 'CSV/JSON: estado, ruedas, riesgo, batería, error de pose, mapa y actividad SLAM.', 0.92, 6.18, 11.72, 0.56, C.green);
}

function slamWaypoint() {
  const s=pSlide('planner local','Ruta directa o SLAM_WAYPOINT',C.violet,'El mapa añade un objetivo intermedio cuando la ruta directa queda bloqueada.');
  roundRect(s,0.82,1.42,7.40,4.90,C.paper,C.line); grid(s,1.00,1.70,7.00,4.20,10,7);
  drawPioneer(s,1.72,2.15,0.72,C.teal,'R1'); rect(s,4.10,3.10,0.82,0.64,'FDECEC',C.red); circle(s,7.12,5.08,0.22,C.green,C.green);
  line(s,2.02,2.38,6.98,5.13,C.orange,1.4,true); line(s,2.02,2.10,3.30,4.90,C.violet,1.2,true,'dash'); line(s,3.30,4.90,6.98,5.13,C.violet,1.2,true,'dash');
  pFormula(s,'Regla','si una celda persistente corta el segmento R1-goal:\n  usar punto lateral dentro del área útil\nsi no:\n  ruta directa',8.68,1.60,3.72,1.36,C.violet,8.4);
  pFormula(s,'Salida','plannedWaypointTo(goal)\nheading = atan2(dy,dx)-theta\ncontrolador diferencial mantiene evitación reactiva',8.68,3.46,3.72,1.34,C.teal,8.2);
  metricTile(s,'5,5 s','ventana','recuperación sin apagar evitación',8.68,5.52,1.80,C.orange);
  metricTile(s,'0,40 m','margen','separación deseada frente al mapa',10.82,5.52,1.80,C.green);
}

function slamKalmanLandmark() {
  const s = pSlide('SLAM', 'Kalman-landmark', C.green, 'Pose probabilística y mapa de puntos observados.');
  const flow = [
    ['odometría u_k', 0.86, 1.64, C.teal],
    ['predicción\nx-, P-', 3.00, 1.64, C.green],
    ['rayos z_i', 0.86, 3.06, C.orange],
    ['asociación\na landmark', 3.00, 3.06, C.violet],
    ['corrección EKF', 5.14, 2.24, C.green],
  ];
  flow.forEach(([txt, x, y, color]) => {
    roundRect(s, x, y, 1.62, 0.72, tint(color), color);
    addText(s, txt, x + 0.12, y + 0.18, 1.36, 0.25, { fontSize: 8.0, bold: true, color, align: 'center', fit: 'shrink' });
  });
  [[2.48, 2.00, 3.00, 2.00], [2.48, 3.42, 3.00, 3.42], [4.62, 3.42, 5.14, 2.70], [4.62, 2.00, 5.14, 2.45]].forEach(a => line(s, ...a, C.muted, 1.0, true));
  pFormula(s, 'Modelo', 'x_k^- = f(x_{k-1},u_k)\nP_k^- = F_k P_{k-1} F_k^T + Q_k\nK_k = P_k^-H_k^T(H_kP_k^-H_k^T+R_k)^-1', 7.42, 1.60, 4.25, 1.45, C.green, 8.2);
  pFormula(s, 'Uso en la simulación', 'Cada impacto de sensor se transforma al marco del almacén. Si coincide con un landmark existente corrige la pose; si no, crea un punto nuevo.', 7.42, 3.35, 4.25, 1.28, C.teal, 8.3);
  metricTile(s, '0,03142 m', 'RMSE Fase 1', 'mejor error de pose', 0.92, 5.30, 2.00, C.green);
  metricTile(s, '20-24', 'landmarks', 'según fase', 3.18, 5.30, 2.00, C.green);
  metricTile(s, 'límite', 'mapa puntual', 'no representa paredes como áreas', 5.44, 5.30, 2.00, C.orange);
}

function slamGmappingGrid() {
  const s = pSlide('SLAM', 'Grid log-odds inspirada en GMapping', C.orange, 'Ocupación por celdas usando la pose estimada; no incluye filtro de partículas.');
  softPanel(s, 0.82, 1.46, 5.60, 4.70, C.orange, C.white);
  for (let i = 0; i < 9; i += 1) line(s, 1.10 + i * 0.48, 1.76, 1.10 + i * 0.48, 5.70, C.line, 0.35);
  for (let i = 0; i < 8; i += 1) line(s, 1.10, 1.76 + i * 0.48, 5.10, 1.76 + i * 0.48, C.line, 0.35);
  circle(s, 1.55, 2.18, 0.20, C.teal, C.teal);
  line(s, 1.66, 2.24, 4.72, 4.58, C.orange, 1.2, true);
  [[2.10, 2.58], [2.58, 2.94], [3.06, 3.30], [3.54, 3.66]].forEach(([x, y]) => rect(s, x, y, 0.26, 0.26, 'E6F4F6', C.teal));
  [[4.50, 4.32], [4.86, 4.68], [4.86, 4.32]].forEach(([x, y]) => rect(s, x, y, 0.30, 0.30, 'FBE8DF', C.orange));
  pFormula(s, 'Actualización', 'L_t(c)=clip(L_{t-1}(c)+l(c|z_t,x_t))\n\nceldas del rayo -> libres\ncelda de impacto -> ocupada', 7.20, 1.60, 4.60, 1.70, C.orange, 8.4);
  pFormula(s, 'Alcance', 'La versión Lua implementa actualización de ocupación por log-odds. No es GMapping completo: no hay filtro de partículas ni árbol de trayectorias.', 7.20, 3.62, 4.60, 1.18, C.green, 7.6);
  metricTile(s, '94', 'celdas', 'ocupadas Fase 1', 0.92, 5.30, 1.80, C.orange);
  metricTile(s, '36', 'rasgos', 'Fase 2', 3.02, 5.30, 1.80, C.orange);
  metricTile(s, 'límite', 'depende', 'de la pose usada para trazar rayos', 5.12, 5.30, 1.95, C.red);
}

function slamHectorMatching() {
  const s = pSlide('SLAM', 'Scan-to-map inspirado en Hector', C.teal, 'Corrección local de pose por encaje contra la grid.');
  softPanel(s, 0.82, 1.46, 5.60, 4.70, C.teal, C.white);
  for (let i = 0; i < 9; i += 1) line(s, 1.10 + i * 0.48, 1.76, 1.10 + i * 0.48, 5.70, C.line, 0.35);
  for (let i = 0; i < 8; i += 1) line(s, 1.10, 1.76 + i * 0.48, 5.10, 1.76 + i * 0.48, C.line, 0.35);
  [[4.20, 4.45], [4.68, 4.45], [4.68, 3.97], [4.20, 3.49], [3.72, 3.49]].forEach(([x, y]) => rect(s, x, y, 0.26, 0.26, 'EAF7F4', C.teal));
  [[1.58, 2.22, C.green], [1.74, 2.36, C.orange], [1.42, 2.38, C.violet]].forEach(([x, y, color]) => circle(s, x, y, 0.22, 'FFFFFF', color));
  [15, 30, 44, 58, 72].forEach((ang, i) => line(s, 1.58, 2.22, 1.58 + Math.cos(ang*Math.PI/180)*(2.3+i*0.08), 2.22 + Math.sin(ang*Math.PI/180)*(2.3+i*0.08), C.teal, 0.55));
  pFormula(s, 'Criterio', 'xi* = argmax_xi (1/N) sum_i M(T_xi p_i)\n\nx_k <- x_k^- + alpha(xi* - x_k^-)', 7.20, 1.60, 4.60, 1.45, C.teal, 8.0);
  pFormula(s, 'Uso en la simulación', 'Se prueban pequeñas correcciones alrededor de la pose predicha. Es una aproximación Lua, no Hector completo multi-resolución.', 7.20, 3.42, 4.60, 1.18, C.green, 7.8);
  metricTile(s, '15,233 m', 'ruta', 'más corta Fase 1', 0.92, 5.30, 1.90, C.teal);
  metricTile(s, '0,333', 'precisión', 'rasgos Fase 2', 3.12, 5.30, 1.90, C.teal);
  metricTile(s, 'límite', 'óptimos', 'locales si falta geometría', 5.32, 5.30, 1.90, C.red);
}

function slamCartographerSubmap() {
  const s = pSlide('SLAM', 'Submapas inspirados en Cartographer', C.violet, 'Submapas locales y cierres de ciclo simplificados.');
  softPanel(s, 0.82, 1.46, 5.60, 4.70, C.violet, C.white);
  [[1.18, 3.60, 'S1'], [2.40, 2.90, 'S2'], [3.58, 3.55, 'S3'], [2.35, 2.05, 'S4']].forEach(([x, y, label]) => {
    roundRect(s, x, y, 1.62, 0.92, 'F0EEFB', C.violet);
    addText(s, label, x + 0.12, y + 0.16, 0.35, 0.12, { fontSize: 8.6, bold: true, color: C.violet });
  });
  line(s, 1.26, 3.96, 4.46, 3.98, C.green, 1.2, true);
  line(s, 4.46, 3.98, 1.62, 3.74, C.orange, 1.0, true, 'dash');
  circle(s, 4.46, 3.98, 0.26, C.teal, C.teal);
  pFormula(s, 'Lógica', 'scan -> submapa activo\nnuevo submapa por distancia/tiempo\nscore alto con submapa antiguo -> cierre', 7.20, 1.60, 4.60, 1.35, C.violet, 8.4);
  pFormula(s, 'Alcance', 'La versión Lua conserva submapas y restricciones locales. No hay optimización global de grafo ni loop closure completo como Cartographer.', 7.20, 3.35, 4.60, 1.24, C.green, 7.8);
  metricTile(s, '13', 'submapas', 'finales', 0.92, 5.30, 1.80, C.violet);
  metricTile(s, '4', 'cierres', 'de ciclo', 3.02, 5.30, 1.80, C.violet);
  metricTile(s, '95,327 %', 'cobertura', 'máxima Fase 2', 5.12, 5.30, 2.00, C.violet);
}

function timelineExported() {
  const s=pSlide('timeline','Estados exportados durante la misión',C.orange,'La misión se valida con estados temporales: tarea, movimiento, planner, Bill, batería y SLAM.');
  addImageFrame(s,img.slamTimeline,0.72,1.45,11.95,4.80,'timeline exportado desde CoppeliaSim',C.orange);
  metricTile(s,'WAIT_B1','espera','R1 se detiene mientras Bill trabaja',0.92,6.38,2.35,C.blue);
  metricTile(s,'AVOIDING','seguridad','riesgo y reducción de velocidad',3.72,6.38,2.35,C.orange);
  metricTile(s,'SLAM','mapa','actualizaciones y planner observables',6.52,6.38,2.35,C.violet);
  metricTile(s,'CHARGE','cierre','retorno final a estación',9.32,6.38,2.35,C.green);
}

function phase2Captures() {
  const s=pSlide('Fase 2','Mapa desconocido con obstáculos dinámicos',C.violet,'El robot empieza sin mapa completo y replanifica cuando aparecen obstáculos detectados por los rayos.');
  addImageFrame(s,img.phase2Initial3d,0.72,1.55,5.95,3.10,'inicio con zona no observada',C.violet);
  addImageFrame(s,img.phase2Replan3d,6.88,1.55,5.95,3.10,'replanificación ante obstáculo dinámico',C.orange);
  metricTile(s,'0,03185 m','Kalman','menor RMSE de pose',0.92,5.55,2.15,C.green);
  metricTile(s,'95,327 %','Submapas','mayor actividad de mapa',3.42,5.55,2.15,C.violet);
  metricTile(s,'17-25','replans','según método SLAM',5.92,5.55,2.15,C.orange);
  metricTile(s,'0-1','recovery','recuperación del planner',8.42,5.55,2.15,C.red);
}

function phase2Exploration() {
  const s = pSlide('Fase 2', 'Exploración y SLAM que converge', C.violet,
    'La misión arranca con una pasada exploratoria que mapea la celda antes de operar y luego repite el ciclo de trabajo. El aprendizaje no se ve en la velocidad (la domina el robot móvil) sino en la calidad del SLAM: el mapa converge y la localización se afina vuelta a vuelta.');
  [['Explora primero','recorre frontiers de los pasillos centrales y mapea con el sonar antes de tocar piezas (EXPLORE_FRONTIERS)',C.teal],
   ['Repite el ciclo','tras explorar ejecuta 3 veces el ciclo T1/T2; el mapa y la pose se conservan entre vueltas',C.green],
   ['Mapa converge','landmarks nuevos por fase caen de ~4 a ~1: deja de descubrir estructura',C.violet],
   ['Localizacion se afina','error de pose medio baja de 0,086 m sin mapa a ~0,03 m con el mapa construido',C.orange]
  ].forEach((r,i)=>{const x=0.82+i*3.05; softPanel(s,x,1.60,2.58,1.46,r[2],tint(r[2])); addText(s,r[0],x+0.18,1.82,2.05,0.16,{fontSize:8.3,bold:true,color:r[2]}); addText(s,r[1],x+0.18,2.14,2.12,0.54,{fontSize:6.6,color:C.ink,fit:'shrink'});});
  addText(s,'Calidad del SLAM por fase (media de 3 ejecuciones)',0.82,3.40,7.4,0.20,{fontSize:9.5,bold:true,color:C.ink});
  drawTable(s,
    ['Fase','Landmarks (fin)','Nuevas','Error pose [m]'],
    [['Explorar','4','+4','0,086'],['Vuelta 1','9','+4','0,033'],['Vuelta 2','10','+1','0,042'],['Vuelta 3','11','+1','0,031']],
    0.82, 3.72, [1.75, 2.05, 1.35, 2.05], 0.34, { accent: C.violet });
  addText(s,'El mapa deja de crecer (landmarks nuevos ~4 → ~1) y, con mas referencias, el EKF localiza mejor: el error medio se reduce ~2,6× al pasar de explorar sin mapa a operar con el mapa construido.',8.35,3.72,4.50,1.70,{fontSize:9.2,color:C.muted});
  metricTile(s,'3','vueltas','completas sobre la celda',0.92,5.92,2.95,C.green);
  metricTile(s,'4 → 1','landmarks nuevos','el mapa converge',3.99,5.92,2.95,C.violet);
  metricTile(s,'2,6×','mejor localizacion','con el mapa construido',7.06,5.92,2.95,C.orange);
  metricTile(s,'0','recovery','en las 3 ejecuciones',10.13,5.92,2.95,C.teal);
}

function phase2Correction() {
  const s=pSlide('corrección Fase 2','Bloqueo local y recuperación por arco',C.red,'Las grids podían bloquear rutas por celdas cercanas al robot o al objetivo. Se añadieron filtros antes de activar waypoints, además de un arco de retroceso y una geo-valla.');
  [['persistencia','celda bloqueante solo tras detecciones repetidas',C.teal],['distancia local','ignora celdas dentro del radio de R1 o pegadas al objetivo',C.green],['área útil','el waypoint fuera del pasillo operativo recibe penalización',C.orange],['recuperación','un arco de retroceso (RECOVER_BACK) saca el chasis si se estanca; la geo-valla evita que escape de la celda',C.violet]].forEach((r,i)=>{const x=0.82+i*3.05; softPanel(s,x,1.62,2.58,1.28,r[2],tint(r[2])); addText(s,r[0],x+0.18,1.86,2.05,0.16,{fontSize:8.3,bold:true,color:r[2]}); addText(s,r[1],x+0.18,2.18,2.06,0.30,{fontSize:6.8,color:C.ink,fit:'shrink'});});
  [['mapa crudo',C.red],['filtros',C.orange],['waypoint',C.violet],['control reactivo',C.teal],['objetivo',C.green]].forEach((f,i)=>{const x=1.00+i*2.35; softPanel(s,x,3.85,1.65,0.62,f[1],tint(f[1])); addText(s,f[0],x+0.10,4.06,1.42,0.12,{fontSize:7.1,bold:true,color:f[1],align:'center'}); if(i<4) line(s,x+1.68,4.16,x+2.18,4.16,C.ink,1.0,true);});
  metricTile(s,'4/4','métodos','completan Fase 2 tras la corrección',1.00,5.72,2.20,C.green);
  metricTile(s,'1','recovery','observada en submapas',3.62,5.72,2.20,C.violet);
  metricTile(s,'17','mínimo','replanificaciones Kalman',6.24,5.72,2.20,C.teal);
  metricTile(s,'25','máximo','replanificaciones submapas',8.86,5.72,2.20,C.orange);
}

function followerSetup() {
  const s = pSlide('parte 1 · seguimiento', 'Bill define el objetivo; el Pioneer regula distancia', C.teal, 'El objetivo real no es el centro de Bill: se calcula un punto p* detrás de la persona.');
  softPanel(s, 0.72, 1.58, 7.15, 5.00, C.teal, C.white);
  grid(s, 0.98, 1.88, 6.60, 4.40, 8, 6);
  drawPioneer(s, 2.25, 5.20, 0.88, C.teal, 'Pioneer');
  drawBill(s, 5.78, 2.34, 0.88);
  circle(s, 4.72, 2.34, 0.18, C.violet, C.violet);
  addText(s, 'p*', 4.42, 2.05, 0.35, 0.16, { fontSize: 9, bold: true, color: C.violet });
  line(s, 2.72, 4.92, 4.62, 2.46, C.orange, 2.2, true);
  line(s, 5.62, 2.34, 4.84, 2.34, C.violet, 1.3, true, 'dash');
  methodChip(s, 'F_att', 3.32, 3.76, C.orange, 0.72);
  methodChip(s, 'd_des', 5.00, 2.08, C.violet, 0.82);

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
  const s = pSlide('modelo', 'Cinemática diferencial del Pioneer P3DX', C.cyan, 'La simulación entrega velocidades de rueda; la comparación de control se expresa en v y omega.');
  grid(s, 0.82, 1.55, 5.65, 5.10, 7, 6);
  drawPioneer(s, 3.55, 4.00, 1.10, C.teal, 'Pioneer P3DX');
  line(s, 4.24, 4.00, 5.35, 4.00, C.teal, 1.8, true);
  addText(s, 'v', 5.42, 3.86, 0.25, 0.16, { fontSize: 8.8, bold: true, color: C.teal });
  pFormula(s, 'Modelo continuo', 'x_dot     = v cos(theta)\ny_dot     = v sin(theta)\ntheta_dot = omega', 7.00, 1.65, 4.85, 1.35, C.cyan, 11.0);
  pFormula(s, 'De v, omega a ruedas', 'omega_L = (v - L omega / 2) / r\nomega_R = (v + L omega / 2) / r\n\nr = 0.0975 m, L = 0.331 m', 7.00, 3.42, 4.85, 1.55, C.violet, 10.5);
  pFormula(s, 'Salida común', 'controlador -> v, omega -> saturación -> ruedas -> CSV logger', 7.00, 5.32, 4.85, 0.86, C.teal, 8.8);
}

function potential() {
  const s = pSlide('campo potencial', 'Fuerza hacia Bill y repulsión local', C.orange, 'El vector de guía combina atracción al punto p* con seguridad ante obstáculos.');
  grid(s, 0.78, 1.50, 5.85, 5.10, 7, 6);
  const robot = { x: 2.18, y: 4.92 };
  const target = { x: 4.52, y: 2.34 };
  const bill = { x: 5.34, y: 2.34 };
  const obs = { x: 3.72, y: 4.34 };

  drawPioneer(s, robot.x, robot.y, 0.78, C.teal, 'p_R robot');
  drawBill(s, bill.x, bill.y, 0.78);
  circle(s, target.x - 0.09, target.y - 0.09, 0.18, C.violet, C.violet);
  addText(s, 'p* detrás de Bill', target.x - 0.62, target.y - 0.45, 1.08, 0.16, { fontSize: 7.7, bold: true, color: C.violet, align: 'center' });

  circle(s, obs.x - 0.48, obs.y - 0.48, 0.96, 'FFF6F6', C.red, 18);
  rect(s, obs.x - 0.30, obs.y - 0.24, 0.60, 0.48, 'FDECEC', C.red);
  addText(s, 'obstáculo', obs.x - 0.45, obs.y - 0.56, 0.90, 0.13, { fontSize: 7.1, bold: true, color: C.red, align: 'center' });

  line(s, robot.x, robot.y, obs.x - 0.05, obs.y + 0.04, C.muted, 0.95, false, 'dash');
  addText(s, 'rho_i', 2.84, 4.50, 0.36, 0.13, { fontSize: 7.2, color: C.muted, italic: true, align: 'center' });

  line(s, robot.x + 0.10, robot.y - 0.10, target.x - 0.10, target.y + 0.10, C.orange, 2.0, true);
  line(s, robot.x - 0.08, robot.y + 0.08, 1.48, 5.54, C.red, 1.9, true);
  line(s, robot.x + 0.12, robot.y - 0.02, 3.34, 3.72, C.teal, 2.5, true);
  pill(s, 'F_att hacia p*', 3.36, 3.08, C.orange, 1.04);
  pill(s, 'F_rep local', 1.24, 5.32, C.red, 0.98);
  pill(s, 'F resultante', 2.74, 4.06, C.teal, 0.92);
  pFormula(s, 'Atracción', 'F_att = k_att (p* - p_R)', 7.05, 1.70, 4.85, 0.92, C.orange, 11.0);
  pFormula(s, 'Repulsión', 'si rho_i < rho_0:\nF_rep,i = eta(1/rho_i - 1/rho_0)(1/rho_i^2)n_i\n\nsi rho_i >= rho_0: F_rep,i = 0', 7.05, 3.00, 4.85, 1.78, C.red, 9.3);
  pFormula(s, 'Vector de guía', 'F = F_att + sum_i F_rep,i\nalpha = atan2(F_y, F_x)', 7.05, 5.15, 4.85, 1.00, C.teal, 10.5);
}

function classicalControl() {
  const s = pSlide('control clásico', 'P, PI y PID: memoria incremental', C.orange, 'Tres niveles de realimentación sobre el mismo error: presente, acumulado y cambio temporal.');
  const cards = [
    ['P', 'presente', 'v = Kp e_d\nomega = Kpsi e_psi', 'corrige rápido, deja offset si Bill se mueve', getMode('P'), C.amber],
    ['PI', 'presente + acumulado', 'u_PI = Kp e_d + Ki I_d\nI_d = sum(e_d dt)', 'reduce error sostenido', getMode('PI'), C.teal],
    ['PID', 'presente + acumulado + cambio', 'u_PID = Kp e_d + Ki I_d\n+ Kd de_d/dt', 'menor error final, más esfuerzo de ruedas', getMode('PID'), C.red],
  ];
  cards.forEach((c, i) => {
    const x = 0.82 + i * 4.08;
    const y = 1.70 + i * 0.18;
    roundRect(s, x, y, 3.55, 2.18, tint(c[5]), c[5]);
    addText(s, c[0], x + 0.22, y + 0.16, 0.60, 0.24, { fontFace: 'Aptos Display', fontSize: 20, bold: true, color: c[5] });
    addText(s, c[1], x + 0.90, y + 0.23, 2.30, 0.14, { fontSize: 7.7, bold: true, color: C.muted });
    addText(s, c[2], x + 0.22, y + 0.70, 3.08, 0.66, { fontFace: 'Cascadia Mono', fontSize: 8.0, color: C.ink, fit: 'shrink' });
    addText(s, c[3], x + 0.22, y + 1.55, 3.05, 0.24, { fontSize: 8.6, color: C.ink });
    if (i < 2) line(s, x + 3.62, y + 1.08, x + 4.00, y + 1.08, c[5], 1.5, true);
  });
  line(s, 0.88, 4.38, 12.15, 4.38, C.line, 1.0);
  addText(s, 'DATOS DEL SEGUIMIENTO', 0.90, 4.66, 2.2, 0.16, { fontSize: 8.0, bold: true, color: C.orange });
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
  const s = pSlide('LQR', 'K se resuelve en la escena (Riccati); Lua aplica u = -Kx', C.violet, 'Q y R penalizan estados y mando; K sale de resolver la Riccati discreta dentro de CoppeliaSim (sin valores precargados) y se aplica sobre el seguimiento nominal.');
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
  pFormula(s, 'Modelo local', 'x = [e_long, e_lat, e_yaw]^T\nu = [delta_v, delta_omega]^T\n\n(e_long,e_lat) = proy(p* - p_R) en marco R1\ne_yaw = e_psi\nA = [[0, omega_ref, 0], [-omega_ref, 0, v_ref], [0,0,0]]', 0.82, 2.82, 5.65, 1.72, C.violet, 7.8);
  pFormula(s, 'Riccati y pesos', 'A_d = I + dt A, B_d = dt B\nQ = diag(35, 80, 18)\nR = diag(6, 3)\n\nP = dare(A_d, B_d, Q, R)\nK = (B_d^T P B_d + R)^-1 B_d^T P A_d', 6.85, 2.82, 5.55, 1.72, C.teal, 8.3);
  pFormula(s, 'Ganancia LQR', 'K = [[-2.3496,  1.2925,  0.1203],\n     [ 0.2427, -4.3570, -2.6887]]\npolos = 0.9741, 0.8884, 0.8856', 0.82, 5.00, 5.65, 1.00, C.green, 8.5);
  pFormula(s, 'Alcance', 'La misión tiene saturaciones, Bill móvil, obstáculos y estados discretos. LQR se aplica alrededor del seguimiento nominal.', 6.85, 4.92, 3.85, 1.20, C.orange, 7.8);
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
  pFormula(s, 'Costo multiobjetivo', 'J = sum_k(c_e + c_u + c_s) + q_f ||p*_N-p_N||^2\nc_e = q_d e_d^2 + q_t ||p*_k-p_k||^2 + q_psi e_psi^2\nc_u = r_v v_k^2 + r_omega omega_k^2 + r_w(omega_L^2+omega_R^2)\nc_s = s_v Delta v_k^2 + s_omega Delta omega_k^2', 5.02, 3.00, 5.38, 2.05, C.teal, 6.2);
  pFormula(s, 'Restricciones', 'v in [v_reverse_max, v_max]\nomega in [-omega_max, omega_max]\n\nbúsqueda directa: 2 pasadas', 10.62, 3.00, 1.78, 2.05, C.orange, 7.5);
  metricTile(s, fmt(getMode('NMPC').mean_abs_error_moving_m), 'error mov. [m]', 'mejor durante Bill móvil', 0.92, 5.42, 2.10, C.green);
  metricTile(s, fmt(getMode('NMPC').wheel_delta_u_rms), 'RMS delta-u', 'mando suave', 3.35, 5.42, 2.10, C.teal);
  metricTile(s, String(getMode('NMPC').stop_velocity_flip_count || '-'), 'flips al parar', 'menos cambios bruscos', 5.78, 5.42, 2.10, C.orange);
  softPanel(s, 8.55, 5.42, 3.50, 1.05, C.violet, tint(C.violet));
  addText(s, 'Pesos usados', 8.78, 5.58, 2.40, 0.18, { fontSize: 8.6, bold: true, color: C.violet, fit: 'shrink' });
  addText(s, 'q_d=48, q_t=7, q_psi=1.2, r_v=1.4, r_omega=1.8, r_w=0.020, s_v=65, s_omega=18, q_f=6.', 8.78, 5.87, 2.92, 0.36, { fontSize: 6.5, color: C.ink, fit: 'shrink' });
}

function followerResults() {
  const s = pSlide('resultados de seguimiento', 'Precisión, seguimiento y esfuerzo no coinciden', C.green, 'La comparación usa la misma trayectoria de Bill y el mismo logger para todos los controladores.');
  const modes = follower.modes || [];
  const bestFinal = [...modes].sort((a, b) => Number(a.final_abs_error_m || 0) - Number(b.final_abs_error_m || 0))[0] || {};
  const bestMoving = [...modes].sort((a, b) => Number(a.mean_abs_error_moving_m || 0) - Number(b.mean_abs_error_moving_m || 0))[0] || {};
  const bestSmooth = [...modes].sort((a, b) => Number(a.wheel_delta_u_rms || 0) - Number(b.wheel_delta_u_rms || 0))[0] || {};
  addImageFrame(s, img.follower, 0.72, 1.58, 6.35, 4.82, 'respuesta temporal exportada', C.green);
  proofTile(s, bestFinal.mode || 'PID', `menor error final: ${fmt(bestFinal.final_abs_error_m)} m`, 7.42, 1.62, 2.15, C.red, 'llegada al setpoint');
  proofTile(s, bestMoving.mode || 'NMPC', `menor error móvil: ${fmt(bestMoving.mean_abs_error_moving_m)} m`, 9.82, 1.62, 2.15, C.green, 'Bill en movimiento');
  proofTile(s, bestSmooth.mode || 'PI', `mando más suave: ${fmt(bestSmooth.wheel_delta_u_rms)}`, 7.42, 3.02, 2.15, C.teal, 'RMS delta-u');
  comparisonBars(s, 'error final [m]', modes, 'final_abs_error_m', 9.82, 3.02, 2.15, 2.00, { color: C.red, digits: 3 });
  darkInsight(s, 'Dato de control', 'PID minimiza error final; LQR/NMPC explican mejor seguimiento móvil y costo de actuación.', 7.42, 5.16, 4.55, 1.12, C.cyan);
}

function wheelCost() {
  const s = pSlide('costo de control', 'Ruedas y esfuerzo de control', C.violet, 'Una trayectoria precisa empeora si exige más energía, oscilación o cambios bruscos de signo.');
  const modes = follower.modes || [];
  addImageFrame(s, img.power, 0.72, 1.55, 6.00, 2.65, 'potencia instantánea y acumulada', C.orange);
  addImageFrame(s, img.smooth, 0.72, 4.52, 6.00, 1.88, 'suavidad del comando de ruedas', C.violet);
  comparisonBars(s, 'energía [J]', modes, 'energy_j', 7.12, 1.58, 2.35, 2.10, { color: C.orange, digits: 1 });
  comparisonBars(s, 'variación total', modes, 'wheel_u_total_variation', 9.82, 1.58, 2.35, 2.10, { color: C.violet, digits: 1 });
  comparisonBars(s, 'flips al detenerse Bill', modes, 'stop_velocity_flip_count', 7.12, 4.02, 2.35, 1.84, { color: C.red, digits: 0 });
  darkInsight(s, 'Interpretación', 'El controlador se elige por precisión y costo físico. Error bajo sin suavidad no da un buen resultado operativo.', 9.82, 4.10, 2.35, 1.45, C.violet);
}

function missionSection() {
  const s = pptx.addSlide();
  slideNo += 1;
  s.background = { color: C.navy };
  rect(s, 0, 0, 13.333, 7.5, C.navy, C.navy);
  slideAddImageFit(s, img.phase1Layout, 6.05, 0.42, 6.95, 6.28, false);
  rect(s, 5.88, 0, 7.45, 7.5, C.navy, C.navy, 58);
  addText(s, 'PARTE 2', 0.75, 0.82, 1.2, 0.18, { fontSize: 8.5, bold: true, color: C.green });
  addText(s, 'De seguimiento a misión en celda', 0.75, 1.36, 5.7, 0.75, { fontFace: 'Aptos Display', fontSize: 31, bold: true, color: C.white });
  addText(s, 'Ahora el robot debe cumplir tarea, esquivar obstáculos, volver a carga y dejar datos de localización y mapa.', 0.78, 2.42, 5.25, 0.58, { fontSize: 12.2, color: 'D9E2EA' });
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
  const s = pSlide('fase 1', 'La misión se ejecuta como máquina de estados', C.cyan, 'Cada transición tiene condición de paso; el logger registra duración, batería, riesgo y control.');
  addImageFrame(s, img.phase1StateMachine, 0.78, 1.55, 7.95, 4.70, 'estado operativo R1', C.orange);
  pFormula(s, 'Entrada del bucle', 'pose + Bill + sensores + batería', 9.05, 1.72, 2.95, 0.82, C.teal, 8.7);
  pFormula(s, 'Secuencia', 'task_state -> planner_mode -> controlador', 9.05, 2.90, 2.95, 0.82, C.violet, 8.7);
  pFormula(s, 'Salida CSV', 'estado, ruedas, riesgo, error y batería', 9.05, 4.08, 2.95, 0.82, C.green, 8.7);
  roundRect(s, 9.05, 5.33, 2.95, 0.62, C.navy, C.navy);
  addText(s, 'Condición final: misión completa y estado CHARGING.', 9.30, 5.52, 2.45, 0.14, { fontSize: 8.2, bold: true, color: C.white, align: 'center' });
}

function phase1Results() {
  const modes = [...(phase1.modes || [])].sort((a, b) => Number(a.score || 0) - Number(b.score || 0));
  const best = modes[0] || {};
  const bestMode = best.mode || 'PID';
  const s = pSlide('fase 1', `${bestMode} obtiene el mejor puntaje operativo`, C.green, 'En la celda también importan tiempo activo, batería, riesgo y estabilidad.');
  roundRect(s, 0.78, 1.58, 3.55, 4.82, C.navy, C.navy);
  addText(s, 'CONTROL SELECCIONADO', 1.06, 1.92, 2.25, 0.16, { fontSize: 7.8, bold: true, color: C.cyan });
  addText(s, bestMode, 1.03, 2.28, 1.42, 0.62, { fontFace: 'Aptos Display', fontSize: 48, bold: true, color: C.white });
  addText(s, 'mejor balance operativo', 1.08, 3.05, 2.55, 0.24, { fontSize: 12.0, bold: true, color: C.white });
  addText(s, `puntaje ${fmt(best.score, 3)}\nduración ${fmt(best.duration_s, 1)} s\nbatería ${fmt(best.battery_used_pct, 1)} %`, 1.08, 3.62, 2.60, 0.72, { fontSize: 10.8, color: 'DFF7F2' });
  line(s, 1.08, 4.72, 3.66, 4.72, C.green, 1.4);
  addText(s, `Todos los modos completan la misión y terminan en CHARGING; ${bestMode} logra el menor riesgo y error de pose sin alargar la misión.`, 1.08, 5.02, 2.70, 0.62, { fontSize: 9.1, bold: true, color: C.white, fit: 'shrink' });
  const maxScore = Math.max(...modes.map(m => Number(m.score || 0))) || 1;
  modes.forEach((m, i) => {
    barMetric(s, m.mode, Number(m.score || 0), maxScore, 4.72, 1.72 + i * 0.36, 2.45, i === 0 ? C.green : C.line);
  });
  addImageFrame(s, img.phase1Metrics, 7.72, 1.55, 4.55, 2.52, 'métricas por modo', C.green);
  softPanel(s, 4.72, 3.58, 2.78, 0.55, C.green, C.white);
  addText(s, 'CRITERIOS DEL PUNTAJE', 4.92, 3.70, 1.58, 0.10, { fontSize: 6.8, bold: true, color: C.green });
  addText(s, 'tiempo · batería · riesgo · pose · suavidad', 4.92, 3.90, 2.25, 0.10, { fontSize: 6.8, color: C.ink, fit: 'shrink' });
  addImageFrame(s, img.phase1, 4.62, 4.35, 4.05, 1.90, 'trayectoria y señales', C.teal);
  pFormula(s, 'Puntaje', `min-max, menor es mejor\n0.28 movimiento + 0.18 batería\n+ 0.20 variación + 0.14 riesgo\n+ 0.12 error pose + 0.08 duración\nriesgo = max_t obstacle_risk(t)`, 8.92, 4.38, 3.10, 1.45, C.green, 7.4);
}

function slamPipeline() {
  const s = pSlide('SLAM', 'Estimación, mapa, planificación y control en ciclo cerrado', C.teal, 'La estimación entrega el estado al planificador local y el planificador vuelve al control diferencial de ruedas.');
  addImageFrame(s, img.phase1EstimatorPipeline, 0.70, 1.58, 8.10, 4.85, 'pipeline de estimación y control', C.teal);
  pFormula(s, 'Predicción', 'x_k^- = f(x_{k-1}, u_k)\nP_k^- = F_k P_{k-1} F_k^T + Q_k', 9.15, 1.78, 2.82, 0.95, C.teal, 8.2);
  pFormula(s, 'Corrección', 'K_k = P_k^- H_k^T (H_k P_k^- H_k^T + R_k)^-1\nx_k = x_k^- + K_k(z_k - h(x_k^-))', 9.15, 3.05, 2.82, 1.20, C.violet, 7.0);
  pFormula(s, 'Mapa', 'landmark/celda -> planner -> waypoint local', 9.15, 4.62, 2.82, 0.90, C.green, 8.2);
}

function proximityRayMethods() {
  const s = pSlide('SLAM con proximidad', 'Log-odds, scan-to-map y submapas', C.violet, 'Tres formas simplificadas de usar rayos de proximidad simulados sobre el mismo recorrido.');
  pFormula(s, 'Proximidad', 'z_i = [rho_i, phi_i]\np_i^W = R(theta)p_i^R + p_R', 0.75, 1.65, 3.55, 1.25, C.teal, 10.0);
  pFormula(s, 'Log-odds', 'l_t(m)=l_{t-1}(m)+logit(P(m|z_t,x_t))-l_0\n\nactualiza grid de ocupación.', 4.90, 1.65, 3.55, 1.25, C.orange, 8.7);
  pFormula(s, 'Scan-to-map', 'x* = argmin_x sum_i [1 - M(T(x)p_i)]^2\n\najuste de escaneo contra grid.', 9.05, 1.65, 3.55, 1.25, C.cyan, 8.7);
  pFormula(s, 'Submapas', 'escaneos locales -> submapa\nrestricciones escaneo-submapa\ncierre de ciclo si error < umbral', 0.75, 3.42, 3.55, 1.35, C.violet, 9.2);
  addImageFrame(s, img.slamOverview, 4.90, 3.28, 3.55, 2.10, 'panel de ejecución', C.green);
  addImageFrame(s, img.slamTimeline, 9.05, 3.28, 3.55, 2.10, 'línea de tiempo', C.orange);
  pFormula(s, 'Salida comparable', 'RMSE + P95 + máximo + celdas, landmarks, submapas y batería.', 1.05, 6.05, 11.15, 0.72, C.green, 8.4);
}

function kalman() {
  const s = pSlide('Kalman landmarks', 'Predicción, asociación y corrección', C.green, 'El modo Kalman landmark mantiene landmarks puntuales y corrige la pose cuando la medición se asocia con un punto conocido.');
  pFormula(s, '1 · Predicción', 'x_k^- = f(x_{k-1}, u_k)\nP_k^- = F_k P_{k-1} F_k^T + Q_k', 0.75, 1.65, 3.65, 1.28, C.teal, 9.8);
  pFormula(s, '2 · Asociación', 'si ||z_i - l_j|| < umbral: usar j\nsi no: crear nuevo landmark', 4.85, 1.65, 3.65, 1.28, C.orange, 9.8);
  pFormula(s, '3 · Corrección', 'K_k = P_k^-H_k^T(H_kP_k^-H_k^T+R_k)^-1\nx_k = x_k^- + K_k(z_k-h(x_k^-))', 8.95, 1.65, 3.65, 1.28, C.violet, 8.7);
  addImageFrame(s, img.slamEstimator, 0.92, 3.52, 5.65, 2.42, 'desempeño del estimador', C.green);
  pFormula(s, 'Interpretación', 'Kalman landmarks obtiene el menor RMSE en esta celda compacta. Submapas representa mejor estructura de mapa, con más coste.', 7.05, 3.72, 4.85, 1.58, C.green, 9.2);
  pStat(s, '0.03142', 'mejor RMSE [m]', 7.25, 5.70, C.green, 1.8);
  pStat(s, '20', 'landmarks finales', 9.35, 5.70, C.green, 1.8);
}

function slamResults() {
  const s = pSlide('comparación SLAM', 'Cuatro modos en la misma celda', C.green, 'Variantes Lua sobre las mismas señales y el mismo recorrido; n=1 ejecución por método.');
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
      ? `${m.cartographer_submaps_final} submapas · ${m.loop_closures_final || 0} cierres`
      : `${m.map_features_final ?? '-'} rasgos`;
    addText(s, featureText, x + 0.14, 3.38, 1.32, 0.14, { fontSize: 7.0, bold: true, color });
  });
  addImageFrame(s, img.slamAlgorithms, 0.78, 4.28, 6.10, 1.95, 'trayectoria, error y mapa', C.green);
  const maxRmse = Math.max(...modes.map(m => Number(m.rmse_position_m || 0))) || 1;
  addText(s, 'RANKING POR RMSE', 6.55, 4.22, 2.2, 0.16, { fontSize: 8.0, bold: true, color: C.green });
  modes.forEach((m, i) => {
    barMetric(s, slamName(m.mode), Number(m.rmse_position_m || 0), maxRmse, 6.55, 4.58 + i * 0.36, 0.62, palette[i] || C.teal, ' m');
  });
  darkInsight(s, 'Interpretación', 'Kalman minimiza error de pose. Las diferencias pequeñas deben leerse con la limitación de una sola ejecución por método.', 10.30, 4.22, 2.10, 1.45, C.green);
}

function slamVisual() {
  {
    const s = pSlide('reconstrucción', 'Mapa común en t = 60 s', C.green, 'Los cuatro modos se comparan en el mismo instante de Fase 2 usando los rayos de proximidad como fuente de mapa.');
    addImageFrame(s, img.phase2Reconstruction, 0.70, 1.45, 11.95, 4.95, 'reconstrucción LiDAR/SLAM con rayos de proximidad', C.green);
    metricTile(s, '4 modos', 'comparación', 'Kalman, log-odds, scan-to-map y submapas', 0.92, 6.38, 2.45, C.violet);
    metricTile(s, 't = 60 s', 'instante', 'mismo corte temporal para todos', 3.85, 6.38, 2.45, C.green);
    metricTile(s, 'CSV', 'fuente', 'phase2_slam_unknown_export', 6.78, 6.38, 2.45, C.teal);
  }
  return;
  const s = pSlide('datos SLAM', 'Trayectoria, error, mapa y métricas en una vista', C.green, 'Todos los modos se ejecutan sobre la misma escena, recorrido y señales exportadas.');
  addImageFrame(s, img.slamAlgorithms, 0.70, 1.55, 7.30, 4.90, 'comparación visual', C.green);
  pBullet(s, 'Todos los modos completan la misión.', 8.45, 1.95, C.green, 3.7);
  pBullet(s, 'El error queda en escala de centímetros.', 8.45, 2.90, C.teal, 3.7);
  pBullet(s, 'Submapas registra cierres de ciclo simplificados.', 8.45, 3.85, C.violet, 3.7);
  pBullet(s, 'Kalman landmark da menor RMSE en esta celda.', 8.45, 4.80, C.orange, 3.7);
}

function phase2Unknown() {
  const s = pSlide('phase 2', 'SLAM con mapa desconocido', C.violet, 'La escena conserva la misión T1 y T2 y añade obstáculos no modelados, zonas desconocidas y replanificación.');
  const modes = [...phase2Modes].sort((a, b) => Number(a.rmse_position_m || 0) - Number(b.rmse_position_m || 0));
  const best = modes[0] || {};
  addImageFrame(s, img.phase2Algorithms, 0.70, 1.55, 6.30, 3.10, 'comparación Fase 2', C.violet);
  addImageFrame(s, img.phase2Snapshots, 0.70, 4.88, 6.30, 1.42, 'reconstrucción por instante', C.green);
  proofTile(s, slamName(best.mode), `mejor RMSE: ${fmt(best.rmse_position_m, 5)} m`, 7.40, 1.62, 2.25, C.green, 'pose estimada');
  const bestEvidence = [...modes].sort((a, b) => Number(b.mapping_evidence_final_pct || 0) - Number(a.mapping_evidence_final_pct || 0))[0] || {};
  proofTile(s, slamName(bestEvidence.mode), `actividad: ${fmt(bestEvidence.mapping_evidence_final_pct, 3)} %`, 9.95, 1.62, 2.25, C.violet, 'actividad de mapa');
  const maxReplans = Math.max(...modes.map(m => Number(m.replan_triggers || 0))) || 1;
  addText(s, 'REPLANIFICACIONES', 7.42, 3.18, 2.05, 0.14, { fontSize: 7.8, bold: true, color: C.violet });
  modes.forEach((m, i) => {
    barMetric(s, slamName(m.mode), Number(m.replan_triggers || 0), maxReplans, 7.42, 3.55 + i * 0.34, 0.72, modeColor(m.mode), '');
  });
  darkInsight(s, 'Comparación', 'Kalman mantiene el menor error de pose. Submapas tarda más, pero deja más actividad de mapa y activa recuperación una vez.', 9.65, 4.72, 2.55, 1.42, C.violet);
}

function phase2TrajectoryComparison() {
  const s = pSlide('fase 2', 'Comparación Fase 2: trayectorias', C.violet, 'Misma misión T1/T2, mismos obstáculos dinámicos y cuatro estimadores SLAM.');
  addImageFrame(s, img.phase2TrajectoryCrop, 0.72, 1.48, 6.28, 4.94, 'trayectorias finales y rasgos detectados', C.violet);
  addText(s, 'Comparación', 7.48, 1.62, 2.35, 0.24, { fontSize: 15.5, bold: true, color: C.ink });
  [
    ['Kalman mantiene la trayectoria más estable en error de pose.', C.green],
    ['Scan-to-map y log-odds siguen una ruta cercana, con más dispersión local.', C.teal],
    ['Submapas añade cierres simplificados y más estructura.', C.violet],
    ['El pallet dinámico modifica el recorrido sin cambiar la misión.', C.orange],
  ].forEach((row, i) => {
    const y = 2.12 + i * 0.56;
    circle(s, 7.52, y + 0.08, 0.10, row[1], row[1]);
    addText(s, row[0], 7.78, y, 4.40, 0.28, { fontSize: 9.1, color: C.ink, fit: 'shrink' });
  });
  metricTile(s, '4', 'modos', 'SLAM comparados', 7.50, 4.72, 1.72, C.violet);
  metricTile(s, '17-25', 'replans', 'rango observado', 9.48, 4.72, 1.72, C.orange);
  metricTile(s, '9-10', 'cruces', 'dinámicos', 7.50, 5.80, 1.72, C.teal);
  metricTile(s, '0-1', 'recovery', 'recuperaciones', 9.48, 5.80, 1.72, C.green);
}

function phase2CoverageTimeline() {
  const s = pSlide('fase 2', 'Comparación Fase 2: cobertura temporal', C.teal, 'La cobertura de mapa se registra durante la ejecución y compara la velocidad de descubrimiento.');
  addImageFrame(s, img.phase2EvidenceCrop, 0.72, 1.42, 8.98, 4.86, 'curva de cobertura de mapa', C.teal);
  addText(s, 'Comportamiento', 10.18, 1.64, 1.95, 0.18, { fontSize: 13.0, bold: true, color: C.ink, fit: 'shrink' });
  addText(s, 'Las grids suben rápido al inicio. Kalman descubre rasgos más despacio, pero termina cerca del mismo rango de cobertura.', 10.18, 2.08, 2.30, 0.92, { fontSize: 8.8, color: C.ink, fit: 'shrink' });
  metricTile(s, '5,1 s', '75 % cobertura', 'log-odds / scan-to-map', 10.18, 3.56, 1.92, C.teal);
  metricTile(s, '98,55 s', '75 % Kalman', 'crecimiento gradual', 10.18, 4.78, 1.92, C.orange);
}

function phase2CoverageFinal() {
  const s = pSlide('fase 2', 'Comparación Fase 2: cobertura final', C.violet, 'Todos los métodos quedan cerca del 95 % de cobertura final, con diferencias pequeñas pero medibles.');
  const bars = [
    ['Submapas', 95.327, C.violet],
    ['Scan-to-map', 94.930, C.teal],
    ['Log-odds', 94.851, C.orange],
    ['Kalman landmark', 94.613, C.green],
  ];
  bars.forEach(([name, value, color], i) => {
    const y = 1.82 + i * 0.78;
    addText(s, name, 0.98, y + 0.05, 2.30, 0.18, { fontSize: 9.4, bold: true, color: C.ink });
    rect(s, 3.48, y + 0.04, 8.20, 0.28, 'E6ECF2', 'E6ECF2');
    rect(s, 3.48, y + 0.04, 8.20 * value / 96, 0.28, color, color);
    addText(s, `${value.toFixed(3).replace('.', ',')} %`, 11.92, y - 0.03, 1.00, 0.20, { fontSize: 12.4, bold: true, color, align: 'right' });
  });
  darkInsight(s, 'Comparación', 'Submapas alcanza la mayor cobertura final; la diferencia frente a scan-to-map y log-odds es menor a medio punto porcentual.', 0.96, 5.40, 10.80, 0.74, C.violet);
}

function phase2UnknownMap() {
  const s = pSlide('fase 2', 'Mapa desconocido y obstáculos dinámicos', C.green, 'La escena introduce zonas no observadas y obstáculos que obligan a replanificar.');
  addImageFrame(s, img.phase2Overview, 0.72, 1.42, 7.75, 4.86, 'mapa y obstáculos', C.green);
  addText(s, 'Elementos de Fase 2', 8.92, 1.62, 2.65, 0.22, { fontSize: 14.0, bold: true, color: C.ink, fit: 'shrink' });
  [
    ['El mapa no se inicializa completo; se revela con sensores.', C.green],
    ['El pallet y el bloque temporal modifican el paso local.', C.orange],
    ['El planner alterna DIRECT, SLAM_WAYPOINT y recuperación.', C.violet],
    ['La misión se conserva para todos los métodos.', C.teal],
  ].forEach((row, i) => {
    const y = 2.16 + i * 0.58;
    circle(s, 8.98, y + 0.08, 0.10, row[1], row[1]);
    addText(s, row[0], 9.24, y, 3.10, 0.28, { fontSize: 8.8, color: C.ink, fit: 'shrink' });
  });
  metricTile(s, '9-10', 'cruces', 'obstáculo dinámico', 8.95, 5.28, 1.86, C.teal);
}

function phase2ExportedSignals() {
  const s = pSlide('phase 2', 'Señales exportadas por el logger', C.orange, 'Las series temporales reconstruyen navegación, riesgo, mapa y batería.');
  addImageFrame(s, img.phase2Signals, 0.72, 1.42, 8.18, 4.86, 'series temporales exportadas', C.orange);
  addText(s, 'Uso técnico', 9.36, 1.62, 2.20, 0.22, { fontSize: 15.2, bold: true, color: C.ink });
  [
    ['Verificar cuándo aparece cada replanificación.', C.orange],
    ['Medir riesgo máximo y distancia mínima.', C.red],
    ['Cruzar mapa revelado con error de pose.', C.green],
    ['Comparar consumo de batería entre métodos.', C.teal],
  ].forEach((row, i) => {
    const y = 2.16 + i * 0.58;
    circle(s, 9.42, y + 0.08, 0.10, row[1], row[1]);
    addText(s, row[0], 9.68, y, 2.92, 0.28, { fontSize: 8.8, color: C.ink, fit: 'shrink' });
  });
  metricTile(s, 'CSV', 'fuente', 'plots y tablas', 9.38, 5.28, 1.86, C.violet);
}

function phase2MetricsComparison() {
  const slide = pSlide('fase 2', 'Comparación Fase 2: métricas', C.green, 'Comparación por estimador: error, ruta, cobertura y replanificación.');
  const cards = [
    ['Kalman', '0,03185 m', 'menor RMSE y duración', C.green],
    ['Scan-to-map', '15,735 m', 'ruta final más corta', C.teal],
    ['Submapas', '95,327 %', 'mayor cobertura', C.violet],
    ['Log-odds', '0 recovery', 'grid estable', C.orange],
  ];
  cards.forEach(([name, metric, note, color], i) => {
    const x = 0.72 + i * 3.05;
    roundRect(slide, x, 1.58, 2.72, 1.00, tint(color), color);
    addText(slide, name, x + 0.18, 1.78, 1.72, 0.16, { fontSize: 9.2, bold: true, color });
    addText(slide, metric, x + 0.18, 2.08, 1.80, 0.22, { fontFace: 'Aptos Display', fontSize: 18.0, bold: true, color: C.ink, fit: 'shrink' });
    addText(slide, note, x + 0.18, 2.38, 2.20, 0.13, { fontSize: 7.0, color: C.muted, fit: 'shrink' });
  });

  const rmseBars = [
    ['Kalman', 0.03185, C.green],
    ['Submapas', 0.03930, C.violet],
    ['Log-odds', 0.04220, C.orange],
    ['Scan-to-map', 0.04587, C.teal],
  ];
  const mapBars = [
    ['Submapas', 95.327, C.violet],
    ['Scan-to-map', 94.930, C.teal],
    ['Log-odds', 94.851, C.orange],
    ['Kalman', 94.613, C.green],
  ];
  softPanel(slide, 0.72, 3.02, 5.85, 2.34, C.green, C.white);
  addText(slide, 'RMSE de pose [m]', 0.96, 3.24, 2.20, 0.16, { fontSize: 10.0, bold: true, color: C.green });
  rmseBars.forEach(([name, value, color], i) => {
    const y = 3.70 + i * 0.36;
    addText(slide, name, 0.96, y, 1.40, 0.12, { fontSize: 7.0, bold: true, color: C.ink });
    rect(slide, 2.40, y + 0.03, 2.90, 0.10, 'E7EDF4', 'E7EDF4');
    rect(slide, 2.40, y + 0.03, 2.90 * (1 - (value - 0.031) / 0.018), 0.10, color, color);
    addText(slide, value.toFixed(5).replace('.', ','), 5.38, y - 0.02, 0.74, 0.13, { fontSize: 6.8, bold: true, color, align: 'right' });
  });

  softPanel(slide, 6.90, 3.02, 5.85, 2.34, C.violet, C.white);
  addText(slide, 'Cobertura de mapa [%]', 7.14, 3.24, 2.20, 0.16, { fontSize: 10.0, bold: true, color: C.violet });
  mapBars.forEach(([name, value, color], i) => {
    const y = 3.70 + i * 0.36;
    addText(slide, name, 7.14, y, 1.58, 0.12, { fontSize: 7.0, bold: true, color: C.ink });
    rect(slide, 8.88, y + 0.03, 2.70, 0.10, 'E7EDF4', 'E7EDF4');
    rect(slide, 8.88, y + 0.03, 2.70 * (value / 96), 0.10, color, color);
    addText(slide, value.toFixed(3).replace('.', ','), 11.68, y - 0.02, 0.74, 0.13, { fontSize: 6.8, bold: true, color, align: 'right' });
  });

  darkInsight(slide, 'Resultado', 'Kalman queda primero por error y tiempo; submapas gana cobertura; scan-to-map acorta ruta; log-odds queda como referencia de grid.', 0.92, 5.78, 11.60, 0.66, C.green);
}

function finalDecision() {
  const s = pSlide('cierre', 'Cierre técnico', C.navy, 'Cada bloque conecta implementación, ecuaciones y datos exportados.');
  const spine = [
    ['1', 'Pioneer/Lua', 'Follower y celda programados con cinemática diferencial y ruedas.', C.teal],
    ['2', 'Campos potenciales', 'F_att hacia p* detrás de Bill y F_rep para obstáculos.', C.orange],
    ['3', 'Anticolisión', '16 sensores, señal de riesgo y modo AVOIDING observado.', C.red],
    ['4', 'Celda robotizada', 'Tareas con Bill, estaciones, shelves, carga y FSM auditada.', C.green],
    ['5', 'Comparación técnica', 'P, PI, PID, LQR y NMPC; cuatro modos SLAM, logs y métricas.', C.violet],
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
  addText(s, 'El comportamiento base se completa; los módulos añadidos generan comparaciones cuantitativas y límites explícitos.', 3.00, 5.56, 7.90, 0.26, { fontSize: 11.2, bold: true, color: C.white });
}

function thanks() {
  const s = pptx.addSlide();
  slideNo += 1;
  s.background = { color: C.paper };
  rect(s, 0, 0, 13.333, 7.5, C.paper, C.paper);
  rect(s, 0, 0, 13.333, 0.08, C.violet, C.violet);
  addText(s, 'Actividad 2', 0.82, 1.28, 2.2, 0.20, { fontSize: 9.5, bold: true, color: C.violet });
  addText(s, 'Discusión técnica', 0.82, 2.15, 6.8, 0.74, { fontFace: 'Aptos Display', fontSize: 42, bold: true, color: C.ink });
  addText(s, 'Control diferencial, evitación reactiva, estimación local y comparación SLAM en CoppeliaSim/Lua.', 0.86, 3.12, 6.4, 0.34, { fontSize: 12, color: C.muted });
  addImageFrame(s, img.simVideoCover, 7.05, 1.20, 4.90, 4.45, 'replay de cierre', C.violet);
  addText(s, `${slideNo}/${TOTAL}`, 11.85, 6.92, 0.55, 0.16, { fontSize: 7.4, bold: true, color: C.muted, align: 'right' });
}

function requirementsValidation() {
  const s = pSlide('validación', 'Validación de requisitos', C.green, 'Cada punto del enunciado se verifica contra la escena ejecutada y los archivos exportados; los catorce bloques quedan en estado OK.');
  const checks = [
    'Escena Sim_T2_Phase1_Basic con R1, B1, T1, T2, C1',
    'Mannequin B1 (Bill) como persona móvil',
    'Warehouse: mesas, estanterías, sofá y panel de tareas',
    'Scripts de R1 y B1 adjuntos a la escena',
    'Cuatro tareas T1/T2 completadas (entrega y retorno)',
    'Bill camina entre estaciones y toma/trabaja/entrega',
    '16 sensores activos y rayos visualizados',
    'Anticolisión: modo AVOIDING y señal de riesgo',
    'Kalman activo, mapa SLAM actualizado, error acotado',
    'Planificación con SLAM_WAYPOINT',
    'Batería: tarea aceptada y retorno a carga',
    'Capturas 3D desde CoppeliaSim (Fase 1 y Fase 2)',
    'Fase 2: mapa desconocido, robot móvil y 4 SLAM',
    'Deck editable .pptx + PDF exportado',
  ];
  checks.forEach((c, i) => {
    const col = i % 2, row = Math.floor(i / 2);
    const x = 0.82 + col * 6.35, y = 2.02 + row * 0.52;
    circle(s, x, y, 0.13, C.green, C.green);
    addText(s, c, x + 0.24, y - 0.13, 5.95, 0.30, { fontSize: 9.6, color: C.ink, fit: 'shrink' });
  });
  metricTile(s, '4/4', 'tareas', 'completadas', 0.82, 5.84, 2.95, C.green);
  metricTile(s, '16', 'sensores', 'activos + rayos', 3.95, 5.84, 2.95, C.teal);
  metricTile(s, '0,254 m', 'error pose máx.', 'acotado', 7.08, 5.84, 2.95, C.violet);
  metricTile(s, '64,7 %', 'batería', 'al volver a carga', 10.21, 5.84, 2.95, C.orange);
}

function fixesRobustness() {
  const s = pSlide('robustez', 'Incidencias corregidas y robustez', C.violet, 'Tres incidencias detectadas en validación y las salvaguardas añadidas para que la misión repita el ciclo sin bloquearse.');
  [['Sincronización T2', 'R1 podía iniciar T2 antes de que Bill llegara a WS2; se bloquea la solicitud hasta que B1 está en su estación', C.red],
   ['Ciclos del planificador', 'celdas de grid persistentes junto al objetivo hacían oscilar el desvío; se exige persistencia, se ignoran celdas pegadas y se vuelve a ruta directa', C.orange],
   ['Oscilación Hector', 'con poca textura el scan-matching daba puntajes casi planos; ventana pequeña, umbral mínimo y ganancia parcial lo estabilizan', C.violet],
  ].forEach((r, i) => {
    const x = 0.82 + i * 4.18;
    softPanel(s, x, 1.60, 3.82, 1.98, r[2], tint(r[2]));
    addText(s, r[0], x + 0.2, 1.82, 3.4, 0.22, { fontSize: 11, bold: true, color: r[2] });
    addText(s, r[1], x + 0.2, 2.24, 3.44, 1.22, { fontSize: 8.5, color: C.ink, fit: 'shrink' });
  });
  addText(s, 'Salvaguardas de navegación añadidas (Fase 2 multi-ciclo)', 0.82, 3.82, 9, 0.22, { fontSize: 10.5, bold: true, color: C.ink });
  [['Arco de retroceso', C.teal], ['Geo-valla anti-escape', C.green], ['Cotas EKF por update', C.violet], ['Throttle de replan', C.orange], ['Ralentí al rack', C.blue]].forEach((p, i) => {
    const x = 0.82 + i * 2.5;
    softPanel(s, x, 4.20, 2.34, 0.62, p[1], tint(p[1]));
    addText(s, p[0], x + 0.1, 4.40, 2.14, 0.22, { fontSize: 8.3, bold: true, color: p[1], align: 'center', fit: 'shrink' });
  });
  metricTile(s, '3', 'incidencias', 'corregidas', 0.82, 5.84, 2.95, C.green);
  metricTile(s, '0', 'recuperaciones', 'en 3 ejecuciones', 3.95, 5.84, 2.95, C.teal);
  metricTile(s, '3', 'vueltas completas', 'sin bloqueo', 7.08, 5.84, 2.95, C.violet);
  metricTile(s, 'en muros', 'geo-valla', 'el chasis no escapa', 10.21, 5.84, 2.95, C.orange);
}

function technicalConclusions() {
  const s = pSlide('conclusiones', 'Resultado técnico', C.green, 'La misión queda cerrada y la comparación ordena métodos según la métrica priorizada.');
  const cards = [
    ['Control elegido', 'PI queda primero en el puntaje de la celda: menor valor ponderado, tiempo corto y consumo estable. NMPC si se priorizan ruta y batería.', C.green],
    ['SLAM elegido', 'Kalman-landmark da el menor RMSE en espacio compacto. Grids sostienen navegación; submapas registran estructura con más coste.', C.violet],
    ['Limitaciones explícitas', 'SLAM simplificado en Lua, rayos de proximidad en lugar de LiDAR real y una ejecución por método en las tablas principales.', C.orange],
    ['Trabajo futuro', 'LiDAR 2D real, optimización de grafo completa para submapas, repetición estadística y más obstáculos dinámicos.', C.teal],
  ];
  cards.forEach((c, i) => {
    const x = i % 2 === 0 ? 0.92 : 6.86;
    const y = i < 2 ? 1.70 : 4.02;
    softPanel(s, x, y, 5.52, 1.68, c[2], tint(c[2]));
    addText(s, c[0], x + 0.22, y + 0.26, 4.95, 0.20, { fontSize: 10.5, bold: true, color: c[2], fit: 'shrink' });
    addText(s, c[1], x + 0.22, y + 0.70, 4.95, 0.56, { fontSize: 8.2, color: C.ink, fit: 'shrink' });
  });
  darkInsight(s, 'Cierre', 'El cierre enlaza especificación, implementación Lua, métricas exportadas y límites técnicos.', 0.92, 6.22, 11.70, 0.56, C.green);
}

function discussionSlide() {
  const s = pptx.addSlide();
  slideNo += 1;
  s.background = { color: C.paper };
  rect(s, 0, 0, 13.333, 7.5, C.paper, C.paper);
  rect(s, 0, 0, 13.333, 0.08, C.violet, C.violet);
  addText(s, 'Actividad 2', 0.82, 1.28, 2.2, 0.20, { fontSize: 9.5, bold: true, color: C.violet });
  addText(s, 'Discusión técnica', 0.82, 2.15, 6.8, 0.74, { fontFace: 'Aptos Display', fontSize: 42, bold: true, color: C.ink });
  addText(s, 'Control diferencial, evitación reactiva, estimación local y comparación SLAM en CoppeliaSim/Lua.', 0.86, 3.12, 6.4, 0.34, { fontSize: 12, color: C.muted });
  addImageFrame(s, img.simVideoCover, 7.05, 1.20, 4.90, 4.45, 'replay de misión', C.violet);
  addText(s, `${slideNo}/${TOTAL}`, 11.85, 6.92, 0.55, 0.16, { fontSize: 7.4, bold: true, color: C.muted, align: 'right' });
}

function coppeliaEvidence() {
  const s = pSlide('escena principal Fase 1', 'Almacén: R1, Bill y herramientas', C.orange, '');
  softPanel(s, 0.76, 1.42, 7.55, 4.62, C.teal, C.panel);
  slideAddImageFit(s, img.phase1Overview3d, 1.02, 1.70, 7.00, 3.94);
  roundRect(s, 1.02, 1.62, 5.55, 0.34, C.panel, C.panel, 8);
  addText(s, 'Escena principal: R1, Bill, rack T1/T2, mesas WS1/WS2 y estacion de carga', 1.16, 1.72, 5.20, 0.12, { fontSize: 7.1, bold: true, color: C.ink });
  addText(s, 'Operación en escena', 8.95, 1.80, 2.60, 0.22, { fontSize: 15.0, bold: true, color: C.ink, fit: 'shrink' });
  [
    ['La misión completa se ejecuta en una celda de almacén, no en una prueba aislada.', C.teal],
    ['Bill permanece orientado hacia la mesa durante el trabajo.', C.green],
    ['La evitación local y el mapa SLAM se actualizan durante la misma ejecución.', C.orange],
    ['El cierre se mide con estado, batería, riesgo, pose y mapa exportados.', C.violet],
  ].forEach((row, i) => {
    const y = 2.30 + i * 0.60;
    circle(s, 9.04, y + 0.08, 0.09, row[1], row[1]);
    addText(s, row[0], 9.28, y, 3.35, 0.30, { fontSize: 8.9, color: C.ink, fit: 'shrink' });
  });
  metricTile(s, '4/4', 'tareas', 'ciclo T1/T2 completo', 8.95, 5.24, 1.80, C.green);
  metricTile(s, '0,034 m', 'pose', 'error final Fase 1', 10.98, 5.24, 1.80, C.teal);
}

function scenarioScreenshots() {
  const s = pSlide('seguimiento, Fase 1 y Fase 2', 'Escenas de simulación', C.teal, '');
  addText(s, 'Tres ejecuciones, tres comportamientos observables', 0.82, 1.52, 5.80, 0.22, { fontSize: 14.2, bold: true, color: C.ink, fit: 'shrink' });
  addText(s, 'Las capturas cubren tres estados del sistema: seguimiento, entrega con evitación y mapa desconocido.', 0.82, 1.88, 10.30, 0.28, { fontSize: 9.0, color: C.muted });
  const cards = [
    [0.82, img.followerReplay, null, 'Seguimiento', 'Bill define el objetivo móvil y se comparan P, PI, PID, LQR y NMPC.', C.teal],
    [4.78, img.phase1Handoff3d, img.phase1SensorRays3d, 'Fase 1', 'Entrega T1/T2, Bill trabajando y evitación durante la misma misión.', C.green],
    [8.74, img.phase2Replan3d, img.phase2Overview, 'Fase 2', 'Mapa desconocido, obstáculo dinámico y reconstrucción exportada.', C.violet],
  ];
  cards.forEach(([x, imageA, imageB, title, body, color]) => {
    softPanel(s, x, 2.42, 3.42, 3.58, color, tint(color));
    slideAddImageFit(s, imageA, x + 0.28, 2.68, 2.86, imageB ? 1.60 : 2.10);
    if (imageB) slideAddImageFit(s, imageB, x + 0.68, 4.00, 2.10, 1.30);
    addText(s, title, x + 0.28, 5.34, 2.60, 0.18, { fontSize: 11.0, bold: true, color });
    addText(s, body, x + 0.28, 5.62, 2.76, 0.34, { fontSize: 8.1, color: C.ink, fit: 'shrink' });
  });
}

function simulationReplaySlide() {
  const s = pSlide('trayectoria, entrega y mapeo', 'Replay de misión', C.violet, '');
  softPanel(s, 0.76, 1.40, 7.55, 4.92, C.violet, C.panel);
  slideAddImageFit(s, img.simVideoCover, 1.04, 1.72, 6.96, 4.28);
  if (fs.existsSync(img.simVideo) && fs.existsSync(img.simVideoCover)) {
    s.addMedia({ type: 'video', path: img.simVideo, cover: dataUri(img.simVideoCover), x: 1.04, y: 1.72, w: 6.96, h: 4.28 });
  }
  circle(s, 4.24, 3.72, 0.66, C.navy, C.white, 18);
  s.addShape(pptx.ShapeType.triangle, { x: 4.45, y: 3.88, w: 0.24, h: 0.24, rotate: 90, fill: { color: C.white }, line: { color: C.white, transparency: 100 } });
  roundRect(s, 1.02, 1.60, 5.20, 0.32, C.panel, C.panel, 8);
  addText(s, 'Replay asociado a la ejecución principal de CoppeliaSim', 1.16, 1.69, 4.90, 0.11, { fontSize: 7.0, bold: true, color: C.ink });
  addText(s, 'Secuencia', 8.95, 1.78, 2.40, 0.22, { fontSize: 15.0, bold: true, color: C.ink });
  [
    ['seguimiento de Bill con orientacion frontal', C.teal],
    ['entrega y retorno de T1/T2', C.green],
    ['evitación con rayos de proximidad', C.orange],
    ['actualizacion SLAM y cierre en carga', C.violet],
  ].forEach((row, i) => {
    const y = 2.36 + i * 0.60;
    circle(s, 9.04, y + 0.08, 0.09, row[1], row[1]);
    addText(s, row[0], 9.28, y, 3.35, 0.22, { fontSize: 8.9, color: C.ink });
  });
  methodChip(s, 'replay MP4', 8.95, 5.42, C.violet, 1.30);
  methodChip(s, 'logs exportados', 10.70, 5.42, C.teal, 1.35);
}

function referencesDisclosure() {
  const s = pSlide('', 'Referencias', C.orange, '');
  [
    ['Siegwart, R.; Nourbakhsh, I.; Scaramuzza, D. (2011). Introduction to Autonomous Mobile Robots. MIT Press.', C.teal],
    ['Tzafestas, S. G. (2014). Introduction to Mobile Robot Control. Elsevier.', C.teal],
    ['LaValle, S. M. (2006). Planning Algorithms. Cambridge University Press.', C.teal],
    ['Kalman, R. E. (1960). A New Approach to Linear Filtering and Prediction Problems. Journal of Basic Engineering.', C.green],
    ['Thrun, S.; Burgard, W.; Fox, D. (2005). Probabilistic Robotics. MIT Press.', C.green],
    ['Grisetti, G.; Stachniss, C.; Burgard, W. (2007). Improved Techniques for Grid Mapping With Rao-Blackwellized Particle Filters.', C.violet],
    ['Kohlbrecher, S.; von Stryk, O.; Meyer, J.; Klingauf, U. (2011). Hector SLAM. IEEE SSRR.', C.violet],
    ['Hess, W.; Kohler, D.; Rapp, H.; Andor, D. (2016). Real-Time Loop Closure in 2D LIDAR SLAM. IEEE ICRA.', C.violet],
    ['Khatib, O. (1986). Real-Time Obstacle Avoidance for Manipulators and Mobile Robots. IJRR.', C.orange],
    ['CoppeliaSim User Manual; Pioneer 3 Operations Manual; enunciado VIU de la Actividad 2.', C.orange],
    ['Repositorios consultados/adaptados: OpenSLAM GMapping, hector_slam, Cartographer y PythonRobotics; Gemini usado para consulta e ideación visual.', C.ink],
  ].forEach((row, i) => {
    const y = 1.38 + i * 0.47;
    circle(s, 0.95, y + 0.08, 0.08, row[1], row[1]);
    addText(s, row[0], 1.16, y, 11.25, 0.22, { fontSize: 7.6, color: C.ink, fit: 'shrink' });
  });
}

const slideFns = [
  cover,
  agendaSlide,
  missionMapSlide,
  problemSlide,
  integratedArchitecture,
  coppeliaEvidence,
  scenarioScreenshots,
  videoPlaceholderFollower,
  videoPlaceholderPhase2,
  simulationReplaySlide,
  missionLoop,
  codeChanges,
  geometry,
  kinematics,
  classicalControl,
  lqr,
  nmpc,
  followerResults,
  wheelCost,
  potential,
  slamWaypoint,
  slamKalmanLandmark,
  slamGmappingGrid,
  slamHectorMatching,
  slamCartographerSubmap,
  slamResults,
  timelineExported,
  phase2Captures,
  phase2Exploration,
  phase2Correction,
  phase2Unknown,
  phase2TrajectoryComparison,
  phase2CoverageTimeline,
  phase2CoverageFinal,
  phase2UnknownMap,
  phase2ExportedSignals,
  phase2MetricsComparison,
  slamVisual,
  requirementsValidation,
  fixesRobustness,
  technicalConclusions,
  referencesDisclosure,
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

// Build a pixel-perfect PPTX from slides.pdf: every page is rendered to a high-res
// image and placed full-bleed on a 16:9 slide, so the PPTX looks identical to the
// polished TikZ deck. Self-contained: it renders the pages with pdftoppm first.
// Run:  node build_pixelperfect_pptx.js
const path = require('path');
const fs = require('fs');
const { createRequire } = require('module');
const { execSync } = require('child_process');

const DPI = 300; // ~1890x1063 px per 16:9 page

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

const PptxGenJS = loadPptxGen();
const pptx = new PptxGenJS();
pptx.author = 'Jorge Luis Mayorga Taborda';
pptx.title = 'Actividad 2 - Pioneer P3DX (pixel perfect)';
pptx.subject = 'Actividad 2 - Pioneer seguimiento y SLAM en CoppeliaSim';
pptx.defineLayout({ name: 'A2_169', width: 13.333, height: 7.5 });
pptx.layout = 'A2_169';

const dir = path.join(__dirname, '_pp');
const pdf = path.join(__dirname, 'slides.pdf');
if (!fs.existsSync(pdf)) throw new Error('slides.pdf not found; compile the deck first.');
fs.rmSync(dir, { recursive: true, force: true });
fs.mkdirSync(dir, { recursive: true });
console.log(`Rendering slides.pdf -> PNG at ${DPI} DPI ...`);
execSync(`pdftoppm -png -r ${DPI} "${pdf}" "${path.join(dir, 'slide')}"`, { stdio: 'inherit' });

const files = fs.readdirSync(dir).filter(f => /^slide-\d+\.png$/.test(f)).sort();
if (files.length === 0) throw new Error('No rendered pages produced by pdftoppm.');

for (const f of files) {
  const s = pptx.addSlide();
  s.background = { color: 'FFFFFF' };
  s.addImage({ path: path.join(dir, f), x: 0, y: 0, w: 13.333, h: 7.5 });
}

const out = path.join(__dirname, 'Actividad2_Pioneer_CoppeliaSim_PixelPerfect.pptx');
pptx.writeFile({ fileName: out }).then(() => {
  console.log(`Wrote ${out} (${files.length} slides)`);
}).catch((err) => { console.error(err); process.exitCode = 1; });

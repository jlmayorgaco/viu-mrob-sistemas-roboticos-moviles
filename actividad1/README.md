# Actividad 1 - Sistemas Robóticos Móviles

Proyecto LaTeX para la Actividad 1: oferta de automatización a planta industrial.

## Contenido

- `main.tex`: informe principal.
- `sections/`: capítulos del informe.
- `slides/slides.tex`: presentación PDF en LaTeX, equivalente a PowerPoint.
- `slides/build_pptx.py`: generador autocontenido de PowerPoint visual desde el PDF de LaTeX/TikZ.
- `slides/build_editable_pptx.js`: generador de PowerPoint nativo editable con el mismo guion y contenido clave.
- `figures/tikz/`: fuentes TikZ reutilizables del informe y la presentación.
- `tables/`: CSV auxiliares de modelos, sensores/BOM, presupuesto, KPIs, trazabilidad, referencias comerciales, supuestos ROI y sensibilidad financiera.
- `references.bib`: bibliografía usada.
- `figures/` y `tables/`: carpetas preparadas para anexar recursos.

Los enunciados originales están en `../docs/enunciado/`.

## Evidencia de entrevista

La guía de la Actividad 1 pide capturas de pantalla de la conversación con ChatGPT. Antes de entregar en el campus, guarda las capturas reales en:

- `figures/entrevista/captura_01.png`
- `figures/entrevista/captura_02.png`
- `figures/entrevista/captura_03.png`
- `figures/entrevista/captura_04.png`

El informe las inserta automáticamente en el Anexo A. Si esos archivos no existen, el PDF compila, pero la entrega no debe considerarse final.

## Compilar informe

```powershell
pdflatex -interaction=nonstopmode -halt-on-error main.tex
bibtex main
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex
```

## Compilar presentación

```powershell
cd slides
pdflatex -interaction=nonstopmode -halt-on-error slides.tex
pdflatex -interaction=nonstopmode -halt-on-error slides.tex
```

## Generar PowerPoint visual

```powershell
cd slides
python build_pptx.py
```

El PPTX conserva el diseño final de `slides.pdf` como diapositivas visuales. La fuente editable de la presentación es `slides/slides.tex`.

## Generar PowerPoint editable

```powershell
cd slides
node build_editable_pptx.js
```

El archivo `Actividad1_AMR_FOD_Kitting_editable.pptx` contiene cajas de texto y formas editables. El archivo generado ya se deja en el repositorio. Para regenerarlo desde cero se requiere Node.js y `pptxgenjs`; si el paquete no está disponible, instala la dependencia fuera del repositorio o define `NODE_PATH` hacia un `node_modules` que la contenga.

## Limpieza

```powershell
Remove-Item *.aux,*.bbl,*.blg,*.log,*.out,*.toc,*.lof,*.lot,*.nav,*.snm -ErrorAction SilentlyContinue
Remove-Item slides/*.aux,slides/*.log,slides/*.out,slides/*.nav,slides/*.snm,slides/*.toc -ErrorAction SilentlyContinue
```

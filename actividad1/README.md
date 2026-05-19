# Actividad 1 - Sistemas Robóticos Móviles

Proyecto LaTeX para la Actividad 1: oferta de automatización a planta industrial.

## Contenido

- `main.tex`: informe principal.
- `sections/`: capítulos del informe.
- `slides/slides.tex`: presentación PDF en LaTeX, equivalente a PowerPoint.
- `slides/build_pptx.py`: generador autocontenido de PowerPoint visual desde el PDF de LaTeX/TikZ.
- `figures/tikz/`: fuentes TikZ reutilizables del informe y la presentación.
- `tables/`: CSV auxiliares de modelos, sensores/BOM, presupuesto, KPIs, trazabilidad, referencias comerciales, supuestos ROI y sensibilidad financiera.
- `references.bib`: bibliografia usada.
- `figures/` y `tables/`: carpetas preparadas para anexar recursos.

Los enunciados originales estan en `../docs/enunciado/`.

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

El PPTX conserva el diseno final de `slides.pdf` como diapositivas visuales. La fuente editable de la presentación es `slides/slides.tex`.

## Limpieza

```powershell
Remove-Item *.aux,*.bbl,*.blg,*.log,*.out,*.toc,*.lof,*.lot,*.nav,*.snm -ErrorAction SilentlyContinue
Remove-Item slides/*.aux,slides/*.log,slides/*.out,slides/*.nav,slides/*.snm,slides/*.toc -ErrorAction SilentlyContinue
```

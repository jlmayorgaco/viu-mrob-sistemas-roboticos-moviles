# Actividad 1 - Sistemas Roboticos Moviles

Proyecto LaTeX para la Actividad 1: oferta de automatizacion a planta industrial.

## Contenido

- `main.tex`: informe principal.
- `sections/`: capitulos del informe.
- `slides/slides.tex`: presentacion PDF en LaTeX, equivalente a PowerPoint.
- `slides/build_pptx.py`: generador autocontenido de la presentacion editable PowerPoint.
- `tables/`: CSV auxiliares de presupuesto, KPIs, trazabilidad, referencias comerciales y supuestos ROI.
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

## Compilar presentacion

```powershell
cd slides
pdflatex -interaction=nonstopmode -halt-on-error slides.tex
pdflatex -interaction=nonstopmode -halt-on-error slides.tex
```

## Generar PowerPoint editable

```powershell
cd slides
python build_pptx.py
```

## Limpieza

```powershell
Remove-Item *.aux,*.bbl,*.blg,*.log,*.out,*.toc,*.lof,*.lot,*.nav,*.snm -ErrorAction SilentlyContinue
Remove-Item slides/*.aux,slides/*.log,slides/*.out,slides/*.nav,slides/*.snm,slides/*.toc -ErrorAction SilentlyContinue
```

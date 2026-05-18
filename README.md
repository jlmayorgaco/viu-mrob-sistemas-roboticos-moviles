# Sistemas Roboticos Moviles - VIU

Repositorio organizado por actividades de la asignatura **Sistemas Roboticos Moviles**.

## Estado

- `actividad1/`: entrega submit-ready con informe PDF, fuentes LaTeX, presentacion PDF, PowerPoint editable, presupuesto y tablas auxiliares.
- `actividad2/`: estructura separada para la segunda actividad, con fuentes y recursos de CoppeliaSim.
- `docs/enunciado/`: guias y archivos base proporcionados para la asignatura.

## Estructura

```text
.
|-- actividad1/
|   |-- main.tex
|   |-- main.pdf
|   |-- sections/
|   |-- slides/
|   |   |-- slides.tex
|   |   |-- slides.pdf
|   |   |-- build_pptx.py
|   |   `-- Actividad1_AMR_FOD_Kitting.pptx
|   |-- tables/
|   |-- references.bib
|   `-- README.md
|-- actividad2/
|   |-- main.tex
|   |-- sections/
|   |-- slides/
|   |-- coppeliasim/
|   |-- references.bib
|   `-- README.md
`-- docs/
    `-- enunciado/
        |-- Actividad_1_SRM.pdf
        |-- Actividad_2_SRM.pdf
        |-- Actividad2_1_Pioneer.ttt
        `-- Actividad2_2_Pioneer.ttt
```

## Actividad 1

La entrega final esta en `actividad1/`.

Entregables directos:

- `actividad1/main.pdf`
- `actividad1/slides/slides.pdf`
- `actividad1/slides/Actividad1_AMR_FOD_Kitting.pptx`

Compilacion completa:

```powershell
cd actividad1
pdflatex -interaction=nonstopmode -halt-on-error main.tex
bibtex main
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex

cd slides
pdflatex -interaction=nonstopmode -halt-on-error slides.tex
pdflatex -interaction=nonstopmode -halt-on-error slides.tex
python build_pptx.py
```

## Actividad 2

La segunda actividad esta aislada en `actividad2/` para no mezclar entregables.

```powershell
cd actividad2
pdflatex -interaction=nonstopmode -halt-on-error main.tex
bibtex main
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex

cd slides
pdflatex -interaction=nonstopmode -halt-on-error slides.tex
pdflatex -interaction=nonstopmode -halt-on-error slides.tex
```

## Limpieza

El repositorio ignora auxiliares de LaTeX (`*.aux`, `*.log`, `*.toc`, etc.) y carpetas de previsualizacion. Los PDFs y el PPTX final de la Actividad 1 se mantienen versionados para entrega.

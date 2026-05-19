# Sistemas Roboticos Moviles - VIU

Repositorio organizado por actividades de la asignatura **Sistemas Roboticos Moviles**.

## Estado

- `actividad1/`: entrega submit-ready con informe PDF, fuentes LaTeX, presentacion PDF, PowerPoint editable, presupuesto y tablas auxiliares.
- `actividad2/`: entrega separada con informe PDF, presentacion PDF/PPTX, escena CoppeliaSim final, scripts Lua/Python y validacion JSON.
- `docs/enunciado/`: guias y archivos base proporcionados para la asignatura.
- `docs/ppt/`: presentaciones y temas cubiertos en el curso.

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
|   |-- main.pdf
|   |-- sections/
|   |-- slides/
|   |   |-- slides.tex
|   |   |-- slides.pdf
|   |   |-- build_editable_pptx.js
|   |   `-- Actividad2_Pioneer_CoppeliaSim.pptx
|   |-- coppeliasim/
|   |   |-- Actividad2_1_Pioneer.ttt
|   |   |-- Actividad2_2_Pioneer.ttt
|   |   |-- Actividad2_Pioneer_Profesional_10_10.ttt
|   |   |-- Actividad2_Pioneer_Profesional_10_10_validation.json
|   |   |-- build_professional_scene.py
|   |   |-- pioneer_professional_controller.lua
|   |   |-- scenario_event_manager.lua
|   |   `-- multi_robot_astar_manager.lua
|   |-- references.bib
|   `-- README.md
`-- docs/
    |-- enunciado/
    |   |-- Actividad_1_SRM.pdf
    |   |-- Actividad_2_SRM.pdf
    |   |-- Actividad2_1_Pioneer.ttt
    |   `-- Actividad2_2_Pioneer.ttt
    `-- ppt/
        |-- Tema_1_Robotica_Movil.pdf
        |-- Tema_1_2_Robotica_Movil.pdf
        |-- Tema_1_3_Otros_Tipos_Robots.pdf
        |-- Tema_2_Diseno_y_Arquitectura.pdf
        |-- Tema_2_Motores.pdf
        |-- Tema_3.pdf
        `-- Tema_4.pdf
```

## Actividad 1

La entrega final esta en `actividad1/`.

Entregables directos:

- `actividad1/main.pdf`
- `actividad1/slides/slides.pdf`
- `actividad1/slides/Actividad1_AMR_FOD_Kitting.pptx`
- `actividad1/slides/Actividad1_AMR_FOD_Kitting_editable.pptx`

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

Entregables directos:

- `actividad2/main.pdf`
- `actividad2/slides/slides.pdf`
- `actividad2/slides/Actividad2_Pioneer_CoppeliaSim.pptx`
- `actividad2/coppeliasim/Actividad2_Pioneer_Profesional_10_10.ttt`
- `actividad2/coppeliasim/Actividad2_Pioneer_Profesional_10_10_validation.json`

```powershell
cd actividad2
make all
```

## Limpieza

El repositorio ignora auxiliares de LaTeX (`*.aux`, `*.log`, `*.toc`, etc.) y carpetas de previsualizacion. Los PDFs y el PPTX final de la Actividad 1 se mantienen versionados para entrega.

# Sistemas Robóticos Móviles - VIU

Repositorio organizado por actividades de la asignatura **Sistemas Robóticos Móviles**.

## Estado

- `actividad1/`: entrega submit-ready con informe PDF, fuentes LaTeX, presentación PDF, PowerPoint visual, presupuesto y tablas auxiliares.
- `actividad2/`: entrega separada con informe PDF, presentación PDF/PPTX, escenas CoppeliaSim validadas, scripts Lua/Python y validación JSON.
- `docs/enunciado/`: guías y archivos base proporcionados para la asignatura.
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
|   |-- coppeliasim/
|   |   |-- Actividad1_AMR_FOD_Kitting_HTP_Alestis.ttt
|   |   |-- Actividad1_AMR_FOD_Kitting_HTP_Alestis_validation.json
|   |   `-- build_activity1_scene.py
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
|   |   |-- Sim_T2_Phase1_Basic.ttt
|   |   |-- Sim_T2_Phase1_Basic_validation.json
|   |   |-- Sim_T2_Phase2_SLAM_Unknown.ttt
|   |   |-- Sim_T2_Phase2_SLAM_Unknown_validation.json
|   |   |-- build_phase1_basic_scene.py
|   |   `-- build_phase2_unknown_slam_scene.py
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

La entrega final está en `actividad1/`.

Entregables directos:

- `actividad1/main.pdf`
- `actividad1/slides/slides.pdf`
- `actividad1/slides/Actividad1_AMR_FOD_Kitting.pptx`
- `actividad1/coppeliasim/Actividad1_AMR_FOD_Kitting_HTP_Alestis.ttt`
- `actividad1/coppeliasim/Actividad1_AMR_FOD_Kitting_HTP_Alestis_validation.json`

Compilación completa:

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

cd ..
python coppeliasim/build_activity1_scene.py
```

## Actividad 2

La segunda actividad está aislada en `actividad2/` para no mezclar entregables.

Entregables directos:

- `actividad2/main.pdf`
- `actividad2/slides/slides.pdf`
- `actividad2/slides/Actividad2_Pioneer_CoppeliaSim.pptx`
- `actividad2/coppeliasim/Sim_T2_Phase1_Basic.ttt`
- `actividad2/coppeliasim/Sim_T2_Phase1_Basic_validation.json`
- `actividad2/coppeliasim/Sim_T2_Phase2_SLAM_Unknown.ttt`
- `actividad2/coppeliasim/Sim_T2_Phase2_SLAM_Unknown_validation.json`

```powershell
cd actividad2
make all
```

## Limpieza

El repositorio ignora auxiliares de LaTeX (`*.aux`, `*.log`, `*.toc`, etc.) y carpetas de previsualización. Los PDFs y el PPTX final de la Actividad 1 se mantienen versionados para entrega.

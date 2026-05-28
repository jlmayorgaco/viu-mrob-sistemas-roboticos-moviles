# Actividad 2 - Sistemas Roboticos Moviles

Proyecto LaTeX y escenas CoppeliaSim para la Actividad 2: programacion y control de un robot terrestre tipo Pioneer.

## Contenido

- `main.tex`: informe principal.
- `sections/`: capitulos del informe.
- `slides/slides.tex`: presentacion PDF en LaTeX.
- `slides/build_editable_pptx.js`: generador del PPTX editable.
- `coppeliasim/`: escenas `.ttt`, scripts Lua/Python, validaciones, logs CSV/JSON y figuras.
- `references.bib`: bibliografia.

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
node build_editable_pptx.js
```

## Escenas CoppeliaSim

Escena principal del informe y de la defensa:

```text
coppeliasim/Sim_T2_Phase1_Basic.ttt
coppeliasim/Sim_T2_Phase1_Basic_validation.json
```

Incluye la celda warehouse con R1, Bill/B1, herramientas T1/T2, mesas WS1/WS2, racks, estacion de carga, bateria simulada, 16 sensores del Pioneer, evitacion reactiva, Kalman landmarks y cola completa de tareas. Las mesas, sofa y racks se importan desde la libreria de modelos de CoppeliaSim cuando esta disponible. La validacion actual termina con `passed=true`, cuatro tareas completadas, estado final `CHARGING`, bateria final `71.77 %`, 21 landmarks y error final de pose `0.019 m`.

Escena Phase 2 para mapa desconocido:

```text
coppeliasim/Sim_T2_Phase2_SLAM_Unknown.ttt
coppeliasim/Sim_T2_Phase2_SLAM_Unknown_validation.json
```

Mantiene la mision T1/T2 y anade obstaculos no conocidos, zonas ocultas y replanificacion. La validacion actual termina con `passed=true`, cuatro tareas completadas, estado final `CHARGING`, bateria final `68.45 %`, 20 landmarks y evidencia maxima de mapeo `84.2 %`.

Escena base de seguimiento de Bill:

```text
coppeliasim/Actividad2_1_Basic_Follower.ttt
coppeliasim/Actividad2_1_Basic_Follower_validation.json
```

Se usa para comparar P, PI, PID, LQR y NMPC sobre la misma trayectoria de Bill.

Escena basica de campos potenciales:

```text
coppeliasim/Actividad2_Pioneer_basic.ttt
coppeliasim/Actividad2_Pioneer_basic_validation.json
```

Se usa como prueba compacta de seguimiento y evitacion reactiva. El controlador incluye una maniobra corta de recuperacion cuando los sensores frontales detectan bloqueo y el robot deja de progresar.

## Entrega de escenas

El paquete para adjuntar se prepara en `entrega_ttt/Actividad2_TTT_CoppeliaSim.zip`. Incluye las escenas `.ttt`, sus validaciones y los scripts fuente usados para construir/controlar las escenas. Para revisar la simulacion basta con abrir la `.ttt`; los scripts Python solo son necesarios si se quiere reconstruir las escenas desde cero.

Presentacion:

```text
slides/Actividad2_Pioneer_CoppeliaSim.pptx
slides/slides.pdf
```

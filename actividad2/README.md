# Actividad 2 - Sistemas Roboticos Moviles

Proyecto LaTeX para la Actividad 2: programacion y control de un robot terrestre tipo Pioneer en CoppeliaSim/Lua.

## Contenido

- `main.tex`: informe principal.
- `sections/`: capitulos del informe.
- `slides/slides.tex`: presentacion PDF en LaTeX con diseno propio, no basada en plantilla de clase.
- `coppeliasim/`: escenas `.ttt` suministradas por la asignatura y escena final generada.
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

## Entrega practica CoppeliaSim

Archivo final:

```text
coppeliasim/Actividad2_Pioneer_Profesional_10_10.ttt
```

Version basica separada, limitada a lo que pide la guia:

```text
coppeliasim/Actividad2_Pioneer_basic.ttt
```

Esta version `_basic` contiene Pioneer P3DX, objetivo `mannequin`/Bill, campos potenciales, anticolision con los 16 ultrasonidos, celda robotizada minima con vallas/transportador/obstaculos y senal `missionReady`. No incluye flota A*, bateria, HMI avanzado, escenarios S1-S8 ni labels/camaras de demo. Se genero con:

```powershell
python coppeliasim\build_basic_scene.py
```

Su validacion queda en:

```text
coppeliasim/Actividad2_Pioneer_basic_validation.json
```

Incluye Pioneer P3DX, celda robotizada, Bill/mannequin, obstaculos, zonas de seguridad, estacion de carga, HMI visual, piso industrial con textura de baldosas, carriles senalizados, franjas de seguridad, grilla A* visible, rutas de flota coloreadas, placas de demo, labels runtime, camaras de inspeccion, 16 ultrasonidos, 6 sensores virtuales adicionales, controlador Lua profesional, gestor de escenarios, flota auxiliar de 3 AMR con A* cooperativo, reservas temporales, estaciones de carga y senales de coordinacion (`missionReady`, `pioneerArrived`, `pioneerState`, `pioneerScenario`, `pioneerBatteryLevel`, `pioneerSpeedZone`, `fleetAllComplete`, `fleetChargingEvents`). Se genero con:

```powershell
python coppeliasim\build_professional_scene.py
```

La validacion headless queda guardada en:

```text
coppeliasim/Actividad2_Pioneer_Profesional_10_10_validation.json
```

La validacion final ejecuta ruta por waypoints, pallet movil, parada de seguridad, objetivo dinamico, pasillo estrecho, degradacion de sensor, bateria baja con limitacion de velocidad y aproximacion final. Resultado actual del Pioneer: `ARRIVED`, distancia final `0,739 m`, 22 sensores activos, 8 escenarios observados, HMI activo, estacion de carga presente y telemetria de bateria/zonas validada. La extension multi-robot completa 3 misiones AMR, genera 16 planes A*, evita 8 conflictos por reservas, ejecuta 4 eventos de carga y deja 3/3 robots recargados en estado READY. Tambien se validan elementos visuales: textura de piso, senalizacion industrial, labels de demo, camaras nombradas, grilla/rutas de flota y marcadores de trazabilidad con los PPTs del curso. El informe incluye una matriz de trazabilidad contra la guia de la Actividad 2 y los temas de clase: locomocion diferencial, sensores, arquitectura/control, campos potenciales, anticolision, navegacion A* y validacion cooperativa.

Presentacion:

```text
slides/Actividad2_Pioneer_CoppeliaSim.pptx
slides/slides.pdf
```

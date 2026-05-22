# Actividad 1 - Sistemas Robóticos Móviles

Proyecto LaTeX para la Actividad 1: oferta de automatización a planta industrial.

## Contenido

- `main.tex`: informe principal.
- `sections/`: capítulos del informe.
- `slides/slides.tex`: presentación PDF en LaTeX, equivalente a PowerPoint.
- `slides/build_pptx.py`: generador autocontenido de PowerPoint visual desde el PDF de LaTeX/TikZ.
- `coppeliasim/`: escena `.ttt` de apoyo para screenshots de la propuesta AMR-FOD-Kitting.
- `figures/tikz/`: fuentes TikZ reutilizables del informe y la presentación.
- `tables/`: CSV auxiliares de modelos, sensores/BOM, presupuesto, KPIs, trazabilidad, referencias comerciales, supuestos ROI y sensibilidad financiera.
- `references.bib`: bibliografía usada.
- `figures/` y `tables/`: carpetas preparadas para anexar recursos.

Los enunciados originales están en `../docs/enunciado/`.

## Evidencia de entrevista

La guía de la Actividad 1 pide capturas de pantalla de la conversación con ChatGPT. Las capturas reales incluidas en esta entrega están en:

- `figures/entrevista/screenshot_chatgpt_sc1.png`
- `figures/entrevista/screenshot_chatgpt_sc2.png`
- ...
- `figures/entrevista/screenshot_chatgpt_sc11.png`

El informe las inserta automáticamente en el Anexo A.

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

## Escena CoppeliaSim

La escena de apoyo para la Actividad 1 está en:

- `coppeliasim/Actividad1_AMR_FOD_Kitting_HTP_Alestis.ttt`
- `coppeliasim/Actividad1_AMR_FOD_Kitting_HTP_Alestis_validation.json`
- `coppeliasim/build_activity1_scene.py`

La escena se centra en el piloto de un único AMR: estación HTP A320/sección 19.1, zona logística/kitting, puerta RFID/QR, punto FOD, ruta de ida/retorno, base de carga, operadores humanos en tareas de planta y cámaras preparadas para capturas. Al iniciar la simulación, el KUKA YouBot cargado como `A1_AMR_Pilot_01_KUKA_YouBot_Model` recorre la misión dock -> kitting -> RFID/QR -> parada ante humano -> esquiva -> HTP -> FOD -> retorno mediante el frame `A1_AMR_Pilot_01_RB_KAIROS_Class_Frame`.

Para regenerarla:

```powershell
python coppeliasim/build_activity1_scene.py
```

Para tomar la captura principal, abrir el `.ttt` en CoppeliaSim y usar la cámara `A1_Camera_Overview_Submit`. También quedan preparadas `A1_Camera_HTP_Station_19_1`, `A1_Camera_Logistics_RFID_AMR` y `A1_Camera_Top_Dimensioning`. El JSON de validación comprueba 704 objetos, 6 modelos de operario, script de tareas humanas, herramienta móvil de handoff, orientación del AMR piloto, rutas dentro del suelo, parada/esquiva ante humano y una prueba corta de estabilidad sin caída. La distancia mínima validada entre ruta y operario es 0,737 m frente a un radio de seguridad de 0,68 m (0,48 m de frenado, 0,10 m de reacción/latencia y 0,10 m de margen). Las marcas de suelo representan la ruta AMR planificada para la simulación; no son guías físicas de AGV.

## Limpieza

```powershell
Remove-Item *.aux,*.bbl,*.blg,*.log,*.out,*.toc,*.lof,*.lot,*.nav,*.snm -ErrorAction SilentlyContinue
Remove-Item slides/*.aux,slides/*.log,slides/*.out,slides/*.nav,slides/*.snm,slides/*.toc -ErrorAction SilentlyContinue
```

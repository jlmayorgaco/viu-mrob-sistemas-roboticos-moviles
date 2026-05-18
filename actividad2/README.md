# Actividad 2 - Sistemas Roboticos Moviles

Proyecto LaTeX para la Actividad 2: programacion y control de un robot terrestre tipo Pioneer en CoppeliaSim/Lua.

## Contenido

- `main.tex`: informe principal.
- `sections/`: capitulos del informe.
- `slides/slides.tex`: presentacion PDF en LaTeX, equivalente a PowerPoint y sin dependencia de Beamer.
- `coppeliasim/`: escenas `.ttt` suministradas por la asignatura.
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
```

## Pendiente practico

Abrir las escenas `.ttt` en CoppeliaSim, insertar o ajustar los scripts Lua definitivos, ejecutar las pruebas y añadir capturas en `figures/`.

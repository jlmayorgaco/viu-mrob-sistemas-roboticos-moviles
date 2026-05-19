# Fuentes TikZ de la Actividad 1

Esta carpeta concentra los dibujos TikZ reutilizables del informe y la presentacion para depurarlos sin tocar todo el documento.

## Archivos

- `slides_theme.tex`: paleta, estilos tipograficos y marco comun de las diapositivas.
- `slides_icons.tex`: iconos TikZ reutilizables para AMR, HTP/seccion 19.1, QR y layout de planta.
- `slide_01_cover.tex`: portada visual de la presentacion.
- `report_architecture_diagram.tex`: diagrama de arquitectura usado por el informe.

## Uso

El informe se compila desde `actividad1/`, por eso usa:

```latex
\input{figures/tikz/report_architecture_diagram}
```

La presentacion se compila desde `actividad1/slides/`, por eso usa rutas relativas:

```latex
\input{../figures/tikz/slides_theme}
\input{../figures/tikz/slides_icons}
```

Al editar un dibujo, recompila primero solo las slides y despues ejecuta `make all` desde `actividad1/`.

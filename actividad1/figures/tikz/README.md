# Fuentes TikZ de la Actividad 1

Esta carpeta concentra los dibujos TikZ reutilizables del informe y la presentación para depurarlos sin tocar todo el documento.

## Archivos

- `slides_theme.tex`: paleta, estilos tipográficos y marco común de las diapositivas.
- `slides_icons.tex`: iconos TikZ reutilizables para AMR, HTP/sección 19.1, QR y layout de planta.
- `slide_01_cover.tex`: portada visual de la presentación.
- `slide_04_contexto.tex`: diagrama del contexto HTP A320 y sección 19.1.
- `slide_05_entrevista.tex`: relación entre entrevista, requisitos y decisiones de diseño.
- `report_architecture_diagram.tex`: diagrama de arquitectura usado por el informe.

## Uso

El informe se compila desde `actividad1/`, por eso usa:

```latex
\input{figures/tikz/report_architecture_diagram}
```

La presentación se compila desde `actividad1/slides/`, por eso usa rutas relativas:

```latex
\input{../figures/tikz/slides_theme}
\input{../figures/tikz/slides_icons}
\input{../figures/tikz/slide_05_entrevista}
```

Al editar un dibujo, recompila primero solo las slides y después ejecuta `make all` desde `actividad1/`.

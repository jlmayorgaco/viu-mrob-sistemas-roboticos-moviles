# TICKETS — Actividad 2 (Pioneer P3DX en CoppeliaSim/Lua)

**Auditoría:** revisión exhaustiva de `main.pdf` (49 pp.), `slides.pdf` (41 sl.), código Lua, escenas `.ttt`, validation JSONs y entregables vs. `docs/enunciado/Actividad_2_SRM.pdf`.
**Postura:** profesor exigente. Objetivo: deliverable **submit-ready 5/5 bulletproof**.
**Fecha auditoría:** 2026-05-28 (entrega pactada: 2026-05-26 23:59 — la entrega ya está cerrada según calendario, los tickets aplican a hardening post-entrega o re-submission).

---

## Resumen ejecutivo

El proyecto está técnicamente completo: 5 controladores comparados, 4 variantes SLAM, FSM válida, Fase 1 + Fase 2, métricas JSON exportadas, replay MP4, entrega TTT empaquetada. **Sin embargo, hay 11 blockers que un profesor riguroso detectará en una primera lectura**, todos del tipo *números en el reporte que no existen en los logs* y *bugs visuales evidentes en las diapositivas*. Resolverlos cuesta < 4 h de trabajo y eleva la nota perceptible.

**Conteo:** 11 P0 (blocker) · 7 P1 (alta) · 12 P2 (media) · 6 P3 (nit). **Total: 36 tickets.**

---

## P0 — BLOCKERS (no entregar sin resolver)

### T-001 — Encoding bug "estimaci?n" en slide 11
**Dónde:** `actividad2/figures/phase1/follower_replay_clean.png` (renderizado en slide 11 del deck, leyenda del eje).
**Problema:** la leyenda imprime literal `estimaci?n` en vez de `estimación` (matplotlib sin glifo ñ/ó).
**Por qué blocker:** primer signo de "trabajo no terminado" que un evaluador ve. Aparece en una de las slides centrales.
**Fix:** regenerar el PNG con `plt.rcParams['font.family'] = 'DejaVu Sans'` o forzar `unicode_minus=False` y `font.sans-serif=['DejaVu Sans']`. Cambiar la cadena del label a `estimación` (UTF-8) y reejecutar el plotter Python que produzca `follower_replay_clean.png`. Verificar también el resto de PNGs (`phase1_slam_*`, `phase2_*`) por el mismo defecto.

### T-002 — Slides 9 y 10 muestran sólo placeholder "VIDEO" sin enlace, QR ni ruta
**Dónde:** `actividad2/slides/slides.tex` líneas 513-521 (slide 9) y 523-531 (slide 10).
**Problema:** ambas diapositivas tituladas *"Video de ejecución I / II"* renderizan únicamente la palabra **VIDEO** en grande sobre un recuadro punteado. No hay `\href{}`, no hay `\qrcode{}`, no hay miniatura. El enunciado pide entregable con vídeo demostrativo.
**Fix:** insertar miniatura + enlace local/remoto. Mínimo aceptable:
```latex
\href{run:videos/phase1_replay.mp4}{\includegraphics[width=0.7\textwidth]{figures/phase1/phase1_replay_clean_cover.png}}
\\[0.5em]
{\small Reproduce: \texttt{videos/phase1\_replay.mp4} · \href{https://youtu.be/XXX}{Mirror online}}
```
Si los MP4 viven en `actividad2/figures/`, listarlos con `\path{}` y embeber un QR (`pst-barcode` / `qrcode`).

### T-003 — Batería final 66,76 % es un número inventado (no aparece en ningún JSON)
**Dónde:**
- `actividad2/slides/slides.tex:376` → `\Metric{9.72}{1.92}{66,76\%}{batería final Fase 1}{Green}`
- `actividad2/sections/06_integracion_celda.tex:22` → texto que cita "Batería final R1 = 66,76 %"
- `main.pdf` cap. 7 hereda este valor.

**Realidad (de `phase1_controller_logs/phase1_controller_summary.json`):**
| Modo | battery_final_pct |
|---|---|
| P    | 76,196 |
| PI   | 76,484 |
| PID  | 76,216 |
| LQR  | 76,495 |
| NMPC | 76,684 |

`phase1_slam_kalman_landmark_summary.json` → 71,984 %. **Ningún artefacto produce 66,76 %.** Y el inset del CSV plot en slide 11 muestra `battery = 76.2%` → contradicción dentro de la misma presentación.
**Fix:** decidir la fuente canónica (recomendado: el modo PI del comparativo de controladores, 76,48 % redondeado a **76,5 %**) y actualizar:
- `slides.tex:376` → `76,5\%`
- `06_integracion_celda.tex:22` → mismo número
- Cualquier eco en `00_resumen.tex` y `08_conclusiones.tex`

### T-004 — "Actualizaciones SLAM = 8532" y "Bill recorrió 7,843 m" tampoco existen
**Dónde:** `actividad2/sections/06_integracion_celda.tex` (texto narrativo, ~líneas 24-30).
**Realidad:** `phase1_slam_algorithm_comparison_metrics.json` reporta 4275, 4470, 4474, 4514 (rango). `Sim_T2_Phase1_Basic_validation.json` → `b1_moved_distance_m = 18,611 m`. 8532 ≈ suma 4275+4514 (sospechoso); 7,843 m no aparece.
**Fix:** sustituir por valores reales con la fuente citada explícitamente (e.g. *"actualizaciones SLAM en el rango 4275-4514 según método (`phase1_slam_*_summary.json`)"*; *"Bill recorrió 18,6 m de ciclo peatonal medido en `Sim_T2_Phase1_Basic_validation.json`"*).

### T-005 — Conflicto interno RMSE Kalman Fase 1: 0,03142 vs 0,03149 en el mismo capítulo
**Dónde:** `actividad2/sections/06_integracion_celda.tex:46` dice `\SI{0.03149}{m}`; la tabla comparativa `06_integracion_celda.tex:97` reporta `\textbf{0,03142}`. Ambos describen Fase 1 Kalman.
**Fix:** unificar al valor de `phase1_slam_kalman_landmark_summary.json` (RMSE pos. = 0,03142 m). Si 0,03149 viene de otra ejecución, declararlo explícitamente. Verificar que `00_resumen.tex`, `slides.tex` y `08_conclusiones.tex` usen el mismo valor (actualmente sí: 0,03142).

### T-006 — `00_resumen.tex` está huérfano: nunca se `\input` en `main.tex`
**Dónde:** `actividad2/main.tex` líneas 39-48 enumeran de `01_introduccion` a `08_conclusiones`. El capítulo Resumen no entra al PDF compilado, pero contiene material crítico (bridging Bill ↔ mannequin, números resumen). Un reporte máster sin abstract es **inaceptable**.
**Fix:** añadir entre línea 37 y 39:
```latex
\input{sections/00_resumen}
\clearpage
```
Compilar y verificar que aparezca en TOC y como primer capítulo no-numerado.

### T-007 — Bugs de "doble-pintado" ocultan o duplican contenido en slides 6, 7, 13, 19, 22, 29, 31
**Patrón:** cada una de estas slides tiene **dos bloques de overlay**. El segundo (`\fill[Panel,rounded corners=6pt] (0.62,0.92) rectangle (14.72,7.0x)`) cubre parte del primero, pero deja restos visibles fuera del recuadro.
**Síntomas confirmados en slides.pdf:**
- **Slide 6:** chip `66,76%` (líneas ~376) duplica con el segundo overlay (además T-003).
- **Slide 7:** banner "Tres ejecuciones registradas" se duplica (líneas 422-423 vs 444); shots ocultos.
- **Slide 13:** la cabecera *"R1 lee sensores, actualiza la FSM…"* (línea 617) y los 4 ClaimBoxes de código quedan **totalmente tapados** por el panel pintado en línea 643.
- **Slide 19:** chips PI/NMPC/LQR/PID duplicados (878-881 vs 865-867); tabla densa.
- **Slide 22:** chips `16 sensores | pose 2D` cortados contra el borde (y=0,94 colisiona con footer).
- **Slide 29:** chips inferiores (`4/4`, `Scan-to-map`, `Submapas`, `4275-4514`) **se solapan visiblemente** con los valores del bar chart (`0,04445` etc.). Bug de layout obvio.
- **Slide 31:** la cabecera *"Misma misión T1 y T2, pero sin mapa completo al inicio"* (línea 1296) queda parcialmente oculta por el panel de 1325-1327.

**Fix:** para cada una de las 7 slides, **borrar el primer overlay completo** (todo el bloque previo al segundo `\fill[Panel,...]`). El intent del autor fue reemplazar, no superponer.

### T-008 — Profesor: "Jose I. Iniguez" vs "Jose I. Iñiguez"
**Dónde:** `main.tex:28` → `Jose I. Iniguez` (sin tilde); `slides/slides.tex:200` y `slides/build_editable_pptx.js:530` → `Jose I. Iñiguez` (con tilde). Mismatch entre portada del reporte y del deck.
**Fix:** unificar a la forma con tilde en `main.tex:28` (`\SetVIUProfessor{\begin{tabular}[t]{@{}l@{}}Jose I. Iñiguez\\...`). El email `jinigueza@professor.universidadviu.com` ya implica la ñ.

### T-009 — `v_max=0,55 m/s` y `omega_max=1,32 rad/s` no coinciden con ningún controlador
**Dónde:** `slides.tex:725-730` (slide 15), `03_modelo_robot.tex` y `09_anexos.tex` (tabla de parámetros).
**Realidad:**
- `phase1_r1_task_controller.lua:21-22` → `vMax=0.62`, `wMax=1.42`
- `pioneer_pid_follower_controller.lua:11,13` → `vMax=0.72`, `wMax=1.65`
- `pioneer_basic_controller.lua:12-13` → `vMax=0.44`, `wMax=1.30`

Ningún Lua usa 0,55 / 1,32. Es una afirmación falsa, verificable abriendo cualquier `.lua`.
**Fix:** ya sea (a) reemplazar en el reporte por una tabla "rango v_max usado por controlador: 0,44 – 0,72 m/s; ω_max 1,30 – 1,65 rad/s", o (b) modificar los Lua a 0,55 / 1,32 si esa es la intención y re-ejecutar (no recomendado, requiere re-correr todo). Opción (a) es trivial.

### T-010 — Dos slides distintas con título idéntico *"Fase 2: mapa desconocido"*
**Dónde:** slide 31 (`slides.tex:1293`) y slide 36 (`slides.tex:1455`).
**Fix:** renombrar slide 36 a algo descriptivo: *"Fase 2: vista cenital del mapa revelado"* o *"Fase 2: telemetría y obstáculos detectados"*.

### T-011 — Resumen afirma "0,040 m de error final de pose" contra validación 0,030 m
**Dónde:** `00_resumen.tex:34` dice *"cerró con \SI{0.040}{m} de error final de pose"*. La tabla del cap. 7 reporta 0,030 m. Las JSONs Fase 1 (P/PI/PID/LQR/NMPC) reportan `max_pose_error_m` ∈ {0,0415, 0,0430, 0,0447, 0,0448, 0,0459}; ninguna es 0,040. La Fase 2 Kalman → 0,0447.
**Fix:** alinear al valor de la fuente declarada (Fase 1: usar 0,030 m, RMSE; Fase 2: usar 0,03185 m, RMSE; *no* mezclar "max" y "mean"). Cuando T-006 quede resuelto, asegurar coherencia.

---

## P1 — ALTA (visibles a primera vista, restan profesionalidad)

### T-012 — Contraste de chips en portada (slide 1): texto blanco sobre pastel
**Dónde:** `slides.tex:194-198` — `\node[font=...,text=white] at (\x+0.65,3.90) {\lab};` con `fill=\col!22` (22 % de saturación, muy claro).
**Fix:** `text=\col` (o `text=Ink`). Mismo patrón ya correcto en `SectionRail` (líneas 68-70).

### T-013 — Fórmula de scoring nunca publicada en el cuerpo del reporte
**Dónde:** `03_modelo_robot.tex:78,88` y `08_conclusiones.tex:27` mencionan *"PI obtuvo el mejor puntaje ponderado"* pero el peso vector (0,28 movimiento + 0,18 batería + 0,20 variación + 0,14 riesgo + 0,12 error pose + 0,08 duración) no aparece. Sí está en `phase1_controller_summary.json:125-132` y `run_phase1_controller_comparison.py:164-171` (verificado idéntico).
**Fix:** añadir nota al pie o párrafo en §03 / §09 anexos con la fórmula y por qué se eligieron esos pesos.

### T-014 — Tablas sin `\caption{}` ni `\label{}` (no se pueden referenciar)
**Dónde:**
- `09_anexos.tex:125-139` (tabla de controladores) → sin caption, sin label.
- `02_entorno_coppeliasim.tex:12-30` (tabla de elementos de la celda) → sin caption, sin label.

**Fix:** añadir `\caption{...}` + `\label{tab:phase1-controller-anexo}` / `\label{tab:warehouse-elements}` y citarlas desde el cuerpo (e.g. *"según la Tabla \ref{tab:warehouse-elements}"*).

### T-015 — La mayoría de figuras flotan sin `\ref{}` en el texto
**Dónde:** ~18 etiquetas `\label{fig:...}` definidas, sólo ~5 se citan vía `\ref` en prosa. Estándar académico: toda figura debe ser referenciada explícitamente.
**Fix:** sweep por cada `\label{fig:XXX}` y asegurar al menos una `\ref{fig:XXX}` en el párrafo más cercano. Lista prioritaria de figuras a referenciar:
`fig:phase1-layout`, `fig:follower-replay`, `fig:follower-geometry`, `fig:follower-pid-comparison`, `fig:controller-comparison`, `fig:estimator-pipeline`, `fig:slam-comparison`, `fig:phase2-slam-comparison`, `fig:phase2-reconstruction-t60`.

### T-016 — Sobrecarga de símbolo en NMPC: `r_w` (rueda) colisiona con `r_ω` (giro)
**Dónde:** `03b_seguimiento_bill.tex:242-252`, slide 18.
La función de coste tiene `r_v v² + r_ω ω² + r_w (ω_L² + ω_R²)`. Tres símbolos parecidos confunden.
**Fix:** renombrar a `r_{whl}` o `r_{rueda}` para `(ω_L² + ω_R²)`. Actualizar slide 18 (línea ~837).

### T-017 — Nombres de estados FSM en slides no coinciden con código
**Dónde:** slide 12 (FSM) usa `DELIVER_T1`, `WAIT_B1_T1`, `RETURN_T1`. El Lua usa `DELIVER_T1_WS1`, `WAIT_B1_WORK_T1`, `RETURN_T1_RACK` (verificado en `phase1_r1_task_controller.lua` y en `task_states_seen` de los JSONs).
**Fix:** alinear nombres en el diagrama de slide 12 (y la prosa de `06_integracion_celda.tex`) a los nombres reales del código. El grader podría comparar slide ↔ Lua.

### T-018 — Path absoluto hardcodeado en `capture_coppeliasim_screenshots.lua`
**Dónde:** `actividad2/coppeliasim/capture_coppeliasim_screenshots.lua:49` → ruta tipo `C:/Users/walla/...`.
**Por qué importa:** no es portable; otro evaluador que ejecute el script tirará a un path inexistente.
**Fix:** usar `sim.getStringParam(sim.stringparam_scene_path)` como fallback o ruta relativa `./figures/phase1`.

---

## P2 — MEDIA (polish y limpieza)

### T-019 — 6 entradas en `references.bib` nunca se citan
**No citadas:** `siegwart2011`, `tzafestas2014`, `lavalle2006`, `coppeliasimManual`, `viuActividad2`, `hart1968`.
**Side effect:** `\bibliographystyle{ieeetr}` sólo imprime las citadas, así que el main.pdf bibliografía no las muestra → mismatch con la lista hardcoded del slide 41 (que sí enumera Siegwart, Tzafestas, LaValle, CoppeliaSim manual).
**Fix:** citar al menos `\cite{siegwart2011}` en §01 introducción (texto general de robótica móvil), `\cite{lavalle2006}` en §04 planificación, `\cite{tzafestas2014}` en §03 control, `\cite{coppeliasimManual}` en §02, `\cite{viuActividad2}` en §01. `hart1968` puede borrarse si A* no se discute.

### T-020 — Subtítulo redundante "Mapa y obstáculos" en slide 36
**Dónde:** `slides.tex:1466` dentro de un panel que ya tiene título *"Fase 2: mapa desconocido"*. Combinado con T-010, da doble redundancia.
**Fix:** eliminar o renombrar a algo informativo (e.g. *"Vista cenital de la celda revelada en t=60 s"*).

### T-021 — Mezcla `.` y `,` como separador decimal en math mode
**Dónde:** `03b_seguimiento_bill.tex:250-252` (pesos NMPC `q_d=48.0, q_t=7.0, q_ψ=1.2`, etc.); `slides.tex:806, 829` (`\Delta t=0,05s`, `\Delta t=0,22s`); `slides.tex:725` (`L=0,331 m`).
`siunitx` está configurado con `output-decimal-marker={,}`, pero math mode literal usa `.`. La coma en math se renderiza como puntuación con espacio fino.
**Fix:** envolver con `{,}`:
- `$L=0{,}331$ m` (slide 15)
- `$\Delta t = 0{,}05\,\mathrm{s}$` (slides 17, 18; secciones 03b)
- `q_d=48{,}0`, `q_t=7{,}0`, etc. en `03b_seguimiento_bill.tex:250-252`
- Matriz K LQR en `03b:208-210`

### T-022 — Formato inconsistente `\path{HECTOR_GRID_MATCHING}` vs `\texttt{KALMAN_LANDMARK}`
**Dónde:** `05_anticolisiones.tex:244` usa `\path{}`; el resto usa `\texttt{}`.
**Fix:** `\texttt{HECTOR\_GRID\_MATCHING}`.

### T-023 — Dos galerías de figuras consecutivas en `06b_phase2_unknown_slam.tex` sin diferenciación textual
**Dónde:** líneas 20-35 y 37-59 — dos `\begin{figure}` seguidas, ninguna citada desde el cuerpo, sin frase de transición.
**Fix:** o bien fusionar en una sola figura de 5 paneles, o añadir frase: *"Las capturas operativas se recogen en la Fig.~\ref{fig:phase2-coppeliasim-captures}; el conjunto extendido (sensores y plano) en la Fig.~\ref{fig:phase2-coppeliasim-screenshots-extra}."*

### T-024 — Submapas Fase 1 = Fase 2 = 13 con 4 cierres (sospechoso copy-paste)
**Dónde:** `06_integracion_celda.tex:102-103` y `06b_phase2_unknown_slam.tex:128-129` reportan idénticos 13/4. ¿Real o copia?
**Fix:** verificar contra `phase1_slam_cartographer_submap_summary.json` y `phase2_slam_unknown_cartographer_submap_summary.json`. Si coinciden, añadir frase aclaratoria: *"(misma cuenta por reusar parametrización de submapa: longitud, edad y umbral idénticos)"*.

### T-025 — Parámetros Cartographer (22 s, 0,45 m, 0,35 puntaje) no listados en anexo
**Dónde:** `05_anticolisiones.tex:290-294` los usa en texto pero `09_anexos.tex` no los enumera.
**Fix:** agregar fila(s) en la tabla de parámetros del anexo: `cartographer.submap_min_age_s`, `cartographer.submap_max_distance_m`, `cartographer.loop_closure_score`.

### T-026 — Bridge mannequin↔Bill se pierde si Resumen sigue huérfano (depende de T-006)
**Dónde:** `00_resumen.tex:9-10` hace el puente; `01_introduccion.tex:5-7` lo repite parcialmente con `\texttt{mannequin}` (monospace).
**Fix:** una vez resuelto T-006, normalizar a `\textit{mannequin}` (cursiva) en todas las apariciones, no `\texttt{}`.

### T-027 — Archivos `.ttt` legacy contaminan el repo
**Dónde:** `actividad2/coppeliasim/Actividad2_1_Pioneer.ttt` y `Actividad2_2_Pioneer.ttt` (May 18, 1,5 MB y 1,6 MB). Las escenas vigentes son `Sim_T2_Phase1_Basic.ttt` y `Sim_T2_Phase2_SLAM_Unknown.ttt` (May 27). El bundle de entrega (`entrega_ttt/Actividad2_TTT_CoppeliaSim/`) sólo lleva las nuevas (correcto), pero un evaluador del repo verá los antiguos sin saber su estado.
**Fix:** mover a `actividad2/coppeliasim/legacy/` o eliminar.

### T-028 — Disclosure de Gemini en slide 41 muy informal
**Dónde:** `slides.tex:1669` — *"Repositorios consultados/adaptados: OpenSLAM GMapping, hector_slam, Cartographer y PythonRobotics; Gemini usado para consulta e ideación visual."*
**Fix:** reescribir como disclosure académica:
> *"Asistencia de IA generativa (Google Gemini) para ideación visual y consulta documental. Código, métricas, validación y conclusiones son del autor; ver `references.bib` para fuentes primarias."*

### T-029 — Magic numbers en `phase1_r1_task_controller.lua` sin comentar
**Dónde:** `phase1_r1_task_controller.lua:21-24` (60+ constantes), `:1395-1422` (ganancias P/PI/PID embebidas).
**Fix:** comentar al menos `vMax`, `wMax`, `avoidRange`, `kRepulsion`, `slamProcessXY`, `gridLogOcc`, `submapDistance`, `pathDetourOffset` con 1 línea cada uno. ~15 min.

### T-030 — `01_introduccion.tex` carece de subsección explícita "Objetivos"
**Dónde:** la introducción tiene una tabla de trazabilidad pero ningún bullet list de objetivos. Estándar máster lo exige.
**Fix:** añadir `\section{Objetivos}` con 4-5 bullets antes de "Relación con el enunciado".

---

## P3 — NITS (typografía y limpieza menor)

### T-031 — `L=0,331 m` math-mode con coma (cubierto en T-021, lo separo por slide 15 específicamente)
Ver T-021. Aplica también a slide 14 (`$d_{des}=0{,}82$ m`).

### T-032 — `__pycache__/` y artefactos build sin `.gitignore`
**Dónde:** `actividad2/coppeliasim/__pycache__/`, `actividad2/slides/build/`, posibles `.aux`/`.log`.
**Fix:** añadir a `.gitignore` raíz del repo.

### T-033 — Nombre de archivo engañoso: `05_anticolisiones.tex` contiene contenido SLAM
**Dónde:** `actividad2/sections/05_anticolisiones.tex` — chapter title es *"Estimación y SLAM"*. El contenido anticolisión real vive en `04_campos_potenciales.tex`.
**Fix:** renombrar archivo a `05_estimacion_slam.tex` y actualizar `main.tex:43-44`. Cosmético pero mejora higiene del repo.

### T-034 — Párrafo huérfano sin línea en blanco en `04_campos_potenciales.tex:54-56`
**Fix:** añadir línea en blanco antes y después; reformatear como párrafo independiente.

### T-035 — `03_modelo_robot.tex:81` cross-reference NMPC vago
**Dónde:** *"Evalúa secuencias de v,ω con restricciones y coste de suavidad mediante búsqueda local."*
**Fix:** añadir `(véase Sección~\ref{sec:nmpc})` con el `\label` apropiado en `03b_seguimiento_bill.tex`.

### T-036 — `08_conclusiones.tex:32-36` carece de `\section{Limitaciones}` propio
**Fix:** envolver el párrafo de limitaciones formales en `\section{Limitaciones y trabajo futuro}` numerada.

---

## Verificado OK (no requiere acción)

- Funciones Lua claim/exist: `readObstacleField` (línea 1172), `registerSlamDetection` (línea 1150), `plannedWaypointTo` (línea 1614), `deliverToolToBill` (línea 1764) — todas existen con semántica declarada.
- Modos planner detectados: `DIRECT`, `DIRECT_AFTER_WAYPOINT`, `SLAM_WAYPOINT`, `RECOVERY_DIRECT` — coinciden con narrativa.
- 16 ultrasonidos: confirmado en todos los validation JSONs (`sensor_count: 16`).
- `L=0,331 m`, `r=0,0975 m`: hardcodeados en Lua, coinciden.
- LQR Q=diag(35,80,18), R=diag(6,3), dt=0,05: `compute_follower_lqr_gain.py:18-19` coincide.
- NMPC N=10, dt=0,22: coincide en Lua y reporte.
- Scoring weights 0,28/0,18/0,20/0,14/0,12/0,08: coinciden en `run_phase1_controller_comparison.py:164-171` y `phase1_controller_summary.json:125-132`.
- RMSE Fase 1: Kalman 0,03142 / Log-odds 0,04117 / Submapas 0,04149 / Scan-to-map 0,04445 → coinciden con `phase1_slam_algorithm_comparison_metrics.json`.
- RMSE Fase 2: Kalman 0,03185 / Submapas 0,03930 / Log-odds 0,04220 / Scan-to-map 0,04587 → coinciden con `phase2_slam_unknown_algorithm_metrics.json`.
- Cobertura Fase 2 (94,613 / 94,851 / 94,930 / 95,327 %): coinciden.
- 17–25 replans / 9–10 cruces dinámicos / 0–1 recoveries: coinciden con summaries Phase 2 (Kalman: 17/9/0; Log-odds: 19/9/0; Hector: 24/9/0; Cartographer: 25/10/1).
- Entrega TTT empaquetada: `actividad2/entrega_ttt/Actividad2_TTT_CoppeliaSim/` + `.zip` existen con 4 escenas, validations y Lua sources.
- Todos los validation JSONs reportan `passed: true`.
- No hay `TODO/FIXME/XXX/HACK/DEBUG` en `.lua` ni `.py`.
- Profesor email `jinigueza@professor.universidadviu.com` consistente.
- Fecha de portada 26 de mayo de 2026 coincide con deadline del enunciado.
- `references.bib` 21 entradas, bien formateadas.
- `enunciado` deliverables: PDF reporte ✓, deck PPTX ✓ (`slides/Actividad2_Pioneer_CoppeliaSim.pptx`), escena CoppeliaSim ✓ (entrega_ttt), Pioneer P3DX ✓, campos potenciales ✓, anticolisión ✓, integración celda ✓.

---

## Orden recomendado de ejecución

**Sesión 1 (1 h, blockers numéricos y portada):** T-003, T-004, T-005, T-008, T-009, T-011 → resolver inconsistencias entre reporte y datos JSON. Después recompilar `main.pdf`.

**Sesión 2 (1,5 h, slides):** T-001 (regenerar PNG), T-002 (insertar enlaces video), T-007 (limpiar 7 slides con doble-overlay), T-010, T-012, T-020 → recompilar `slides.pdf`.

**Sesión 3 (1 h, estructura LaTeX):** T-006 (input Resumen), T-013, T-014, T-015, T-017, T-019 (citar refs unused).

**Sesión 4 (30 min, código y limpieza):** T-018 (path portable), T-027 (mover legacy ttt), T-029 (comentar magic numbers), T-022, T-023, T-028.

**Sesión 5 (30 min, nits):** T-016, T-021, T-024, T-025, T-026, T-030, T-031, T-032, T-033, T-034, T-035, T-036.

**Total estimado:** ~4,5 h para llegar a 5/5.

---

## Apéndice: cómo verificar tras los fixes

```powershell
# Recompilar el reporte
cd actividad2
pdflatex main.tex; bibtex main; pdflatex main.tex; pdflatex main.tex

# Recompilar slides
cd slides
pdflatex slides.tex; pdflatex slides.tex

# Verificar bibliografía limpia
Select-String -Path main.bbl -Pattern "Warning|Error"

# Verificar no quedan refs huérfanas
Select-String -Path main.log -Pattern "undefined|multiply defined"

# Verificar números clave (re-grep)
Select-String -Path "slides/slides.tex","sections/*.tex" -Pattern "66,76|8532|0,03149|0,55 m/s|1,32 rad/s"
# expected: 0 matches
```

# Comparación SLAM - Phase 2 Unknown Map

## Alcance

La comparación usa la misma escena `Sim_T2_Phase2_SLAM_Unknown.ttt`, el mismo controlador PID y los mismos sensores de proximidad visualizados como rayos. R1 parte sin mapa completo y reconstruye obstáculos desde lecturas en línea. Los nombres GMapping, Hector y Cartographer identifican el enfoque implementado en Lua dentro de CoppeliaSim.

Solo `P2_Dynamic_Pallet` y `P2_Temporary_Blocker` se mueven por script. Su movimiento es determinístico y periódico; las cajas y marcadores desconocidos permanecen fijos.

La figura `phase2_slam_unknown_reconstruction_t60.png` compara la reconstrucción del mapa al mismo instante común: t=60.0 s.

## Resultados

| Métrica | GMAPPING_GRID | HECTOR_GRID_MATCHING | CARTOGRAPHER_SUBMAP | KALMAN_LANDMARK |
|---|---:|---:|---:|---:|
| Completado | True | True | True | True |
| Duración [s] | 128.0 | 129.4 | 138.65 | 124.8 |
| Evidencia mapa final [%] | 94.851 | 94.93 | 95.327 | 94.613 |
| Tiempo a 50% evidencia [s] | 1.55 | 1.55 | 1.55 | 19.8 |
| Tiempo a 75% evidencia [s] | 5.1 | 5.1 | 5.1 | 98.55 |
| Rasgos t=60s | 36 | 36 | 36 | 11 |
| Rasgos finales | 36 | 36 | 36 | 24 |
| Recall proxy t=60s | 0.25 | 0.25 | 0.25 | 0.25 |
| Precisión proxy final | 0.25 | 0.333 | 0.278 | 0.25 |
| Actualizaciones SLAM | 5558 | 5686 | 6520 | 5219 |
| RMSE posición [m] | 0.0422 | 0.04587 | 0.0393 | 0.03185 |
| Error P95 pose [m] | 0.05638 | 0.0759 | 0.05773 | 0.03985 |
| Replanificaciones | 19 | 24 | 25 | 17 |
| Recuperaciones del planificador | 0 | 0 | 1 | 0 |
| Cruces pallet | 9 | 9 | 10 | 9 |
| Distancia mínima a obstáculo [m] | 0.05562 | 0.1014 | 0.06047 | 0.05401 |
| Riesgo máximo | 0.82863 | 0.69965 | 0.80613 | 0.80168 |
| Batería usada [%] | 24.57625 | 24.47612 | 25.91574 | 24.32425 |
| Submapas | 0 | 0 | 13 | 0 |
| Cierres de ciclo | 0 | 0 | 4 | 0 |

## Interpretación técnica

La evidencia de mapa mide actividad de mapeo. La calidad geométrica se reporta con proxies de recall y precisión frente a obstáculos Phase 2 conocidos. `GMAPPING_GRID`, `HECTOR_GRID_MATCHING` y `CARTOGRAPHER_SUBMAP` reconstruyen una grid dispersa desde rayos; `KALMAN_LANDMARK` reconstruye landmarks puntuales. Hector agrega ajuste local de escaneos y Cartographer agrega submapas con cierres de ciclo locales.

La columna `Completado` tiene prioridad sobre RMSE o evidencia de mapa al seleccionar el método operativo.

# Comparación SLAM - Phase 2 Unknown Map

## Alcance

La comparación usa la misma escena `Sim_T2_Phase2_SLAM_Unknown.ttt`, el mismo controlador PID y los mismos sensores de proximidad visualizados como rayos. R1 parte sin mapa completo y reconstruye obstáculos desde lecturas en línea. Los nombres GMapping, Hector y Cartographer identifican el enfoque implementado en Lua dentro de CoppeliaSim.

Solo `P2_Dynamic_Pallet` y `P2_Temporary_Blocker` se mueven por script. Su movimiento es determinístico y periódico; las cajas y marcadores desconocidos permanecen fijos.

La figura `phase2_slam_unknown_reconstruction_t60.png` compara la reconstrucción del mapa al mismo instante común: t=60.0 s.

## Resultados

| Métrica | GMAPPING_GRID | HECTOR_GRID_MATCHING | CARTOGRAPHER_SUBMAP | KALMAN_LANDMARK |
|---|---:|---:|---:|---:|
| Completado | True | True | True | True |
| Duración [s] | 92.45 | 91.55 | 104.2 | 88.6 |
| Evidencia mapa final [%] | 90.421 | 90.433 | 91.288 | 50.119 |
| Tiempo a 50% evidencia [s] | 11.0 | 10.8 | 10.8 | 84.75 |
| Tiempo a 75% evidencia [s] | 55.4 | 54.05 | 60.65 | None |
| Rasgos t=60s | 22 | 23 | 18 | 9 |
| Rasgos finales | 29 | 31 | 27 | 9 |
| Recall proxy t=60s | 0.5 | 0.25 | 0.5 | 0.5 |
| Precisión proxy final | 0.172 | 0.323 | 0.333 | 0.333 |
| Actualizaciones SLAM | 2714 | 2718 | 3018 | 2779 |
| RMSE posición [m] | 0.01664 | 0.08182 | 0.04011 | 0.07392 |
| Error P95 pose [m] | 0.02186 | 0.19962 | 0.08094 | 0.13366 |
| Replanificaciones | 15 | 16 | 20 | 14 |
| Recuperaciones del planificador | 0 | 0 | 0 | 0 |
| Cruces pallet | 1 | 2 | 2 | 4 |
| Distancia mínima a obstáculo [m] | 0.05682 | 0.21537 | 0.05125 | 0.05112 |
| Riesgo máximo | 0.82511 | 0.42591 | 0.83971 | 0.84191 |
| Batería usada [%] | 23.41406 | 23.1142 | 25.46576 | 24.33432 |
| Submapas | 0 | 0 | 16 | 0 |
| Cierres de ciclo | 0 | 0 | 4 | 0 |

## Interpretación técnica

La evidencia de mapa mide actividad de mapeo. La calidad geométrica se reporta con proxies de recall y precisión frente a obstáculos Phase 2 conocidos. `GMAPPING_GRID`, `HECTOR_GRID_MATCHING` y `CARTOGRAPHER_SUBMAP` reconstruyen una grilla dispersa desde rayos; `KALMAN_LANDMARK` reconstruye landmarks puntuales. Hector agrega ajuste local de escaneos y Cartographer agrega submapas con cierres de ciclo locales.

La columna `Completado` tiene prioridad sobre RMSE o evidencia de mapa al seleccionar el método operativo.

# Comparación SLAM - Phase 1 Basic

## Alcance

La comparación usa modos implementados en CoppeliaSim con los mismos sensores, tarea, controlador y escenario. Los nombres GMapping, Hector y Cartographer identifican el enfoque usado en cada variante, no la ejecución de paquetes ROS externos:

- `GMAPPING_GRID`: mapeo tipo GMapping basado en grilla de ocupación con actualización log-odds por rayos de proximidad.
- `HECTOR_GRID_MATCHING`: ajuste local de escaneos contra grilla de ocupación, inspirado en Hector SLAM.
- `CARTOGRAPHER_SUBMAP`: grilla con submapas y cierres de ciclo locales, inspirado en Google Cartographer.
- `KALMAN_LANDMARK`: localización Kalman/EKF y rasgos de obstáculos actualizados con Kalman.

## Resultados

| Métrica | GMAPPING_GRID | HECTOR_GRID_MATCHING | CARTOGRAPHER_SUBMAP | KALMAN_LANDMARK |
|---|---:|---:|---:|---:|
| Completado | True | True | True | True |
| Duración [s] | 84.3 | 80.0 | 80.7 | 79.9 |
| Longitud de ruta [m] | 16.34 | 15.884 | 15.919 | 16.379 |
| RMSE posición [m] | 0.01696 | 0.09079 | 0.07882 | 0.06089 |
| Error P95 [m] | 0.03097 | 0.245 | 0.19774 | 0.13648 |
| Error máximo [m] | 0.03896 | 0.28226 | 0.31163 | 0.20768 |
| Rasgos/celdas finales | 26 | 27 | 27 | 9 |
| Actualizaciones SLAM | 2583 | 2307 | 2382 | 2340 |
| Submapas | 0 | 0 | 16 | 0 |
| Cierres de ciclo | 0 | 0 | 2 | 0 |
| Distancia mínima a obstáculo [m] | 0.05976 | 0.12413 | 0.18206 | 0.05878 |
| Riesgo máximo | 0.81651 | 0.63437 | 0.49732 | 0.81936 |
| Batería usada [%] | 24.05397 | 23.25518 | 23.2671 | 23.88346 |

## Interpretación técnica

`GMAPPING_GRID`, `HECTOR_GRID_MATCHING` y `CARTOGRAPHER_SUBMAP` producen mapas de ocupación. `KALMAN_LANDMARK` produce un mapa compacto de puntos de obstáculo. Hector usa ajuste local de escaneos contra la grilla. Cartographer mantiene submapas y registra cierres de ciclo locales. La comparación queda acotada a CoppeliaSim y a los sensores de proximidad de la escena.

Conclusión: los resultados comparan cuatro estrategias de estimación y mapeo dentro de la misma misión simulada.

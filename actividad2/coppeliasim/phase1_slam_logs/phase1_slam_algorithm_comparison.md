# Comparación SLAM - Phase 1 Basic

## Alcance

La comparación usa modos implementados en CoppeliaSim con los mismos sensores, tarea, controlador y escenario. Los nombres GMapping, Hector y Cartographer identifican el enfoque usado en cada variante, no la ejecución de paquetes ROS externos:

- `GMAPPING_GRID`: mapeo tipo GMapping basado en grid de ocupación con actualización log-odds por rayos de proximidad.
- `HECTOR_GRID_MATCHING`: ajuste local de escaneos contra grid de ocupación, inspirado en Hector SLAM.
- `CARTOGRAPHER_SUBMAP`: grid con submapas y cierres de ciclo locales, inspirado en Google Cartographer.
- `KALMAN_LANDMARK`: localización Kalman/EKF y rasgos de obstáculos actualizados con Kalman.

## Resultados

| Métrica | GMAPPING_GRID | HECTOR_GRID_MATCHING | CARTOGRAPHER_SUBMAP | KALMAN_LANDMARK |
|---|---:|---:|---:|---:|
| Completado | True | True | True | True |
| Duración [s] | 125.6 | 123.55 | 125.25 | 121.45 |
| Longitud de ruta [m] | 15.997 | 15.233 | 15.968 | 15.763 |
| RMSE posición [m] | 0.04117 | 0.04445 | 0.04149 | 0.03142 |
| Error P95 [m] | 0.05718 | 0.07596 | 0.06026 | 0.0467 |
| Error máximo [m] | 0.07354 | 0.10862 | 0.07362 | 0.05824 |
| Rasgos/celdas finales | 94 | 84 | 91 | 20 |
| Actualizaciones SLAM | 4514 | 4470 | 4474 | 4275 |
| Submapas | 0 | 0 | 13 | 0 |
| Cierres de ciclo | 0 | 0 | 4 | 0 |
| Distancia mínima a obstáculo [m] | 0.05407 | 0.1288 | 0.0595 | 0.10396 |
| Riesgo máximo | 0.80407 | 0.59926 | 0.80463 | 0.69276 |
| Batería usada [%] | 24.62225 | 23.6279 | 24.49654 | 24.01627 |

## Interpretación técnica

`GMAPPING_GRID`, `HECTOR_GRID_MATCHING` y `CARTOGRAPHER_SUBMAP` producen mapas de ocupación. `KALMAN_LANDMARK` produce un mapa compacto de puntos de obstáculo. Hector usa ajuste local de escaneos contra la grid. Cartographer mantiene submapas y registra cierres de ciclo locales. La comparación queda acotada a CoppeliaSim y a los sensores de proximidad de la escena.

Conclusión: los resultados comparan cuatro estrategias de estimación y mapeo dentro de la misma misión simulada.

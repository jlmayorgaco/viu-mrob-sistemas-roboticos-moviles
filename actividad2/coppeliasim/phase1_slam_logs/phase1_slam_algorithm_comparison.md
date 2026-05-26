# Comparacion SLAM - Phase 1 Basic

## Alcance

No se ejecutaron paquetes ROS reales (`slam_gmapping`, `hector_mapping` o Google Cartographer) porque el entorno Windows no tiene `rosrun` ni `ros2`. La comparacion usa modos implementados en CoppeliaSim con los mismos sensores, tarea, controlador y escenario:

- `GMAPPING_GRID`: mapper tipo GMapping basado en grilla de ocupacion con actualizacion log-odds por rayos LiDAR/proximidad.
- `HECTOR_GRID_MATCHING`: scan matching local contra grilla de ocupacion, inspirado en Hector SLAM.
- `CARTOGRAPHER_SUBMAP`: grilla con submaps y loop-closure simplificado, inspirado en Google Cartographer.
- `KALMAN_LANDMARK`: localizacion Kalman/EKF reducida y landmarks de obstaculos actualizados con Kalman.

## Resultados

| Metrica | GMAPPING_GRID | HECTOR_GRID_MATCHING | CARTOGRAPHER_SUBMAP | KALMAN_LANDMARK |
|---|---:|---:|---:|---:|
| Completado | True | True | True | True |
| Duracion [s] | 102.6 | 102.5 | 101.65 | 101.6 |
| Longitud de ruta [m] | 10.906 | 10.88 | 10.774 | 10.771 |
| RMSE posicion [m] | 0.04135 | 0.04072 | 0.03842 | 0.0316 |
| Error P95 [m] | 0.05697 | 0.06485 | 0.05673 | 0.04959 |
| Error maximo [m] | 0.07722 | 0.11112 | 0.0934 | 0.06433 |
| Features/celdas finales | 63 | 56 | 55 | 15 |
| Updates SLAM | 1457 | 1426 | 1432 | 1447 |
| Submaps | 0 | 0 | 10 | 0 |
| Loop closures | 0 | 0 | 1 | 0 |
| Distancia minima obstaculo [m] | 0.28405 | 0.2826 | 0.28451 | 0.29035 |
| Riesgo maximo | 0.28735 | 0.29455 | 0.29144 | 0.27995 |
| Bateria usada [%] | 16.82153 | 16.78037 | 16.65956 | 16.63498 |

## Lectura tecnica

`GMAPPING_GRID`, `HECTOR_GRID_MATCHING` y `CARTOGRAPHER_SUBMAP` producen mapas de ocupacion. `KALMAN_LANDMARK` produce un mapa compacto de puntos de obstaculo. Hector se diferencia por usar scan matching local contra la grilla. Cartographer se diferencia por mantener submaps y registrar cierres de ciclo simplificados. Para navegacion local en este escenario pequeno, todos son validos como comparacion controlada, pero deben presentarse como implementaciones reducidas dentro de CoppeliaSim.

Conclusion recomendada: reportar los resultados como benchmark academico reproducible, no como ejecucion de paquetes ROS originales.

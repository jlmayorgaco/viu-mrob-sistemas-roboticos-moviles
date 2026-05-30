# Análisis Phase 1 Basic - estimación, SLAM y planificación

## Qué hace el estimador

El estimador implementa un ciclo clásico de predicción y corrección. Primero predice la pose del Pioneer con el modelo cinemático diferencial y la odometría de ruedas. Luego corrige esa pose con una medición simulada con ruido mediante una ganancia tipo Kalman. Con la pose estimada, cada lectura de proximidad se transforma de coordenadas locales del sensor a coordenadas globales del almacén.

Para el mapa se usa asociación por cercanía: si una detección cae cerca de una landmark existente, esa landmark se actualiza con un filtro Kalman escalar; si cae fuera del radio de asociación, se crea una nueva landmark. El resultado es un mapa disperso de obstáculos adecuado para navegación local en esta celda.

## Desempeño numérico

- RMSE posición: 0.06618 m
- Error medio de posición: 0.04496 m
- Error P95 de posición: 0.14488 m
- Error máximo de posición: 0.29105 m
- RMSE orientación: 0.03445 rad
- Covarianza media publicada: 0.02829

## Mapeo y planificación

- Landmarks finales: 8
- Actualizaciones SLAM/Kalman: 2461
- Frecuencia media de actualización: 31.251 actualizaciones/s
- Actualizaciones por landmark: 307.62
- Duración por modo de planificador: {'DIRECT': 69.2, 'DIRECT_AFTER_WAYPOINT': 4.6, 'SLAM_WAYPOINT': 4.95}
- Duración por modo de movimiento: {'ARRIVED_TARGET': 0.35, 'AVOIDING': 33.65, 'MANIPULATING': 7.0, 'ROUTE': 8.1, 'WAIT_B1': 29.65}

## Seguridad operacional

- Distancia mínima positiva a obstáculo: 0.06861 m
- Riesgo máximo de obstáculo: 0.77164
- Batería inicial/final: 96.0% -> 72.43446%
- Tareas completadas: 4
- Estado final: CHARGING

## Interpretación para la guía

El comportamiento corresponde a una implementación clásica dentro de CoppeliaSim: EKF para localización de pose, filtro Kalman para landmarks de obstáculos, asociación por distancia y planificación por punto intermedio cuando el mapa detecta bloqueo en la ruta directa.

# Análisis Phase 1 Basic - estimación, SLAM y planificación

## Qué hace el estimador

El estimador implementa un ciclo clásico de predicción y corrección. Primero predice la pose del Pioneer con el modelo cinemático diferencial y la odometría de ruedas. Luego corrige esa pose con una medición simulada con ruido mediante una ganancia tipo Kalman. Con la pose estimada, cada lectura de proximidad se transforma de coordenadas locales del sensor a coordenadas globales del almacén.

Para el mapa se usa asociación por cercanía: si una detección cae cerca de una landmark existente, esa landmark se actualiza con un filtro Kalman escalar; si cae fuera del radio de asociación, se crea una nueva landmark. El resultado es un mapa disperso de obstáculos adecuado para navegación local en esta celda.

## Desempeño numérico

- RMSE posición: 0.03149 m
- Error medio de posición: 0.02981 m
- Error P95 de posición: 0.0476 m
- Error máximo de posición: 0.05626 m
- RMSE orientación: 0.01987 rad
- Covarianza media publicada: 0.00081

## Mapeo y planificación

- Landmarks finales: 20
- Actualizaciones SLAM/Kalman: 4295
- Frecuencia media de actualización: 35.306 actualizaciones/s
- Actualizaciones por landmark: 214.75
- Duración por modo de planificador: {'DIRECT': 105.4, 'DIRECT_AFTER_WAYPOINT': 14.0, 'SLAM_WAYPOINT': 2.25}
- Duración por modo de movimiento: {'ARRIVED_TARGET': 0.4, 'AVOIDING': 35.9, 'MANIPULATING': 7.1, 'ROUTE': 4.25, 'WAIT_B1': 74.0}

## Seguridad operacional

- Distancia mínima positiva a obstáculo: 0.09656 m
- Riesgo máximo de obstáculo: 0.71277
- Batería inicial/final: 96.0% -> 71.79783%
- Tareas completadas: 4
- Estado final: CHARGING

## Interpretación para la guía

El comportamiento corresponde a una implementación clásica dentro de CoppeliaSim: EKF para localización de pose, filtro Kalman para landmarks de obstáculos, asociación por distancia y planificación por punto intermedio cuando el mapa detecta bloqueo en la ruta directa.

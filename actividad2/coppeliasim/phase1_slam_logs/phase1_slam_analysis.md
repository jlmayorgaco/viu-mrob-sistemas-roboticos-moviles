# Analisis Phase 1 Basic - estimacion, SLAM y planificacion

## Que hace el estimador

El estimador no une puntos de forma geometrica. Usa un ciclo clasico de prediccion y correccion. Primero predice la pose del Pioneer con el modelo cinematico diferencial y la odometria de ruedas. Luego corrige esa pose con una medicion de pose simulada con ruido mediante una ganancia tipo Kalman. Con la pose estimada, cada lectura de proximidad se transforma de coordenadas locales del sensor a coordenadas globales del almacen.

Para el mapa se usa asociacion por cercania: si una deteccion cae cerca de una landmark existente, esa landmark se actualiza con un filtro Kalman escalar; si no cae cerca, se crea una nueva landmark. Por eso el resultado es un mapa disperso de obstaculos, no una grilla de ocupacion ni un Graph-SLAM completo.

## Desempeno numerico

- RMSE posicion: 0.03125 m
- Error medio de posicion: 0.02958 m
- Error P95 de posicion: 0.0471 m
- Error maximo de posicion: 0.06272 m
- RMSE orientacion: 0.01809 rad
- Covarianza media publicada: 0.00081

## Mapeo y planificacion

- Landmarks finales: 16
- Actualizaciones SLAM/Kalman: 2615
- Frecuencia media de actualizacion: 23.601 updates/s
- Actualizaciones por landmark: 163.44
- Duracion por modo de planificador: {'DIRECT': 105.55, 'DIRECT_AFTER_WAYPOINT': 0.9, 'SLAM_WAYPOINT': 4.35}
- Duracion por modo de movimiento: {'ARRIVED_TARGET': 0.35, 'AVOIDING': 21.95, 'MANIPULATING': 5.3, 'ROUTE': 9.6, 'SLAM_PATH': 0.15, 'WAIT_B1': 73.45}

## Seguridad operacional

- Distancia minima positiva a obstaculo: 0.19551 m
- Riesgo maximo de obstaculo: 0.46877
- Bateria inicial/final: 96.0% -> 76.21563%
- Tareas completadas: 3
- Estado final: CHARGING

## Lectura para la guia

El comportamiento es defendible como una implementacion clasica reducida: EKF para localizacion de pose, filtro Kalman para landmarks de obstaculos, asociacion por distancia y planificacion por waypoint cuando el mapa detecta bloqueo en la ruta directa. No debe presentarse como SLAM denso de mapa completo ni como EKF-SLAM con matriz de covarianza completa robot-landmarks.

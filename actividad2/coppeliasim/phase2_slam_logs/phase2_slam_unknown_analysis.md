# Phase 2 Unknown SLAM - export de mapeo

## Supuesto de mapa desconocido

R1 no recibe el mapa completo al inicio. La escena contiene zonas desconocidas, frontiers, obstaculos estaticos no modelados, una tarima dinamica y un bloque temporal. El mapa publicado crece con lecturas de proximidad y actualizaciones SLAM.

Los objetos que se mueven por script son: P2_Dynamic_Pallet;P2_Temporary_Blocker. El modelo de movimiento es deterministic_periodic.

## Evidencia exportada

- Evidencia de mapeo final: 89.204%
- Tiempo hasta 25/50/75%: 2.4 s / 87.15 s / 98.4 s
- Landmarks finales: 22
- Recall proxy de obstaculos Phase 2: 1.0
- Precision proxy de features: 0.273
- Actualizaciones SLAM: 5208
- Frontiers declarados: 6
- Celdas desconocidas declaradas: 32

La evidencia de mapeo no es cobertura geometrica contra ground truth. Es un indicador de actividad del mapa; la calidad geometrica se estima con proxies de obstaculos detectados.

## Obstaculos dinamicos y replanning

- Cruces de la tarima dinamica: 9
- Triggers de replanning: 15
- Recuperaciones del planner: 0
- Riesgo maximo de obstaculo: 0.803
- Distancia minima positiva a obstaculo: 0.052 m

## Estimador

- Error medio de pose: 0.02809 m
- Error P95 de pose: 0.03971 m
- Error maximo de pose: 0.04511 m

## Modos

- Planner: {'DIRECT': 105.35, 'DIRECT_AFTER_WAYPOINT': 13.55, 'SLAM_WAYPOINT': 5.4}
- Movimiento: {'ARRIVED_TARGET': 0.45, 'AVOIDING': 40.7, 'MANIPULATING': 7.1, 'ROUTE': 2.0, 'WAIT_B1': 74.05}

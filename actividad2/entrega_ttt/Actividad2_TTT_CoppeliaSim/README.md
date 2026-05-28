# Actividad 2 - Escenas CoppeliaSim

Este paquete contiene las escenas CoppeliaSim y el codigo fuente asociado a la Actividad 2.
Las escenas `.ttt` ya incluyen los modelos importados de la libreria de CoppeliaSim; no hace falta ejecutar Python para revisar la simulacion.

## Escenas

- `escenas/Actividad2_1_Basic_Follower.ttt`: seguimiento de Bill y comparacion P, PI, PID, LQR y NMPC.
- `escenas/Actividad2_Pioneer_basic.ttt`: prueba basica de seguimiento con campos potenciales y evitacion de obstaculos.
- `escenas/Sim_T2_Phase1_Basic.ttt`: celda principal con R1, Bill/B1, T1/T2, estaciones de trabajo, rack, carga, sensores y SLAM.
- `escenas/Sim_T2_Phase2_SLAM_Unknown.ttt`: extension con mapa parcialmente desconocido, obstaculos nuevos y replanificacion.

## Validaciones

- `validaciones/Actividad2_1_Basic_Follower_validation.json`
- `validaciones/Actividad2_Pioneer_basic_validation.json`
- `validaciones/Sim_T2_Phase1_Basic_validation.json`
- `validaciones/Sim_T2_Phase2_SLAM_Unknown_validation.json`

Los cuatro archivos JSON terminan con `passed=true`.

## Codigo fuente

- `codigo_lua/`: controladores y gestores ejecutados en las escenas.
- `generadores/`: scripts Python usados para reconstruir o validar las escenas si se necesita.

Para revisar una escena, abrir el archivo `.ttt` correspondiente en CoppeliaSim Edu.

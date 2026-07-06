# Hollymatic_AI_V2

Se han identificado fallas recurrentes en el ensamblaje de los equipos Hollymatic por parte del personal de Eat Burgers. Esta situación ha derivado en un desabastecimiento de patties de carne y un incremento considerable en los gastos de mantenimiento técnico, evidenciando una oportunidad de mejora operativa crítica.

Para mitigar estos inconvenientes, es imperativo implementar un protocolo estandarizado de armado y una auditoría de procesos rigurosa. Bajo esta premisa surge Hollymatic SAFIA, una solución tecnológica diseñada para supervisar el montaje correcto del equipo mediante un sistema automatizado de notificaciones integradas en Google Chat.

Este sistema permitirá bajar los costos en mantenimiento del equipo y reducir el indice de desabasto de patties en sucursal.
ya que el equipo a descomponerse limita la formación de patties para su venta.


## Objetivos generales:
	1. Reducir costos en mantenimiento reactivo
	2. Reducir el down time del equipo
	3. Auditar el correcto uso y armado del equipo

## Metodología;
	Paara realiazar este proceso tenemos un sistema de 3 cámaras que identifican sus respectivas piezas para valorar si el equipo fue correctamente ensamblado, atravez de una interfaz de acción de 3 botones.

	1, Verde: Este color indica arranque de la detección. toma una fotografía para cada cámara y pasa por un doble filtro de 		inteligencia artifcial. Clasificación la cual permite determinar que vista se tiene del equipo (cenital, frontral o tracera). y detección la cual identifica especificamente que pieza es la que esta correctamente armada o en su defecto la cual no cumple. 

## NOTA: 
Apartir de la version 1.5 también permite almacenar esto en una base de datos local. La cual registra intentos de armado para posteriormente generar KPIs especificos sobre el uso de este equipo.

## Azul:
Este botón gestiona la calibración. Se le da un espacio temporal a la persona de aproximadamente 1 minuto para poder calibrar la hollymatic realizando un encendido del enchufe una espera de poco mas de un minuto y posteriormente solicita cortar la corriente a los plugs del KP200.




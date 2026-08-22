# Empezamos con los
# Tengo que crear una columna en tarea para el número de horas mínimas y máximas necesarias 

'''

Antes de nada, creamos una columna en la tabla 'contrato' con el número de horas anuales y semanales:
- id_contrato = 1 son anuales: 1770, semanales: 37.5
- id_contrato = 2 son anuales:  1614, semanales: 30
- id_contrato = 3 son anuales: 1593, semanales: round(37.5*0.90)
- id_contrato = 4 son anuales: 1239, semanales: round(37.5*0.70)
- id_contrato = 5 son anuales: 720, semanales: round(37.5*0.407)
- id_contrato = 6 son anuales: 708, semanales: round(37.5*0.40)
- id_contrato = 7 son anuales: 447, semanales: 10

La tabla tarea la sustituimos por los siguientes nombres, todas ellas deben tener el valor activa = 1 y añadimos dos columnas con el mínimo y el máximo número de horas necesarias por turno para completar. A continuación están las min= y max= en formato Horas:Minutos
- RUNNER + DEV A TIENDA: min (6:15) y max (12:30)
- CONSOLA + DEV EDIG: min = 6 y max = 12:15
- ECI EXPRESS + CLICK&CAR: min= 6:15 y max = 12:30
- HOME DELIVERY: min= 6:15 y max = 6:15
- SITE TO STORE: min=0 y max=6:15
- DERIVADAS: min=0 y max=6:15
- GESTIÓN DE MOSTRADOR: min=6:15 y max=6:15
- MOSTRADOR: min=12:30 y max 18:45
- INFORMAR: min=6 y max=12:15
- INFORMAR LOS ENCARGOS DEL MURO: min=6 y max 12:15
- INFORMAR PALETS/EXPEDICION: min=6 y max=12:15
- SALES FORCE: min=0 y max=6:15

DISTRIBUCIÓN DE LAS HORAS ORDINARIAS

A continuación vamos a crear la distribución semanal. Hay dos turnos, por la mañana y por la tarde. Ambos turnos tienen las mismas tareas pero la distribución de horas necesarias según el número de pedidos recibidos es distinto: por la mañana debe de haber un 60% del personal y por la tarde un 40% del total del día.
Las jornadas de los trabajadores son variables y se indicarán a continuación pero varían entre 5, 6 6:15 y 7. La suma de las horas diarias que haga cada trabajador a lo largo de la semana debe sumar al total de sus horas semanales excepto en el caso en el que se aplique la regla 

1. Empezamos con los trabajadores que únicamente de mañanas o de tardes (en la tabla 'trabajador' está indicado con la letra ("M" o "T") en la columna de 'disponibilidad') y entre esos escogemos según la regla (a)
   Cuando seleccionemos al trabajador sacamos el número de horas semanales que deben hacer y lo guardamos en un variable horas_semana, para que a medida que vayamos distribuyendo, el contador se reduzca hasta llegar a 0.
     Primero Hacemos primero todos los que tengan el id_contrato = 1 (37.5 horas semanales), luego hacemos los que tengan id_contrato = 2, hacer los mismos pasos (1.2, 1.3, 1.4, 1.5 y 1.6 PERO el día de esa semana que más horas sean necesarias para completar los pedidos diarios (la columna de 'horas_necesarias' en la tabla de 'prediccion') se le asignarán a su tarea 4 horas y los restantes días se le asignarán 6 horas) y finalmente los que tengan un id_contraro = 5: se le asignan 5 horas a cada tarea.
     1.1 BUCLE PRINCIPAL
        1.2 Seguir con el paso (b)
            1.2.1 en el caso de que sea de id_contrato = 1, Se le asignan 6:15 al trabajador
        1.3 A continuación pasar al paso (d)
        1.4 Ahora el paso (e), siempre teniendo en cuenta que esta persona va únicamente de mañanas o únicamente de tardes siempre, no hay una alternación entre mañanas y tardes
        1.5 Seguimos ahora con el paso (f), (g) y (h)
        1.6 Ahora con los huecos que se quedan pasamos al siguiente tipo de contrato 

2. Continuamos con los trabajadores que como código en la tabla de 'trabajador' en la columna de 'disponibilidad' tengan una 'A', que signfica que pueden ir tanto de mañanas como de tardes
    2. Comenzamos con los que tengan jornada completa y a esos se les asignan 6:15 EXCEPTO SI A LO LARGO DEL BUCLE SE INDICA LO CONTRARIO
        2.1 Y hacemos todo lo que se indica en el bucle 1.

IMPORTANTE RESTRICCION: Al día, la suma de las horas ordinarias deben de ser menor o igual a las horas_necesarias para completar los pedidos ese día. Y la suma mensual debe de ser igual a la suma obtenida en la variables X_HO_[numero de mes en el que estemos]

YA HEMOS FINALIZADO DE REPARTIR LAS HORAS ORDINARIAS

3. Cuando finalizamos esto, comparamos las horas que se han distribuido ya con las necesarias para completar los pedidos recibidos ese día y estas son las horas complementarias/fijos discontinuos
    Nota: Aquí para hacer un check, imprimir las que falten
    3.1 Vemos el output del arhicvo de optimizacion_FINAL y vemos las horas que nos quedan por distribuir
        3.2 Si hay que distribuir horas complementarias, a aquellos trabajadores que no tengan un id_contrato = 1 se les suma 1 hora a sus jornadas diarias hasta llegar a lo necesario y cumpliendo que cada trabajador no puede superar un 60% de la jornada ya establecida al principio.
        3.3 Si hay que distribuir horas de fijos discontinuos cogemos a los trabajadores que tengan un id_contrato = 3 y hacemos el proceso que hemos hecho con los otros trabajadores (en el apartado de DISTRIBUCIÓN DE HORAS ORDINARIAS) pero con el calendario que queda.
            - En este caso no se tiene en cuenta las máximas horas necesarias de cada tarea y ponemos como máximo 20 horas y priorizamos primero asignar a los trabajadores a :
                    MOSTRADOR, RUNNER + DEV A TIENDA, INFORMAR, INFORMAR LOS ENCARGOS DEL MURO, INFORMAR PALETS/EXPEDICION en ese orden
            - Hay que tener en cuenta que la jornada de los fijos disctoniuos es mínimo de 4 horas y serán esas las que se asignen a las tareas.
    Al finalizar todo esto, las horas complementarias/fijos discontinuos deben sumar a las calculadas en el fichero optimizacion_FINAL para este mes en concreto. Si no coinciden, no debe de dar error, simeplemente avisar cuantas se han superado/faltan para llegar.


REGLAS:

(a). Comenzamos con el trabajador que menos tareas activadas tenga, asignarle la tarea que menos trabajadores compartan y aquella tarea en la que sus horas mínimas para completarla sean igual o mayor a las horas dirarias del trabajador. Ante una igualdad, asignarle la tarea que más trabajadores necesite.
    (a.i) Ej. En el caso de que una persona trabaje un día 6:15, se escogerá una tarea que mínimo necesite 6:15 diarias para completarla. Si para un día se le asigna a una persona 4 horas, se asignará a la tarea que necesite 4 horas diarias.
(b). Para esa persona asignarle esa misma tarea toda la semana y el mismo horario. (Ej. va en el turno de mañanas toda esa semana para la tarea Runner + Dev Edig)
(c). Para la semana siguiente, esa persona tendrá asignada el turno opuesto la semana siguiente (Mismo Ej. irá de tardes la semana siguiente).
(d). Esa persona tiene que descansar un mínimo de 1,5 días a la semana (Ej. una tarde y el día siguiente).
    (d.i) En el caso de que esa persona vaya de mañanas esa semana y el domingo el centro esté cerrado, la tarde del sábado y el domingo será su 1,5 día de descanso
    (d.ii) En el caso de que el domingo el centro no esté cerrado, se debe de buscar otro momento de la semana. 
        (d.ii.1) En el caso de que esa persona vaya de mañanas, su descanso será una tarde y el día siguiente anterior
        (d.iii.2) En el caso de que esa persona vaya de tardes, su descanso será una mañana y el día entero anterior.
        Nota: El día entero anterior o siguiente no puede pertenecer a la semana anterior o siguiente, respectivamente, siempre debe de ser de la semana actual.
(e). Esa persona no puede trabajar 10 días consecutivos. (Ej. si una persona descansa el lunes completo y la mañana del martes de la semana 1, el próximo descanso debe empezar como máximo la mañana del viernes de la semana siguiente (semana 2).)
    Nota: La forma en la que se cuentan los días consecutivos son: un día entero es un día y medio día es medio día. dos medios días en días distintos suman un día completo
    Nota: Esto siempre es en los casos en los que el domingo no cierre porque si cierra, eso ya se considera como día de descanso y se vuelve a empezar el contador de los 10 días.
    5.1 Se ampliarán a 11 días consecutivos desde el Black Friday hasta el 28 de febrero
(f). En el caso de que ese trabajador tenga un ese trabajador no puede trabajar más de 22 domingos y festivos al año
(g). Por cada domingo que el centro esté abierto y el trabajador trabaje, la semana que viene tendrá un día libre extra la semana siguiente o la anterior.
(h). Si el trabajador tiene una jornada de más del 75%, o sea, un id_contrato de 1 y 2, deberán de tener a lo largo del año 9 fines de semana libres (sábado y domingo)
    Nota: estos días ya contarían dentro de la restricción número 4.
    (h.i) En el caso de que estemos tratando con un trabajador de jornada completa, se le puede asignar 7h.

'''


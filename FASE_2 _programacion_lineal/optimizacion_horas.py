from sqlalchemy import create_engine
import pandas as pd
import pulp
import math

engine = create_engine("mysql+pymysql://root:root2004@localhost/emplea")

# Tipos de jornada 

query_trabajadores = """
SELECT id_contrato
FROM trabajador
"""

df_trabajadores = pd.read_sql(query_trabajadores, con=engine)
count_tipos_contratos = df_trabajadores['id_contrato'].value_counts().to_dict()

num_trabajadores_100_C = count_tipos_contratos.get(1)
horas_100 = 40 * 4
max_horas_100_C = num_trabajadores_100_C * horas_100

num_trabajadores_912_C = count_tipos_contratos[2]
horas_JP_912 = 40 * 0.912 * 4
max_horas_912_C = num_trabajadores_912_C * horas_JP_912

num_trabajadores_90_FD = count_tipos_contratos[3]
horas_JP_90 = 40 * 0.90 * 4
max_horas_90_FD = num_trabajadores_90_FD * horas_JP_90

num_trabajadores_70_C = count_tipos_contratos[4]
horas_JP_70 = 40 * 0.70 * 4
max_horas_70_C = num_trabajadores_70_C * horas_JP_70

num_trabajadores_JP_407_C = count_tipos_contratos[5]
horas_JP_407 = 40 * 0.407 * 4
max_horas_407_C = num_trabajadores_JP_407_C * horas_JP_407

num_trabajadores_JP_40_C = count_tipos_contratos[6]
horas_JP_40 = 40 * 0.40 * 4
max_horas_40_C = num_trabajadores_JP_40_C * horas_JP_40

num_trabajadores_JP_253_C = count_tipos_contratos[7]
horas_JP_253 = 40 * 0.253 * 4
max_horas_253_C = num_trabajadores_JP_253_C * horas_JP_253

max_horas = max_horas_100_C + max_horas_912_C + max_horas_70_C + max_horas_407_C + max_horas_40_C + max_horas_253_C
max_horas_sin_100 = max_horas_912_C + max_horas_70_C + max_horas_407_C + max_horas_40_C + max_horas_253_C


# Definción del problema

prob = pulp.LpProblem("Optimizacion_Coste", pulp.LpMinimize)

# Variables de decisión

X_HO_1 = pulp.LpVariable("X_HO_1", lowBound=0, upBound=max_horas, cat="Continuous")  # Horas ordinarias en el mes 1
X_HO_2 = pulp.LpVariable("X_HO_2", lowBound=0, upBound=max_horas, cat="Continuous")  # Horas ordinarias en el mes 2
X_HO_3 = pulp.LpVariable("X_HO_3", lowBound=0, upBound=max_horas, cat="Continuous")  # Horas ordinarias en el mes 3

X_HC_1 = pulp.LpVariable("X_HC_1", lowBound=0, upBound=(max_horas_sin_100)*0.6, cat="Continuous")  # Horas complementarias en el mes 1
X_HC_2 = pulp.LpVariable("X_HC_2", lowBound=0, upBound=(max_horas_sin_100)*0.6, cat="Continuous")  # Horas complementarias en el mes 2
X_HC_3 = pulp.LpVariable("X_HC_3", lowBound=0, upBound=(max_horas_sin_100)*0.6, cat="Continuous")  # Horas complementarias en el mes 3

X_HFD_1 = pulp.LpVariable("X_HFD_1", lowBound=0, cat=pulp.LpInteger)  # Horas de fijos discontinuos en el mes 1
X_HFD_2 = pulp.LpVariable("X_HFD_2", lowBound=0, cat=pulp.LpInteger)  # Horas de fijos discontinuos en el mes 2
X_HFD_3 = pulp.LpVariable("X_HFD_3", lowBound=0, cat=pulp.LpInteger)  # Horas de fijos discontinuos en el mes 3

K_HFD_1 = pulp.LpVariable("K_HFD_1", lowBound=0, cat=pulp.LpInteger)  # AUXILIAR Horas de fijos discontinuos en el mes 1
K_HFD_2 = pulp.LpVariable("K_HFD_2", lowBound=0, cat=pulp.LpInteger)  # AUXILIAR Horas de fijos discontinuos en el mes 2
K_HFD_3 = pulp.LpVariable("K_HFD_3", lowBound=0, cat=pulp.LpInteger)  # AUXILIAR Horas de fijos discontinuos en el mes 3

B_HO_1 = pulp.LpVariable("B_HO_1", cat=pulp.LpBinary)  # Variable binaria para indicar si hay disponibilidad de horas ordinarias en el mes 1
B_HO_2 = pulp.LpVariable("B_HO_2", cat=pulp.LpBinary)  # Variable binaria para indicar si hay disponibilidad de horas ordinarias en el mes 2
B_HO_3 = pulp.LpVariable("B_HO_3", cat=pulp.LpBinary)  # Variable binaria para indicar si hay disponibilidad de horas ordinarias en el mes 3

B_HC_1 = pulp.LpVariable("B_HC_1", cat=pulp.LpBinary)  # Variable binaria para indicar si hay disponibilidad de horas complementarias en el mes 1
B_HC_2 = pulp.LpVariable("B_HC_2", cat=pulp.LpBinary)  # Variable binaria para indicar si hay disponibilidad de horas complementarias en el mes 2
B_HC_3 = pulp.LpVariable("B_HC_3", cat=pulp.LpBinary)  # Variable binaria para indicar si hay disponibilidad de horas complementarias en el mes 3

B_HFD_1 = pulp.LpVariable("B_HFD_1", cat=pulp.LpBinary)  # Variable binaria para indicar si hay disponibilidad de horas de fijos discontinuos en el mes 1
B_HFD_2 = pulp.LpVariable("B_HFD_2", cat=pulp.LpBinary)  # Variable binaria para indicar si hay disponibilidad de horas de fijos discontinuos en el mes 2
B_HFD_3 = pulp.LpVariable("B_HFD_3", cat=pulp.LpBinary)  # Variable binaria para indicar si hay disponibilidad de horas de fijos discontinuos en el mes 3

# Otras variables

query_prediccion = """
SELECT fecha, pedidos_acumulados
FROM prediccion
ORDER BY fecha
"""

df_prediccion = pd.read_sql(query_prediccion, con=engine)

df_prediccion['fecha'] = pd.to_datetime(df_prediccion['fecha'])
df_prediccion['pedidos_acumulados'] = pd.to_numeric(df_prediccion['pedidos_acumulados'], errors='coerce').fillna(0).astype(int)
df_prediccion = df_prediccion.sort_values('fecha').reset_index(drop=True)
df_prediccion['mes'] = df_prediccion['fecha'].dt.month

meses_horizonte = df_prediccion['mes'].drop_duplicates().tolist()[:3]

if len(meses_horizonte) < 3:
    raise ValueError("No hay suficientes meses de predicción para calcular los meses 1, 2 y 3.")

pedidos_mes_1 = int(df_prediccion[df_prediccion['mes'] == meses_horizonte[0]]['pedidos_acumulados'].sum())
pedidos_mes_2 = int(df_prediccion[df_prediccion['mes'] == meses_horizonte[1]]['pedidos_acumulados'].sum())
pedidos_mes_3 = int(df_prediccion[df_prediccion['mes'] == meses_horizonte[2]]['pedidos_acumulados'].sum())

query_promociones = """
SELECT fecha_inicio, fecha_fin
FROM promocion
WHERE id_centro = 1
"""

df_promociones = pd.read_sql(query_promociones, con=engine)
df_promociones['fecha_inicio'] = pd.to_datetime(df_promociones['fecha_inicio'])
df_promociones['fecha_fin'] = pd.to_datetime(df_promociones['fecha_fin'])


def hay_promocion(mes):
    fechas_mes = df_prediccion[df_prediccion['mes'] == mes]['fecha']
    if fechas_mes.empty:
        return False
    mes_inicio = fechas_mes.min().normalize()
    mes_fin = fechas_mes.max().normalize()
    activo = df_promociones[
        (df_promociones['fecha_inicio'] <= mes_fin) &
        (df_promociones['fecha_fin'] >= mes_inicio)
    ]
    return not activo.empty

promo_1 = hay_promocion(meses_horizonte[0])
promo_2 = hay_promocion(meses_horizonte[1])
promo_3 = hay_promocion(meses_horizonte[2])


# Función objetivo

precio_hora_ordinaria = 13.18
precio_hora_complementaria = 13.18
precio_hora_fijo_discontinuo = 13.18
# precio_hora_contratacion_temporal = precio_hora_ordinaria * 1.15 # 15% más considerando que es un contrato temporal y hay que formar al trabajador
# precio_hora_extraordinaria = precio_hora_ordinaria * 1.3

prob += precio_hora_ordinaria * (X_HO_1 + X_HO_2 + X_HO_3) + \
        precio_hora_complementaria * (X_HC_1 + X_HC_2 + X_HC_3) + \
        precio_hora_fijo_discontinuo * (X_HFD_1 + X_HFD_2 + X_HFD_3), "Minimizar_Coste_Total"


# Restricciones

    # La suma de todas los tipos de horas tiene que ser capaz de completar todos los pedidos mensuales

horas_recoleccion_1 = 0.00029611101
horas_recoleccion_2 = 0.00005238316019
horas_empaquetado = (0.007350211777 + 0.009435869071)/2
horas_almacenado = (0.001311401251 + 0.006738298913 + 0.01256998856 + 0.009548456075)/4
horas_entrega = (0.0002393378489 + 0.009691886578)/2
horas_pedidos = horas_recoleccion_1 + horas_recoleccion_2 + horas_empaquetado + horas_almacenado + horas_entrega
# Falta incluir que considere las horas según las horas que está abierto el centro
horas_presencia_mostrador = 11
horas_otras_gestiones = 1
horas_gestion_mostrador = 3
porcentaje_devoluciones = 0.05
horas_gestion_devoluciones = 3
 
prob += X_HO_1 + X_HC_1 + X_HFD_1 >= pedidos_mes_1 * (horas_pedidos + porcentaje_devoluciones * horas_gestion_devoluciones) + horas_presencia_mostrador + horas_otras_gestiones + horas_gestion_mostrador, "Horas_Completar_Pedidos_Mes_1"
prob += X_HO_2 + X_HC_2 + X_HFD_2 >= pedidos_mes_2 * (horas_pedidos + porcentaje_devoluciones * horas_gestion_devoluciones) + horas_presencia_mostrador + horas_otras_gestiones + horas_gestion_mostrador, "Horas_Completar_Pedidos_Mes_2"
prob += X_HO_3 + X_HC_3 + X_HFD_3 >= pedidos_mes_3 * (horas_pedidos + porcentaje_devoluciones * horas_gestion_devoluciones) + horas_presencia_mostrador + horas_otras_gestiones + horas_gestion_mostrador, "Horas_Completar_Pedidos_Mes_3"


    # Relacionamos las variables binarias con las continuas

prob += X_HO_1 <= B_HO_1 * (max_horas)
prob += X_HO_2 <= B_HO_2 * (max_horas)
prob += X_HO_3 <= B_HO_3 * (max_horas)

prob += X_HC_1 <= B_HC_1 * (max_horas_sin_100)*0.6
prob += X_HC_2 <= B_HC_2 * (max_horas_sin_100)*0.6
prob += X_HC_3 <= B_HC_3 * (max_horas_sin_100)*0.6

prob += X_HFD_1 <= B_HFD_1 * 10000
prob += X_HFD_2 <= B_HFD_2 * 10000
prob += X_HFD_3 <= B_HFD_3 * 10000

    # Primero se deben de completar las horas ordinarias antes que las demás

prob += X_HO_1 >= B_HC_1 * (max_horas) 
prob += X_HO_2 >= B_HC_2 * (max_horas)
prob += X_HO_3 >= B_HC_3* (max_horas)

prob += X_HO_1 >= B_HFD_1 * (max_horas)
prob += X_HO_2 >= B_HFD_2 * (max_horas)
prob += X_HO_3 >= B_HFD_3* (max_horas)

    # Jornadas de 5 horas

prob += X_HFD_1 == 5 * K_HFD_1
prob += X_HFD_2 == 5 * K_HFD_2
prob += X_HFD_3 == 5 * K_HFD_3

    # Los fijos discontinuos solamente pueden estar contratados:
    # - Desde el 27 de noviembre hasta el 28 de febrero del año siguiente.
    # - Desde la segunda semana de junio hasta la segunda semana de septiembre.

# Determinamos si cada mes está dentro de los periodos permitidos (27 Nov - 28 Feb) y 
def is_in_fd_period(fecha):
    month = fecha.month
    day = fecha.day
    
    # Noviembre: desde día 27 hasta fin de mes
    if month == 11:
        return True
    # Diciembre: todo el mes
    if month == 12:
        return True
    # Enero y Febrero: hasta día 28
    if month in [1, 2]:
        return True
    if month == 6:
        return True
    if month == 9:
        return True
    
    return False

# Determinamos si cada mes del horizonte contiene fechas dentro del período permitido
meses_en_periodo_fd = []
for mes in meses_horizonte:
    fechas_mes = df_prediccion[df_prediccion['mes'] == mes]['fecha']
    if not fechas_mes.empty:
        # Verificamos si alguna fecha del mes está en el período permitido
        tiene_fechas_validas = fechas_mes.apply(is_in_fd_period).any()
        meses_en_periodo_fd.append(tiene_fechas_validas)
    else:
        meses_en_periodo_fd.append(False)


# Aplicamos restricciones: si el mes no está en el período, X_HFD = 0
if not meses_en_periodo_fd[0]:
    prob += X_HFD_1 == 0, "Restriccion_FD_Periodo_Mes_1"
if not meses_en_periodo_fd[1]:
    prob += X_HFD_2 == 0, "Restriccion_FD_Periodo_Mes_2"
if not meses_en_periodo_fd[2]:
    prob += X_HFD_3 == 0, "Restriccion_FD_Periodo_Mes_3"

if promo_1 == False:
    prob += X_HC_1 == 0
if promo_2 == False:
    prob += X_HC_2 == 0
if promo_3 == False:
    prob += X_HC_3 == 0

# Según el día se trabajan 10 u 11 horas

prob.solve()

print("Estado del modelo:", pulp.LpStatus[prob.status], "\n")


print(f"Horas ordinarias en el mes 1: {round(X_HO_1.varValue)}")
print(f"Horas ordinarias en el mes 2: {round(X_HO_2.varValue)}")
print(f"Horas ordinarias en el mes 3: {round(X_HO_3.varValue)}")
print(f"Horas complementarias en el mes 1: {round(X_HC_1.varValue)}")
print(f"Horas complementarias en el mes 2: {round(X_HC_2.varValue)}")
print(f"Horas complementarias en el mes 3: {round(X_HC_3.varValue)}")
print(f"Horas FD en el mes 1: {round(X_HFD_1.varValue / 5) * 5}")
print(f"Horas FD en el mes 2: {round(X_HFD_2.varValue / 5) * 5}")
print(f"Horas FD en el mes 3: {round(X_HFD_3.varValue / 5) * 5}")

from sqlalchemy import create_engine
import pandas as pd
import pulp
import math



# Objetivo: minimizar el backlog total de pedidos


# Importamos lo que se ha hecho en la fase 1

engine = create_engine("mysql+pymysql://root:root2004@localhost/emplea")

# query para obtener la prediccion

query_prediccion = """
SELECT 
       id_prediccion AS id,
       fecha,
       pedidos_previstos, 
       limite_inferior, 
       limite_superior
FROM prediccion
"""
df_pedidos_pred = pd.read_sql(query_prediccion, con=engine)
df_pedidos_pred['id'] = pd.to_numeric(df_pedidos_pred['id'])
df_pedidos_pred['fecha'] = pd.to_datetime(df_pedidos_pred['fecha'])



# query para obtener el horario y si el centro está abierto

query_calendario = """
SELECT 
    fecha,
    centro_abierto,
    hora_apertura,
    hora_cierre
FROM calendario
"""

df_calendario = pd.read_sql(query_calendario, con=engine)
print(df_calendario.head())
df_calendario['fecha'] = pd.to_datetime(df_calendario['fecha'])
df_calendario['hora_apertura'] =pd.to_timedelta(df_calendario['hora_apertura'])
df_calendario['hora_cierre'] =pd.to_timedelta(df_calendario['hora_cierre'])
df_calendario['centro_abierto'] = pd.to_numeric(df_calendario['centro_abierto'])


'''



# Tareas por lotes
volumetria_expedicion = 31
tiempo_expedicion = 1248

volumetria_recoleccion = 25.6
tiempo_recoleccion = 368.3

# Tareas por linea
tiempo_linea_empaquetado = 94.93
tiempo_linea_almacenado = 282.7
tiempo_linea_entrega_expedicion = 29.95
tiempo_linea_gestion_mostrador = 0
tiempo_linea_devoluciones = 26.92

# Tareas de cobertura continua
horas_presencia_mostrador = 11
horas_otras_gestiones = 2

# PRUEBA

dias = [1, 2, 3, 4, 5]
demanda = {1: 150, 2: 200, 3: 180, 4: 250, 5: 120}
centro_abierto = {1: 1, 2: 1, 3: 0, 4: 1, 5: 1} 
porcentaje_devoluciones = 0.05 
horas_max_dia = 24 

prob = pulp.LpProblem("Optimizacion_Lineas", pulp.LpMinimize)

#Variables de decisión

# Líneas procesadas en un día d
L = pulp.LpVariable.dicts("Lineas", dias, lowBound=0, cat='Integer')

# Backlog de pedidos al final del día d
B = pulp.LpVariable.dicts("Backlog", dias, lowBound=0, cat='Integer')

# Horas totales asignadas al final del día d
# ESTO ES REALMENTE NECESARIO?
H_totales = pulp.LpVariable.dicts("Horas Totales", dias, lowBound=0, upBound=horas_max_dia, cat='Continuous')


# ESTO igual lo quitaría, pero es significaría quitar lo de la capacidad de arriba?
velocidad_expedicion = pulp.LpVariable.dicts("Viajes_Exp", dias, lowBound=0, cat='Integer')
velocidad_recoleccion = pulp.LpVariable.dicts("Viajes_Rec", dias, lowBound=0, cat='Integer')

# El objetivo es minimizar el Backlog total de pedidos

prob += pulp.lpSum([B[d] for d in dias]), "Minimizar_Backlog_Total"

# Restricciones

backlog_inicial = 0

for d in dias:
    # Voy a probarlo pero el día 1 solamente sería
    # Lo que puedo hacer es convertir las fechas a día 1...75 para tneer contados los días predecidos
     
    # Balance de flujo de pedidos
    
    if d == 1:
        prob += B[d] == backlog_inicial + demanda[d] - L[d], f"Backlog_Dia_{d}"
    else:
        prob += B[d] == B[d-1] + demanda[d] - L[d], f"Backlog_Dia_{d}"

    
    # Restricción de que si el centro está cerrado, no se pueden procesar líneas
    prob += L[d] <= centro_abierto[d] * 10000, f"Centro_Abierto_Dia_{d}"  

    # Restricción de capacidad de expedición y recolección (como tenemos que hacer viajes, lo hacemos en función de los viajes)
    prob += L[d] <= velocidad_expedicion[d] * volumetria_expedicion, f"Cap_Expedicion_{d}"
    prob += L[d] <= velocidad_recoleccion[d] * volumetria_recoleccion, f"Cap_Recoleccion_{d}"

    # Cálculo de las horas necesarias - lo pasamos a horas dividiendo entre 3600

    horas_lotes = (velocidad_expedicion[d] * tiempo_expedicion + velocidad_recoleccion[d] * tiempo_recoleccion) / 3600
    horas_linea = (L[d] * (tiempo_linea_empaquetado + tiempo_linea_almacenado + tiempo_linea_entrega_expedicion + tiempo_linea_gestion_mostrador)) / 3600
    hora_cobertura = (horas_presencia_mostrador + horas_otras_gestiones) / 3600
    horas_devoluciones = (demanda[d] * porcentaje_devoluciones * tiempo_linea_devoluciones) / 3600

    prob += H_totales[d] >= horas_lotes + horas_linea + hora_cobertura + horas_devoluciones, f"Horas_Totales_{d}"

    # Restricción de que debe ser menor que las horas máximas del día

    prob += H_totales[d] <= horas_max_dia, f"Horas_Maximas_{d}"


    prob.solve()

print("Estado del modelo:", pulp.LpStatus[prob.status], "\n")

print("-" * 50)
for d in dias:
    print(f"DÍA {d} (Abierto: {'Sí' if centro_abierto[d] else 'No'})")
    print(f"  Demanda del día: {demanda[d]} | Backlog de ayer: {0 if d==1 else B[d-1].varValue}")
    print(f"  Pedidos Procesados Hoy: {L[d].varValue}")
    print(f"  Pedidos Atrasados (Backlog para mañana): {B[d].varValue}")
    print(f"  --> HORAS HOMBRE NECESARIAS: {H_totales[d].varValue:.2f} horas")
    print("-" * 50)



ESTO SERÁ LO QUE HAYA DESPUÉS de la PRUEBA

dias = df_pedidos_pred['fecha'].dt.date.unique()
demanda = df_pedidos_pred.groupby(df_pedidos_pred['fecha'].dt.date)['pedidos_previstos'].sum().to_dict()
centro_abierto = df_calendario.set_index(df_calendario['fecha'].dt.date)['centro_abierto'].to_dict()
porcentaje_devoluciones = 0.05  # Suponemos un 5% de devoluciones sobre el total de pedidos
horas_max_dia = 

'''



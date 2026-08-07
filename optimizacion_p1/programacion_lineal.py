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

# Creamos esta columna temporalmente para poder manejar las fechas como strings y hacer el merge con el calendario
df_pedidos_pred['fecha_str'] = df_pedidos_pred['fecha'].dt.strftime('%Y-%m-%d')


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
df_calendario['fecha'] = pd.to_datetime(df_calendario['fecha'])
df_calendario['hora_apertura'] =pd.to_timedelta(df_calendario['hora_apertura'])
df_calendario['hora_cierre'] =pd.to_timedelta(df_calendario['hora_cierre'])
df_calendario['centro_abierto'] = pd.to_numeric(df_calendario['centro_abierto'])

# Lo mismo que con los pedidos, creamos una columna temporal para manejar las fechas como strings
df_calendario['fecha_str'] = pd.to_datetime(df_calendario['fecha']).dt.strftime('%Y-%m-%d')



# Tareas por lotes
volumetria_expedicion = 31
tiempo_expedicion = 1248 / 3600

volumetria_recoleccion = 25.6
tiempo_recoleccion = 368.3 /3600

# Tareas por linea
tiempo_linea_empaquetado = 94.93 / 3600
tiempo_linea_almacenado = 282.7 / 3600
tiempo_linea_entrega_expedicion = 29.95 / 3600
tiempo_linea_devoluciones = 26.92 / 3600

# Tareas de cobertura continua
horas_presencia_mostrador = 11
horas_otras_gestiones = 2
tiempo_linea_gestion_mostrador = 5

dias = sorted(list(df_pedidos_pred['fecha_str'].unique()))

demanda = df_pedidos_pred.set_index('fecha_str')['pedidos_previstos'].to_dict()
centro_abierto = df_calendario.set_index('fecha_str')['centro_abierto'].to_dict()
porcentaje_devoluciones = 0.05 
# Me falta solucionar esto
#horas_max_dia = df_calendario.set_index('fecha_str').apply(lambda row: (row['hora_cierre'] - row['hora_apertura']).total_seconds() / 3600, axis=1).to_dict()
horas_max_dia = 17 * 8

prob = pulp.LpProblem("Optimizacion_Lineas", pulp.LpMinimize)

#Variables de decisión

# Líneas procesadas en un día d
L = pulp.LpVariable.dicts("Lineas", dias, lowBound=0, cat='Integer')

# Backlog de pedidos al final del día d
B = pulp.LpVariable.dicts("Backlog", dias, lowBound=0, cat='Integer')

# Horas totales asignadas al final del día d
H_totales = pulp.LpVariable.dicts("Horas_Totales", dias, lowBound=0, cat='Continuous')


# ESTO igual lo quitaría, pero es significaría quitar lo de la capacidad de arriba?
velocidad_expedicion = pulp.LpVariable.dicts("Viajes_Exped", dias, lowBound=0, cat='Integer')
velocidad_recoleccion = pulp.LpVariable.dicts("Viajes_Recolec", dias, lowBound=0, cat='Integer')

# El objetivo es minimizar el Backlog total de pedidos

# prob += pulp.lpSum([B[d] for d in dias]), "Minimizar_Backlog_Total"
prob += pulp.lpSum([B[d] for d in dias]) - 0.001 * pulp.lpSum([L[d] for d in dias]), "Minimizar_Backlog_Total"


# Restricciones

backlog_inicial = 0

for i, d in enumerate(dias):
    # Balance de flujo de pedidos
    
    if d == dias[0]:  
        prob += B[d] == backlog_inicial + demanda[d] - L[d], f"Backlog_Dia_{d}"
    else:
        dia_anterior = dias[i-1]
        prob += B[d] == B[dia_anterior] + demanda[d] - L[d], f"Backlog_Dia_{d}"

    
    # Restricción de que si el centro está cerrado, no se pueden procesar líneas
    prob += L[d] <= centro_abierto[d] * 10000, f"Centro_Abierto_Dia_{d}"  

    # Restricción de capacidad de expedición y recolección (como tenemos que hacer viajes, lo hacemos en función de esto)
    prob += L[d] <= velocidad_expedicion[d] * volumetria_expedicion, f"Capacidad_Expedicion_{d}"
    prob += L[d] <= velocidad_recoleccion[d] * volumetria_recoleccion, f"Cap_Recoleccion_{d}"

    # Cálculo de las horas necesarias
    horas_lotes = (velocidad_expedicion[d] * tiempo_expedicion + velocidad_recoleccion[d] * tiempo_recoleccion) 
    horas_linea = (L[d] * (tiempo_linea_empaquetado + tiempo_linea_almacenado + tiempo_linea_entrega_expedicion )) 
    hora_cobertura = (horas_presencia_mostrador + horas_otras_gestiones + tiempo_linea_gestion_mostrador) * centro_abierto[d]
    horas_devoluciones = (demanda[d] * porcentaje_devoluciones * tiempo_linea_devoluciones) 

    prob += H_totales[d] >= horas_lotes + horas_linea + hora_cobertura + horas_devoluciones, f"Horas_Totales_{d}"

    # Restricción de que debe ser menor que las horas máximas del día

    prob += H_totales[d] <= horas_max_dia, f"Horas_Maximas_{d}"

    prob.solve()

print("Estado del modelo:", pulp.LpStatus[prob.status], "\n")

print("-" * 50)
for i, d in enumerate(dias):
    # Condición para detener el bucle de impresión después de 5 días
    if i == 30:
        break

    # 1. Determinamos el backlog del día anterior usando el índice 'i'
    if i == 0:
        # Aquí puedes usar tu variable backlog_inicial si la tienes definida
        backlog_ayer = 0 
    else:
        dia_anterior = dias[i-1]
        backlog_ayer = B[dia_anterior].varValue
        
    # 2. Imprimimos los resultados de forma segura
    print(f"DÍA {d} (Abierto: {'Sí' if centro_abierto[d] else 'No'})")
    print(f"  Demanda del día: {demanda[d]} | Backlog de ayer: {backlog_ayer}")
    print(f"  Pedidos Procesados Hoy: {L[d].varValue}")
    print(f"  Pedidos Atrasados (Backlog para mañana): {B[d].varValue}")
    print(f"  --> HORAS HOMBRE NECESARIAS: {H_totales[d].varValue:.2f} horas")
    print("-" * 50)

'''

print("-" * 50)
for i, d in enumerate(dias):
    # 1. Determinamos el backlog del día anterior usando el índice 'i'
    if i == 0:
        # En tu código original ponías 0, aunque si tienes la variable 'backlog_inicial' definida, sería ideal usarla aquí.
        backlog_ayer = 0 
    else:
        dia_anterior = dias[i-1]
        backlog_ayer = B[dia_anterior].varValue
        
    # 2. Imprimimos los resultados de forma segura
    print(f"DÍA {d} (Abierto: {'Sí' if centro_abierto[d] else 'No'})")
    print(f"  Demanda del día: {demanda[d]} | Backlog de ayer: {backlog_ayer}")
    print(f"  Pedidos Procesados Hoy: {L[d].varValue}")
    print(f"  Pedidos Atrasados (Backlog para mañana): {B[d].varValue}")
    print(f"  --> HORAS HOMBRE NECESARIAS: {H_totales[d].varValue:.2f} horas")
    print("-" * 50)

'''

'''

ESTO SERÁ LO QUE HAYA DESPUÉS de la PRUEBA

dias = df_pedidos_pred['fecha'].dt.date.unique()
demanda = df_pedidos_pred.groupby(df_pedidos_pred['fecha'].dt.date)['pedidos_previstos'].sum().to_dict()
centro_abierto = df_calendario.set_index(df_calendario['fecha'].dt.date)['centro_abierto'].to_dict()
porcentaje_devoluciones = 0.05  # Suponemos un 5% de devoluciones sobre el total de pedidos
horas_max_dia = 

'''



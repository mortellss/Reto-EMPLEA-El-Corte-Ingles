from sqlalchemy import create_engine
import pandas as pd
import pulp as plp

engine = create_engine("mysql+pymysql://root:root2004@localhost/emplea")


# query para obtener la prediccion

query_prediccion = """
SELECT fecha,
       pedidos_previstos, 
       limite_inferior, 
       limite_superior
FROM prediccion
"""
df_pedidos_pred = pd.read_sql(query_prediccion, con=engine)
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
df_calendario['fecha'] = pd.to_datetime(df_calendario['fecha'])
df_calendario['hora_apertura'] =pd.to_timedelta(df_calendario['hora_apertura'])
df_calendario['hora_cierre'] =pd.to_timedelta(df_calendario['hora_cierre'])

# El objetivo es minimizar el coste
# Cuando está cerrado, se pasa al día siguiente



prob = plp.LpProblem("Min_Coste", plp.LpMinimize)

horas_horario1 = plp.LpVariable('horas_horario1', lowBound=0, upperBound=11, cat='Continuous')
horario1 = plp.LpVariable(cat = 'Binary')
horas_horario2 = plp.LpVariable('horas_horario2', lowBound = 0, upBound=10, cat='Continuous')
# El horario 2 es lo contrario al horario 2

coste_horario1 = 1
coste_horario2 = 1

prob -= 3*horas_ma + 5*horas_ta, "Funcion_Objetivo"

prob += 2*x + y <= 10, "Restriccion_1"
prob += x + 2*y <= 12, "Restriccion_2"

prob.solve()

print(f"Estado: {plp.LpStatus[prob.status]}")
print(f"Valor óptimo de x: {plp.value(x)}")
print(f"Valor óptimo de y: {plp.value(y)}")
print(f"Valor máximo de Z: {plp.value(prob.objective)}")
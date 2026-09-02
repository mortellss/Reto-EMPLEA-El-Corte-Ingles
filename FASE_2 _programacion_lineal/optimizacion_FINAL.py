import argparse
from sqlalchemy import create_engine, text
import pandas as pd
import pulp
import math
import os
from pathlib import Path
from dotenv import load_dotenv
'''

load_dotenv()

usuario = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")

engine = create_engine(
    f"mysql+pymysql://{usuario}:{password}@localhost/emplea"
)

'''
import os
from sqlalchemy import create_engine

PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")
load_dotenv(PROJECT_ROOT / "interfaz" / "backend" / ".env")



DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_SSL_CA = os.getenv("DB_SSL_CA")

engine = create_engine(
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}",
    connect_args={
        "ssl": {
            "ca": DB_SSL_CA
        }
    },
    pool_pre_ping=True
)

parser = argparse.ArgumentParser()
parser.add_argument("--fecha-inicio", required=False)
parser.add_argument("--fecha-fin", required=False)
args = parser.parse_args()

fecha_inicio_filtro = pd.to_datetime(args.fecha_inicio) if args.fecha_inicio else None
fecha_fin_filtro = pd.to_datetime(args.fecha_fin) if args.fecha_fin else None

if fecha_inicio_filtro is not None and fecha_fin_filtro is not None and fecha_inicio_filtro > fecha_fin_filtro:
    raise ValueError("La fecha de inicio no puede ser posterior a la fecha de fin.")

# Tipos de jornada 

query_trabajadores = """
SELECT id_contrato
FROM trabajador
"""

df_trabajadores = pd.read_sql(query_trabajadores, con=engine)
count_tipos_contratos = df_trabajadores['id_contrato'].value_counts().to_dict()
print(count_tipos_contratos)


num_trabajadores_100_C = count_tipos_contratos.get(1)
horas_100 = 37.5 * 4
max_horas_100_C = num_trabajadores_100_C * horas_100

num_trabajadores_912_C = count_tipos_contratos.get(2)
horas_JP_912 = 37.5 * 0.912 * 4
max_horas_912_C = num_trabajadores_912_C * horas_JP_912

num_trabajadores_90_FD = count_tipos_contratos.get(3)
horas_JP_90 = 37.5 * 0.90 * 4
max_horas_90_FD = num_trabajadores_90_FD * horas_JP_90

num_trabajadores_70_C = count_tipos_contratos.get(4)
horas_JP_70 = 37.5 * 0.70 * 4
max_horas_70_C = num_trabajadores_70_C * horas_JP_70

num_trabajadores_JP_407_C = count_tipos_contratos.get(5)
horas_JP_407 = 37.5 * 0.407 * 4
max_horas_407_C = num_trabajadores_JP_407_C * horas_JP_407

num_trabajadores_JP_40_C = count_tipos_contratos.get(6)
horas_JP_40 = 37.5 * 0.40 * 4
max_horas_40_C = num_trabajadores_JP_40_C * horas_JP_40

num_trabajadores_JP_253_C = count_tipos_contratos.get(7)
horas_JP_253 = 37.5 * 0.253 * 4
max_horas_253_C = num_trabajadores_JP_253_C * horas_JP_253

max_horas = max_horas_100_C + max_horas_912_C + max_horas_70_C + max_horas_407_C + max_horas_40_C + max_horas_253_C
max_horas_sin_100 = max_horas_912_C + max_horas_70_C + max_horas_407_C + max_horas_40_C + max_horas_253_C


# Definción del problema

prob = pulp.LpProblem("Optimizacion_Coste", pulp.LpMinimize)

query_prediccion = """
SELECT fecha, pedidos_acumulados
FROM prediccion
ORDER BY fecha
"""

def get_optimizacion_config():
    with engine.begin() as conn:
        row = conn.execute(text("""
            SELECT
                horas_presencia_mostrador,
                horas_otras_gestiones,
                porcentaje_devoluciones,
                horas_gestion_devoluciones,
                recoleccion_1_lineas,
                recoleccion_1_tiempo_min,
                recoleccion_2_lineas,
                recoleccion_2_tiempo_min,
                empaquetado_lineas,
                empaquetado_tiempo_min,
                almacenado_lineas,
                almacenado_tiempo_min,
                entrega_lineas,
                entrega_tiempo_min
            FROM configuracion_optimizacion
            WHERE id_centro = 1
        """)).mappings().first()

    if row is None:
        return {
            "horas_presencia_mostrador": 11.0,
            "horas_otras_gestiones": 1.0,
            "porcentaje_devoluciones": 0.05,
            "horas_gestion_devoluciones": 3.0,
            "recoleccion_1_lineas": 1000,
            "recoleccion_1_tiempo_min": 1.8,
            "recoleccion_2_lineas": 1000,
            "recoleccion_2_tiempo_min": 0.315,
            "empaquetado_lineas": 1000,
            "empaquetado_tiempo_min": 5.04,
            "almacenado_lineas": 1000,
            "almacenado_tiempo_min": 4.35,
            "entrega_lineas": 1000,
            "entrega_tiempo_min": 2.98,
        }

    return {
        "horas_presencia_mostrador": float(row["horas_presencia_mostrador"]),
        "horas_otras_gestiones": float(row["horas_otras_gestiones"]),
        "porcentaje_devoluciones": float(row["porcentaje_devoluciones"]),
        "horas_gestion_devoluciones": float(row["horas_gestion_devoluciones"]),
        "recoleccion_1_lineas": int(row["recoleccion_1_lineas"]),
        "recoleccion_1_tiempo_min": float(row["recoleccion_1_tiempo_min"]),
        "recoleccion_2_lineas": int(row["recoleccion_2_lineas"]),
        "recoleccion_2_tiempo_min": float(row["recoleccion_2_tiempo_min"]),
        "empaquetado_lineas": int(row["empaquetado_lineas"]),
        "empaquetado_tiempo_min": float(row["empaquetado_tiempo_min"]),
        "almacenado_lineas": int(row["almacenado_lineas"]),
        "almacenado_tiempo_min": float(row["almacenado_tiempo_min"]),
        "entrega_lineas": int(row["entrega_lineas"]),
        "entrega_tiempo_min": float(row["entrega_tiempo_min"]),
    }


df_prediccion = pd.read_sql(query_prediccion, con=engine)
df_prediccion['fecha'] = pd.to_datetime(df_prediccion['fecha'])
if fecha_inicio_filtro is not None:
    df_prediccion = df_prediccion[df_prediccion['fecha'] >= fecha_inicio_filtro].copy()
if fecha_fin_filtro is not None:
    df_prediccion = df_prediccion[df_prediccion['fecha'] <= fecha_fin_filtro].copy()

df_prediccion['pedidos_acumulados'] = pd.to_numeric(df_prediccion['pedidos_acumulados'], errors='coerce').fillna(0).astype(int)
df_prediccion = df_prediccion.sort_values('fecha').reset_index(drop=True)

if df_prediccion.empty:
    raise ValueError("No hay datos de predicción disponibles. Genera la predicción antes de ejecutar la planificación.")

# Si el filtro elegido por la interfaz no coincide con ninguna fecha, evitamos
# que el código intente construir un horizonte vacío y falle más adelante.
df_prediccion['mes'] = df_prediccion['fecha'].dt.to_period('M')
meses_horizonte = df_prediccion['mes'].drop_duplicates().tolist()
if not meses_horizonte:
    raise ValueError("No hay meses de predicción para el rango solicitado. Genera la predicción antes de planificar.")

NUM_MESES = len(meses_horizonte)
meses = range(1, NUM_MESES + 1)

config_optimizacion = get_optimizacion_config()

# Variables de decisión para x meses del horizonte
X_HO = {
    mes: pulp.LpVariable(f"X_HO_{mes}", lowBound=0, upBound=max_horas, cat="Continuous")
    for mes in meses
}
X_HC = {
    mes: pulp.LpVariable(f"X_HC_{mes}", lowBound=0, upBound=max_horas_sin_100 * 0.6, cat="Continuous")
    for mes in meses
}
X_HFD = {
    mes: pulp.LpVariable(f"X_HFD_{mes}", lowBound=0, cat=pulp.LpInteger)
    for mes in meses
}
K_HFD = {
    mes: pulp.LpVariable(f"K_HFD_{mes}", lowBound=0, cat=pulp.LpInteger)
    for mes in meses
}
B_HO = {mes: pulp.LpVariable(f"B_HO_{mes}", cat=pulp.LpBinary) for mes in meses}
B_HC = {mes: pulp.LpVariable(f"B_HC_{mes}", cat=pulp.LpBinary) for mes in meses}
B_HFD = {mes: pulp.LpVariable(f"B_HFD_{mes}", cat=pulp.LpBinary) for mes in meses}

# Otras variables

meses_horizonte = df_prediccion['mes'].drop_duplicates().tolist()

if len(meses_horizonte) < NUM_MESES:
    raise ValueError(f"No hay {NUM_MESES} meses de predicción para calcular el horizonte completo")

pedidos_mes = {
    indice: int(df_prediccion[df_prediccion['mes'] == periodo]['pedidos_acumulados'].sum())
    for indice, periodo in enumerate(meses_horizonte, start=1)
}


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

promociones_mes = {
    indice: hay_promocion(periodo)
    for indice, periodo in enumerate(meses_horizonte, start=1)
    
}


# Función objetivo

precio_hora_ordinaria = 13.18
precio_hora_complementaria = 13.18
precio_hora_fijo_discontinuo = 13.18
# precio_hora_contratacion_temporal = precio_hora_ordinaria * 1.15 # 15% más considerando que es un contrato temporal y hay que formar al trabajador
# precio_hora_extraordinaria = precio_hora_ordinaria * 1.3

prob += precio_hora_ordinaria * pulp.lpSum(X_HO.values()) + \
    precio_hora_complementaria * pulp.lpSum(X_HC.values()) + \
    precio_hora_fijo_discontinuo * pulp.lpSum(X_HFD.values()), "Minimizar_Coste_Total"


def guardar_horas_mensuales():
    datos = []
    for mes in meses:
        horas_ordinarias = int(round(float(X_HO[mes].varValue))) if X_HO[mes].varValue is not None else 0
        horas_complementarias = int(round(float(X_HC[mes].varValue))) if X_HC[mes].varValue is not None else 0
        horas_fd = int(round(float(X_HFD[mes].varValue))) if X_HFD[mes].varValue is not None else 0

        datos.append({
            "mes": int(mes),
            "fecha_generacion": pd.Timestamp.today().normalize().strftime("%Y-%m-%d"),
            "horas_ordinarias": horas_ordinarias,
            "horas_complementarias": horas_complementarias,
            "horas_fd": horas_fd,
        })

    if not datos:
        return {}

    with engine.begin() as conexion:
        for fila in datos:
            conexion.execute(
                text("""
                    INSERT INTO horas_mensuales (mes, fecha_generacion, horas_ordinarias, horas_complementarias, horas_fd)
                    VALUES (:mes, :fecha_generacion, :horas_ordinarias, :horas_complementarias, :horas_fd)
                    ON DUPLICATE KEY UPDATE
                        fecha_generacion = VALUES(fecha_generacion),
                        horas_ordinarias = VALUES(horas_ordinarias),
                        horas_complementarias = VALUES(horas_complementarias),
                        horas_fd = VALUES(horas_fd)
                """),
                fila,
            )

    return {
        fila["mes"]: {
            "horas_ordinarias": fila["horas_ordinarias"],
            "horas_complementarias": fila["horas_complementarias"],
            "horas_fd": fila["horas_fd"],
        }
        for fila in datos
    }


# Restricciones

    # La suma de todas los tipos de horas tiene que ser capaz de completar todos los pedidos mensuales

def tiempo_por_linea_horas(lineas, tiempo_total_segundos):
    if lineas is None or lineas <= 0:
        return 0.0
    # En este caso los tiempos ya vienen en segundos; solo hay que convertir
    # el tiempo por línea a horas dividendo entre 3600.
    return (float(tiempo_total_segundos) / float(lineas)) / 3600.0

horas_recoleccion_1 = tiempo_por_linea_horas(
    config_optimizacion["recoleccion_1_lineas"],
    config_optimizacion["recoleccion_1_tiempo_min"],
)
horas_recoleccion_2 = tiempo_por_linea_horas(
    config_optimizacion["recoleccion_2_lineas"],
    config_optimizacion["recoleccion_2_tiempo_min"],
)
horas_empaquetado = tiempo_por_linea_horas(
    config_optimizacion["empaquetado_lineas"],
    config_optimizacion["empaquetado_tiempo_min"],
)
horas_almacenado = tiempo_por_linea_horas(
    config_optimizacion["almacenado_lineas"],
    config_optimizacion["almacenado_tiempo_min"],
)
horas_entrega = tiempo_por_linea_horas(
    config_optimizacion["entrega_lineas"],
    config_optimizacion["entrega_tiempo_min"],
)
horas_pedidos = horas_recoleccion_1 + horas_recoleccion_2 + horas_empaquetado + horas_almacenado + horas_entrega
# Falta incluir que considere las horas según las horas que está abierto el centro
horas_presencia_mostrador = config_optimizacion["horas_presencia_mostrador"]
horas_otras_gestiones = config_optimizacion["horas_otras_gestiones"]
horas_gestion_mostrador = config_optimizacion["horas_gestion_devoluciones"]
porcentaje_devoluciones = config_optimizacion["porcentaje_devoluciones"]
horas_gestion_devoluciones = config_optimizacion["horas_gestion_devoluciones"]
 
for mes in meses:
    horas_necesarias = (
        pedidos_mes[mes] * (horas_pedidos + porcentaje_devoluciones * horas_gestion_devoluciones)
        + horas_presencia_mostrador
        + horas_otras_gestiones
        + horas_gestion_mostrador
    )
    prob += X_HO[mes] + X_HC[mes] + X_HFD[mes] >= horas_necesarias, f"Horas_Completar_Pedidos_Mes_{mes}"


    # Relacionamos las variables binarias con las continuas

for mes in meses:
    prob += X_HO[mes] <= B_HO[mes] * max_horas
    prob += X_HC[mes] <= B_HC[mes] * max_horas_sin_100 * 0.6
    prob += X_HFD[mes] <= B_HFD[mes] * max_horas_90_FD

    # Primero se deben de completar las horas ordinarias antes que las demás

for mes in meses:
    prob += X_HO[mes] >= B_HC[mes] * max_horas
    prob += X_HO[mes] >= B_HFD[mes] * max_horas

    # Jornadas de 5 horas

for mes in meses:
    prob += X_HFD[mes] == 4 * K_HFD[mes]

    # Los fijos discontinuos solamente pueden estar contratados:
    # - Desde el 27 de noviembre hasta el 28 de febrero del año siguiente.
    # - Desde la segunda semana de junio hasta la segunda semana de septiembre.

# Determinamos si cada mes está dentro de los periodos permitidos (27 Nov - 28 Feb) y 
def is_in_fd_period(fecha):
    month = fecha.month
    day = fecha.day
    
    # Noviembre: desde día 27 hasta fin de mes
    if month == 11 and day >= 27:
        return True
    # Diciembre: todo el mes
    if month == 12:
        return True
    # Enero y Febrero: hasta día 28
    if month in [1, 2]:
        return True
    if month == 6 and day >= 4:
        return True
    if month == 9 and day <= 4:
        return True
    if month in [7, 8]: 
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

# Aplicamos restricciones para cada uno de los 12 meses.
for mes in meses:
    if not meses_en_periodo_fd[mes - 1]:
        prob += X_HFD[mes] == 0, f"Restriccion_FD_Periodo_Mes_{mes}"

# Según el día se trabajan 10 u 11 horas

prob.solve()

resultado_horas = guardar_horas_mensuales()
print("Horas guardadas en horas_mensuales:", resultado_horas)

print("Estado del modelo:", pulp.LpStatus[prob.status], "\n")

# Creamos un índice para eliminar las desviaciones que puedan haber debido a los errores en la medición del tiempo

index = 0.15


for indice, periodo in enumerate(meses_horizonte, start=1):
    print(f"{periodo}: horas ordinarias={round((X_HO[indice].varValue) / (1 + index))}, "
          f"complementarias={round((X_HC[indice].varValue) / (1 + index))}, "
          f"FD={round(((X_HFD[indice].varValue / 5) * 5) / ( 1 + index))}")



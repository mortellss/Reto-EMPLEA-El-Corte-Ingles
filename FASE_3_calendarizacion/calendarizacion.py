from pathlib import Path
import sys
import importlib.util
from sqlalchemy import create_engine
import pandas as pd
import pulp
import math


engine = create_engine("mysql+pymysql://root:root2004@localhost/emplea")



# Importamos las variables obtenidas en la optimización final

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

RUTA_OPTIMIZACION = ROOT / "FASE_2 _programacion_lineal" / "optimizacion_FINAL.py"
spec = importlib.util.spec_from_file_location("optimizacion_final", RUTA_OPTIMIZACION)
if spec is None or spec.loader is None:
    raise ImportError(f"No se pudo cargar {RUTA_OPTIMIZACION}")

optimizacion_final = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = optimizacion_final
spec.loader.exec_module(optimizacion_final)

X_HO_1 = optimizacion_final.X_HO[1]
X_HO_2 = optimizacion_final.X_HO[2]
X_HO_3 = optimizacion_final.X_HO[3]
X_HC_1 = optimizacion_final.X_HC[1]
X_HC_2 = optimizacion_final.X_HC[2]
X_HC_3 = optimizacion_final.X_HC[3]
X_HFD_1 = optimizacion_final.X_HFD[1]
X_HFD_2 = optimizacion_final.X_HFD[2]
X_HFD_3 = optimizacion_final.X_HFD[3]

var_values = {
    "X_HO_1": X_HO_1.varValue,
    "X_HO_2": X_HO_2.varValue,
    "X_HO_3": X_HO_3.varValue,
    "X_HC_1": X_HC_1.varValue,
    "X_HC_2": X_HC_2.varValue,
    "X_HC_3": X_HC_3.varValue,
    "X_HFD_1": X_HFD_1.varValue,
    "X_HFD_2": X_HFD_2.varValue,
    "X_HFD_3": X_HFD_3.varValue,
}

query_trabajadores = """
SELECT id_contrato, nombre, estado
FROM trabajador
WHERE estado = 1
"""

df_trabajadores = pd.read_sql(query_trabajadores, con=engine)
tipo_contrato_nombre = df_trabajadores.groupby('id_contrato')['nombre'].apply(list).to_dict()

count_tipos_contratos = df_trabajadores['id_contrato'].value_counts().to_dict()

num_trabajadores_100_C = count_tipos_contratos.get(1)
horas_100_semana = 40 
max_horas_100_C_semana = num_trabajadores_100_C * horas_100_semana

num_trabajadores_912_C = count_tipos_contratos.get(2)
horas_JP_912_semana = 40 * 0.912 
max_horas_912_C_semana = num_trabajadores_912_C * horas_JP_912_semana

num_trabajadores_90_FD = count_tipos_contratos.get(3)
horas_JP_90_semana = 40 * 0.90 
max_horas_90_FD = num_trabajadores_90_FD * horas_JP_90_semana

num_trabajadores_70_C = count_tipos_contratos.get(4)
horas_JP_70_semana = 40 * 0.70
max_horas_70_C_semana = num_trabajadores_70_C * horas_JP_70_semana

num_trabajadores_JP_407_C = count_tipos_contratos.get(5)
horas_JP_407_semana = 40 * 0.407
max_horas_407_C_semana = num_trabajadores_JP_407_C * horas_JP_407_semana

num_trabajadores_JP_40_C = count_tipos_contratos.get(6)
horas_JP_40_semana = 40 * 0.40
max_horas_40_C_semana = num_trabajadores_JP_40_C * horas_JP_40_semana

num_trabajadores_JP_253_C = count_tipos_contratos.get(7)
horas_JP_253_semana = 40 * 0.253
max_horas_253_C_semana = num_trabajadores_JP_253_C * horas_JP_253_semana

total_horas_semana_fijas = max_horas_100_C_semana + max_horas_912_C_semana + max_horas_70_C_semana + max_horas_407_C_semana + max_horas_40_C_semana + max_horas_253_C_semana


NUM_MESES = 6
meses = range(1, NUM_MESES + 1)

query_prediccion = """
SELECT fecha, pedidos_acumulados
FROM prediccion
ORDER BY fecha
"""

df_prediccion = pd.read_sql(query_prediccion, con=engine)

df_prediccion['fecha'] = pd.to_datetime(df_prediccion['fecha'])
df_prediccion['pedidos_acumulados'] = pd.to_numeric(df_prediccion['pedidos_acumulados'], errors='coerce').fillna(0).astype(int)
df_prediccion = df_prediccion.sort_values('fecha').reset_index(drop=True)
df_prediccion['mes'] = df_prediccion['fecha'].dt.to_period('M')

meses_horizonte = df_prediccion['mes'].drop_duplicates().tolist()[:NUM_MESES]

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

# Para comprobar si hay una promoción activa en una fecha concreta

def hay_promocion(fecha):
    fecha = pd.Timestamp(fecha).normalize()
    activo = df_promociones[
        (df_promociones['fecha_inicio'] <= fecha) &
        (df_promociones['fecha_fin'] >= fecha)
    ]
    return not activo.empty

promociones_mes = {
    indice: df_prediccion.loc[
        df_prediccion['mes'] == periodo, 'fecha'
    ].apply(hay_promocion).any()
    
    for indice, periodo in enumerate(meses_horizonte, start=1)
}

# Comprobar si una fecha concreta pertenece a un periodo permitido de FD

def is_in_fd_period(fecha):
    fecha = pd.Timestamp(fecha)
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

# Determinamos si cada mes del horizonte contiene días en el periodo permitido

meses_en_periodo_fd = {
    indice: df_prediccion.loc[
        df_prediccion['mes'] == periodo, 'fecha'
    ].apply(is_in_fd_period).any()
    for indice, periodo in enumerate(meses_horizonte, start=1)
}

# Las horas diarias necesarias están


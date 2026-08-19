from pathlib import Path
import sys
from sqlalchemy import create_engine
import pandas as pd
import pulp
import math


engine = create_engine("mysql+pymysql://root:root2004@localhost/emplea")



# Importamos las variables obtenidas en la fase 1

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from programacion_lineal.optimizacion_horas import (
    X_HO_1,
    X_HO_2,
    X_HO_3,
    X_HC_1,
    X_HC_2,
    X_HC_3,
    X_HFD_1,
    X_HFD_2,
    X_HFD_3,
)

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

num_trabajadores_100_C = count_tipos_contratos[1]
horas_100_semana = 40 
max_horas_100_C_semana = num_trabajadores_100_C * horas_100_semana

num_trabajadores_912_C = count_tipos_contratos[2]
horas_JP_912_semana = 40 * 0.912 
max_horas_912_C_semana = num_trabajadores_912_C * horas_JP_912_semana

num_trabajadores_90_FD = count_tipos_contratos[3]
horas_JP_90_semana = 40 * 0.90 
max_horas_90_FD = num_trabajadores_90_FD * horas_JP_90_semana

num_trabajadores_70_C = count_tipos_contratos[4]
horas_JP_70_semana = 40 * 0.70
max_horas_70_C_semana = num_trabajadores_70_C * horas_JP_70_semana

num_trabajadores_JP_407_C = count_tipos_contratos[5]
horas_JP_407_semana = 40 * 0.407
max_horas_407_C_semana = num_trabajadores_JP_407_C * horas_JP_407_semana

num_trabajadores_JP_40_C = count_tipos_contratos[6]
horas_JP_40_semana = 40 * 0.40
max_horas_40_C_semana = num_trabajadores_JP_40_C * horas_JP_40_semana

num_trabajadores_JP_253_C = count_tipos_contratos[7]
horas_JP_253_semana = 40 * 0.253
max_horas_253_C_semana = num_trabajadores_JP_253_C * horas_JP_253_semana

total_horas_semana_fijas = max_horas_100_C_semana + max_horas_912_C_semana + max_horas_70_C_semana + max_horas_407_C_semana + max_horas_40_C_semana + max_horas_253_C_semana



print(total_horas_semana_fijas)



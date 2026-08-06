import os
import pandas as pd
from sqlalchemy import create_engine

 
engine = create_engine(
    "mysql+pymysql://root:root2004@localhost/emplea"
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ruta_archivo = os.path.join(BASE_DIR, "..", "data", "Tablas Emplea.xlsx")

print(f"\nImportando datos desde: {ruta_archivo}")

# Leer el contenido de la hoja de los pedidos históricos

df = pd.read_excel(ruta_archivo, sheet_name="Pedido Histórico")

#  Renombrar las columnas
df.columns = [
    "fecha",
    "envios_2h_mcia_general_pedidos",
    "envios_2h_mcia_general_lineas",
    "envios_2h_food_pedidos",
    "envios_2h_food_lineas",
    "encargos_pedidos",
    "encargos_lineas",
    "home_delivery_pedidos",
    "home_delivery_lineas",
    "total_pedidos",
    "total_lineas"
]

# Limpieza de nulos

df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")
df = df.dropna(subset=["fecha"])
df["fecha"] = df["fecha"].dt.date


df["id_centro"] = 1

# Insertar
try:

    df.to_sql(
        "pedidohistorico",
        con=engine,
        if_exists="replace", 
        index=False
    )
    print(f"{len(df)} importados a la base de datos.")
except Exception as e:
    print(f"{e}")

# Insertar los datos del calendario

df_cal = pd.read_excel(ruta_archivo, sheet_name="Calendario")
df_cal = df_cal[['fecha', 'centro_abierto', 'es_festivo', 'dia_posterior_festivo', 'hora_apertura', 'hora_cierre']]

df_cal["fecha"] = pd.to_datetime(df_cal["fecha"], errors="coerce")
df_cal = df_cal.dropna(subset=["fecha"])
df_cal["fecha"] = df_cal["fecha"].dt.date

df_cal["centro_abierto"] = df_cal["centro_abierto"].astype(int)
df_cal["es_festivo"] = df_cal["es_festivo"].astype(int)
df_cal["dia_posterior_festivo"] = df_cal["dia_posterior_festivo"].astype(int)

df_cal.to_sql(name='calendario', con=engine, if_exists='append', index=False)

print("¡Datos insertados correctamente en la base de datos!")
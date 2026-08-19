from sqlalchemy import create_engine
import pandas as pd
import pulp
import math



engine = create_engine("mysql+pymysql://root:root2004@localhost/emplea")

query_prediccion = """
SELECT fecha, pedidos_acumulados
FROM prediccion
ORDER BY fecha
"""

df_prediccion = pd.read_sql(query_prediccion, con=engine)

df_prediccion['fecha'] = pd.to_datetime(df_prediccion['fecha'])

start = pd.Timestamp(f"{df_prediccion['fecha'][1].year}-11-01")
end = pd.Timestamp(f"{df_prediccion['fecha'][1].year + 1}-02-28")

mask = df_prediccion["fecha"].between(start, end, inclusive="both")


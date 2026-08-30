from sqlalchemy import create_engine
import pandas as pd

# Cálculo de horas necesarias con los datos reales proporcionados 
# Nota: Para que se calcule bien, en el archivo de importar_datos tiene que estar bien puesta la referencia a la hoja de excel


engine = create_engine("mysql+pymysql://root:root2004@localhost/emplea")

year = 2026
mes_inicial = 1
meses_a_calcular = 6
fecha_inicio = f"{year}-{mes_inicial:02d}-01"
fecha_fin = f"{year}-{mes_inicial + meses_a_calcular:02d}-01"

query_pedidos = f"""
SELECT fecha, total_lineas
FROM pedidohistorico
WHERE id_centro = 1
	AND fecha >= '{fecha_inicio}'
	AND fecha < '{fecha_fin}'
ORDER BY fecha
"""

df_pedidos = pd.read_sql(query_pedidos, con=engine)
df_pedidos["fecha"] = pd.to_datetime(df_pedidos["fecha"])
df_pedidos["total_lineas"] = pd.to_numeric(
	df_pedidos["total_lineas"], errors="coerce"
).fillna(0)
df_pedidos["mes"] = df_pedidos["fecha"].dt.to_period("M")


query_calendario = """
SELECT 
    fecha, 
    centro_abierto,
    es_festivo,
    dia_posterior_festivo
FROM calendario
WHERE id_centro = 1
"""
df_calendario = pd.read_sql(query_calendario, con=engine)
df_calendario['fecha'] = pd.to_datetime(df_calendario['fecha'])
df_calendario = df_calendario.drop_duplicates(subset=['fecha'], keep='last').sort_values('fecha').reset_index(drop=True)
df_calendario['centro_cerrado'] = 1 - df_calendario['centro_abierto']

df_final = pd.merge(df_pedidos, df_calendario, on='fecha', how='left')


pedidos_mes = (
	df_pedidos.groupby("mes", as_index=True)["total_lineas"]
	.sum()
	.reindex(
		pd.period_range(
			f"{year}-{mes_inicial:02d}", periods=meses_a_calcular, freq="M"
		),
		fill_value=0,
	)
)

horas_recoleccion_1 = 0.00029611101
horas_recoleccion_2 = 0.00005238316019
horas_empaquetado = (0.007350211777 + 0.009435869071) / 2
horas_almacenado = (
	0.001311401251 + 0.006738298913 + 0.01256998856 + 0.009548456075
) / 4
horas_entrega = (0.0002393378489 + 0.009691886578) / 2
horas_pedidos = (
	horas_recoleccion_1
	+ horas_recoleccion_2
	+ horas_empaquetado
	+ horas_almacenado
	+ horas_entrega
)

horas_presencia_mostrador = 11
horas_otras_gestiones = 1
horas_gestion_mostrador = 3
porcentaje_devoluciones = 0.05
horas_gestion_devoluciones = 3

horas_fijas_diarias = (
	horas_presencia_mostrador
	+ horas_otras_gestiones
	+ horas_gestion_mostrador
)
horas_por_pedido = horas_pedidos + porcentaje_devoluciones * horas_gestion_devoluciones

df_final['horas_necesarias'] = (df_final['total_lineas'] * horas_por_pedido) + horas_fijas_diarias

df_final['centro_abierto'] = df_final['centro_abierto'].fillna(1)
df_final.loc[df_final['centro_abierto'] == 0, 'horas_necesarias'] = 0

resultado = df_final.groupby("mes").agg(
    total_lineas=('total_lineas', 'sum'),
    horas_necesarias=('horas_necesarias', 'sum')
).reindex(
    pd.period_range(
        f"{year}-{mes_inicial:02d}", periods=meses_a_calcular, freq="M"
    ),
    fill_value=0,
)


print(f"Horas por pedido: {horas_por_pedido:.9f}")
print(f"\nHoras necesarias por mes de los primeros {meses_a_calcular} meses de {year}:")
print(resultado.to_string(float_format=lambda valor: f"{valor:.2f}"))
print(f"\nTotal pedidos de los primeros {meses_a_calcular} meses de {year}: {resultado['total_lineas'].sum():.0f}")
print(f"Total horas: {resultado['horas_necesarias'].sum():.2f}")

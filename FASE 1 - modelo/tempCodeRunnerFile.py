
query_promociones = """
SELECT
    nombre,
    fecha_inicio AS inicio,
    fecha_fin AS fin
FROM promocion
WHERE id_centro = 1
"""
promociones = pd.read_sql(query_promociones, con=engine).to_dict(orient="records")

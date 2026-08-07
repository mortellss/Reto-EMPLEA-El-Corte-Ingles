query_calendario = """
SELECT 
    fecha AS ds, 
    centro_abierto,
    es_festivo,
    dia_posterior_festivo
FROM calendario
"""
df_calendario = pd.read_sql(query_calendario, con=engine)
print(df_calendario.head())
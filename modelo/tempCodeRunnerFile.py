df_cv['error_porcentual'] = abs((df_cv['y'] - df_cv['yhat']) / df_cv['y']) * 100

# 2. Ordenamos para obtener los errores más graves
peores_dias = df_cv.sort_values(by='error_porcentual', ascending=False).head(15)

print("\n--- Fechas críticas que están disparando el MAPE ---")
print(peores_dias[['ds', 'cutoff', 'y', 'yhat', 'error_porcentual']])
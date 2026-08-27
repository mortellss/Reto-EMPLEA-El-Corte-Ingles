horas_necesarias_por_dia = {
    row["fecha"].date(): row["horas_necesarias"] for _, row in df_prediccion.iterrows()
}

print(horas_necesarias_por_dia)
print
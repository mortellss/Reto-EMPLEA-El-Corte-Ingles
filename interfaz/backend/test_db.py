from db import engine

try:
    with engine.connect() as conn:
        resultado = conn.exec_driver_sql("SHOW TABLES")

        print("TABLAS DE AIVEN:")
        for fila in resultado:
            print(fila[0])

except Exception as e:
    print("ERROR:")
    print(e)
from prophet import Prophet
import pandas as pd
from prophet.make_holidays import make_holidays_df
import matplotlib.pyplot as plt
from prophet.diagnostics import cross_validation, performance_metrics
from sqlalchemy import create_engine

engine = create_engine("mysql+pymysql://root:root2004@localhost/emplea")

query_pedidos = """
SELECT fecha AS ds, total_lineas AS y 
FROM pedidohistorico
"""
df_pedidos = pd.read_sql(query_pedidos, con=engine)

query_calendario = """
SELECT 
    fecha AS ds, 
    centro_abierto,
    es_festivo,
    dia_posterior_festivo
FROM calendario
"""
df_calendario = pd.read_sql(query_calendario, con=engine)

df_pedidos['ds'] = pd.to_datetime(df_pedidos['ds'])
df_calendario['ds'] = pd.to_datetime(df_calendario['ds'])

df_calendario['centro_cerrado'] = 1 - df_calendario['centro_abierto']

df_final = pd.merge(df_pedidos, df_calendario, on='ds', how='left')

df_final['centro_cerrado'] = df_final['centro_cerrado'].fillna(0)
df_final['es_festivo'] = df_final['es_festivo'].fillna(0)
df_final['dia_posterior_festivo'] = df_final['dia_posterior_festivo'].fillna(0)

# Eliminar los NaN porque Prophet no los lee bien
# df = df[df["y"] >= 0].copy()
# df = df.dropna(subset=["y"])

'''
promociones = pd.DataFrame([
    #ENERO 2023
    {"holiday": "feliz_año", "ds": "2022-12-25", "lower_window": 0, "upper_window": 11},
    {"holiday": "blancolor", "ds": "2023-01-19", "lower_window": 0, "upper_window": 9},
    {"holiday": "reyes_tecnologia", "ds": "2022-12-26", "lower_window": 0, "upper_window": 10},
    {"holiday": "rebajas_enero", "ds": "2023-01-06", "lower_window": 0, "upper_window":12},
    {"holiday": "tecnoprecios", "ds": "2023-01-07", "lower_window": 0, "upper_window": 24},
    #{"holiday": "drogueria_perfumeria_menaje", "ds": "2023-01-12", "lower_window": 0, "upper_window": 13},
    {"holiday": "segundas_rebajas_enero", "ds": "2023-01-19", "lower_window": 0, "upper_window": 14},
    {"holiday": "feria_artesania", "ds": "2023-01-27", "lower_window": 0, "upper_window": 24},
    {"holiday": "semana_deporte", "ds": "2023-01-26", "lower_window": 0, "upper_window": 7},
    #FEBRERO 2023
    {"holiday": "rebaja_final", "ds": "2023-02-02", "lower_window": 0, "upper_window": 26},
    {"holiday": "san_valentin", "ds": "2023-02-02", "lower_window": 0, "upper_window": 12},
    {"holiday": "ofertas_limite_1", "ds": "2023-02-02", "lower_window": 0, "upper_window": 3},
    {"holiday": "ofertas_limite_2", "ds": "2023-02-09", "lower_window": 0, "upper_window": 3},
    {"holiday": "ofertas_limite_3", "ds": "2023-02-16", "lower_window": 0, "upper_window": 3},
    {"holiday": "ofertas_limite_4", "ds": "2023-02-23", "lower_window": 0, "upper_window": 3},
    {"holiday": "financiaciacion_total", "ds": "2023-02-16", "lower_window": 0, "upper_window": 6},
    {"holiday": "tecnoprecios", "ds": "2023-02-24", "lower_window": 0, "upper_window": 16},
    {"holiday": "aire_acondicionado", "ds": "2023-02-23", "lower_window": 0, "upper_window": 20},
    #{"holiday": "hogar_decoracion", "ds": "2023-02-23", "lower_window": 0, "upper_window": 487},
    #MARZO 2023
    {"holiday": "tecnoprecios", "ds": "2023-03-09", "lower_window": 0, "upper_window": 13},
    {"holiday": "feria_alimentacion", "ds": "2023-03-02", "lower_window": 0, "upper_window": 29},
    {"holiday": "hogar_baby", "ds": "2023-03-10", "lower_window": 0, "upper_window": 23},
    {"holiday": "especial_deportes", "ds": "2023-03-09", "lower_window": 0, "upper_window": 10},
    {"holiday": "dia_padre", "ds": "2023-03-09", "lower_window": 0, "upper_window": 10},
    {"holiday": "primavera", "ds": "2023-03-23", "lower_window": 0, "upper_window": 21},
    {"holiday": "descuentos_top", "ds": "2023-03-16", "lower_window": 0, "upper_window": 17},
    {"holiday": "tecnoprecios", "ds": "2023-03-23", "lower_window": 0, "upper_window": 6},
    {"holiday": "dia_poesia", "ds": "2023-03-21", "lower_window": 0, "upper_window": 0},
    #ABRIL 2023
    {"holiday": "cocinas", "ds": "2023-04-01", "lower_window": 0, "upper_window": 30},
    {"holiday": "dia_libro_juvenil", "ds": "2023-04-02", "lower_window": 0, "upper_window": 0},
    {"holiday": "aire_acondicionado", "ds": "2023-04-10", "lower_window": 0, "upper_window": 9},
    {"holiday": "emidio_tucci", "ds": "2023-04-11", "lower_window": 0, "upper_window": 19},
    {"holiday": "8_dias_oro", "ds": "2023-04-13", "lower_window": 0, "upper_window": 10},
    {"holiday": "8_dias_oro_hogar", "ds": "2023-04-13", "lower_window": 0, "upper_window": 17},
    {"holiday": "tecnoprecios", "ds": "2023-04-20", "lower_window": 0, "upper_window": 13},
    {"holiday": "dia_libro", "ds": "2023-04-22", "lower_window": 0, "upper_window": 3},
    {"holiday": "dias_belleza", "ds": "2023-04-24", "lower_window": 0, "upper_window": 15},
    {"holiday": "dia_madre", "ds": "2023-04-24", "lower_window": 0, "upper_window": 10},
    #MAYO 2023
    {"holiday": "semana_internet", "ds": "2023-05-08", "lower_window": 0, "upper_window": 9},
    {"holiday": "financiacion_total", "ds": "2023-05-25", "lower_window": 0, "upper_window": 8},
    {"holiday": "tecnoprecios", "ds": "2023-05-04", "lower_window": 0, "upper_window": 13},
    {"holiday": "supertecnoprecios", "ds": "2023-05-18", "lower_window": 0, "upper_window": 3},
    {"holiday": "tecnoprecios", "ds": "2023-05-22", "lower_window": 0, "upper_window": 16},
    {"holiday": "mes_friki", "ds": "2023-05-15", "lower_window": 0, "upper_window": 24},
    {"holiday": "cuidado_bienestar", "ds": "2023-05-18", "lower_window": 0, "upper_window": 13},
    {"holiday": "comuniones", "ds": "2023-05-01", "lower_window": 0, "upper_window": 31},
    {"holiday": "deportes_outdoor", "ds": "2023-05-18", "lower_window": 0, "upper_window": 20},
    #JUNIO 2023
    {"holiday": "venta_privada", "ds": "2023-06-08", "lower_window": 0, "upper_window": 3},
    {"holiday": "rebajas_junio", "ds": "2023-06-22", "lower_window": 0, "upper_window": 13},
    {"holiday": "descuentos_top", "ds": "2023-06-12", "lower_window": 0, "upper_window": 9},
    {"holiday": "juguetes_verano", "ds": "2023-06-01", "lower_window": 0, "upper_window": 30},
    {"holiday": "dia_sin_iva_tecnologia", "ds": "2023-06-02", "lower_window": 0, "upper_window": 1},
    {"holiday": "tecnologia_ofertas", "ds": "2023-06-22", "lower_window": 0, "upper_window": 14},
    {"holiday": "regalos_profesores", "ds": "2023-06-01", "lower_window": 0, "upper_window": 15},
    {"holiday": "libros_bolsillo", "ds": "2023-06-15", "lower_window": 0, "upper_window": 5},
    {"holiday": "libros_infantiles_idiomas", "ds": "2023-06-23", "lower_window": 0, "upper_window": 5},
    #{"holiday": "hogar_cocinas", "ds": "2023-06-01", "lower_window": 0, "upper_window": 65},
    #JULIO 2023
    {"holiday": "segundas_rebajas_julio", "ds": "2023-07-06", "lower_window": 0, "upper_window": 13},
    {"holiday": "supertecnoprecios", "ds": "2023-07-07", "lower_window": 0, "upper_window": 4},
    {"holiday": "semana_deporte", "ds": "2023-07-13", "lower_window": 0, "upper_window": 6},
    {"holiday": "especial_baño", "ds": "2023-07-13", "lower_window": 0, "upper_window": 6},
    {"holiday": "rebaja_final", "ds": "2023-07-20", "lower_window": 0, "upper_window": 42},
    {"holiday": "electro_3_1", "ds": "2023-07-24", "lower_window": 0, "upper_window": 32},
    {"holiday": "electro_3_2", "ds": "2023-07-20", "lower_window": 0, "upper_window": 32},
    #AGOSTO 2023
    {"holiday": "libros_bolsillo", "ds": "2023-08-01", "lower_window": 0, "upper_window": 31},
    {"holiday": "limite_fase_1", "ds": "2023-08-03", "lower_window": 0, "upper_window": 3},
    {"holiday": "limite_fase_2", "ds": "2023-08-10", "lower_window": 0, "upper_window": 3},
    {"holiday": "limite_fase_3", "ds": "2023-08-17", "lower_window": 0, "upper_window": 3},
    {"holiday": "limite_fase_4", "ds": "2023-08-24", "lower_window": 0, "upper_window": 3},
    #SEPTIEMBRE 2023
    {"holiday": "supertecnoprecios", "ds": "2023-09-28", "lower_window": 0, "upper_window": 4},
    {"holiday": "dias_belleza", "ds": "2023-09-25", "lower_window": 0, "upper_window": 16},
    {"holiday": "semana_lenceria", "ds": "2023-09-28", "lower_window": 0, "upper_window": 17},
    {"holiday": "financiacion", "ds": "2023-09-28", "lower_window": 0, "upper_window": 6},
    #OCTUBRE 2023
    {"holiday": "8_dias_oro", "ds": "2023-10-19", "lower_window": 0, "upper_window": 17},
    {"holiday": "adelanto_1_black_friday", "ds": "2023-10-30", "lower_window": 0, "upper_window": 6},
    #NOVIEMBRE 2023
    {"holiday": "adelanto_2_black_friday", "ds": "2023-11-06", "lower_window": 0, "upper_window": 6},
    {"holiday": "adelanto_3_black_friday", "ds": "2023-11-13", "lower_window": 0, "upper_window": 6},
    {"holiday": "black_friday", "ds": "2023-11-20", "lower_window": 0, "upper_window": 6},
    {"holiday": "cyber_monday", "ds": "2023-11-27", "lower_window": 0, "upper_window": 0},
    {"holiday": "cheques_magicos", "ds": "2023-11-17", "lower_window": 0, "upper_window": 2},
    {"holiday": "wintersports", "ds": "2023-11-08", "lower_window": 0, "upper_window": 11},
    {"holiday": "navidad_hogar", "ds": "2023-11-09", "lower_window": 0, "upper_window": 31},
    #DICIEMBRE 2023
    {"holiday": "navidad_juguetes", "ds": "2023-12-01", "lower_window": 0, "upper_window": 31},
    {"holiday": "venta_privada", "ds": "2023-12-07", "lower_window": 0, "upper_window": 4},
    {"holiday": "lo_quiero", "ds": "2023-12-12", "lower_window": 0, "upper_window": 24},
    {"holiday": "feliz_año", "ds": "2023-12-26", "lower_window": 0, "upper_window": 10},
    #ENERO 2024
    {"holiday": "rebajas_enero", "ds": "2024-01-06", "lower_window": 0, "upper_window": 11},
    {"holiday": "blancolor", "ds": "2024-01-15", "lower_window": 0, "upper_window": 14},
    {"holiday": "segundas_rebajas_enero", "ds": "2024-01-18", "lower_window": 0, "upper_window": 13},
    {"holiday": "semana_deporte", "ds": "2024-01-25", "lower_window": 0, "upper_window": 6},
    #FEBRERO 2024
    {"holiday": "ofertas_limite_1", "ds": "2024-02-01", "lower_window": 0, "upper_window": 3},
    {"holiday": "ofertas_limite_2", "ds": "2024-02-08", "lower_window": 0, "upper_window": 3},
    {"holiday": "ofertas_limite_3", "ds": "2024-02-15", "lower_window": 0, "upper_window": 3},
    {"holiday": "ofertas_limite_4", "ds": "2024-02-22", "lower_window": 0, "upper_window": 3},
    {"holiday": "financiacion_total", "ds": "2024-02-15", "lower_window": 0, "upper_window": 6},
    {"holiday": "rebaja_final", "ds": "2024-02-15", "lower_window": 0, "upper_window": 14},
    {"holiday": "san_valentin", "ds": "2024-02-05", "lower_window": 0, "upper_window": 9},
    {"holiday": "mes_hogar", "ds": "2024-02-01", "lower_window": 0, "upper_window": 29},
    {"holiday": "aire_acondicionado", "ds": "2024-02-29", "lower_window": 0, "upper_window": 14},
    #MARZO 2024
    {"holiday": "dia_padre", "ds": "2024-03-11", "lower_window": 0, "upper_window": 8},
    {"holiday": "woman_sports", "ds": "2024-03-18", "lower_window": 0, "upper_window": 13},
    {"holiday": "semana_santa", "ds": "2024-03-17", "lower_window": 0, "upper_window": 7},
    {"holiday": "dia_comic", "ds": "2024-03-15", "lower_window": 0, "upper_window": 9},
    {"holiday": "dia_poesia", "ds": "2024-03-21", "lower_window": 0, "upper_window": 0},
    #ABRIL 2024
    {"holiday": "8_dias_oro", "ds": "2024-04-04", "lower_window": 0, "upper_window": 17},
    {"holiday": "smart_days", "ds": "2024-04-04", "lower_window": 0, "upper_window": 3},
    {"holiday": "supertecnoprecios", "ds": "2024-04-11", "lower_window": 0, "upper_window": 3},
    {"holiday": "dias_belleza", "ds": "2024-04-25", "lower_window": 0, "upper_window": 15},
    {"holiday": "dia_libro", "ds": "2024-04-23", "lower_window": 0, "upper_window": 0},
    {"holiday": "emidio_tucci", "ds": "2024-04-25", "lower_window": 0, "upper_window": 17},
    {"holiday": "summertime", "ds": "2024-04-25", "lower_window": 0, "upper_window": 35},
    {"holiday": "dia_madre", "ds": "2024-04-25", "lower_window": 0, "upper_window": 10},
    #MAYO 2024
    {"holiday": "dias_flash", "ds": "2024-05-08", "lower_window": 0, "upper_window": 9},
    {"holiday": "financiacion_total", "ds": "2024-05-27", "lower_window": 0, "upper_window": 6},
    {"holiday": "adelanto_eurocopa_1", "ds": "2024-05-13", "lower_window": 0, "upper_window": 8},
    {"holiday": "adelanto_eurocopa_2", "ds": "2024-05-27", "lower_window": 0, "upper_window": 6},
    {"holiday": "tecnologia", "ds": "2024-05-24", "lower_window": 0, "upper_window": 2},
    #JUNIO 2024
    {"holiday": "rebajas_junio", "ds": "2024-06-28", "lower_window": 0, "upper_window": 12},
    {"holiday": "venta_privada", "ds": "2024-06-06", "lower_window": 0, "upper_window": 4},
    {"holiday": "descuentos_top", "ds": "2024-06-11", "lower_window": 0, "upper_window": 16},
    {"holiday": "adelanto_eurocopa_3", "ds": "2024-06-03", "lower_window": 0, "upper_window": 9},
    {"holiday": "adelanto_eurocopa_4", "ds": "2024-06-17", "lower_window": 0, "upper_window": 5},
    #JULIO 2024
    {"holiday": "segundas_rebajas_julio", "ds": "2024-07-11", "lower_window": 0, "upper_window": 20},
    {"holiday": "supertecnoprecios", "ds": "2024-07-12", "lower_window": 0, "upper_window": 4},
    {"holiday": "semana_deporte", "ds": "2024-07-18", "lower_window": 0, "upper_window": 6},
    {"holiday": "semana_hogar", "ds": "2024-07-22", "lower_window": 0, "upper_window": 6},
    {"holiday": "semana_deporte", "ds": "2024-07-18", "lower_window": 0, "upper_window": 6},
    {"holiday": "smart_days", "ds": "2024-07-29", "lower_window": 0, "upper_window": 2},
    #AGOSTO 2024
    {"holiday": "rebaja_final", "ds": "2024-08-01", "lower_window": 0, "upper_window": 31},
    {"holiday": "ofertas_limite_1", "ds": "2024-08-01", "lower_window": 0, "upper_window": 3},
    {"holiday": "ofertas_limite_2", "ds": "2024-08-08", "lower_window": 0, "upper_window": 3},
    {"holiday": "ofertas_limite_3", "ds": "2024-08-15", "lower_window": 0, "upper_window": 3},
    {"holiday": "ofertas_limite_4", "ds": "2024-08-22", "lower_window": 0, "upper_window": 3},
    {"holiday": "electro_3_1", "ds": "2023-08-05", "lower_window": 0, "upper_window": 2},
    {"holiday": "electro_3_2", "ds": "2023-08-12", "lower_window": 0, "upper_window": 2},
    {"holiday": "electro_3_3", "ds": "2023-08-19", "lower_window": 0, "upper_window": 2},
    {"holiday": "remate_final_hogar", "ds": "2025-08-26", "lower_window": 0, "upper_window": 5},
    #SEPTIEMBRE 2024
    {"holiday": "supertecnoprecios", "ds": "2025-09-12", "lower_window": 0, "upper_window": 3},
    {"holiday": "feria_bebe", "ds": "2025-09-16", "lower_window": 0, "upper_window": 27},
    {"holiday": "dias_belleza", "ds": "2025-09-26", "lower_window": 0, "upper_window": 10},
    {"holiday": "semana_lenceria", "ds": "2025-09-26", "lower_window": 0, "upper_window": 10},
    {"holiday": "financiacion", "ds": "2025-09-26", "lower_window": 0, "upper_window": 7},
    #OCTUBRE 2024
    {"holiday": "emidio_tucci", "ds": "2025-10-11", "lower_window": 0, "upper_window": 16},
    {"holiday": "tecnoprecios", "ds": "2025-10-07", "lower_window": 0, "upper_window": 16},
    {"holiday": "8_dias_oro", "ds": "2025-10-17", "lower_window": 0, "upper_window": 17},
    {"holiday": "supertecnoprecios", "ds": "2025-10-24", "lower_window": 0, "upper_window": 3},
    #NOVIEMBRE 2024
    {"holiday": "emidio_tucci", "ds": "2025-10-11", "lower_window": 0, "upper_window": 16},
    {"holiday": "adelanto_1_black_friday", "ds": "2024-11-04", "lower_window": 0, "upper_window": 6},
    {"holiday": "adelanto_2_black_friday", "ds": "2024-11-11", "lower_window": 0, "upper_window": 6},
    {"holiday": "adelanto_3_black_friday", "ds": "2024-11-18", "lower_window": 0, "upper_window": 6},
    {"holiday": "black_friday", "ds": "2024-11-25", "lower_window": 0, "upper_window": 6},
    {"holiday": "navidad_hogar", "ds": "2024-11-06", "lower_window": 0, "upper_window": 18},
    {"holiday": "dia_shopping", "ds": "2024-11-08", "lower_window": 0, "upper_window": 3},
    {"holiday": "navidad_juguetes", "ds": "2024-11-04", "lower_window": 0, "upper_window": 23},
    #DICIEMBRE 2024
    {"holiday": "cyber_monday", "ds": "2024-12-02", "lower_window": 0, "upper_window": 1},
    {"holiday": "venta_privada", "ds": "2024-12-12", "lower_window": 0, "upper_window": 4},
    {"holiday": "lo_quiero", "ds": "2024-12-17", "lower_window": 0, "upper_window": 19},
    {"holiday": "cheques_magicos", "ds": "2024-12-04", "lower_window": 0, "upper_window": 2},
    {"holiday": "tecnoprecios", "ds": "2024-12-03", "lower_window": 0, "upper_window": 12},
    {"holiday": "supertecnoprecios", "ds": "2024-12-19", "lower_window": 0, "upper_window": 3},
    {"holiday": "feliz_año", "ds": "2024-12-26", "lower_window": 0, "upper_window": 10},
    #ENERO 2025
    {"holiday": "rebajas_enero", "ds": "2025-01-07", "lower_window": 0, "upper_window": 52},
    {"holiday": "dia_sin_iva", "ds": "2025-01-19", "lower_window": 0, "upper_window": 0},
    {"holiday": "semana_deporte", "ds": "2025-01-23", "lower_window": 0, "upper_window": 6},
    {"holiday": "blancolor", "ds": "2025-01-13", "lower_window": 0, "upper_window": 46},
    #FEBRERO 2025
    {"holiday": "limite_48_horas", "ds": "2025-02-06", "lower_window": 0, "upper_window": 3},
    {"holiday": "ofertas_limite", "ds": "2025-02-20", "lower_window": 0, "upper_window": 3},
    {"holiday": "semana_telefonia", "ds": "2025-02-20", "lower_window": 0, "upper_window": 6},
    {"holiday": "20_fotografia", "ds": "2025-02-20", "lower_window": 0, "upper_window": 3},
    #MARZO 2025
    {"holiday": "tecnoprecios", "ds": "2025-03-13", "lower_window": 0, "upper_window": 13},
    {"holiday": "supertecnoprecios", "ds": "2025-03-26", "lower_window": 0, "upper_window": 4},
    #ABRIL 2025
    {"holiday": "8_dias_oro", "ds": "2025-04-03", "lower_window": 0, "upper_window": 10},
    {"holiday": "supertecnoprecios", "ds": "2025-04-24", "lower_window": 0, "upper_window": 3},
    {"holiday": "dias_belleza", "ds": "2025-04-24", "lower_window": 0, "upper_window": 15},
    #MAYO 2025
    {"holiday": "ofertas_flash", "ds": "2025-05-08", "lower_window": 0, "upper_window": 3},
    {"holiday": "semana_internet", "ds": "2025-05-12", "lower_window": 0, "upper_window": 6},
    {"holiday": "supertecnoprecios", "ds": "2025-05-22", "lower_window": 0, "upper_window": 3},
    {"holiday": "financiacion_total", "ds": "2025-05-26", "lower_window": 0, "upper_window": 9},
    {"holiday": "tecnoprecios", "ds": "2025-05-26", "lower_window": 0, "upper_window": 9},
    {"holiday": "samsung_days", "ds": "2025-05-29", "lower_window": 0, "upper_window": 3},
    #JUNIO 2025
    {"holiday": "ventas_privadas", "ds": "2025-06-05", "lower_window": 0, "upper_window": 4},
    {"holiday": "dias_sin_iva", "ds": "2025-06-13", "lower_window": 0, "upper_window": 2},
    {"holiday": "descuentos_top", "ds": "2025-06-10", "lower_window": 0, "upper_window": 16},
    {"holiday": "rebajas_junio", "ds": "2025-06-27", "lower_window": 0, "upper_window": 65},
    {"holiday": "vuelta_al_cole_julio", "ds": "2025-06-19", "lower_window": 0, "upper_window": 42},
    {"holiday": "yellow_days", "ds": "2025-06-19", "lower_window": 0, "upper_window":7},
    {"holiday": "discos", "ds": "2025-06-19", "lower_window": 0, "upper_window": 3},
    {"holiday": "tecnoprecios", "ds": "2025-06-27", "lower_window": 0, "upper_window": 13},
    #JULIO 2025
    {"holiday": "segundas_rebajas_julio", "ds": "2025-07-14", "lower_window": 0, "upper_window": 17},
    {"holiday": "ad", "ds": "2025-07-14", "lower_window": 0, "upper_window": 17},
    {"holiday": "supertecnoprecios", "ds": "2025-07-11", "lower_window": 0, "upper_window": 4},
    {"holiday": "semana_deporte", "ds": "2025-07-17", "lower_window": 0, "upper_window": 6},
    {"holiday": "especial_baño", "ds": "2025-07-14", "lower_window": 0, "upper_window": 6},
    #AGOSTO 2025
    {"holiday": "rebajas_agosto", "ds": "2025-08-01", "lower_window": 0, "upper_window": 31},
    {"holiday": "limite_fase_1", "ds": "2025-07-31", "lower_window": 0, "upper_window": 8},
    {"holiday": "limite_fase_2", "ds": "2025-08-07", "lower_window": 0, "upper_window": 3},
    {"holiday": "limite_fase_3", "ds": "2025-08-21", "lower_window": 0, "upper_window": 3},
    {"holiday": "limite_fase_4", "ds": "2025-08-28", "lower_window": 0, "upper_window": 3},
    {"holiday": "electro_3_1", "ds": "2025-08-04", "lower_window": 0, "upper_window": 3},
    {"holiday": "parafarmacia", "ds": "2025-08-06", "lower_window": 0, "upper_window": 2},
    {"holiday": "remate_final_hogar", "ds": "2025-08-25", "lower_window": 0, "upper_window": 6},
    {"holiday": "agosto_smart_days", "ds": "2025-08-14", "lower_window": 0, "upper_window": 3},
    {"holiday": "mes_descanso", "ds": "2025-08-08", "lower_window": 0, "upper_window": 23},
    {"holiday": "electro_3_2", "ds": "2025-08-22", "lower_window": 0, "upper_window": 2},
    {"holiday": "university", "ds": "2025-08-21", "lower_window": 0, "upper_window": 17},
    #SEPTIEMBRE 2025
    {"holiday": "tecnoprecios", "ds": "2025-09-08", "lower_window": 0, "upper_window": 9},
    {"holiday": "feria_bebe", "ds": "2025-09-15", "lower_window": 0, "upper_window": 27},
    {"holiday": "supertecnoprecios", "ds": "2025-09-18", "lower_window": 0, "upper_window": 3},
    {"holiday": "colchones", "ds": "2025-09-18", "lower_window": 0, "upper_window": 17},
    {"holiday": "vuelta_al_cole_septiembre", "ds": "2025-09-01", "lower_window": 0, "upper_window": 30},
    {"holiday": "financiacion", "ds": "2025-09-22", "lower_window": 0, "upper_window": 10},
    {"holiday": "dias_belleza", "ds": "2025-09-25", "lower_window": 0, "upper_window": 13},
    {"holiday": "semana_lenceria", "ds": "2025-09-25", "lower_window": 0, "upper_window": 10},
    #OCTUBRE 2025
    {"holiday": "dia_sin_iva", "ds": "2025-10-03", "lower_window": 0, "upper_window": 2},
    {"holiday": "tecnoprecios", "ds": "2025-10-06", "lower_window": 0, "upper_window": 16},
    {"holiday": "emidio_tucci", "ds": "2025-10-08", "lower_window": 0, "upper_window": 23},
    {"holiday": "8_dias_oro", "ds": "2025-10-16", "lower_window": 0, "upper_window": 17},
    {"holiday": "cancer_mama", "ds": "2025-10-19", "lower_window": 0, "upper_window": 0},
    {"holiday": "supertecnoprecios", "ds": "2025-10-27", "lower_window": 0, "upper_window": 3},
    {"holiday": "tecnoprecios", "ds": "2025-10-23", "lower_window": 0, "upper_window": 6},
    {"holiday": "navidad_hogar", "ds": "2025-10-28", "lower_window": 0, "upper_window": 45},
    #NOVIEMBRE 2025
    {"holiday": "navidad_juguetes", "ds": "2025-11-03", "lower_window": 0, "upper_window": 23},
    {"holiday": "black_friday", "ds": "2025-11-24", "lower_window": 0, "upper_window": 6},
    {"holiday": "adelanto_1_black_friday", "ds": "2025-11-03", "lower_window": 0, "upper_window": 6},
    {"holiday": "adelanto_2_black_friday", "ds": "2025-11-10", "lower_window": 0, "upper_window": 6},
    {"holiday": "adelanto_3_black_friday", "ds": "2025-11-17", "lower_window": 0, "upper_window": 6},
    #DICIEMBRE 2025
    {"holiday": "cyber_monday", "ds": "2025-12-01", "lower_window": 0, "upper_window": 0},
    {"holiday": "cheques_magicos", "ds": "2025-12-04", "lower_window": 0, "upper_window": 32},
    {"holiday": "ventas_privadas", "ds": "2025-12-11", "lower_window": 0, "upper_window": 4},
    {"holiday": "supertecnoprecios", "ds": "2025-12-18", "lower_window": 0, "upper_window": 5},
    {"holiday": "feliz_año", "ds": "2025-12-29", "lower_window": 0, "upper_window": 10},
    #ENERO 2026
    {"holiday": "rebajas_enero", "ds": "2026-01-07", "lower_window": 0, "upper_window": 52},
    {"holiday": "ofertas_informaticas", "ds": "2026-01-07", "lower_window": 0, "upper_window": 14},
    {"holiday": "blancolor", "ds": "2026-01-08", "lower_window": 0, "upper_window": 51},
    {"holiday": "limpieza_perfumeria", "ds": "2026-01-07", "lower_window": 0, "upper_window": 21},
    {"holiday": "segundas_rebajas_enero", "ds": "2026-01-15", "lower_window": 0, "upper_window": 13},
    {"holiday": "adicional", "ds": "2026-01-15", "lower_window": 0, "upper_window": 13},
    {"holiday": "dia_sin_iva", "ds": "2026-01-22", "lower_window": 0, "upper_window": 3},
    {"holiday": "semana_deporte", "ds": "2026-01-22", "lower_window": 0, "upper_window": 6},
    #FEBRERO 2026
    {"holiday": "ofertas_limite_1", "ds": "2026-01-29", "lower_window": 0, "upper_window": 3},
    {"holiday": "ofertas_limite_2", "ds": "2026-02-05", "lower_window": 0, "upper_window": 3},
    {"holiday": "ofertas_limite_3", "ds": "2026-02-12", "lower_window": 0, "upper_window": 3},
    {"holiday": "ofertas_limite_4", "ds": "2026-02-19", "lower_window": 0, "upper_window": 3},
    {"holiday": "remate_final_hogar", "ds": "2026-02-23", "lower_window": 0, "upper_window": 5},
    #MARZO 2026
    {"holiday": "aire_acondicionado", "ds": "2026-03-05", "lower_window": 0, "upper_window": 17},
    {"holiday": "tecnoprecios_apple", "ds": "2026-03-10", "lower_window": 0, "upper_window": 9},
    {"holiday": "wake_up_make_up", "ds": "2026-03-05", "lower_window": 0, "upper_window": 10},
    {"holiday": "baby_news", "ds": "2026-03-12", "lower_window": 0, "upper_window": 17},
    {"holiday": "tecnoprecios", "ds": "2026-03-19", "lower_window": 0, "upper_window": 3},
    #ABRIL 2026
    {"holiday": "8_dias_oro", "ds": "2026-04-09", "lower_window": 0, "upper_window": 10},
    {"holiday": "happy_days", "ds": "2026-04-14", "lower_window": 0, "upper_window": 1},
    {"holiday": "dia_libro", "ds": "2026-04-23", "lower_window": 0, "upper_window": 0},
    {"holiday": "supertecnoprecios", "ds": "2026-04-23", "lower_window": 0, "upper_window": 3},
    {"holiday": "dias_belleza", "ds": "2026-04-23", "lower_window": 0, "upper_window": 15},
    {"holiday": "dia_niño", "ds": "2026-04-26", "lower_window": 0, "upper_window": 0},
    #MAYO 2026
    {"holiday": "semana_internet", "ds": "2026-05-11", "lower_window": 0, "upper_window": 6},
    {"holiday": "aire_acondicionado", "ds": "2026-05-07", "lower_window": 0, "upper_window":17},
    {"holiday": "tv_video", "ds": "2026-05-01", "lower_window": 0, "upper_window": 20},
    {"holiday": "juguetes", "ds": "2026-05-01", "lower_window": 0, "upper_window": 31},
    {"holiday": "medias_verano", "ds": "2026-04-30", "lower_window": 0, "upper_window": 18},
    {"holiday": "dia_sin_iva", "ds": "2026-05-21", "lower_window": 0, "upper_window": 3},
    #JUNIO 2026
    {"holiday": "financiacion", "ds": "2026-05-21", "lower_window": 0, "upper_window": 13},
    {"holiday": "colchones", "ds": "2026-05-21", "lower_window": 0, "upper_window": 18},
    {"holiday": "lotes_person", "ds": "2026-05-27", "lower_window": 0, "upper_window": 14},
    {"holiday": "summertime", "ds": "2026-06-01", "lower_window": 0, "upper_window": 30},
    {"holiday": "supertecnoprecios", "ds": "2026-06-04", "lower_window": 0, "upper_window": 3},
    {"holiday": "google_days", "ds": "2026-06-04", "lower_window": 0, "upper_window": 6},
    {"holiday": "aire_acondicionado", "ds": "2026-06-04", "lower_window": 0, "upper_window": 13},
    {"holiday": "solares_avene", "ds": "2026-06-05", "lower_window": 0, "upper_window": 7},
    {"holiday": "wake_up_make_up", "ds": "2026-06-10", "lower_window": 0, "upper_window": 4},
    {"holiday": "ventas_privadas", "ds": "2026-06-11", "lower_window": 0, "upper_window": 4},
    {"holiday": "deportes_tecnologia_alimentacion", "ds": "2026-06-11", "lower_window": 0, "upper_window": 8},
    {"holiday": "descuentos_top", "ds": "2026-06-16", "lower_window": 0, "upper_window": 8},
    #HASTA CUANDO ES LA VUELTA AL COLE
    {"holiday": "vuelta_al_cole", "ds": "2026-06-18", "lower_window": 0, "upper_window": 65},
    {"holiday": "discos", "ds": "2026-06-18", "lower_window": 0, "upper_window": 3},
    {"holiday": "colchones_bases", "ds": "2026-06-18", "lower_window": 0, "upper_window": 12},
    {"holiday": "rebajas_junio", "ds": "2026-06-18", "lower_window": 0, "upper_window": 13},
    
])
'''

# PARA QUE NO SE SUMEN LOS DÍAS QUE HAY PROMOCIÓN: 

promociones = [
    # ENERO 2023
    {"inicio": "2022-12-25", "fin": "2023-01-05"}, # feliz_año
    {"inicio": "2023-01-19", "fin": "2023-01-28"}, # blancolor
    {"inicio": "2022-12-26", "fin": "2023-01-05"}, # reyes_tecnologia
    {"inicio": "2023-01-06", "fin": "2023-01-18"}, # rebajas_enero
    {"inicio": "2023-01-07", "fin": "2023-01-31"}, # tecnoprecios
    {"inicio": "2023-01-19", "fin": "2023-02-02"}, # segundas_rebajas_enero
    {"inicio": "2023-01-27", "fin": "2023-02-20"}, # feria_artesania
    {"inicio": "2023-01-26", "fin": "2023-02-02"}, # semana_deporte
    
    # FEBRERO 2023
    {"inicio": "2023-02-02", "fin": "2023-02-28"}, # rebaja_final
    {"inicio": "2023-02-02", "fin": "2023-02-14"}, # san_valentin
    {"inicio": "2023-02-02", "fin": "2023-02-05"}, # ofertas_limite_1
    {"inicio": "2023-02-09", "fin": "2023-02-12"}, # ofertas_limite_2
    {"inicio": "2023-02-16", "fin": "2023-02-19"}, # ofertas_limite_3
    {"inicio": "2023-02-23", "fin": "2023-02-26"}, # ofertas_limite_4
    {"inicio": "2023-02-16", "fin": "2023-02-22"}, # financiaciacion_total
    {"inicio": "2023-02-24", "fin": "2023-03-12"}, # tecnoprecios
    {"inicio": "2023-02-23", "fin": "2023-03-15"}, # aire_acondicionado
    
    # MARZO 2023
    {"inicio": "2023-03-09", "fin": "2023-03-22"}, # tecnoprecios
    {"inicio": "2023-03-02", "fin": "2023-03-31"}, # feria_alimentacion
    {"inicio": "2023-03-10", "fin": "2023-04-02"}, # hogar_baby
    {"inicio": "2023-03-09", "fin": "2023-03-19"}, # especial_deportes
    {"inicio": "2023-03-09", "fin": "2023-03-19"}, # dia_padre
    {"inicio": "2023-03-23", "fin": "2023-04-13"}, # primavera
    {"inicio": "2023-03-16", "fin": "2023-04-02"}, # descuentos_top
    {"inicio": "2023-03-23", "fin": "2023-03-29"}, # tecnoprecios
    {"inicio": "2023-03-21", "fin": "2023-03-21"}, # dia_poesia
    
    # ABRIL 2023
    {"inicio": "2023-04-01", "fin": "2023-05-01"}, # cocinas
    {"inicio": "2023-04-02", "fin": "2023-04-02"}, # dia_libro_juvenil
    {"inicio": "2023-04-10", "fin": "2023-04-19"}, # aire_acondicionado
    {"inicio": "2023-04-11", "fin": "2023-04-30"}, # emidio_tucci
    {"inicio": "2023-04-13", "fin": "2023-04-23"}, # 8_dias_oro
    {"inicio": "2023-04-13", "fin": "2023-04-30"}, # 8_dias_oro_hogar
    {"inicio": "2023-04-20", "fin": "2023-05-03"}, # tecnoprecios
    {"inicio": "2023-04-22", "fin": "2023-04-25"}, # dia_libro
    {"inicio": "2023-04-24", "fin": "2023-05-09"}, # dias_belleza
    {"inicio": "2023-04-24", "fin": "2023-05-04"}, # dia_madre
    
    # MAYO 2023
    {"inicio": "2023-05-08", "fin": "2023-05-17"}, # semana_internet
    {"inicio": "2023-05-25", "fin": "2023-06-02"}, # financiacion_total
    {"inicio": "2023-05-04", "fin": "2023-05-17"}, # tecnoprecios
    {"inicio": "2023-05-18", "fin": "2023-05-21"}, # supertecnoprecios
    {"inicio": "2023-05-22", "fin": "2023-06-07"}, # tecnoprecios
    {"inicio": "2023-05-15", "fin": "2023-06-08"}, # mes_friki
    {"inicio": "2023-05-18", "fin": "2023-05-31"}, # cuidado_bienestar
    {"inicio": "2023-05-01", "fin": "2023-06-01"}, # comuniones
    {"inicio": "2023-05-18", "fin": "2023-06-07"}, # deportes_outdoor
    
    # JUNIO 2023
    {"inicio": "2023-06-08", "fin": "2023-06-11"}, # venta_privada
    {"inicio": "2023-06-22", "fin": "2023-07-05"}, # rebajas_junio
    {"inicio": "2023-06-12", "fin": "2023-06-21"}, # descuentos_top
    {"inicio": "2023-06-01", "fin": "2023-07-01"}, # juguetes_verano
    {"inicio": "2023-06-02", "fin": "2023-06-03"}, # dia_sin_iva_tecnologia
    {"inicio": "2023-06-22", "fin": "2023-07-06"}, # tecnologia_ofertas
    {"inicio": "2023-06-01", "fin": "2023-06-16"}, # regalos_profesores
    {"inicio": "2023-06-15", "fin": "2023-06-20"}, # libros_bolsillo
    {"inicio": "2023-06-23", "fin": "2023-06-28"}, # libros_infantiles_idiomas
    
    # JULIO 2023
    {"inicio": "2023-07-06", "fin": "2023-07-19"}, # segundas_rebajas_julio
    {"inicio": "2023-07-07", "fin": "2023-07-11"}, # supertecnoprecios
    {"inicio": "2023-07-13", "fin": "2023-07-19"}, # semana_deporte
    {"inicio": "2023-07-13", "fin": "2023-07-19"}, # especial_baño
    {"inicio": "2023-07-20", "fin": "2023-08-31"}, # rebaja_final
    {"inicio": "2023-07-24", "fin": "2023-08-25"}, # electro_3_1
    {"inicio": "2023-07-20", "fin": "2023-08-21"}, # electro_3_2
    
    # AGOSTO 2023
    {"inicio": "2023-08-01", "fin": "2023-09-01"}, # libros_bolsillo
    {"inicio": "2023-08-03", "fin": "2023-08-06"}, # limite_fase_1
    {"inicio": "2023-08-10", "fin": "2023-08-13"}, # limite_fase_2
    {"inicio": "2023-08-17", "fin": "2023-08-20"}, # limite_fase_3
    {"inicio": "2023-08-24", "fin": "2023-08-27"}, # limite_fase_4
    {"inicio": "2023-08-05", "fin": "2023-08-07"}, # electro_3_1
    {"inicio": "2023-08-12", "fin": "2023-08-14"}, # electro_3_2
    {"inicio": "2023-08-19", "fin": "2023-08-21"}, # electro_3_3
    
    # SEPTIEMBRE 2023
    {"inicio": "2023-09-28", "fin": "2023-10-02"}, # supertecnoprecios
    {"inicio": "2023-09-25", "fin": "2023-10-11"}, # dias_belleza
    {"inicio": "2023-09-28", "fin": "2023-10-15"}, # semana_lenceria
    {"inicio": "2023-09-28", "fin": "2023-10-04"}, # financiacion
    
    # OCTUBRE 2023
    {"inicio": "2023-10-19", "fin": "2023-11-05"}, # 8_dias_oro
    {"inicio": "2023-10-30", "fin": "2023-11-05"}, # adelanto_1_black_friday
    
    # NOVIEMBRE 2023
    {"inicio": "2023-11-06", "fin": "2023-11-12"}, # adelanto_2_black_friday
    {"inicio": "2023-11-13", "fin": "2023-11-19"}, # adelanto_3_black_friday
    {"inicio": "2023-11-20", "fin": "2023-11-26"}, # black_friday
    {"inicio": "2023-11-27", "fin": "2023-11-27"}, # cyber_monday
    {"inicio": "2023-11-17", "fin": "2023-11-19"}, # cheques_magicos
    {"inicio": "2023-11-08", "fin": "2023-11-19"}, # wintersports
    {"inicio": "2023-11-09", "fin": "2023-12-10"}, # navidad_hogar
    
    # DICIEMBRE 2023
    {"inicio": "2023-12-01", "fin": "2024-01-01"}, # navidad_juguetes
    {"inicio": "2023-12-07", "fin": "2023-12-11"}, # venta_privada
    {"inicio": "2023-12-12", "fin": "2024-01-05"}, # lo_quiero
    {"inicio": "2023-12-26", "fin": "2024-01-05"}, # feliz_año
    
    # ENERO 2024
    {"inicio": "2024-01-06", "fin": "2024-01-17"}, # rebajas_enero
    {"inicio": "2024-01-15", "fin": "2024-01-29"}, # blancolor
    {"inicio": "2024-01-18", "fin": "2024-01-31"}, # segundas_rebajas_enero
    {"inicio": "2024-01-25", "fin": "2024-01-31"}, # semana_deporte
    
    # FEBRERO 2024
    {"inicio": "2024-02-01", "fin": "2024-02-04"}, # ofertas_limite_1
    {"inicio": "2024-02-08", "fin": "2024-02-11"}, # ofertas_limite_2
    {"inicio": "2024-02-15", "fin": "2024-02-18"}, # ofertas_limite_3
    {"inicio": "2024-02-22", "fin": "2024-02-25"}, # ofertas_limite_4
    {"inicio": "2024-02-15", "fin": "2024-02-21"}, # financiacion_total
    {"inicio": "2024-02-15", "fin": "2024-02-29"}, # rebaja_final
    {"inicio": "2024-02-05", "fin": "2024-02-14"}, # san_valentin
    {"inicio": "2024-02-01", "fin": "2024-03-01"}, # mes_hogar
    {"inicio": "2024-02-29", "fin": "2024-03-14"}, # aire_acondicionado
    
    # MARZO 2024
    {"inicio": "2024-03-11", "fin": "2024-03-19"}, # dia_padre
    {"inicio": "2024-03-18", "fin": "2024-03-31"}, # woman_sports
    {"inicio": "2024-03-17", "fin": "2024-03-24"}, # semana_santa
    {"inicio": "2024-03-15", "fin": "2024-03-24"}, # dia_comic
    {"inicio": "2024-03-21", "fin": "2024-03-21"}, # dia_poesia
    
    # ABRIL 2024
    {"inicio": "2024-04-04", "fin": "2024-04-21"}, # 8_dias_oro
    {"inicio": "2024-04-04", "fin": "2024-04-07"}, # smart_days
    {"inicio": "2024-04-11", "fin": "2024-04-14"}, # supertecnoprecios
    {"inicio": "2024-04-25", "fin": "2024-05-10"}, # dias_belleza
    {"inicio": "2024-04-23", "fin": "2024-04-23"}, # dia_libro
    {"inicio": "2024-04-25", "fin": "2024-05-12"}, # emidio_tucci
    {"inicio": "2024-04-25", "fin": "2024-05-30"}, # summertime
    {"inicio": "2024-04-25", "fin": "2024-05-05"}, # dia_madre
    
    # MAYO 2024
    {"inicio": "2024-05-08", "fin": "2024-05-17"}, # dias_flash
    {"inicio": "2024-05-27", "fin": "2024-06-02"}, # financiacion_total
    {"inicio": "2024-05-13", "fin": "2024-05-21"}, # adelanto_eurocopa_1
    {"inicio": "2024-05-27", "fin": "2024-06-02"}, # adelanto_eurocopa_2
    {"inicio": "2024-05-24", "fin": "2024-05-26"}, # tecnologia
    
    # JUNIO 2024
    {"inicio": "2024-06-28", "fin": "2024-07-10"}, # rebajas_junio
    {"inicio": "2024-06-06", "fin": "2024-06-10"}, # venta_privada
    {"inicio": "2024-06-11", "fin": "2024-06-27"}, # descuentos_top
    {"inicio": "2024-06-03", "fin": "2024-06-12"}, # adelanto_eurocopa_3
    {"inicio": "2024-06-17", "fin": "2024-06-22"}, # adelanto_eurocopa_4
    
    # JULIO 2024
    {"inicio": "2024-07-11", "fin": "2024-07-31"}, # segundas_rebajas_julio
    {"inicio": "2024-07-12", "fin": "2024-07-16"}, # supertecnoprecios
    {"inicio": "2024-07-18", "fin": "2024-07-24"}, # semana_deporte
    {"inicio": "2024-07-22", "fin": "2024-07-28"}, # semana_hogar
    {"inicio": "2024-07-29", "fin": "2024-07-31"}, # smart_days
    
    # AGOSTO 2024
    {"inicio": "2024-08-01", "fin": "2024-09-01"}, # rebaja_final
    {"inicio": "2024-08-01", "fin": "2024-08-04"}, # ofertas_limite_1
    {"inicio": "2024-08-08", "fin": "2024-08-11"}, # ofertas_limite_2
    {"inicio": "2024-08-15", "fin": "2024-08-18"}, # ofertas_limite_3
    {"inicio": "2024-08-22", "fin": "2024-08-25"}, # ofertas_limite_4
    
    # SEPTIEMBRE 2024 (Se ajustan los años a partir de aquí basándome en tus datos)
    {"inicio": "2025-08-26", "fin": "2025-08-31"}, # remate_final_hogar
    {"inicio": "2025-09-12", "fin": "2025-09-15"}, # supertecnoprecios
    {"inicio": "2025-09-16", "fin": "2025-10-13"}, # feria_bebe
    {"inicio": "2025-09-26", "fin": "2025-10-06"}, # dias_belleza
    {"inicio": "2025-09-26", "fin": "2025-10-06"}, # semana_lenceria
    {"inicio": "2025-09-26", "fin": "2025-10-03"}, # financiacion
    
    # OCTUBRE 2024
    {"inicio": "2025-10-11", "fin": "2025-10-27"}, # emidio_tucci
    {"inicio": "2025-10-07", "fin": "2025-10-23"}, # tecnoprecios
    {"inicio": "2025-10-17", "fin": "2025-11-03"}, # 8_dias_oro
    {"inicio": "2025-10-24", "fin": "2025-10-27"}, # supertecnoprecios
    
    # NOVIEMBRE 2024
    {"inicio": "2024-11-04", "fin": "2024-11-10"}, # adelanto_1_black_friday
    {"inicio": "2024-11-11", "fin": "2024-11-17"}, # adelanto_2_black_friday
    {"inicio": "2024-11-18", "fin": "2024-11-24"}, # adelanto_3_black_friday
    {"inicio": "2024-11-25", "fin": "2024-12-01"}, # black_friday
    {"inicio": "2024-11-06", "fin": "2024-11-24"}, # navidad_hogar
    {"inicio": "2024-11-08", "fin": "2024-11-11"}, # dia_shopping
    {"inicio": "2024-11-04", "fin": "2024-11-27"}, # navidad_juguetes
    
    # DICIEMBRE 2024
    {"inicio": "2024-12-02", "fin": "2024-12-03"}, # cyber_monday
    {"inicio": "2024-12-12", "fin": "2024-12-16"}, # venta_privada
    {"inicio": "2024-12-17", "fin": "2025-01-05"}, # lo_quiero
    {"inicio": "2024-12-04", "fin": "2024-12-06"}, # cheques_magicos
    {"inicio": "2024-12-03", "fin": "2024-12-15"}, # tecnoprecios
    {"inicio": "2024-12-19", "fin": "2024-12-22"}, # supertecnoprecios
    {"inicio": "2024-12-26", "fin": "2025-01-05"}, # feliz_año
    
    # ENERO 2025
    {"inicio": "2025-01-07", "fin": "2025-02-28"}, # rebajas_enero
    {"inicio": "2025-01-19", "fin": "2025-01-19"}, # dia_sin_iva
    {"inicio": "2025-01-23", "fin": "2025-01-29"}, # semana_deporte
    {"inicio": "2025-01-13", "fin": "2025-02-28"}, # blancolor
    
    # FEBRERO 2025
    {"inicio": "2025-02-06", "fin": "2025-02-09"}, # limite_48_horas
    {"inicio": "2025-02-20", "fin": "2025-02-23"}, # ofertas_limite
    {"inicio": "2025-02-20", "fin": "2025-02-26"}, # semana_telefonia
    {"inicio": "2025-02-20", "fin": "2025-02-23"}, # 20_fotografia
    
    # MARZO 2025
    {"inicio": "2025-03-13", "fin": "2025-03-26"}, # tecnoprecios
    {"inicio": "2025-03-26", "fin": "2025-03-30"}, # supertecnoprecios
    
    # ABRIL 2025
    {"inicio": "2025-04-03", "fin": "2025-04-13"}, # 8_dias_oro
    {"inicio": "2025-04-24", "fin": "2025-04-27"}, # supertecnoprecios
    {"inicio": "2025-04-24", "fin": "2025-05-09"}, # dias_belleza
    
    # MAYO 2025
    {"inicio": "2025-05-08", "fin": "2025-05-11"}, # ofertas_flash
    {"inicio": "2025-05-12", "fin": "2025-05-18"}, # semana_internet
    {"inicio": "2025-05-22", "fin": "2025-05-25"}, # supertecnoprecios
    {"inicio": "2025-05-26", "fin": "2025-06-04"}, # financiacion_total
    {"inicio": "2025-05-26", "fin": "2025-06-04"}, # tecnoprecios
    {"inicio": "2025-05-29", "fin": "2025-06-01"}, # samsung_days
    
    # JUNIO 2025
    {"inicio": "2025-06-05", "fin": "2025-06-09"}, # ventas_privadas
    {"inicio": "2025-06-13", "fin": "2025-06-15"}, # dias_sin_iva
    {"inicio": "2025-06-10", "fin": "2025-06-26"}, # descuentos_top
    {"inicio": "2025-06-27", "fin": "2025-08-31"}, # rebajas_junio
    {"inicio": "2025-06-19", "fin": "2025-07-31"}, # vuelta_al_cole_julio
    {"inicio": "2025-06-19", "fin": "2025-06-26"}, # yellow_days
    {"inicio": "2025-06-19", "fin": "2025-06-22"}, # discos
    {"inicio": "2025-06-27", "fin": "2025-07-10"}, # tecnoprecios
    
    # JULIO 2025
    {"inicio": "2025-07-14", "fin": "2025-07-31"}, # segundas_rebajas_julio
    {"inicio": "2025-07-14", "fin": "2025-07-31"}, # ad
    {"inicio": "2025-07-11", "fin": "2025-07-15"}, # supertecnoprecios
    {"inicio": "2025-07-17", "fin": "2025-07-23"}, # semana_deporte
    {"inicio": "2025-07-14", "fin": "2025-07-20"}, # especial_baño
    
    # AGOSTO 2025
    {"inicio": "2025-08-01", "fin": "2025-09-01"}, # rebajas_agosto
    {"inicio": "2025-07-31", "fin": "2025-08-08"}, # limite_fase_1
    {"inicio": "2025-08-07", "fin": "2025-08-10"}, # limite_fase_2
    {"inicio": "2025-08-21", "fin": "2025-08-24"}, # limite_fase_3
    {"inicio": "2025-08-28", "fin": "2025-08-31"}, # limite_fase_4
    {"inicio": "2025-08-04", "fin": "2025-08-07"}, # electro_3_1
    {"inicio": "2025-08-06", "fin": "2025-08-08"}, # parafarmacia
    {"inicio": "2025-08-25", "fin": "2025-08-31"}, # remate_final_hogar
    {"inicio": "2025-08-14", "fin": "2025-08-17"}, # agosto_smart_days
    {"inicio": "2025-08-08", "fin": "2025-08-31"}, # mes_descanso
    {"inicio": "2025-08-22", "fin": "2025-08-24"}, # electro_3_2
    {"inicio": "2025-08-21", "fin": "2025-09-07"}, # university
    
    # SEPTIEMBRE 2025
    {"inicio": "2025-09-08", "fin": "2025-09-17"}, # tecnoprecios
    {"inicio": "2025-09-15", "fin": "2025-10-12"}, # feria_bebe
    {"inicio": "2025-09-18", "fin": "2025-09-21"}, # supertecnoprecios
    {"inicio": "2025-09-18", "fin": "2025-10-05"}, # colchones
    {"inicio": "2025-09-01", "fin": "2025-10-01"}, # vuelta_al_cole_septiembre
    {"inicio": "2025-09-22", "fin": "2025-10-02"}, # financiacion
    {"inicio": "2025-09-25", "fin": "2025-10-08"}, # dias_belleza
    {"inicio": "2025-09-25", "fin": "2025-10-05"}, # semana_lenceria
    
    # OCTUBRE 2025
    {"inicio": "2025-10-03", "fin": "2025-10-05"}, # dia_sin_iva
    {"inicio": "2025-10-06", "fin": "2025-10-22"}, # tecnoprecios
    {"inicio": "2025-10-08", "fin": "2025-10-31"}, # emidio_tucci
    {"inicio": "2025-10-16", "fin": "2025-11-02"}, # 8_dias_oro
    {"inicio": "2025-10-19", "fin": "2025-10-19"}, # cancer_mama
    {"inicio": "2025-10-27", "fin": "2025-10-30"}, # supertecnoprecios
    {"inicio": "2025-10-23", "fin": "2025-10-29"}, # tecnoprecios
    {"inicio": "2025-10-28", "fin": "2025-12-12"}, # navidad_hogar
    
    # NOVIEMBRE 2025
    {"inicio": "2025-11-03", "fin": "2025-11-26"}, # navidad_juguetes
    {"inicio": "2025-11-24", "fin": "2025-11-30"}, # black_friday
    {"inicio": "2025-11-03", "fin": "2025-11-09"}, # adelanto_1_black_friday
    {"inicio": "2025-11-10", "fin": "2025-11-16"}, # adelanto_2_black_friday
    {"inicio": "2025-11-17", "fin": "2025-11-23"}, # adelanto_3_black_friday
    
    # DICIEMBRE 2025
    {"inicio": "2025-12-01", "fin": "2025-12-01"}, # cyber_monday
    {"inicio": "2025-12-04", "fin": "2026-01-05"}, # cheques_magicos
    {"inicio": "2025-12-11", "fin": "2025-12-15"}, # ventas_privadas
    {"inicio": "2025-12-18", "fin": "2025-12-23"}, # supertecnoprecios
    {"inicio": "2025-12-29", "fin": "2026-01-08"}, # feliz_año
    
    # ENERO 2026
    {"inicio": "2026-01-07", "fin": "2026-02-28"}, # rebajas_enero
    {"inicio": "2026-01-07", "fin": "2026-01-21"}, # ofertas_informaticas
    {"inicio": "2026-01-08", "fin": "2026-02-28"}, # blancolor
    {"inicio": "2026-01-07", "fin": "2026-01-28"}, # limpieza_perfumeria
    {"inicio": "2026-01-15", "fin": "2026-01-28"}, # segundas_rebajas_enero
    {"inicio": "2026-01-15", "fin": "2026-01-28"}, # adicional
    {"inicio": "2026-01-22", "fin": "2026-01-25"}, # dia_sin_iva
    {"inicio": "2026-01-22", "fin": "2026-01-28"}, # semana_deporte
    
    # FEBRERO 2026
    {"inicio": "2026-01-29", "fin": "2026-02-01"}, # ofertas_limite_1
    {"inicio": "2026-02-05", "fin": "2026-02-08"}, # ofertas_limite_2
    {"inicio": "2026-02-12", "fin": "2026-02-15"}, # ofertas_limite_3
    {"inicio": "2026-02-19", "fin": "2026-02-22"}, # ofertas_limite_4
    {"inicio": "2026-02-23", "fin": "2026-02-28"}, # remate_final_hogar
    
    # MARZO 2026
    {"inicio": "2026-03-05", "fin": "2026-03-22"}, # aire_acondicionado
    {"inicio": "2026-03-10", "fin": "2026-03-19"}, # tecnoprecios_apple
    {"inicio": "2026-03-05", "fin": "2026-03-15"}, # wake_up_make_up
    {"inicio": "2026-03-12", "fin": "2026-03-29"}, # baby_news
    {"inicio": "2026-03-19", "fin": "2026-03-22"}, # tecnoprecios
    
    # ABRIL 2026
    {"inicio": "2026-04-09", "fin": "2026-04-19"}, # 8_dias_oro
    {"inicio": "2026-04-14", "fin": "2026-04-15"}, # happy_days
    {"inicio": "2026-04-23", "fin": "2026-04-23"}, # dia_libro
    {"inicio": "2026-04-23", "fin": "2026-04-26"}, # supertecnoprecios
    {"inicio": "2026-04-23", "fin": "2026-05-08"}, # dias_belleza
    {"inicio": "2026-04-26", "fin": "2026-04-26"}, # dia_niño
    
    # MAYO 2026
    {"inicio": "2026-05-11", "fin": "2026-05-17"}, # semana_internet
    {"inicio": "2026-05-07", "fin": "2026-05-24"}, # aire_acondicionado
    {"inicio": "2026-05-01", "fin": "2026-05-21"}, # tv_video
    {"inicio": "2026-05-01", "fin": "2026-06-01"}, # juguetes
    {"inicio": "2026-04-30", "fin": "2026-05-18"}, # medias_verano
    {"inicio": "2026-05-21", "fin": "2026-05-24"}, # dia_sin_iva
    
    # JUNIO 2026
    {"inicio": "2026-05-21", "fin": "2026-06-03"}, # financiacion
    {"inicio": "2026-05-21", "fin": "2026-06-08"}, # colchones
    {"inicio": "2026-05-27", "fin": "2026-06-10"}, # lotes_person
    {"inicio": "2026-06-01", "fin": "2026-07-01"}, # summertime
    {"inicio": "2026-06-04", "fin": "2026-06-07"}, # supertecnoprecios
    {"inicio": "2026-06-04", "fin": "2026-06-10"}, # google_days
    {"inicio": "2026-06-04", "fin": "2026-06-17"}, # aire_acondicionado
    {"inicio": "2026-06-05", "fin": "2026-06-12"}, # solares_avene
    {"inicio": "2026-06-10", "fin": "2026-06-14"}, # wake_up_make_up
    {"inicio": "2026-06-11", "fin": "2026-06-15"}, # ventas_privadas
    {"inicio": "2026-06-11", "fin": "2026-06-19"}, # deportes_tecnologia_alimentacion
    {"inicio": "2026-06-16", "fin": "2026-06-24"}, # descuentos_top
    {"inicio": "2026-06-18", "fin": "2026-08-22"}, # vuelta_al_cole
    {"inicio": "2026-06-18", "fin": "2026-06-21"}, # discos
    {"inicio": "2026-06-18", "fin": "2026-06-30"}, # colchones_bases
    {"inicio": "2026-06-18", "fin": "2026-07-01"}  # rebajas_junio
]

dias_con_promo = set()

for promo in promociones:
    rango_fechas = pd.date_range(start=promo["inicio"], end=promo["fin"])
    dias_con_promo.update(rango_fechas)

# Creamos la nueva columna en nuestro dataframe histórico (1 si la fecha está en el set, 0 si no)
df_final['hay_promocion'] = df_final['ds'].isin(dias_con_promo).astype(int)


# promociones["ds"] = pd.to_datetime(promociones["ds"])

# No sigue un patrón de que los domingos siempre cierra sino que según el momento del año

model = Prophet()

# Añadimos los dos regresores: el de cierres y el nuevo de promociones
model.add_regressor('centro_cerrado', mode='multiplicative')
model.add_regressor('hay_promocion', mode='multiplicative')

model.add_country_holidays(country_name="ES")
#model.add_regressor("centro_cerrado", mode="multiplicative")

model.fit(df_final)

print("Entrenamiento completado")

# PREDICCIÓN

future = model.make_future_dataframe(periods=90)
future = pd.merge(future, df_calendario, on='ds', how='left')
future['centro_cerrado'] = future['centro_cerrado'].fillna(0)

# Aplicamos la misma lógica para saber si los días futuros tendrán promoción
future['hay_promocion'] = future['ds'].isin(dias_con_promo).astype(int)

forecast = model.predict(future)

# Las columnas más importantes del resultado:
# ds          → la fecha
# yhat        → predicción central (el valor más probable)
# yhat_lower  → límite inferior del intervalo de confianza
# yhat_upper  → límite superior del intervalo de confianza


# Ver solo el trimestre futuro
trimestre = forecast[forecast["ds"] > df_final["ds"].max()][
    ["ds", "yhat", "yhat_lower", "yhat_upper"]
].reset_index(drop=True)

print(trimestre.head(10))

# Visualizar el modelo 

fig1 = model.plot(forecast)
plt.title("Previsión de pedidos omnicanal")
plt.xlabel("Fecha")
plt.ylabel("Número de pedidos")
plt.show()

# Gráfico de componentes: tendencia + estacionalidades por separado
fig2 = model.plot_components(forecast)
plt.show()

# Medir como de bueno es el modelo
# Parámetros:
# initial: cuánto histórico usar para el primer entrenamiento (mínimo recomendado: 1 año)
# period:  cada cuánto reentrenar
# horizon: hasta cuánto tiempo futuro medir el error


df_cv = cross_validation(
    model,
    initial="730 days",
    period="30 days",
    horizon="90 days"
)

metricas = performance_metrics(df_cv)

# Las métricas clave:
# mae   → error medio absoluto (en número de pedidos)
# mape  → error medio porcentual (en %)
# rmse  → raíz del error cuadrático medio

print(metricas[["horizon", "mae", "mape", "rmse"]])


# Para comprobar los mejores parámetros para changepoints
"""
from prophet.diagnostics import cross_validation, performance_metrics
import itertools

param_grid = {
    "n_changepoints": [15, 25, 35],
    "changepoint_prior_scale": [0.01, 0.05, 0.1, 0.5],
}

combinaciones = [dict(zip(param_grid.keys(), v))
                 for v in itertools.product(*param_grid.values())]

resultados = []
for params in combinaciones:
    m = Prophet(**params, holidays=eventos, seasonality_mode="multiplicative")
    m.fit(df)
    df_cv = cross_validation(m, initial="365 days", period="30 days",
                             horizon="90 days", parallel="processes")
    metricas = performance_metrics(df_cv)
    resultados.append({
        **params,
        "mape_medio": metricas["mape"].mean()
    })

mejor = min(resultados, key=lambda x: x["mape_medio"])
print(f"Mejor combinación: {mejor}")
"""


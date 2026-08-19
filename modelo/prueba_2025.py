# importación de lo necesario

import math

from prophet import Prophet
import pandas as pd
from prophet.make_holidays import make_holidays_df
import matplotlib.pyplot as plt
from prophet.diagnostics import cross_validation, performance_metrics
from sqlalchemy import create_engine, text
import numpy as np
from datetime import datetime

# función que maneja los NaN

def limpiar_regresor(df, columna):
    if columna in df.columns:
        df[columna] = pd.to_numeric(df[columna], errors='coerce')
        df[columna] = df[columna].fillna(0).astype(int)
    else:
        df[columna] = 0
    return df


engine = create_engine("mysql+pymysql://root:root2004@localhost/emplea")

# query para obtener el total de líneas

query_pedidos = """
SELECT fecha AS ds, total_lineas AS y 
FROM pedidohistorico
WHERE id_centro = 1
"""
df_pedidos = pd.read_sql(query_pedidos, con=engine)
df_pedidos['ds'] = pd.to_datetime(df_pedidos['ds'])
df_pedidos = df_pedidos.groupby('ds', as_index=False)['y'].sum()


# query para obtener cuando está abierto y cuando no el centro

query_calendario = """
SELECT 
    fecha AS ds, 
    centro_abierto,
    es_festivo,
    dia_posterior_festivo
FROM calendario
WHERE id_centro = 1
"""
df_calendario = pd.read_sql(query_calendario, con=engine)
df_calendario['ds'] = pd.to_datetime(df_calendario['ds'])
df_calendario = df_calendario.drop_duplicates(subset=['ds'], keep='last').sort_values('ds').reset_index(drop=True)
df_calendario['centro_cerrado'] = 1 - df_calendario['centro_abierto']

# Crear el dataframe final

df_final = pd.merge(df_pedidos, df_calendario, on='ds', how='left')

# Regresores que voy

regresores = ['centro_cerrado', 
              'es_festivo', 
              'dia_posterior_festivo', 
              #'hay_promocion',
              'promo_tier_1', 
              'promo_tier_2', 
              'promo_tier_3'
              ]

# Limpiamos regresores

for reg in regresores:
    df_final = limpiar_regresor(df_final, reg)

# Cambiar esto a que lo coja de la base de dtos automáticamente

promociones = [
    # ENERO 2023
    {"nombre": "feliz_año", "inicio": "2022-12-25", "fin": "2023-01-05"},
    {"nombre": "tecnologia", "inicio": "2022-12-26", "fin": "2023-01-05"},
    {"nombre": "tecnoprecios", "inicio": "2023-01-07", "fin": "2023-01-31"},
    {"nombre": "blancolor", "inicio": "2023-01-19", "fin": "2023-01-28"},
    {"nombre": "rebajas_enero", "inicio": "2023-01-06", "fin": "2023-01-18"},
    {"nombre": "segundas_rebajas_enero", "inicio": "2023-01-19", "fin": "2023-02-02"},
    {"nombre": "feria_artesania", "inicio": "2023-01-27", "fin": "2023-02-20"},
    {"nombre": "semana_deporte", "inicio": "2023-01-26", "fin": "2023-02-02"},

    
    # FEBRERO 2023
    {"nombre": "rebaja_final", "inicio": "2023-02-02", "fin": "2023-02-28"},
    {"nombre": "san_valentin", "inicio": "2023-02-02", "fin": "2023-02-14"},
    {"nombre": "limite_1", "inicio": "2023-02-02", "fin": "2023-02-05"},
    {"nombre": "limite_2", "inicio": "2023-02-09", "fin": "2023-02-12"},
    {"nombre": "limite_3", "inicio": "2023-02-16", "fin": "2023-02-19"},
    {"nombre": "limite_4", "inicio": "2023-02-23", "fin": "2023-02-26"},
    {"nombre": "financiaciacion", "inicio": "2023-02-16", "fin": "2023-02-22"},
    {"nombre": "tecnoprecios", "inicio": "2023-02-24", "fin": "2023-03-09"},
    
    # MARZO 2023
    {"nombre": "hogar", "inicio": "2023-03-01", "fin": "2023-06-30"},
    {"nombre": "tecnoprecios", "inicio": "2023-03-09", "fin": "2023-03-22"},
    {"nombre": "hogar", "inicio": "2023-03-10", "fin": "2023-04-02"},
    {"nombre": "dia_padre", "inicio": "2023-03-09", "fin": "2023-03-19"},
    {"nombre": "libros", "inicio": "2023-03-17", "fin": "2023-04-02"},
    {"nombre": "descuentos_top", "inicio": "2023-03-16", "fin": "2023-04-02"},
    {"nombre": "tecnoprecios", "inicio": "2023-03-23", "fin": "2023-04-09"},
    {"nombre": "libros", "inicio": "2023-03-21", "fin": "2023-03-21"},
    {"nombre": "juguetes", "inicio": "2023-03-30", "fin": "2023-08-31"},
    {"nombre": "ocio", "inicio": "2023-03-12", "fin": "2023-03-19"},
    
    # ABRIL 2023
    {"nombre": "libros", "inicio": "2023-04-02", "fin": "2023-04-02"},
    {"nombre": "hogar", "inicio": "2023-04-03", "fin": "2023-08-31"},
    {"nombre": "emidio_tucci", "inicio": "2023-04-11", "fin": "2023-04-30"},
    {"nombre": "8_dias_oro", "inicio": "2023-04-13", "fin": "2023-04-23"},
    {"nombre": "8_dias_oro_hogar", "inicio": "2023-04-13", "fin": "2023-04-30"},
    {"nombre": "tecnoprecios", "inicio": "2023-04-20", "fin": "2023-05-03"},
    {"nombre": "dia_libro", "inicio": "2023-04-23", "fin": "2023-04-23"},
    {"nombre": "dias_belleza", "inicio": "2023-04-24", "fin": "2023-05-09"},
    {"nombre": "dia_madre", "inicio": "2023-04-24", "fin": "2023-05-07"},
    
    # MAYO 2023
    {"nombre": "hogar", "inicio": "2023-05-01", "fin": "2023-05-15"},
    {"nombre": "ocio", "inicio": "2023-05-04", "fin": "2023-05-28"},
    {"nombre": "tecnoprecios", "inicio": "2023-05-04", "fin": "2023-05-17"},
    {"nombre": "hipercor", "inicio": "2023-05-11", "fin": "2023-06-05"},
    {"nombre": "semana_internet", "inicio": "2023-05-08", "fin": "2023-05-17"},
    {"nombre": "deportes", "inicio": "2023-05-18", "fin": "2023-06-07"},
    {"nombre": "financiacion", "inicio": "2023-05-25", "fin": "2023-06-01"},
    {"nombre": "supertecnoprecios", "inicio": "2023-05-18", "fin": "2023-05-21"},
    {"nombre": "tecnoprecios", "inicio": "2023-05-22", "fin": "2023-06-07"},
    {"nombre": "hogar", "inicio": "2023-05-25", "fin": "2023-06-11"},    
    {"nombre": "libros", "inicio": "2023-05-26", "fin": "2023-06-11"},
    
    # JUNIO 2023
    {"nombre": "belleza", "inicio": "2023-06-01", "fin": "2023-06-30"},
    {"nombre": "tecnologia", "inicio": "2023-06-02", "fin": "2023-06-03"},
    {"nombre": "venta_privada", "inicio": "2023-06-08", "fin": "2023-06-11"},
    {"nombre": "rebajas_junio", "inicio": "2023-06-22", "fin": "2023-07-05"},
    {"nombre": "descuentos_top", "inicio": "2023-06-12", "fin": "2023-06-21"},
    {"nombre": "tecnologia", "inicio": "2023-06-22", "fin": "2023-07-06"},
    {"nombre": "libros", "inicio": "2023-06-15", "fin": "2023-08-20"},
    {"nombre": "libros", "inicio": "2023-06-23", "fin": "2023-06-28"},
    
    # JULIO 2023
    {"nombre": "segundas_rebajas_julio", "inicio": "2023-07-06", "fin": "2023-07-19"},
    {"nombre": "supertecnoprecios", "inicio": "2023-07-07", "fin": "2023-07-11"},
    {"nombre": "semana_deporte", "inicio": "2023-07-13", "fin": "2023-07-19"},
    {"nombre": "especial_baño", "inicio": "2023-07-13", "fin": "2023-07-19"},
    {"nombre": "rebaja_final", "inicio": "2023-07-20", "fin": "2023-08-31"},
    {"nombre": "electro_3_1", "inicio": "2023-07-24", "fin": "2023-08-26"},
    
    # AGOSTO 2023
    {"nombre": "libros", "inicio": "2023-08-01", "fin": "2023-09-01"},
    {"nombre": "limite_1", "inicio": "2023-08-03", "fin": "2023-08-06"},
    {"nombre": "limite_2", "inicio": "2023-08-10", "fin": "2023-08-13"},
    {"nombre": "limite_3", "inicio": "2023-08-17", "fin": "2023-08-20"},
    {"nombre": "limite_4", "inicio": "2023-08-24", "fin": "2023-08-27"},
    {"nombre": "hogar", "inicio": "2023-08-16", "fin": "2023-09-06"},
    {"nombre": "electro_3_2", "inicio": "2023-08-31", "fin": "2023-09-02"},
    
    # SEPTIEMBRE 2023
    {"nombre": "electro_3_3", "inicio": "2023-09-07", "fin": "2023-09-09"},
    {"nombre": "deportes", "inicio": "2023-09-07", "fin": "2023-10-01"},
    {"nombre": "moda", "inicio": "2023-09-26", "fin": "2023-10-11"},
    {"nombre": "supertecnoprecios", "inicio": "2023-09-28", "fin": "2023-10-01"},
    {"nombre": "dias_belleza", "inicio": "2023-09-25", "fin": "2023-10-11"},
    {"nombre": "semana_lenceria", "inicio": "2023-09-28", "fin": "2023-10-15"},
    {"nombre": "financiacion", "inicio": "2023-09-28", "fin": "2023-10-04"},
    {"nombre": "financiacion", "inicio": "2023-09-28", "fin": "2023-10-15"},
    
    # OCTUBRE 2023
    {"nombre": "8_dias_oro", "inicio": "2023-10-19", "fin": "2023-11-05"},
    {"nombre": "adelanto_1_black_friday", "inicio": "2023-10-30", "fin": "2023-11-05"},
    {"nombre": "cancer_mama", "inicio": "2024-10-05", "fin": "2024-10-20"},
    
    # NOVIEMBRE 2023
    {"nombre": "8_dias_oro_hogar", "inicio": "2023-11-06", "fin": "2023-11-12"},
    {"nombre": "adelanto_2_black_friday", "inicio": "2023-11-06", "fin": "2023-11-12"},
    {"nombre": "adelanto_3_black_friday", "inicio": "2023-11-13", "fin": "2023-11-19"},
    {"nombre": "black_friday", "inicio": "2023-11-20", "fin": "2023-11-26"},
    {"nombre": "cyber_monday", "inicio": "2023-11-27", "fin": "2023-11-27"},
    {"nombre": "cheques_magicos", "inicio": "2023-11-17", "fin": "2023-11-19"},
    {"nombre": "deportes", "inicio": "2023-11-08", "fin": "2023-11-19"},
    {"nombre": "hogar", "inicio": "2023-11-09", "fin": "2023-12-10"},
    {"nombre": "libros", "inicio": "2023-11-16", "fin": "2023-11-16"},
    
    # DICIEMBRE 2023
    {"nombre": "belleza", "inicio": "2023-12-05", "fin": "2023-12-05"},
    {"nombre": "navidad_juguetes", "inicio": "2023-12-01", "fin": "2024-01-01"},
    {"nombre": "venta_privada", "inicio": "2023-12-07", "fin": "2023-12-11"},
    {"nombre": "feliz_año", "inicio": "2023-12-26", "fin": "2024-01-05"},

    # ENERO 2024
    {"nombre": "rebajas_enero", "inicio": "2024-01-06", "fin": "2024-01-17"},
    {"nombre": "blancolor", "inicio": "2024-01-15", "fin": "2024-01-29"},
    {"nombre": "segundas_rebajas_enero", "inicio": "2024-01-18", "fin": "2024-01-31"},
    {"nombre": "semana_deporte", "inicio": "2024-01-25", "fin": "2024-01-31"},
    
    # FEBRERO 2024
    {"nombre": "limite_1", "inicio": "2024-02-01", "fin": "2024-02-04"},
    {"nombre": "limite_2", "inicio": "2024-02-08", "fin": "2024-02-11"},
    {"nombre": "limite_3", "inicio": "2024-02-15", "fin": "2024-02-18"},
    {"nombre": "limite_4", "inicio": "2024-02-22", "fin": "2024-02-25"},
    {"nombre": "financiacion", "inicio": "2024-02-15", "fin": "2024-02-21"},
    {"nombre": "rebaja_final", "inicio": "2024-02-15", "fin": "2024-02-29"},
    {"nombre": "san_valentin", "inicio": "2024-02-05", "fin": "2024-02-14"},
    {"nombre": "mes_hogar", "inicio": "2024-02-01", "fin": "2024-03-01"},
    {"nombre": "aire_acondicionado", "inicio": "2024-02-29", "fin": "2024-03-14"},
    
    # MARZO 2024
    {"nombre": "dia_padre", "inicio": "2024-03-11", "fin": "2024-03-19"},
    {"nombre": "deportes", "inicio": "2024-03-18", "fin": "2024-03-31"},
    {"nombre": "semana_santa", "inicio": "2024-03-17", "fin": "2024-03-24"},
    {"nombre": "libros", "inicio": "2024-03-15", "fin": "2024-03-24"},
    {"nombre": "libros", "inicio": "2024-03-21", "fin": "2024-03-21"},
    
    # ABRIL 2024
    {"nombre": "8_dias_oro", "inicio": "2024-04-04", "fin": "2024-04-21"},
    {"nombre": "tecnologia", "inicio": "2024-04-04", "fin": "2024-04-07"},
    {"nombre": "supertecnoprecios", "inicio": "2024-04-11", "fin": "2024-04-14"},
    {"nombre": "dias_belleza", "inicio": "2024-04-25", "fin": "2024-05-10"},
    {"nombre": "dia_libro", "inicio": "2024-04-23", "fin": "2024-04-23"},
    {"nombre": "moda", "inicio": "2024-04-25", "fin": "2024-05-12"},
    {"nombre": "summertime", "inicio": "2024-04-25", "fin": "2024-05-30"},
    {"nombre": "dia_madre", "inicio": "2024-04-25", "fin": "2024-05-05"},
    
    # MAYO 2024
    {"nombre": "dias_flash", "inicio": "2024-05-08", "fin": "2024-05-17"},
    {"nombre": "financiacion_total", "inicio": "2024-05-27", "fin": "2024-06-02"},
    {"nombre": "tecnologia", "inicio": "2024-05-24", "fin": "2024-05-26"},
    
    # JUNIO 2024
    {"nombre": "rebajas_junio", "inicio": "2024-06-28", "fin": "2024-07-10"},
    {"nombre": "venta_privada", "inicio": "2024-06-06", "fin": "2024-06-10"},
    {"nombre": "descuentos_top", "inicio": "2024-06-11", "fin": "2024-06-27"},
    
    # JULIO 2024
    {"nombre": "segundas_rebajas_julio", "inicio": "2024-07-11", "fin": "2024-07-31"},
    {"nombre": "supertecnoprecios", "inicio": "2024-07-12", "fin": "2024-07-16"},
    {"nombre": "semana_deporte", "inicio": "2024-07-18", "fin": "2024-07-24"},
    {"nombre": "hogar", "inicio": "2024-07-22", "fin": "2024-07-28"},
    {"nombre": "tecnologia", "inicio": "2024-07-29", "fin": "2024-07-31"},
    
    # AGOSTO 2024
    {"nombre": "rebaja_final", "inicio": "2024-08-01", "fin": "2024-08-31"},
    {"nombre": "limite_1", "inicio": "2024-08-01", "fin": "2024-08-04"},
    {"nombre": "limite_2", "inicio": "2024-08-08", "fin": "2024-08-11"},
    {"nombre": "limite_3", "inicio": "2024-08-15", "fin": "2024-08-18"},
    {"nombre": "limite_4", "inicio": "2024-08-22", "fin": "2024-08-25"},
    {"nombre": "electro_3_1", "inicio": "2024-08-05", "fin": "2024-08-07"},
    {"nombre": "electro_3_2", "inicio": "2024-08-12", "fin": "2024-08-14"},
    {"nombre": "electro_3_3", "inicio": "2024-08-19", "fin": "2024-08-21"},
    
    # SEPTIEMBRE 2024
    {"nombre": "remate_final_hogar", "inicio": "2024-08-26", "fin": "2024-08-31"},
    {"nombre": "supertecnoprecios", "inicio": "2024-09-12", "fin": "2024-09-15"},
    {"nombre": "feria_bebe", "inicio": "2024-09-16", "fin": "2024-10-13"},
    {"nombre": "dias_belleza", "inicio": "2024-09-26", "fin": "2024-10-06"},
    {"nombre": "semana_lenceria", "inicio": "2024-09-26", "fin": "2024-10-06"},
    {"nombre": "financiacion", "inicio": "2024-09-26", "fin": "2024-10-03"},
    
    # OCTUBRE 2024
    {"nombre": "moda", "inicio": "2024-10-11", "fin": "2024-10-27"},
    {"nombre": "tecnoprecios", "inicio": "2024-10-07", "fin": "2024-10-23"},
    {"nombre": "8_dias_oro", "inicio": "2024-10-17", "fin": "2024-11-03"},
    {"nombre": "8_dias_oro_hogar", "inicio": "2024-10-06", "fin": "2024-11-12"},
    {"nombre": "supertecnoprecios", "inicio": "2024-10-24", "fin": "2024-10-27"},
    {"nombre": "cancer_mama", "inicio": "2024-10-03", "fin": "2024-10-20"},

    
    # NOVIEMBRE 2024
    {"nombre": "adelanto_1_black_friday", "inicio": "2024-11-04", "fin": "2024-11-10"},
    {"nombre": "adelanto_2_black_friday", "inicio": "2024-11-11", "fin": "2024-11-17"},
    {"nombre": "adelanto_3_black_friday", "inicio": "2024-11-18", "fin": "2024-11-24"},
    {"nombre": "black_friday", "inicio": "2024-11-25", "fin": "2024-12-01"},
    {"nombre": "navidad_hogar", "inicio": "2024-11-06", "fin": "2024-11-24"},
    {"nombre": "navidad_juguetes", "inicio": "2024-11-04", "fin": "2024-11-27"},
    
    # DICIEMBRE 2024
    {"nombre": "cyber_monday", "inicio": "2024-12-02", "fin": "2024-12-03"},
    {"nombre": "venta_privada", "inicio": "2024-12-12", "fin": "2024-12-16"},
    {"nombre": "lo_quiero", "inicio": "2024-12-17", "fin": "2025-01-05"},
    {"nombre": "cheques_magicos", "inicio": "2024-12-04", "fin": "2024-12-06"},
    {"nombre": "tecnoprecios", "inicio": "2024-12-03", "fin": "2024-12-15"},
    {"nombre": "supertecnoprecios", "inicio": "2024-12-19", "fin": "2024-12-22"},
    {"nombre": "feliz_año", "inicio": "2024-12-26", "fin": "2025-01-05"},
    
    # ENERO 2025
    {"nombre": "rebajas_enero", "inicio": "2025-01-07", "fin": "2025-02-28"},
    {"nombre": "dia_sin_iva", "inicio": "2025-01-19", "fin": "2025-01-19"},
    {"nombre": "semana_deporte", "inicio": "2025-01-23", "fin": "2025-01-29"},
    {"nombre": "blancolor", "inicio": "2025-01-13", "fin": "2025-02-28"},
    
    # FEBRERO 2025
    {"nombre": "limite_1", "inicio": "2025-02-06", "fin": "2025-02-09"},
    {"nombre": "limite_2", "inicio": "2025-02-20", "fin": "2025-02-23"},
    {"nombre": "semana_telefonia", "inicio": "2025-02-20", "fin": "2025-02-26"},
    {"nombre": "20_fotografia", "inicio": "2025-02-20", "fin": "2025-02-23"},
    
    # MARZO 2025
    {"nombre": "tecnoprecios", "inicio": "2025-03-13", "fin": "2025-03-26"},
    {"nombre": "supertecnoprecios", "inicio": "2025-03-26", "fin": "2025-03-30"},
    
    # ABRIL 2025
    {"nombre": "8_dias_oro", "inicio": "2025-04-03", "fin": "2025-04-13"},
    {"nombre": "supertecnoprecios", "inicio": "2025-04-24", "fin": "2025-04-27"},
    {"nombre": "dias_belleza", "inicio": "2025-04-24", "fin": "2025-05-09"},
    {"nombre": "dia_libro", "inicio": "2025-04-23", "fin": "2025-04-23"},
    
    # MAYO 2025
    {"nombre": "ofertas_flash", "inicio": "2025-05-08", "fin": "2025-05-11"},
    {"nombre": "semana_internet", "inicio": "2025-05-12", "fin": "2025-05-18"},
    {"nombre": "supertecnoprecios", "inicio": "2025-05-22", "fin": "2025-05-25"},
    {"nombre": "financiacion_total", "inicio": "2025-05-26", "fin": "2025-06-04"},
    {"nombre": "tecnoprecios", "inicio": "2025-05-26", "fin": "2025-06-04"},
    {"nombre": "samsung_days", "inicio": "2025-05-29", "fin": "2025-06-01"},
    
    # JUNIO 2025
    {"nombre": "ventas_privadas", "inicio": "2025-06-05", "fin": "2025-06-09"},
    {"nombre": "dia_sin_iva", "inicio": "2025-06-13", "fin": "2025-06-15"},
    {"nombre": "descuentos_top", "inicio": "2025-06-10", "fin": "2025-06-26"},
    {"nombre": "rebajas_junio", "inicio": "2025-06-27", "fin": "2025-08-31"},
    {"nombre": "vuelta_al_cole", "inicio": "2025-06-19", "fin": "2025-07-31"},
    {"nombre": "yellow_days", "inicio": "2025-06-19", "fin": "2025-06-26"},
    {"nombre": "ocio", "inicio": "2025-06-19", "fin": "2025-06-22"},
    {"nombre": "tecnoprecios", "inicio": "2025-06-27", "fin": "2025-07-10"},
    
    # JULIO 2025
    {"nombre": "segundas_rebajas_julio", "inicio": "2025-07-14", "fin": "2025-07-31"},
    {"nombre": "supertecnoprecios", "inicio": "2025-07-11", "fin": "2025-07-15"},
    {"nombre": "semana_deporte", "inicio": "2025-07-17", "fin": "2025-07-23"},
    {"nombre": "especial_baño", "inicio": "2025-07-14", "fin": "2025-07-20"},
    
    # AGOSTO 2025
    {"nombre": "rebajas_agosto", "inicio": "2025-08-01", "fin": "2025-09-01"},
    {"nombre": "limite_1", "inicio": "2025-07-31", "fin": "2025-08-08"},
    {"nombre": "limite_2", "inicio": "2025-08-07", "fin": "2025-08-10"},
    {"nombre": "limite_3", "inicio": "2025-08-21", "fin": "2025-08-24"},
    {"nombre": "limite_4", "inicio": "2025-08-28", "fin": "2025-08-31"},
    {"nombre": "electro_3_1", "inicio": "2025-08-04", "fin": "2025-08-07"},
    {"nombre": "parafarmacia", "inicio": "2025-08-06", "fin": "2025-08-08"},
    {"nombre": "hogar", "inicio": "2025-08-25", "fin": "2025-08-31"},
    {"nombre": "tecnologia", "inicio": "2025-08-14", "fin": "2025-08-17"},
    {"nombre": "hogar", "inicio": "2025-08-08", "fin": "2025-08-31"},
    {"nombre": "electro_3_2", "inicio": "2025-08-22", "fin": "2025-08-24"},
    {"nombre": "university", "inicio": "2025-08-21", "fin": "2025-09-07"},

    # SEPTIEMBRE 2025
    {"nombre": "tecnoprecios", "inicio": "2025-09-08", "fin": "2025-09-17"},
    {"nombre": "baby", "inicio": "2025-09-15", "fin": "2025-10-12"},
    {"nombre": "supertecnoprecios", "inicio": "2025-09-18", "fin": "2025-09-21"},
    {"nombre": "colchones", "inicio": "2025-09-18", "fin": "2025-10-05"},
    {"nombre": "vuelta_al_cole", "inicio": "2025-09-01", "fin": "2025-10-01"},
    {"nombre": "financiacion", "inicio": "2025-09-22", "fin": "2025-10-02"},
    {"nombre": "dias_belleza", "inicio": "2025-09-25", "fin": "2025-10-08"},
    {"nombre": "semana_lenceria", "inicio": "2025-09-25", "fin": "2025-10-05"},
    
    # OCTUBRE 2025
    {"nombre": "dia_sin_iva", "inicio": "2025-10-03", "fin": "2025-10-05"},
    {"nombre": "tecnoprecios", "inicio": "2025-10-06", "fin": "2025-10-22"},
    {"nombre": "moda", "inicio": "2025-10-08", "fin": "2025-10-31"},
    {"nombre": "8_dias_oro", "inicio": "2025-10-16", "fin": "2025-11-02"},
    {"nombre": "8_dias_oro_hogar", "inicio": "2025-10-16", "fin": "2025-11-09"},
    {"nombre": "cancer_mama", "inicio": "2025-10-02", "fin": "2025-10-19"},
    {"nombre": "supertecnoprecios", "inicio": "2025-10-27", "fin": "2025-10-30"},
    {"nombre": "tecnoprecios", "inicio": "2025-10-23", "fin": "2025-10-29"},
    {"nombre": "navidad_hogar", "inicio": "2025-10-28", "fin": "2025-12-12"},
    
    # NOVIEMBRE 2025
    {"nombre": "navidad_juguetes", "inicio": "2025-11-03", "fin": "2025-11-26"},
    {"nombre": "black_friday", "inicio": "2025-11-24", "fin": "2025-11-30"},
    {"nombre": "adelanto_1_black_friday", "inicio": "2025-11-03", "fin": "2025-11-09"},
    {"nombre": "adelanto_2_black_friday", "inicio": "2025-11-10", "fin": "2025-11-16"},
    {"nombre": "adelanto_3_black_friday", "inicio": "2025-11-17", "fin": "2025-11-23"},
    
    # DICIEMBRE 2025
    {"nombre": "cyber_monday", "inicio": "2025-12-01", "fin": "2025-12-01"},
    {"nombre": "cheques_magicos", "inicio": "2025-12-04", "fin": "2026-01-05"},
    {"nombre": "ventas_privadas", "inicio": "2025-12-11", "fin": "2025-12-15"},
    {"nombre": "supertecnoprecios", "inicio": "2025-12-18", "fin": "2025-12-23"},
    {"nombre": "feliz_año", "inicio": "2025-12-29", "fin": "2026-01-08"},
    
    # ENERO 2026
    {"nombre": "rebajas_enero", "inicio": "2026-01-07", "fin": "2026-02-28"},
    {"nombre": "tecnología", "inicio": "2026-01-07", "fin": "2026-01-21"},
    {"nombre": "blancolor", "inicio": "2026-01-08", "fin": "2026-02-28"},
    {"nombre": "limpieza_perfumeria", "inicio": "2026-01-07", "fin": "2026-01-28"},
    {"nombre": "segundas_rebajas_enero", "inicio": "2026-01-15", "fin": "2026-01-28"},
    {"nombre": "dia_sin_iva", "inicio": "2026-01-22", "fin": "2026-01-25"},
    {"nombre": "semana_deporte", "inicio": "2026-01-22", "fin": "2026-01-28"},
    
    # FEBRERO 2026
    {"nombre": "limite_1", "inicio": "2026-01-29", "fin": "2026-02-01"},
    {"nombre": "limite_2", "inicio": "2026-02-05", "fin": "2026-02-08"},
    {"nombre": "limite_3", "inicio": "2026-02-12", "fin": "2026-02-15"},
    {"nombre": "limite_4", "inicio": "2026-02-19", "fin": "2026-02-22"},
    {"nombre": "hogar", "inicio": "2026-02-23", "fin": "2026-02-28"},
    
    # MARZO 2026
    {"nombre": "tecnoprecios", "inicio": "2026-03-10", "fin": "2026-03-19"},
    {"nombre": "belleza", "inicio": "2026-03-05", "fin": "2026-03-15"},
    {"nombre": "baby", "inicio": "2026-03-12", "fin": "2026-03-29"},
    {"nombre": "tecnoprecios", "inicio": "2026-03-19", "fin": "2026-03-22"},
    
    # ABRIL 2026
    {"nombre": "8_dias_oro", "inicio": "2026-04-09", "fin": "2026-04-19"},
    {"nombre": "happy_days", "inicio": "2026-04-14", "fin": "2026-04-15"},
    {"nombre": "dia_libro", "inicio": "2026-04-23", "fin": "2026-04-23"},
    {"nombre": "supertecnoprecios", "inicio": "2026-04-23", "fin": "2026-04-26"},
    {"nombre": "dias_belleza", "inicio": "2026-04-23", "fin": "2026-05-08"},
    {"nombre": "juguetes", "inicio": "2026-04-26", "fin": "2026-04-26"},
    
    # MAYO 2026
    {"nombre": "semana_internet", "inicio": "2026-05-11", "fin": "2026-05-17"},
    {"nombre": "tecnologia", "inicio": "2026-05-01", "fin": "2026-05-21"},
    {"nombre": "juguetes", "inicio": "2026-05-01", "fin": "2026-06-01"},
    {"nombre": "medias_verano", "inicio": "2026-04-30", "fin": "2026-05-18"},
    {"nombre": "dia_sin_iva", "inicio": "2026-05-21", "fin": "2026-05-24"},
    
    # JUNIO 2026
    {"nombre": "financiacion", "inicio": "2026-05-21", "fin": "2026-06-03"},
    {"nombre": "hogar_casa", "inicio": "2026-05-21", "fin": "2026-06-08"},
    {"nombre": "lotes_verano", "inicio": "2026-05-27", "fin": "2026-06-10"},
    {"nombre": "summertime", "inicio": "2026-06-01", "fin": "2026-07-01"},
    {"nombre": "supertecnoprecios", "inicio": "2026-06-04", "fin": "2026-06-07"},
    {"nombre": "tecnologia", "inicio": "2026-06-04", "fin": "2026-06-10"},
    {"nombre": "belleza", "inicio": "2026-06-05", "fin": "2026-06-12"},
    {"nombre": "días_belleza", "inicio": "2026-06-10", "fin": "2026-06-14"},
    {"nombre": "ventas_privadas", "inicio": "2026-06-11", "fin": "2026-06-15"},
    {"nombre": "descuentos_top", "inicio": "2026-06-16", "fin": "2026-06-24"},
    {"nombre": "vuelta_al_cole", "inicio": "2026-06-18", "fin": "2026-08-22"},
    {"nombre": "ocio", "inicio": "2026-06-18", "fin": "2026-06-21"},
    {"nombre": "hogar_casa", "inicio": "2026-06-18", "fin": "2026-06-30"},
    {"nombre": "rebajas_junio", "inicio": "2026-06-25", "fin": "2026-07-09"},

    #JULIO 2026
    {"nombre": "segundas_rebajas_julio", "inicio": "2026-07-10", "fin": "2026-07-29"},
    {"nombre": "semana_deporte", "inicio": "2026-07-16", "fin": "2026-07-22"},
    {"nombre": "especial_baño", "inicio": "2026-07-16", "fin": "2026-07-22"},
    {"nombre": "semana_deporte", "inicio": "2026-06-18", "fin": "2026-07-01"},
    
    #AGOSTO 2026
    {"nombre": "rebaja_final", "inicio": "2026-07-30", "fin": "2026-08-31"},
    {"nombre": "limite_1", "inicio": "2026-08-06", "fin": "2026-08-09"},
    {"nombre": "limite_2", "inicio": "2026-08-13", "fin": "2026-08-16"},
    {"nombre": "limite_3", "inicio": "2026-08-20", "fin": "2026-08-23"},
    {"nombre": "limite_4", "inicio": "2026-08-27", "fin": "2026-08-30"},
    {"nombre": "electro_3_1", "inicio": "2026-08-10", "fin": "2026-08-12"},
    {"nombre": "electro_3_2", "inicio": "2026-08-17", "fin": "2026-08-19"},
    {"nombre": "electro_3_3", "inicio": "2026-08-24", "fin": "2026-08-26"},

    #SEPTIEMBRE 2026
    {"nombre": "tecnoprecios", "inicio": "2026-08-22", "fin": "2026-09-09"},
    {"nombre": "supertecnoprecios", "inicio": "2026-09-17", "fin": "2026-09-20"},
    {"nombre": "dias_belleza", "inicio": "2026-09-24", "fin": "2026-10-07"},
    {"nombre": "semana_lenceria", "inicio": "2026-09-24", "fin": "2026-10-04"},

    #OCTUBRE 2026
    {"nombre": "cancer_mama", "inicio": "2026-10-01", "fin": "2026-10-18"},
    {"nombre": "8_dias_oro", "inicio": "2026-10-15", "fin": "2026-10-31"},
    {"nombre": "8_dias_oro_hogar", "inicio": "2026-10-15", "fin": "2026-11-07"},
    {"nombre": "tecnoprecios", "inicio": "2026-10-05", "fin": "2026-10-21"},
    {"nombre": "supertecnoprecios", "inicio": "2026-10-22", "fin": "2026-10-25"},

    #NOVIEMBRE 2026
    {"nombre": "navidad_hogar", "inicio": "2026-10-28", "fin": "2026-11-29"},
    {"nombre": "adelanto_1_black_friday", "inicio": "2026-11-02", "fin": "2026-11-08"},
    {"nombre": "adelanto_2_black_friday", "inicio": "2026-11-09", "fin": "2026-11-15"},
    {"nombre": "adelanto_3_black_friday", "inicio": "2026-11-16", "fin": "2026-11-23"},
    {"nombre": "black_friday", "inicio": "2026-11-23", "fin": "2026-11-29"},
    {"nombre": "cyber_monday", "inicio": "2026-11-30", "fin": "2026-11-30"},

    #DICIEMBRE 2026
    {"nombre": "cheques_magicos", "inicio": "2026-12-02", "fin": "2026-12-03"},
    {"nombre": "venta_privada", "inicio": "2026-12-10", "fin": "2026-12-14"},
    {"nombre": "tecnoprecios", "inicio": "2026-12-01", "fin": "2026-12-12"},
    {"nombre": "supertecnoprecios", "inicio": "2026-12-17", "fin": "2026-12-20"},
    {"nombre": "feliz_año", "inicio": "2026-12-26", "fin": "2027-01-05"},
]

#Definir cuales son los de tier 1, 2 y 3

promo_tier_1 = [
    "rebajas_enero", 
    "ventas_privadas",
    "semana_internet",
    "rebajas_junio",
    "semana_deporte"
]

promo_tier_2 = [
    "tecnoprecios",
    "supertecnoprecios",
    "dias_belleza",
    "8_dias_oro",
    "segundas_rebajas_enero",
    "segundas_rebajas_julio",
    "descuentos_top"
]

fechas_t1 = set()
fechas_t2 = set()
fechas_t3 = set()

# Clasifica cada una de las promociones y guarda las fechas

for promo in promociones:
    rango_fechas = pd.date_range(start=promo["inicio"], end=promo["fin"])
    nombre = promo.get("nombre", "").lower()
    
    # Clasificación automática
    if nombre in promo_tier_1:
        fechas_t1.update(rango_fechas)
    elif nombre in promo_tier_2:
        fechas_t2.update(rango_fechas)
    else:
        fechas_t3.update(rango_fechas)

df_final['promo_tier_1'] = df_final['ds'].isin(fechas_t1).astype(int)
df_final['promo_tier_2'] = df_final['ds'].isin(fechas_t2).astype(int)
df_final['promo_tier_3'] = df_final['ds'].isin(fechas_t3).astype(int)


# Creamos el modelo

model = Prophet(
    yearly_seasonality=20,
    weekly_seasonality=3,
    daily_seasonality=False,
    seasonality_mode="multiplicative",
    interval_width=0.8,
    n_changepoints=50)

#for reg in regresores:
#    model.add_regressor(reg, mode='multiplicative')

model.add_regressor('centro_cerrado', mode="multiplicative")
model.add_regressor('es_festivo')
model.add_regressor('dia_posterior_festivo')

model.add_regressor('promo_tier_1', prior_scale=30.0) 
model.add_regressor('promo_tier_2', prior_scale=15.0)
model.add_regressor('promo_tier_3', prior_scale=5.0)

model.add_country_holidays(country_name="ES")
model.fit(df_final)

# Predicción

future = model.make_future_dataframe(periods=180)
future = pd.merge(future, df_calendario, on='ds', how='left')

future['promo_tier_1'] = future['ds'].isin(fechas_t1).astype(int)
future['promo_tier_2'] = future['ds'].isin(fechas_t2).astype(int)
future['promo_tier_3'] = future['ds'].isin(fechas_t3).astype(int)


for reg in regresores:
    future = limpiar_regresor(future, reg)

forecast = model.predict(future)


tasa_crecimiento_anual = 0.15

fecha_max_historica = df_final['ds'].max()

def aplicar_crecimiento(row, col_name):
    if row['ds'] > fecha_max_historica:
        diferencia = (row['ds'] - fecha_max_historica).days
        prediccion = math.ceil(diferencia/365.25)

        
        factor_crecimiento = (1 + tasa_crecimiento_anual) ** prediccion
        return row[col_name] * factor_crecimiento
    
    return row[col_name]

forecast['yhat'] = forecast.apply(lambda r: aplicar_crecimiento(r, 'yhat'), axis=1)
forecast['yhat_lower'] = forecast.apply(lambda r: aplicar_crecimiento(r, 'yhat_lower'), axis=1)
forecast['yhat_upper'] = forecast.apply(lambda r: aplicar_crecimiento(r, 'yhat_upper'), axis=1)



trimestre = forecast[forecast["ds"] > df_final["ds"].max()][
    ["ds", "yhat", "yhat_lower", "yhat_upper"]
].reset_index(drop=True)

trimestre = trimestre.drop_duplicates(subset=['ds'], keep='last').sort_values('ds').reset_index(drop=True)

print(trimestre[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].head(30))

trimestre = trimestre.rename(columns={
    "ds": "fecha",
    "yhat": "pedidos_previstos",
    "yhat_lower": "limite_inferior",
    "yhat_upper": "limite_superior"
})


columnas_numericas = ["pedidos_previstos", "limite_inferior", "limite_superior"]
trimestre[columnas_numericas] = trimestre[columnas_numericas].round().astype(int)
trimestre = trimestre.drop_duplicates(subset=['fecha'], keep='last').sort_values('fecha').reset_index(drop=True)

# Duplicamos pedidos_previstos en pedidos_acumulados y, si el centro está cerrado,
# sumamos ese valor al día siguiente para no perderlo en la previsión acumulada.
trimestre = trimestre.merge(
    df_calendario[['ds', 'centro_abierto']].rename(columns={'ds': 'fecha'}),
    on='fecha',
    how='left'
)
trimestre['pedidos_acumulados'] = trimestre['pedidos_previstos'].copy()

for i in range(len(trimestre) - 1):
    if trimestre.at[i, 'centro_abierto'] == 0:
        trimestre.at[i + 1, 'pedidos_acumulados'] = (
            trimestre.at[i + 1, 'pedidos_acumulados'] + trimestre.at[i, 'pedidos_previstos']
        )

trimestre = trimestre.drop(columns=['centro_abierto'])
trimestre["fecha_generacion"] = datetime.now()
trimestre["id_centro"] = 1
trimestre = trimestre[[
    'fecha',
    'pedidos_previstos',
    'pedidos_acumulados',
    'limite_inferior',
    'limite_superior',
    'fecha_generacion',
    'id_centro'
]]


try:
    with engine.begin() as conn:
        conn.execute(text("DELETE FROM prediccion"))
        trimestre.to_sql(
            name="prediccion",
            con=conn,
            if_exists="append",
            index=False
        )
    print("Valores predecidos con éxito")
except Exception as e:
    print(f"Error: {e}")

'''


# GRÁFICOS

# Gráfico general

fig1 = model.plot(forecast)

fecha_corte = pd.to_datetime('2026-06-30')

pasado = forecast[forecast['ds'] <= fecha_corte]
futuro = forecast[forecast['ds'] >= fecha_corte]

plt.fill_between(forecast['ds'], forecast['yhat_lower'], forecast['yhat_upper'], color='#00784E', alpha=0.25)

plt.plot(pasado['ds'], pasado['yhat'], color='#00784E', linewidth=2, label='Ajuste Histórico')
plt.plot(futuro['ds'], futuro['yhat'], color='#84bda9', linewidth=2, label='Previsión Futura')

plt.scatter(model.history['ds'], model.history['y'], color='black', s=10, label='Datos Reales')

plt.title("Previsión de pedidos omnicanal")
plt.xlabel("Fecha", fontsize=11)
plt.ylabel("Número de líneas", fontsize=11)
plt.show()

# Gráfico por componentes

fig2 = model.plot_components(forecast)
model.plot
# Me queda que solamente se vean los componentes por separado
plt.show()




# MÉTRICAS

df_cv = cross_validation(
    model,
    initial="730 days",
    period="30 days",
    horizon="90 days"
)

def aplicar_crecimiento_cv(row, col_name):
    # En CV, la base histórica es el "cutoff" de la simulación
    dias_diferencia = (row['ds'] - row['cutoff']).days
    if dias_diferencia > 0:
        ano_prediccion = math.ceil(dias_diferencia / 365.25)
        factor_crecimiento = (1 + tasa_crecimiento_anual) ** ano_prediccion
        return row[col_name] * factor_crecimiento
    return row[col_name]

# Aplicamos el crecimiento a los resultados del CV
df_cv['yhat'] = df_cv.apply(lambda r: aplicar_crecimiento_cv(r, 'yhat'), axis=1)
df_cv['yhat_lower'] = df_cv.apply(lambda r: aplicar_crecimiento_cv(r, 'yhat_lower'), axis=1)
df_cv['yhat_upper'] = df_cv.apply(lambda r: aplicar_crecimiento_cv(r, 'yhat_upper'), axis=1)

metricas = performance_metrics(df_cv)

print("\n--- Métricas CV con Tasa de Crecimiento Aplicada ---")
print(metricas.head(10))

df_cv['error_porcentual'] = abs((df_cv['y'] - df_cv['yhat']) / df_cv['y']) * 100

# 2. Ordenamos para obtener los errores más graves
peores_dias = df_cv.sort_values(by='error_porcentual', ascending=False).head(15)

print("\n--- Fechas críticas que están disparando el MAPE ---")
print(peores_dias[['ds', 'cutoff', 'y', 'yhat', 'error_porcentual']])

'''


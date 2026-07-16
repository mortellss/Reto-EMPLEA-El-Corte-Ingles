from prophet import Prophet
import pandas as pd
from prophet.make_holidays import make_holidays_df
import matplotlib.pyplot as plt
from prophet.diagnostics import cross_validation, performance_metrics


#from sqlalchemy import create_engine

#engine = create_engine("sqlite:///omnicanal.db")

# from sqlalchemy import create_engine

df = pd.read_excel("data\Tablas Emplea.xlsx", sheet_name="Pedido Histórico")

# De esta forma lo lee bien Prophet
df = df.rename(columns={"Fecha de venta": "ds", "Total LÍNEAS": "y"})

# Eliminar los NaN porque Prophet no los lee bien
df = df[df["y"] >= 0].copy()
df = df.dropna(subset=["y"])

# Eventos
# La estructura de los eventos:
# {"holiday": nombre, "ds": fecha, "lower_window": , "upper_window": },

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

promociones["ds"] = pd.to_datetime(promociones["ds"])

# No sigue un patrón de que los domingos siempre cierra sino que según el momento del año


# ESTO NO LO PUEDO AÑADIR HASTA QUE NO CREEMOS LA BASE DE DATOS
#calendario = pd.read_sql("""
#    SELECT fecha AS ds, 
#           CASE WHEN abierto = 0 THEN 1 ELSE 0 END AS centro_cerrado
#    FROM calendario_apertura
#""", engine)
#calendario["ds"] = pd.to_datetime(calendario["ds"])

# Añadirlo al DataFrame de entrenamiento
#df = df.merge(calendario, on="ds", how="left")
# df["centro_cerrado"] = df["centro_cerrado"].fillna(0)  # si no hay registro = abierto


model = Prophet(
    holidays=promociones,
    yearly_seasonality=True,
    weekly_seasonality=True,
    daily_seasonality=False,
    #el modelo de estacionalidad multiplicativo implica que
    # el efecto estacional es proporcional al nivel de la serie temporal
    seasonality_mode="multiplicative",
    interval_width=0.95,
    # Número de checkpoints que utilizará para ir validando los datos
    # Aunque tiene una técnica interna que elimina los innecesarios

    # De momento lo dejo en 15 hasta que tenga más datos
    n_changepoints=15
)

model.add_country_holidays(country_name="ES")
#model.add_regressor("centro_cerrado", mode="multiplicative")

model.fit(df)

print("Entrenamiento completado")

# Crear el DataFrame de fechas futuras (90 días = un trimestre)
# include_history=True incluye también las fechas pasadas para poder visualizar
futuro = model.make_future_dataframe(periods=90, freq="D", include_history=True)

# Generar predicciones
forecast = model.predict(futuro)

# Las columnas más importantes del resultado:
# ds          → la fecha
# yhat        → predicción central (el valor más probable)
# yhat_lower  → límite inferior del intervalo de confianza
# yhat_upper  → límite superior del intervalo de confianza

# Ver solo el trimestre futuro
trimestre = forecast[forecast["ds"] > df["ds"].max()][
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
    initial="365 days",
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


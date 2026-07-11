from prophet import Prophet
import pandas as pd

# from sqlalchemy import create_engine

df = pd.read_excel("data\Tablas Emplea_inacabado.xlsx", sheet_name="Hoja2")

# De esta forma lo lee bien Prophet
df = df.rename(columns={"Fecha de venta": "ds", "Total LÍNEAS": "y"})

# Eliminar los NaN porque Prophet no los lee bien
df = df[df["y"] >= 0].copy()
df = df.dropna(subset=["y"])

# Eventos
# La estructura de los eventos:
# {"holiday": nombre, "ds": fecha, "lower_window": , "upper_window": },

eventos = pd.DataFrame([
    {"holiday": "rebajas_enero", "ds": "2025-01-07", "lower_window": 0, "upper_window": 52},
    {"holiday": "dia_sin_iva", "ds": "2025-01-19", "lower_window": 0, "upper_window": 0},
    {"holiday": "semana_deporte", "ds": "2025-01-23", "lower_window": 0, "upper_window": 6},
    {"holiday": "blancolor", "ds": "2025-01-13", "lower_window": 0, "upper_window": 46},

    {"holiday": "limite_48_horas", "ds": "2025-02-06", "lower_window": 0, "upper_window": 3},
    {"holiday": "ofertas_limite", "ds": "2025-02-20", "lower_window": 0, "upper_window": 3},
    {"holiday": "semana_telefonia", "ds": "2025-02-20", "lower_window": 0, "upper_window": 6},
    {"holiday": "20_fotografia", "ds": "2025-02-20", "lower_window": 0, "upper_window": 3},

    {"holiday": "tecnoprecios", "ds": "2025-03-13", "lower_window": 0, "upper_window": 13},
    {"holiday": "supertecnoprecios", "ds": "2025-03-26", "lower_window": 0, "upper_window": 4},

    {"holiday": "8_dias_oro", "ds": "2025-04-03", "lower_window": 0, "upper_window": 10},
    {"holiday": "supertecnoprecios", "ds": "2025-04-24", "lower_window": 0, "upper_window": 3},
    {"holiday": "dias_belleza", "ds": "2025-04-24", "lower_window": 0, "upper_window": 15},

    {"holiday": "ofertas_flash", "ds": "2025-05-08", "lower_window": 0, "upper_window": 3},
    {"holiday": "semana_internet", "ds": "2025-05-12", "lower_window": 0, "upper_window": 6},
    {"holiday": "supertecnoprecios", "ds": "2025-05-22", "lower_window": 0, "upper_window": 3},
    {"holiday": "financiacion_total", "ds": "2025-05-26", "lower_window": 0, "upper_window": 9},
    {"holiday": "tecnoprecios", "ds": "2025-05-26", "lower_window": 0, "upper_window": 9},
    {"holiday": "samsung_days", "ds": "2025-05-29", "lower_window": 0, "upper_window": 3},

    {"holiday": "financiacion_total", "ds": "2025-07-01", "lower_window": 0, "upper_window": 52},
    {"holiday": "samsung_days", "ds": "2025-05-26", "lower_window": 0, "upper_window": 9},
    {"holiday": "ventas_privadas", "ds": "2025-05-26", "lower_window": 0, "upper_window": 9},
    {"holiday": "dias_sin_iva", "ds": "2025-05-26", "lower_window": 0, "upper_window": 9},
    {"holiday": "descuentos_top", "ds": "2025-05-26", "lower_window": 0, "upper_window": 9},
    {"holiday": "rebajas_junio", "ds": "2025-05-26", "lower_window": 0, "upper_window": 9},
    {"holiday": "vuelta_al_cole", "ds": "2025-05-26", "lower_window": 0, "upper_window": 9},
    {"holiday": "yellow_days", "ds": "2025-05-26", "lower_window": 0, "upper_window": 9},
    {"holiday": "discos", "ds": "2025-05-26", "lower_window": 0, "upper_window": 9},
    {"holiday": "tecnoprecios", "ds": "2025-05-26", "lower_window": 0, "upper_+window": 9},
])



# importación de lo necesario

import math
import os
import argparse
from prophet import Prophet
from dotenv import load_dotenv
import pandas as pd
from prophet.make_holidays import make_holidays_df
import matplotlib.pyplot as plt
from prophet.diagnostics import cross_validation, performance_metrics
from sqlalchemy import create_engine, text
import numpy as np
from datetime import datetime
import os
from sqlalchemy import create_engine
from dotenv import load_dotenv

# función que maneja los NaN

def limpiar_regresor(df, columna):
    if columna in df.columns:
        df[columna] = pd.to_numeric(df[columna], errors='coerce')
        df[columna] = df[columna].fillna(0).astype(int)
    else:
        df[columna] = 0
    return df


load_dotenv()

# ============================================================
# PERIODO DE PREDICCIÓN
# ============================================================

parser = argparse.ArgumentParser()

parser.add_argument("--fecha-inicio", required=False)
parser.add_argument("--fecha-fin", required=False)
parser.add_argument("--yearly-seasonality", type=int, default=20)
parser.add_argument("--weekly-seasonality", type=int, default=3)
parser.add_argument("--daily-seasonality", type=str, default="false")
parser.add_argument("--seasonality-mode", type=str, default="multiplicative")
parser.add_argument("--interval-width", type=float, default=0.8)
parser.add_argument("--n-changepoints", type=int, default=50)
parser.add_argument("--tasa-crecimiento", type=float, default=0.0)

args = parser.parse_args()

fecha_inicio_prediccion = (
    pd.to_datetime(args.fecha_inicio)
    if args.fecha_inicio
    else None
)

fecha_fin_prediccion = (
    pd.to_datetime(args.fecha_fin)
    if args.fecha_fin
    else None
)

yearly_seasonality = args.yearly_seasonality
weekly_seasonality = args.weekly_seasonality
daily_seasonality = str(args.daily_seasonality).lower() in {"1", "true", "yes", "verdadero"}
seasonality_mode = args.seasonality_mode if args.seasonality_mode in {"additive", "multiplicative"} else "multiplicative"
interval_width = args.interval_width
n_changepoints = args.n_changepoints
tasa_crecimiento_anual = args.tasa_crecimiento

if fecha_inicio_prediccion is not None and fecha_fin_prediccion is not None:

    if fecha_inicio_prediccion > fecha_fin_prediccion:
        raise ValueError(
            "La fecha de inicio no puede ser posterior a la fecha de fin."
        )

    print(
        f"Periodo seleccionado: "
        f"{fecha_inicio_prediccion.date()} "
        f"-> "
        f"{fecha_fin_prediccion.date()}"
    )
else:

    print(
        "No se ha seleccionado un periodo. "
        "Se utilizará el horizonte completo de 1 año desde el último dato histórico."
    )


DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_SSL_CA = os.getenv("DB_SSL_CA")

engine = create_engine(
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}",
    connect_args={
        "ssl": {
            "ca": DB_SSL_CA
        }
    },
    pool_pre_ping=True
)



# engine = create_engine("mysql+pymysql://root:root2004@localhost/emplea")

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

query_promociones = """
SELECT
    nombre,
    fecha_inicio AS inicio,
    fecha_fin AS fin
FROM promocion
WHERE id_centro = 1
"""
promociones = pd.read_sql(query_promociones, con=engine).to_dict(orient="records")

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
    yearly_seasonality=yearly_seasonality,
    weekly_seasonality=weekly_seasonality,
    daily_seasonality=daily_seasonality,
    seasonality_mode=seasonality_mode,
    interval_width=interval_width,
    n_changepoints=n_changepoints)

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
# Siempre generamos un horizonte completo de 1 año a partir del último valor histórico.
# La interfaz solo mostrará el rango que haya indicado el usuario dentro de ese horizonte.

fecha_max_historica = df_final["ds"].max()
fecha_horizonte_max = fecha_max_historica + pd.DateOffset(days=365)

if fecha_inicio_prediccion is None:
    fecha_inicio_prediccion = fecha_max_historica
if fecha_fin_prediccion is None:
    fecha_fin_prediccion = fecha_horizonte_max

if fecha_inicio_prediccion < fecha_max_historica:
    raise ValueError(
        "La fecha de inicio no puede ser anterior a la última fecha histórica disponible."
    )

if fecha_fin_prediccion > fecha_horizonte_max:
    raise ValueError(
        "La fecha de fin seleccionada supera el horizonte máximo permitido: "
        f"{fecha_horizonte_max.date()}"
    )

if fecha_inicio_prediccion > fecha_fin_prediccion:
    raise ValueError(
        "La fecha de inicio no puede ser posterior a la fecha de fin."
    )

if (fecha_fin_prediccion - fecha_inicio_prediccion).days > 365:
    raise ValueError(
        "El periodo seleccionado no puede superar 1 año. "
        "La predicción máxima es de un año desde el último dato histórico."
    )

future = model.make_future_dataframe(periods=365)

future = future[
    (future["ds"] >= fecha_max_historica) &
    (future["ds"] <= fecha_horizonte_max)
].copy()

future = pd.merge(
    future,
    df_calendario,
    on="ds",
    how="left"
)

future['promo_tier_1'] = future['ds'].isin(fechas_t1).astype(int)
future['promo_tier_2'] = future['ds'].isin(fechas_t2).astype(int)
future['promo_tier_3'] = future['ds'].isin(fechas_t3).astype(int)



for reg in regresores:
    future = limpiar_regresor(future, reg)

forecast = model.predict(future)

# Se aplica el ajuste de crecimiento antes de filtrar el rango visible,
# porque el DataFrame que luego se guarda en BD debe reflejar exactamente
# lo que la interfaz va a mostrar.
fecha_max_historica = df_final['ds'].max()

def aplicar_crecimiento(row, col_name):
    if row['ds'] > fecha_max_historica:
        diferencia = (row['ds'] - fecha_max_historica).days
        prediccion = math.ceil(diferencia / 365.25)
        factor_crecimiento = (1 + tasa_crecimiento_anual) ** prediccion
        return row[col_name] * factor_crecimiento

    return row[col_name]

forecast['yhat'] = forecast.apply(lambda r: aplicar_crecimiento(r, 'yhat'), axis=1)
forecast['yhat_lower'] = forecast.apply(lambda r: aplicar_crecimiento(r, 'yhat_lower'), axis=1)
forecast['yhat_upper'] = forecast.apply(lambda r: aplicar_crecimiento(r, 'yhat_upper'), axis=1)

periodo_mostrado = forecast[
    (forecast["ds"] >= fecha_inicio_prediccion) &
    (forecast["ds"] <= fecha_fin_prediccion)
].copy()

print(
    f"Horizonte generado: {fecha_max_historica.date()} -> {fecha_horizonte_max.date()}"
)
print(
    f"Periodo visible en interfaz: {fecha_inicio_prediccion.date()} -> {fecha_fin_prediccion.date()}"
)

trimestre = periodo_mostrado[
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

def calc_horas_totales(pedidos):
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

    return pedidos * horas_por_pedido + horas_fijas_diarias

# Duplicamos pedidos_previstos en pedidos_acumulados y, si el centro está cerrado,
# sumamos ese valor al día siguiente para no perderlo en la previsión acumulada.
trimestre = trimestre.merge(
    df_calendario[['ds', 'centro_abierto']].rename(columns={'ds': 'fecha'}),
    on='fecha',
    how='left'
)
trimestre['pedidos_acumulados'] = trimestre['pedidos_previstos'].copy()
trimestre['horas_necesarias'] = trimestre['pedidos_previstos'].apply(calc_horas_totales).round().astype(int)
trimestre.loc[trimestre['centro_abierto'] == 0, 'horas_necesarias'] = 0
trimestre['dia_semana'] = trimestre["fecha"].dt.day_name().map({
    "Monday": "Lunes",
    "Tuesday": "Martes",
    "Wednesday": "Miércoles",
    "Thursday": "Jueves",
    "Friday": "Viernes",
    "Saturday": "Sábado",
    "Sunday": "Domingo",
})


inicio_trimestre = trimestre['fecha'].min().replace(day=1)
dias_hasta_primer_domingo = 6 - inicio_trimestre.weekday()
'''
inicio_segunda_semana = inicio_trimestre + pd.Timedelta(
    days=dias_hasta_primer_domingo + 1
)
trimestre["num_semana"] = 1
fechas_desde_segunda_semana = trimestre['fecha'] >= inicio_segunda_semana
trimestre.loc[fechas_desde_segunda_semana, "num_semana"] = (
    (trimestre.loc[fechas_desde_segunda_semana, 'fecha'] - inicio_segunda_semana).dt.days // 7
) + 2
'''


for i in range(len(trimestre) - 1):
    if trimestre.at[i, 'centro_abierto'] == 0:
        trimestre.at[i + 1, 'pedidos_acumulados'] = (
            trimestre.at[i + 1, 'pedidos_acumulados'] + trimestre.at[i, 'pedidos_previstos']
        )

trimestre = trimestre.drop(columns=['centro_abierto'])
trimestre["fecha_generacion"] = datetime.now()
trimestre["id_centro"] = 1
trimestre["horas_ordinarias"] = 0
trimestre["horas_complementarias"] = 0
trimestre["horas_FD"] = 0
trimestre = trimestre[[
    'fecha',
    'dia_semana',
    #'num_semana',
    'pedidos_previstos',
    'pedidos_acumulados',
    'horas_necesarias',
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

print(trimestre.head(30))


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


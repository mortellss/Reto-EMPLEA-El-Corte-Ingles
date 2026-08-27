from pathlib import Path
import sys
from sqlalchemy import create_engine
import collections
from dataclasses import dataclass, field
from datetime import date, timedelta
import importlib.util
import os
import pandas as pd
from ortools.sat.python import cp_model

engine = create_engine("mysql+pymysql://root:root2004@localhost/emplea")


ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

RUTA_OPTIMIZACION = ROOT / "FASE_2 _programacion_lineal" / "optimizacion_FINAL.py"
spec = importlib.util.spec_from_file_location("optimizacion_final", RUTA_OPTIMIZACION)
if spec is None or spec.loader is None:
    raise ImportError(f"No se pudo cargar {RUTA_OPTIMIZACION}")

optimizacion_final = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = optimizacion_final
spec.loader.exec_module(optimizacion_final)

X_HO_1 = optimizacion_final.X_HO[1]
X_HO_2 = optimizacion_final.X_HO[2]
X_HO_3 = optimizacion_final.X_HO[3]
X_HC_1 = optimizacion_final.X_HC[1]
X_HC_2 = optimizacion_final.X_HC[2]
X_HC_3 = optimizacion_final.X_HC[3]
X_HFD_1 = optimizacion_final.X_HFD[1]
X_HFD_2 = optimizacion_final.X_HFD[2]
X_HFD_3 = optimizacion_final.X_HFD[3]

var_values = {
    "X_HO_1": X_HO_1.varValue,
    "X_HO_2": X_HO_2.varValue,
    "X_HO_3": X_HO_3.varValue,
    "X_HC_1": X_HC_1.varValue,
    "X_HC_2": X_HC_2.varValue,
    "X_HC_3": X_HC_3.varValue,
    "X_HFD_1": X_HFD_1.varValue,
    "X_HFD_2": X_HFD_2.varValue,
    "X_HFD_3": X_HFD_3.varValue,
}
#Lo pasamos todo a cuartos de hora porque no admite variables enteras

QH = 4 

def horas_a_qh(h: float) -> int:
    """Convierte horas (float, ej. 6.25) a cuartos de hora (int)."""
    return round(h * QH)
 
def qh_a_horas(qh: int) -> float:
    return qh / QH

JORNADAS_DIARIAS_H = [4, 5, 6, 6.25, 7]
JORNADAS_DIARIAS_QH = sorted({horas_a_qh(h) for h in JORNADAS_DIARIAS_H})

TURNO_MANANA = 0
TURNO_TARDE = 1
TURNOS = [TURNO_MANANA, TURNO_TARDE]

CONTRATOS_ORDINARIAS = {1, 2, 4, 5, 6, 7}
CONTRATOS_COMPLEMENTARIAS = {2, 4, 5, 6, 7}
CONTRATOS_FIJO_DISCONTINUO = {3}
CONTRATOS_JORNADA_EXTRA = {1, 2}

HORAS_SEMANALES_POR_CONTRATO = {
    1: 37.5, 
    2: 35,
    3: 30,
    4: 26,
    5: 16,
    6: 15,
    7: 10
}

@dataclass
class Trabajador:
    id: int
    id_contrato: int
    disponibilidad: str  # "M", "T" o "A"
    horas_semanales: float
    domingos_trabajados: int = 0  # Regla f
    findes_libres: int = 0 # Regla h
    # Regla e
    ultimo_turno_semana_anterior: int | None = None
    racha_dias_consecutivos: list[int] = field(default_factory=list)


query_trabajadores = """
SELECT id_trabajador, activo, id_contrato, disponibilidad, horas_semanales
FROM trabajador
WHERE activo = 1
"""

df_trabajadores = pd.read_sql(query_trabajadores, con=engine)
df_trabajadores['id_trabajador'] = pd.to_numeric(df_trabajadores["id_trabajador"])
df_trabajadores['id_contrato'] = pd.to_numeric(df_trabajadores['id_contrato'])


def cargar_trabajadores() -> dict[int, Trabajador]:
    trabajadores = {}
    for row in df_trabajadores.itertuples(index=False):

        trabajador = Trabajador(
            id=row.id_trabajador,
            id_contrato=row.id_contrato,
            disponibilidad=row.disponibilidad,
            horas_semanales=row.horas_semanales,
        )

        trabajadores[row.id_trabajador] = trabajador

    return trabajadores

'''
IMPRIMIR LA TABLA DE TRABAJADORES


trabajadores = cargar_trabajadores()

df_check = pd.DataFrame([
    {
        "id_trabajador": trabajador.id,
        "id_contrato": trabajador.id_contrato,
        "disponibilidad": trabajador.disponibilidad,
        "horas_semanales": trabajador.horas_semanales,
    }
    for trabajador in trabajadores.values()
])

print(df_check.to_string(index=False))
'''


query_prediccion = """
SELECT fecha, pedidos_acumulados, horas_necesarias
FROM prediccion
"""
df_prediccion = pd.read_sql(query_prediccion, con=engine)
df_prediccion['fecha'] = pd.to_datetime(df_prediccion['fecha'])
df_prediccion['pedidos_acumulados'] = pd.to_numeric(df_prediccion['pedidos_acumulados'], errors='coerce').fillna(0).astype(int)
df_prediccion['horas_necesarias'] = pd.to_numeric(df_prediccion['horas_necesarias'], errors='coerce').fillna(0).astype(int)


query_promociones_BF = """
SELECT fecha_inicio, fecha_fin
FROM promocion
WHERE nombre = "black_friday"
    AND YEAR(fecha_inicio) = YEAR(CURDATE())
"""
df_promocion_BF = pd.read_sql(query_promociones_BF, con=engine)
df_promocion_BF['fecha_inicio'] = pd.to_datetime(df_promocion_BF['fecha_inicio'])


'''
ESTO ESTÁ PENDIENTE


def cargar_valores():
    df_valores = pd.DataFrame([
        "fecha": 
        "tareas":
        "horas_necesarias":
        "X_HO_"
    ])
'''

def tareas_por_prioridades():
    return [
        "MOSTRADOR",
        "GESTIÓN DE MOSTRADOR",
        "RUNNER + DEV A TIENDA",
        "CONSOLA + DEV EDIG"
        "ECI EXPRESS + CLICK&CAR",
        "INFORMAR",
        "INFORMAR LOS ENCARGOS DEL MURO",
        "INFORMAR PALETS + EXPEDICIÓN",
        "HOME DELIVERY",
        "SITE TO STORE",
        "DERIVADAS",
        "SALES FORCE"

    ]

@dataclass
class Calendario:
    dias: list[date]
    cerrado: dict[date, bool]
    semana_de: dict[date, int]
    segmentos_racha: list[list[date]]

def construir_calendario(engine, id_centro: int = 1) -> Calendario:
    """Construye el calendario usando las fechas y cierres almacenados."""
    df_fechas = pd.read_sql(
        """
        SELECT fecha, num_semana
        FROM prediccion
        WHERE id_centro = %(id_centro)s
        ORDER BY fecha
        """,
        con=engine,
        params={"id_centro": id_centro},
    )
    df_calendario = pd.read_sql(
        """
        SELECT fecha, centro_abierto, es_festivo
        FROM calendario
        WHERE id_centro = %(id_centro)s
        ORDER BY fecha
        """,
        con=engine,
        params={"id_centro": id_centro},
    )

    

    if df_fechas.empty:
        return Calendario([], {}, {}, [])

    df_fechas["fecha"] = pd.to_datetime(df_fechas["fecha"]).dt.date
    df_calendario["fecha"] = pd.to_datetime(df_calendario["fecha"]).dt.date
    df_fechas = df_fechas.drop_duplicates("fecha")
    df_calendario = df_calendario.drop_duplicates("fecha", keep="last")
    datos = df_fechas.merge(df_calendario, on="fecha", how="left")

    dias = datos["fecha"].tolist()
    cerrado = {
        fila.fecha: (
            pd.isna(fila.centro_abierto)
            or int(fila.centro_abierto) == 0
            or int(fila.es_festivo) == 1
        )
        for fila in datos.itertuples()
    }
    semana_de = {
        fila.fecha: int(fila.num_semana)
        if not pd.isna(fila.num_semana)
        else (fila.fecha - dias[0]).days // 7 + 1
        for fila in datos.itertuples()
    }

    # Segmentos -> segmentos entre que el centro está cerrado
    segmentos, actual = [], []
    for dia in dias:
        if cerrado[dia]:
            if actual:
                segmentos.append(actual)
                actual = []
        else:
            actual.append(dia)
    if actual:
        segmentos.append(actual)

    return Calendario(dias, cerrado, semana_de, segmentos)


calendario_prediccion = construir_calendario(engine)

def calcular_dia_pico_por_semana(cal:Calendario) -> dict[int, date]:
    horas_por_dia = df_prediccion.groupby(df_prediccion["fecha"].dt.date)["horas_necesarias"].sum()
    dias_abiertos = [d for d in cal.dias if not cal.cerrado[d]]    
    semanas = sorted(set(cal.semana_de[d] for d in dias_abiertos))

    dia_pico_semana = {}
    for sem in semanas:
        dias_semana = [d for d in dias_abiertos if cal.semana_de[d] == sem]
        dia_pico_semana[sem] = max(dias_semana, key = lambda d: horas_por_dia.get(d, 0))
    return dia_pico_semana

def limite_dias_consecutivos(d: date) -> int:
    #Regla (e) + (5.1): 10 días normalmente, 11 desde Black Friday
    black_friday = df_promocion_BF['fecha_inicio'].iloc[0].date()
    fin_periodo = date(d.year if d.month <= 2 else d.year + 1, 2, 28)
    if black_friday <= d <= fin_periodo:
        return 11
    return 10

# AQUÍ EMPIEZA EL MODELO EN CUESTIÓN

@dataclass
class ModeloResultado:
    model: cp_model.CpModel
    work: dict          # (w, d, s) -> BoolVar   (trabaja ese día/turno)
    horas: dict          # (w, d, s) -> IntVar (QH) horas asignadas ese día/turno
    tarea: dict          # (w, d, s, t) -> BoolVar  (asignado a esa tarea)
    turno_semana: dict   # (w, semana) -> IntVar en {SHIFT_MANANA, SHIFT_TARDE}
    desviacion_mensual: dict  # (mes, tipo_hora) -> IntVar (para el objetivo)


def construir_modelo(trabajadores: dict[int, Trabajador],
                     cal: Calendario,
                     tareas: list[str]) -> ModeloResultado:
    
    model = cp_model.CpModel()

    ids_trabajadores = list(trabajadores.keys())
    dias_abiertos = [d for d in cal.dias if not cal.cerrado[d]]
    semanas = sorted(set(cal.semana_de[d] for d in dias_abiertos))

    meses_trimestre = sorted({d.month for d in dias_abiertos})
    x_ho_meses = dict(zip(meses_trimestre, [X_HO_1, X_HO_2, X_HO_3]))

    trabaja = {} # trabaja ese día/turno (bool)
    horas = {} # horas asignadas ese día/turno
    tarea = {} # asignación a tarea concreta

    # Bucle principal 

    for i in ids_trabajadores:
        for d in dias_abiertos:
            for s in TURNOS:
                trabaja[i, d, s] = model.NewBoolVar(f"work_i{i}_d{d}_s{s}")
                horas[i, d, s] = model.NewIntVar(
                    0, max(JORNADAS_DIARIAS_QH), f"horas_i{i}_d{d}_s{s}"
                )
                model.Add(horas[i, d, s] == 0).OnlyEnforceIf(trabaja[i, d, s].Not())
                model.AddAllowedAssignments(
                    [horas[i, d, s]],
                    [[qh] for qh in JORNADAS_DIARIAS_QH],
                ).OnlyEnforceIf(trabaja[i, d, s])

                for t in tareas:
                    tarea[i, d, s, t] = model.NewBoolVar(f"tarea_i{i}_d{d}_s{s}_{t}")


    # Se debe cumplir que para un turno, un trabajador hace una tarea y solo si trabaja
    for i in ids_trabajadores:
        for d in dias_abiertos:
            for s in TURNOS:
                model.Add(
                    sum(tarea[i, d, s, t] for t in tareas) == trabaja[i, d, s]
                )

    # Solamente un turno por día
    for i in ids_trabajadores:
        for d in dias_abiertos:
            model.Add(trabaja[i, d, TURNO_MANANA] + trabaja[i, d, TURNO_TARDE] <= 1)

    # Trabajadores con disponibilidad de tipo A (una semana van de mañanas y otro de tardes)

    turno_semana = {}
    for i in ids_trabajadores:
        disp = trabajadores[i].disponibilidad
        for sem in semanas:
            if disp == "A":
                turno_semana[i, sem] = model.NewIntVar(0, 1, f"turno_i{i}_sem{sem}")


    # Los que no tienen disponibilidad de tipo "A" nunca alternan semana mañana, semana tardes

    for i in ids_trabajadores:
        disp = trabajadores[i].disponibilidad
        for d in dias_abiertos:
            if disp == "M":
                model.Add(trabaja[i, d, TURNO_TARDE] == 0)
            elif disp == "T":
                model.Add(trabaja[i, d, TURNO_MANANA] == 0)
            elif disp == "A":
                sem = cal.semana_de[d]
                model.Add(trabaja[i, d, TURNO_TARDE] == 0).OnlyEnforceIf(
                    turno_semana[i, sem].Not()
                )
                model.Add(trabaja[i, d, TURNO_MANANA] == 0).OnlyEnforceIf(
                                    turno_semana[i, sem]
                                )

    # Los de disponibilidad A deben alternar

    for i in ids_trabajadores:
        if trabajadores[i]. disponibilidad != "A":
            continue
        for sem in semanas:
            if sem + 1 in semanas:
                model.Add(turno_semana[i, sem + 1] == 1 - turno_semana[i, sem])
        if semanas and trabajadores[i].ultimo_turno_semana_anterior is not None:
            model.Add(
                turno_semana[i, semanas[0]] == 1 - trabajadores[i].ultimo_turno_semana_anterior
            )


    # Tipo de horas permitido según el contrato

    horas_ord = {}
    horas_comp = {}
    horas_fd = {}

    for i in ids_trabajadores:
        contrato = trabajadores[i].id_contrato
        for d in dias_abiertos:
            for s in TURNOS:
                horas_ord[i, d, s] = model.NewIntVar(
                    0,  max(JORNADAS_DIARIAS_QH), f"ho_i{i}_d{d}_s{s}"
                )
                horas_comp[i, d, s] = model.NewIntVar(
                    0, max(JORNADAS_DIARIAS_QH), f"hc_i{i}_d{d}_s{s}"
                )
                horas_fd[i, d, s] = model.NewIntVar(
                    0, max(JORNADAS_DIARIAS_QH), f"hfd_i{i}_d{d}_s{s}"
                )

                model.Add(horas_ord[i, d, s] + horas_comp[i, d, s] + horas_fd[i, d, s]
                          == horas[i, d, s])

                """
                Los id_contrato 1 solo pueden hacer horas ordinarias, 
                Los id_contrato 3 solo pueden hacer horas de FD
                Y el resto pueden hacer horas ordinarias y horas complementarias
                """

                if contrato not in CONTRATOS_ORDINARIAS:
                    model.Add(horas_ord[i, d, s] == 0)
                if contrato not in CONTRATOS_COMPLEMENTARIAS:
                    model.Add(horas_comp[i, d, s] == 0)
                if contrato not in CONTRATOS_FIJO_DISCONTINUO:
                    model.Add(horas_fd[i, d, s] == 0)

    # Ahora la restricción de que las horas ordinarias deben sumar las horas semanales dictadas

    for i in ids_trabajadores:
        contrato = trabajadores[i].id_contrato
        objetivo_qh = horas_a_qh(trabajadores[i].horas_semanales)
        for sem in semanas:
            dias_semana = [d for d in dias_abiertos if cal.semana_de[d] == sem]

            if contrato in CONTRATOS_ORDINARIAS:
                total_ordinarias_semana = sum(
                                    horas_ord[i, d, s] for d in dias_semana for s in TURNOS
                                )
                model.Add(total_ordinarias_semana == objetivo_qh)

            if contrato in CONTRATOS_COMPLEMENTARIAS:
                total_complementarias_semana = sum(
                    horas_comp[i, d, s] for d in dias_semana for s in TURNOS
                )
                model.Add(total_complementarias_semana * 100 <= objetivo_qh * 60)

    horas_necesarias_por_dia = {row["fecha"].date(): row["horas_necesarias"] for _, row in df_prediccion.iterrows()}

    for _, row in df_prediccion.iterrows():
        fecha = row['fecha'].date()
        horas_necesarias = row['horas_necesarias']

    # El tope por día es que las horas ordinarias debe ser <= horas necesarias al día

    horas_necesarias_por_dia = {
        row["fecha"]:row["horas_necesarias"] for _, row in df_prediccion.iterrows()
    }

    for d in dias_abiertos:
        h_nec = horas_necesarias_por_dia.get(d)
        if h_nec is None:
            continue
        horas_ord_dia = sum(
            horas_ord[i, d, s] for i in ids_trabajadores for s in TURNOS
        )

        model.Add(horas_ord_dia <= horas_a_qh(h_nec))

    # Mínimo la persona tiene que descansar 1,5 días - 3 medias jornadas seguidas.
    # CAMBIAR
    '''
    for i in ids_trabajadores:
        for segmento in cal.segmentos_racha:
            limite = limite_dias_consecutivos(segmento[0])
            ventana = limite + 1
            for i in range(len(segmento) - ventana + 1):
                dias_ventana = segmento[i : i + ventana]
                trabaja_dia = []
                for d in dias_ventana:
                    trabaja_d = model.NewBoolVar(f"trabaja_i{i}_d{d}")
                    model.AddMaxEquality(
                        trabaja_d, [trabaja[i, d, TURNO_MANANA], trabaja[i, d, TURNO_TARDE]]
                    )
                    trabaja_dia.append(trabaja_dia)
                model.Add(sum(trabaja_dia) <= limite)
    '''

    # Límite de 10/11 días trabajados

    UMBRAL_MEDIO_DIA_QH = horas_a_qh(6.15)

    for i in ids_trabajadores:
        for idx_segmento, segmento in enumerate(cal.segmentos_racha):
            limite = limite_dias_consecutivos(segmento[0])
            ventana = limite + 1
            tope_unidades = 2 * limite # Ahora un día son 2 mitades

            unidad_dia = {}
            for d in segmento:
                trabaja_d = model.NewBoolVar(f"trabaja_i{i}_d{d}")
                model.AddMaxEquality(
                    trabaja_d, [trabaja[i, d, TURNO_MANANA], trabaja[i, d, TURNO_TARDE]]
                )

                horas_dia_total = horas[i, d, TURNO_MANANA] + horas[i, d, TURNO_TARDE]

                es_dia_completo = model.NewBoolVar(f"completo_i{i}_d{d}")
                model.Add(horas_dia_total >= UMBRAL_MEDIO_DIA_QH).OnlyEnforceIf(es_dia_completo)
                model.Add(horas_dia_total < UMBRAL_MEDIO_DIA_QH).OnlyEnforceIf(es_dia_completo.Not())
 
                u = model.NewIntVar(0, 2, f"unidad_i{i}_d{d}")
                model.Add(u == 0).OnlyEnforceIf(trabaja_d.Not())
                model.Add(u == 1).OnlyEnforceIf([trabaja_d, es_dia_completo.Not()])
                model.Add(u == 2).OnlyEnforceIf([trabaja_d, es_dia_completo])
                unidad_dia[d] = u

                prefijo_constante: list[int] = []
            if idx_segmento == 0 and segmento[0] == cal.dias[0]:
                # Como mucho los últimos `limite` días del arrastre; el
                # resto no puede llegar a caer dentro de ninguna ventana
                # de este trimestre.
                prefijo_constante = trabajadores[i].racha_dias_consecutivos[-limite:]
 
            secuencia = [("const", v) for v in prefijo_constante] + [
                ("var", d) for d in segmento
            ]

            for i in range(len(secuencia) - ventana + 1):
                tramo = secuencia[i : i + ventana]
                if not any(tipo == "var" for tipo, _ in tramo):
                    continue
                terminos = [
                    unidad_dia[val] if tipo == "var" else val
                    for tipo, val in tramo
                ]
                model.Add(sum(terminos) <= tope_unidades)


    #Máximo de domingos/festivos trabajados al año

    domingos_o_festivos = [d for d in dias_abiertos if d.weekday() == 6]  # TODO: + festivos
    for i in ids_trabajadores:
        trabaja_domingo = []
        for d in domingos_o_festivos:
            td = model.NewBoolVar(f"domingo_w{i}_d{d}")
            model.AddMaxEquality(td, [trabaja[i, d, TURNO_MANANA], trabaja[i, d, TURNO_TARDE]])
            trabaja_domingo.append(td)
        model.Add(
            sum(trabaja_domingo) + trabajadores[i].domingos_trabajados_ytd <= 22
        )
    

    # --- (IX) 9 fines de semana libres al año para jornada >75% (regla h) ---
    # TODO: variables booleanas "finde libre" (sáb + dom sin trabajar) y
    # acumular con finde_libres_ytd, solo para contratos en CONTRATOS_JORNADA_ALTA.
    
     # --- (VI) Descanso mínimo de 1,5 días por semana (regla d) ---
    # TODO: modelar "1,5 día" como al menos 3 medias-jornadas de descanso
    # dentro de la semana (ver discusión de unidades en el mensaje anterior),
    # + casos especiales d.i / d.ii según si el domingo cierra o no.


    # --------------------------------------------------------------
    # 4.3 RESTRICCIONES / OBJETIVO BLANDOS
    # --------------------------------------------------------------
 
    desviacion_mensual = {}
    # Por cada mes del trimestre, comparamos el total de horas_ord
    # asignadas contra tu variable X_HO_mes correspondiente, con una
    # variable de desviación en vez de una igualdad estricta: así, si no
    # cuadra exactamente, el modelo sigue siendo factible y el
    # validador simplemente avisa del desfase (apartado 3).
    for mes in meses_trimestre:
        dias_mes = [d for d in dias_abiertos if d.month == mes]
        total_ord_mes_qh = sum(
            horas_ord[w, d, s]
            for w in ids_trabajadores
            for d in dias_mes
            for s in TURNOS
        )
        objetivo_mes_qh = horas_a_qh(X_HO[mes])
 
        desviacion = model.NewIntVar(0, 1_000_000, f"desv_HO_mes{mes}")
        # |total - objetivo| expresado con dos desigualdades (CP-SAT no
        # tiene valor absoluto directo sobre expresiones lineales).
        model.Add(total_ord_mes_qh - objetivo_mes_qh <= desviacion)
        model.Add(objetivo_mes_qh - total_ord_mes_qh <= desviacion)
        desviacion_mensual[mes, "ordinarias"] = desviacion
 
    # TODO: cuando tengas también X_HC_mes / X_HFD_mes guardados, repetir
    # este mismo patrón sumando horas_comp / horas_fd en vez de horas_ord.
 
    terminos_objetivo = list(desviacion_mensual.values())
    # TODO: añadir también penalizaciones por incumplir la regla de
    # prioridad (a) al asignar tareas (p. ej. bonus si se respeta el
    # desempate "tarea que más trabajadores necesite").
 
    if terminos_objetivo:
        model.Minimize(sum(terminos_objetivo))
 
    return ModeloResultado(model, trabaja, horas, tarea, turno_semana, desviacion_mensual)



def resolver(resultado: ModeloResultado, tiempo_limite_s: int = 120) -> pd.DataFrame:
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = tiempo_limite_s
    solver.parameters.num_search_workers = 8
 
    # Warm-start: si ya tienes una solución generada por el algoritmo
    # heurístico/voraz que describiste, puedes cargarla aquí con
    # model.AddHint(...) para acelerar mucho la búsqueda.
    # TODO: cargar hints desde la solución del algoritmo greedy.
 
    status = solver.Solve(resultado.model)
 
    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        raise RuntimeError(f"No se encontró solución factible (status={status})")
 
    filas = []
    for (w, d, s), var in resultado.work.items():
        if solver.Value(var):
            h = qh_a_horas(solver.Value(resultado.horas[w, d, s]))
            tareas_asignadas = [
                t
                for (ww, dd, ss, t), tv in resultado.tarea.items()
                if ww == w and dd == d and ss == s and solver.Value(tv)
            ]
            filas.append(
                {
                    "trabajador": w,
                    "fecha": d,
                    "turno": "mañana" if s == TURNO_MANANA else "tarde",
                    "horas": h,
                    "tarea": tareas_asignadas[0] if tareas_asignadas else None,
                }
            )
 
    return pd.DataFrame(filas)



if __name__ == "__main__":
    # --- 1. Cargar datos ---
    trabajadores = cargar_trabajadores()                
    # TODO: sustituir por tus tres variables reales (ya calculadas en la
    # fase de optimizacion_FINAL), en orden cronológico de mes.
    X_HO_mes1 = X_HO_1
    X_HO_mes2 = X_HO_2
    X_HO_mes3 = X_HO_3
    tareas_por_dia = tareas_por_prioridades()
 
    # --- 2. Calendario del trimestre ---
    cal = construir_calendario(engine)
 
    # --- 3. Modelo y resolución ---
    resultado = construir_modelo(
        trabajadores, cal, tareas_por_dia
    )
    df_solucion = resolver(resultado)
 
  
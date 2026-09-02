#CAPACIDAD_MAXIMA_TAREA porque se pasa
# Máximo de 1 por tarea
# Meter a fijos discontinuos
# se tiene en cuenta el contrato semanal? (las )

import argparse
from pathlib import Path
import sys
from sqlalchemy import create_engine, text, bindparam
import collections
from dataclasses import dataclass, field
from datetime import date, timedelta
import importlib.util
import pandas as pd
from ortools.sat.python import cp_model
from dotenv import load_dotenv
import os

PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")
load_dotenv(PROJECT_ROOT / "interfaz" / "backend" / ".env")
'''
load_dotenv()

usuario = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")

engine = create_engine(
    f"mysql+pymysql://{usuario}:{password}@localhost/emplea"
)
'''

import os
from sqlalchemy import create_engine


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

parser = argparse.ArgumentParser()
parser.add_argument("--fecha-inicio", required=False)
parser.add_argument("--fecha-fin", required=False)
args = parser.parse_args()

fecha_inicio_plan = pd.to_datetime(args.fecha_inicio) if args.fecha_inicio else None
fecha_fin_plan = pd.to_datetime(args.fecha_fin) if args.fecha_fin else None

if fecha_inicio_plan is not None and fecha_fin_plan is not None and fecha_inicio_plan > fecha_fin_plan:
    raise ValueError("La fecha de inicio no puede ser posterior a la fecha de fin.")

TURNO_MANANA = 0
TURNO_TARDE = 1
TURNOS = [TURNO_MANANA, TURNO_TARDE]

CONTRATOS_ORDINARIAS = {1, 2, 4, 5, 6, 7}
CONTRATOS_COMPLEMENTARIAS = {2, 4, 5, 6, 7}
CONTRATOS_FIJO_DISCONTINUO = {3}
CONTRATOS_JORNADA_EXTRA = {1, 2}

TURNOS_NORMALES_MES_CONTRATO = {
    2: 6 * 4,
    4: 5 * 4,
    5: 3 * 4,
    6: 3 * 4,
    7: 2 * 4,
}

# Estas son horas aproximadas -> CAMBIAR PARA QUE SEA MÁS EXACTO

HORAS_POR_TURNO_CONTRATO = {
    1: 6.25,  # 6 turnos/semana -> 37.5 h/semana
    2: 6.25,  # 6 turnos/semana -> 37.5 h/semana
    4: 5.0,   # 5 turnos/semana -> 25 h/semana
    5: 5.0,   # 3 turnos/semana -> 15 h/semana
    6: 5.0,   # 3 turnos/semana -> 15 h/semana
    7: 5.0,   # 2 turnos/semana -> 10 h/semana
}

# Capacidad del máximo de trabajadores realizando la tarea a la vez
CAPACIDAD_MAXIMA_TAREA = {
    "MOSTRADOR": 4,
    "INFORMAR": 2,
    "INFORMAR DE LOS ENCARGOS DEL MURO": 2,
    "HOME DELIVERY": 2,
    "SITE TO STORE": 2,
    "ECI EXPRESS + CLICK&CAR": 2,
    "RUNNER + DEV A TIENDA": 2,
    "DERIVADAS": 1,
    "GESTIÓN MOSTRADOR": 1,
    "INFORMAR PALETS/EXPEDICIÓN": 2,
    "CONSOLA + DEV. EDIG": 2,
}

CAPACIDAD_MAXIMA_DEFECTO = 4

CAPACIDAD_MINIMA_TAREA = {
    "MOSTRADOR": 1,
    "RUNNER + DEV A TIENDA": 1,
}

CAPACIDAD_MINIMA_DEFECTO = 0

def capacidad_maxima(tareas):
   
    tarea_nombre =  {
       t.nombre: id_tarea
       for id_tarea, t in tareas.items() 
    }

    capacidad = {}
    nombres_sin_encontrar = []
    for nombre, cap in CAPACIDAD_MAXIMA_TAREA.items():
        id_tarea = tarea_nombre.get(nombre)
        if id_tarea is None:
            nombres_sin_encontrar.append(nombre)
        else:
            capacidad[id_tarea] = cap

    if nombres_sin_encontrar:
        disponibles = ', '.join(f"'{t.nombre}'" for t in tareas.values())
        print(f"Aviso: no se encontraron en `tarea` estos nombres: "
                f"{', '.join(repr(n) for n in nombres_sin_encontrar)}. "
                f"Se quedan con el límite por defecto de {CAPACIDAD_MAXIMA_DEFECTO} "
                f"persona(s) por turno. Nombres disponibles en la tabla: {disponibles}")
    return capacidad

def capacidad_minima(tareas):

    tarea_nombre = {
        t.nombre: id_tarea
        for id_tarea, t in tareas.items()
    }

    capacidad = {}
    nombres_sin_encontrar = []
    for nombre, cap in CAPACIDAD_MINIMA_TAREA.items():
        id_tarea = tarea_nombre.get(nombre)
        if id_tarea is None:
            nombres_sin_encontrar.append(nombre)
        else:
            capacidad[id_tarea] = cap

    if nombres_sin_encontrar:
        disponibles = ', '.join(f"'{t.nombre}'" for t in tareas.values())
        print(f"Aviso: no se encontraron en `tarea` estos nombres: "
                f"{', '.join(repr(n) for n in nombres_sin_encontrar)}. "
                f"Se quedan con el mínimo por defecto de {CAPACIDAD_MINIMA_DEFECTO} "
                f"persona(s) por turno. Nombres disponibles en la tabla: {disponibles}")
    return capacidad

   


opciones_duracion_qh = {
        1: [25],
        2: [20, 28],
        3: [20, 24],
        4: [16, 20],
        5: [16, 20, 24],
        6: [20],
        7: [20]
    }

QH = 4 

@dataclass
class Trabajador:
    id_trabajador: int
    nombre: str
    disponibilidad: str
    id_contrato: int
    fijo_discontinuo: bool
    dias_trabajados_seguidos: int
    domingos_trabajados: int
    

@dataclass
class Calendario:
    dias: list[date]
    cerrado: dict[date, bool]
    semana_de: dict[date, int]
    segmentos_racha: list[list[date]]
    horas_necesarias: dict[date,float]

@dataclass
class Tareas:
    id_tarea: int
    nombre: str

def horas_a_qh(h: float) -> int:
    return round(h * QH)
 
def qh_a_horas(qh: int) -> float:
    return qh / QH

def cargar_trabajadores():
    query_trabajadores = """
    SELECT id_trabajador, nombre, disponibilidad, id_contrato, fijo_discontinuo
    FROM trabajador
    WHERE activo = 1
    """

    query_calendario_trabajadores = """
        SELECT id_trabajador, estado
        FROM calendario_trabajadores
    """

    df_trabajadores = pd.read_sql(query_trabajadores, con=engine)
    df_trabajadores['id_trabajador'] = pd.to_numeric(df_trabajadores["id_trabajador"])
    df_trabajadores['id_contrato'] = pd.to_numeric(df_trabajadores["id_contrato"])
    #df_trabajadores['horas_semanales'] = pd.to_numeric(df_trabajadores["horas_semanales"])
    df_trabajadores['fijo_discontinuo'] = pd.to_numeric(df_trabajadores["fijo_discontinuo"])

    df_calendario_trabajadores = pd.read_sql(query_calendario_trabajadores, con=engine)
    df_trabajadores['id_trabajador'] = pd.to_numeric(df_trabajadores["id_trabajador"])

    datos = df_trabajadores.merge(df_calendario_trabajadores, how="left", on="id_trabajador")


    trabajadores = {}
    for row in df_trabajadores.itertuples(index=False):
        trabajador = Trabajador(
            id_trabajador=row.id_trabajador,
            nombre=row.nombre,
            disponibilidad=row.disponibilidad,
            id_contrato = row.id_contrato,
            dias_trabajados_seguidos= 0,
            domingos_trabajados = 0,
            fijo_discontinuo=bool(row.fijo_discontinuo),
        )

        trabajadores[row.id_trabajador] = trabajador
    return trabajadores

def obtener_horizonte_prediccion():
    if fecha_inicio_plan is not None or fecha_fin_plan is not None:
        fecha_inicio = fecha_inicio_plan.date() if fecha_inicio_plan is not None else None
        fecha_fin = fecha_fin_plan.date() if fecha_fin_plan is not None else None
        if fecha_inicio is not None and fecha_fin is not None and fecha_inicio > fecha_fin:
            raise ValueError("La fecha de inicio no puede ser posterior a la fecha de fin.")
        return fecha_inicio, fecha_fin

    query = """
        SELECT MIN(fecha) AS fecha_inicio, MAX(fecha) AS fecha_fin
        FROM prediccion
        WHERE fecha IS NOT NULL
    """

    df = pd.read_sql(query, con=engine)

    if df.empty or pd.isna(df.iloc[0]["fecha_inicio"]) or pd.isna(df.iloc[0]["fecha_fin"]):
        return None

    fecha_inicio = pd.to_datetime(df.iloc[0]["fecha_inicio"]).date()
    fecha_fin = pd.to_datetime(df.iloc[0]["fecha_fin"]).date()

    return fecha_inicio, fecha_fin


def cargar_calendario():
    query_calendario = """
        SELECT fecha, centro_abierto
        FROM calendario
        ORDER BY fecha
    """

    query_prediccion = """
        SELECT fecha, pedidos_acumulados, horas_necesarias, num_semana
        FROM prediccion
        ORDER BY fecha
    """

    query_calendario_trabajadores = """
        SELECT fecha, id_trabajador, estado
        FROM calendario_trabajadores
        ORDER BY fecha
    """
    
    df_calendario = pd.read_sql(query_calendario, con=engine)
    df_calendario["fecha"] = pd.to_datetime(df_calendario["fecha"]).dt.date

    df_prediccion = pd.read_sql(query_prediccion, con=engine)
    df_prediccion["fecha"] = pd.to_datetime(df_prediccion["fecha"]).dt.date
    df_prediccion["pedidos_acumulados"] = pd.to_numeric(df_prediccion["pedidos_acumulados"])
    df_prediccion["horas_necesarias"] = pd.to_numeric(df_prediccion["horas_necesarias"])
    df_prediccion["num_semana"] = pd.to_numeric(df_prediccion["num_semana"])

    horizonte = obtener_horizonte_prediccion()
    if horizonte is not None:
        fecha_inicio, fecha_fin = horizonte
        df_prediccion = df_prediccion[
            (df_prediccion["fecha"] >= fecha_inicio) &
            (df_prediccion["fecha"] <= fecha_fin)
        ].copy()

    df_calendario_trabajadores = pd.read_sql(query_calendario_trabajadores, con=engine)
    df_calendario_trabajadores["fecha"] = pd.to_datetime(df_calendario_trabajadores["fecha"]).dt.date

    d = df_calendario.merge(df_calendario_trabajadores, how="left", on="fecha")

    datos = df_prediccion.merge(d, how="left", on="fecha")
    datos = datos.drop_duplicates("fecha")

    dias = datos["fecha"].tolist()
    cerrado = {
        fila.fecha: (
            pd.isna(fila.centro_abierto)
            or int(fila.centro_abierto) == 0
        )
        for fila in datos.itertuples()
    }
    semana_de = {
        fila.fecha: int(fila.num_semana)
        if not pd.isna(fila.num_semana)
        else (fila.fecha - dias[0]).days // 7 + 1
        for fila in datos.itertuples()
    }
    horas_necesarias = {
            fila.fecha: float(fila.horas_necesarias) if not pd.isna(fila.horas_necesarias) else 0.0
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

    return Calendario(dias, cerrado, semana_de, segmentos, horas_necesarias)

def cargar_estado_trabajador():
    query_calendario = """
            SELECT fecha, centro_abierto
            FROM calendario
            ORDER BY fecha
        """
    
    query_calendario_trabajadores = """
        SELECT fecha, id_trabajador, estado
        FROM calendario_trabajadores
        ORDER BY fecha
    """

    df_calendario = pd.read_sql(query_calendario, con=engine)
    df_calendario["fecha"] = pd.to_datetime(df_calendario["fecha"]).dt.date

    df_calendario_trabajadores = pd.read_sql(query_calendario_trabajadores, con=engine)
    df_calendario_trabajadores["fecha"] = pd.to_datetime(df_calendario_trabajadores["fecha"]).dt.date
    df_calendario_trabajadores["id_trabajador"] = pd.to_numeric(df_calendario_trabajadores["id_trabajador"])

    datos = df_calendario.merge(df_calendario_trabajadores, on="fecha", how="inner")

    estados_dict = {
        (fila.id_trabajador, fila.fecha): int(fila.estado)
        for fila in datos.itertuples()
    }
    
    return estados_dict

def cargar_tareas():

    query_tareas = """
        SELECT id_tarea, nombre
        FROM tarea
        WHERE activa = 1 
    """
    df_tarea = pd.read_sql(query_tareas, con=engine)
    df_tarea["id_tarea"] = pd.to_numeric(df_tarea["id_tarea"])
    #df_tarea["horas_min"] = pd.to_numeric(df_tarea["horas_min"])
    #df_tarea["horas_max"] = pd.to_numeric(df_tarea["horas_max"])

    tareas = {}
    for row in df_tarea.itertuples(index=False):
        tarea = Tareas(
            id_tarea=row.id_tarea,
            nombre=row.nombre
        )
        tareas[row.id_tarea] = tarea
    return tareas

def cargar_habilidades():
    query_habilidades = """
        SELECT id_trabajador, id_tarea 
        FROM trabajador_tarea
    """
    df_habilidades = pd.read_sql(query_habilidades, con=engine)
    
    habilidades = {}
    for row in df_habilidades.itertuples(index=False):
        t = int(row.id_trabajador)
        tar = int(row.id_tarea)
        
        if t not in habilidades:
            habilidades[t] = []
        habilidades[t].append(tar)
        
    return habilidades


def cargar_cambios_forzados():
    query = """
        SELECT
            cp.id_version,
            cp.fecha,
            cp.id_tarea,
            cp.trabajador_anterior,
            cp.trabajador_nuevo,
            cp.turno,
            cp.motivo,
            cp.forzado
        FROM cambios_planificacion cp
        INNER JOIN (
            SELECT id_version
            FROM planificacion_version
            WHERE activa = 1
            ORDER BY id_version DESC
            LIMIT 1
        ) pv
            ON cp.id_version = pv.id_version
        WHERE cp.forzado = 1
        ORDER BY cp.fecha, cp.turno, cp.id_tarea
    """

    df = pd.read_sql(query, con=engine)

    if df.empty:
        return []

    cambios = []
    for row in df.itertuples(index=False):
        if pd.isna(row.trabajador_nuevo):
            continue

        cambios.append({
            "id_version": int(row.id_version),
            "fecha": pd.to_datetime(row.fecha).date(),
            "id_tarea": int(row.id_tarea),
            "trabajador_anterior": int(row.trabajador_anterior),
            "trabajador_nuevo": int(row.trabajador_nuevo),
            "turno": int(row.turno),
            "motivo": row.motivo,
            "forzado": bool(row.forzado),
        })

    return cambios


def cargar_horas_mensuales():
    query = """
        SELECT mes, horas_ordinarias, horas_complementarias, horas_fd
        FROM horas_mensuales
        ORDER BY mes
    """

    df = pd.read_sql(query, con=engine)

    if df.empty:
        return {}, {}, {}

    horas_ordinarias = {
        int(row.mes): int(row.horas_ordinarias)
        for row in df.itertuples(index=False)
    }
    horas_complementarias = {
        int(row.mes): int(row.horas_complementarias)
        for row in df.itertuples(index=False)
    }
    horas_fd = {
        int(row.mes): int(row.horas_fd)
        for row in df.itertuples(index=False)
    }

    return horas_ordinarias, horas_complementarias, horas_fd


def crear_version_planificacion(dias_abiertos):
    fecha_inicio = min(dias_abiertos)
    fecha_fin = max(dias_abiertos)

    with engine.begin() as conexion:
        conexion.execute(
            text("UPDATE planificacion_version SET activa = 0 WHERE activa = 1")
        )

        conexion.execute(
            text("""
                INSERT INTO planificacion_version (fecha_generacion, fecha_inicio, fecha_fin, activa)
                VALUES (NOW(), :fecha_inicio, :fecha_fin, 1)
            """),
            {"fecha_inicio": fecha_inicio, "fecha_fin": fecha_fin},
        )

        id_version = conexion.execute(
            text("SELECT LAST_INSERT_ID()")
        ).scalar_one()

    return int(id_version)


def preparar_version_activa(id_version, fecha_inicio, fecha_fin):
    """Conserva en la nueva versión los días que no se están regenerando."""
    with engine.begin() as conexion:
        conexion.execute(
            text("""
                UPDATE calendarizacion
                SET id_version = :id_version
                WHERE fecha < :fecha_inicio OR fecha > :fecha_fin
            """),
            {
                "id_version": id_version,
                "fecha_inicio": fecha_inicio,
                "fecha_fin": fecha_fin,
            },
        )
        conexion.execute(
            text("""
                DELETE FROM calendarizacion
                WHERE fecha BETWEEN :fecha_inicio AND :fecha_fin
            """),
            {
                "fecha_inicio": fecha_inicio,
                "fecha_fin": fecha_fin,
            },
        )


def guardar_calendarizacion(solver, calendario, ids_trabajadores, ids_tareas,
                             dias_abiertos, turnos_asignados, tarea_asignada,
                             id_version):
    
    filas = []
    for d in dias_abiertos:
        num_semana = calendario.semana_de[d]
        for t in ids_trabajadores:
            for s in TURNOS:
                if solver.Value(turnos_asignados[(t, d, s)]) == 1:
                    tarea_realizada = None
                    for id_tarea in ids_tareas:
                        if solver.Value(tarea_asignada[(t, d, id_tarea)]) == 1:
                            tarea_realizada = id_tarea
                            break

                    if tarea_realizada is None:
                        continue

                    filas.append({
                        "fecha": d,
                        "num_semana": num_semana,
                        "id_tarea": tarea_realizada,
                        "id_trabajador": t,
                        "turno": s,
                        "id_version": id_version,
                    })

    df_resultado = pd.DataFrame(
        filas, columns=["fecha", "num_semana", "id_tarea", "id_trabajador", "turno", "id_version"]
    )

    if df_resultado.empty:
        print("No hay asignaciones que guardar en calendarizacion.")
        return

    with engine.begin() as conexion:
        df_resultado.to_sql("calendarizacion", con=conexion, if_exists="append", index=False)

    print(f"Guardadas {len(df_resultado)} filas en calendarizacion "
          f"({dias_abiertos[0]} a {dias_abiertos[-1]}), version={id_version}.")


def crear_calendario_base(trabajadores, calendario, calendario_trabajadores, tareas, habilidades, objetivo_horas_por_mes, objetivo_horas_hc_por_mes=None, objetivo_horas_fd_por_mes=None, cambios_forzados=None):

    ids_trabajadores = list(trabajadores.keys())
    
    dias_abiertos = [d for d in calendario.dias if not calendario.cerrado[d]]
    cambios_forzados = cambios_forzados or []
    
    # Inicializamos el modelo
    modelo = cp_model.CpModel()

    # Definimos las variables decisión

    turnos_asignados = {}
    for t in ids_trabajadores:
        for d in dias_abiertos:
            for s in TURNOS:
                nombre_var = f'T{t}_D{d}_S{s}'
                turnos_asignados[(t, d, s)] = modelo.NewBoolVar(nombre_var)

    tarea_asignada = {}
    trabaja = {}
    ids_tareas = list(tareas.keys())

    #asignaciones_sin_habilidad = []

    for t in ids_trabajadores:
        tareas_permitidas = habilidades.get(t, [])
        
        for d in dias_abiertos:
            for id_tarea in ids_tareas:
                nombre_var_tarea = f'Tarea_T{t}_D{d}_Tar{id_tarea}'     
                tarea_asignada[(t, d, id_tarea)] = modelo.NewBoolVar(nombre_var_tarea)          
                #var_tarea = modelo.NewBoolVar(nombre_var_tarea)
                #tarea_asignada[(t, d, id_tarea)] = var_tarea
                #tarea_asignada[(t, d, id_tarea)] = modelo.NewBoolVar(nombre_var_tarea)
            
                if id_tarea not in tareas_permitidas:
                    modelo.Add(tarea_asignada[(t, d, id_tarea)] == 0)
                    #asignaciones_sin_habilidad.append(var_tarea)

            tareas_del_dia = [tarea_asignada[(t, d, id_tarea)] for id_tarea in ids_tareas]

            var_trabaja = modelo.NewBoolVar(f'Aux_Trabaja_T{t}_D{d}')
            modelo.Add(var_trabaja == sum(turnos_asignados[(t, d, s)] for s in TURNOS))
            trabaja[(t, d)] = var_trabaja
            
            modelo.Add(sum(tareas_del_dia) == 1).OnlyEnforceIf(var_trabaja)
            modelo.Add(sum(tareas_del_dia) == 0).OnlyEnforceIf(var_trabaja.Not())
    
    # Cambios forzados respecto a la planificación anterior
    if cambios_forzados:
        print(f"Se aplican {len(cambios_forzados)} cambios forzados desde la planificación anterior.")

        for cambio in cambios_forzados:
            fecha = cambio["fecha"]
            turno = cambio["turno"]
            id_tarea = cambio["id_tarea"]
            trabajador_nuevo = cambio["trabajador_nuevo"]
            trabajador_anterior = cambio["trabajador_anterior"]

            if fecha not in calendario.dias or fecha not in dias_abiertos:
                continue

            if trabajador_nuevo not in ids_trabajadores or turno not in TURNOS:
                continue

            if id_tarea not in ids_tareas:
                continue

            modelo.Add(turnos_asignados[(trabajador_nuevo, fecha, turno)] == 1)
            modelo.Add(tarea_asignada[(trabajador_nuevo, fecha, id_tarea)] == 1)

            if trabajador_anterior in ids_trabajadores and trabajador_anterior != trabajador_nuevo:
                modelo.Add(turnos_asignados[(trabajador_anterior, fecha, turno)] == 0)
                modelo.Add(tarea_asignada[(trabajador_anterior, fecha, id_tarea)] == 0)

    # RESTRICCIÓN
    # - Un trabajador solo puede hacer un máximo de un turno por día
    for t in ids_trabajadores:
        for d in dias_abiertos:
            turnos_al_dia = [turnos_asignados[(t, d, s)] for s in TURNOS]
            modelo.AddAtMostOne(turnos_al_dia)
    
    
    # RESTRICCION 
    # - Los trabajadores que tienen disponibilidad "M" pueden ir por la mañana
    # - Si tiene disponibilidad "T" solo puede ir por la tarde
    
    for t in ids_trabajadores:
        disp = trabajadores[t].disponibilidad
        for d in dias_abiertos:
            if disp == "M":
                modelo.Add(turnos_asignados[(t, d, TURNO_TARDE)] == 0)
            elif disp == "T":
                modelo.Add(turnos_asignados[(t, d, TURNO_MANANA)] == 0)

    # RESTRICCION
    # - Que haya más trabajadores por la mañana que por la tarde
    for d in dias_abiertos:
        total_manana = sum(turnos_asignados[(t, d, TURNO_MANANA)] for t in ids_trabajadores)
        total_tarde = sum(turnos_asignados[(t, d, TURNO_TARDE)] for t in ids_trabajadores)
        modelo.Add(total_manana >= total_tarde + 1)


    # RESTRICCION
    # - Si la persona tiene disponibilidad "A" - debe de ir una semana de tardes y el otra de mañanas

    semanas_completas = {}
    for d in dias_abiertos:
        num_semana = calendario.semana_de[d]
        if num_semana not in semanas_completas:
            semanas_completas[num_semana] = []
        semanas_completas[num_semana].append(d)

    contador_alternos = 0
    
    for t in ids_trabajadores:
        if trabajadores[t].disponibilidad != "A":
            continue
        empieza_manana = (contador_alternos % 2 == 0)
        contador_alternos += 1
        for num_semana, dias_semana in semanas_completas.items():
            es_semana_de_manana = (num_semana % 2 == 0) == empieza_manana
            
            turno_prohibido = TURNO_TARDE if es_semana_de_manana else TURNO_MANANA
            for d in dias_semana:
                modelo.Add(turnos_asignados[(t, d, turno_prohibido)] == 0)

    # RESTRICCIÓN 
    # - Tenemos en cuenta cuando trabajan (si tienen vacaciones o no)
    
    for t in ids_trabajadores:
        for d in dias_abiertos:
            estado_dia = calendario_trabajadores.get((t, d), 1)

            turnos_del_dia = [turnos_asignados[(t, d, s)] for s in TURNOS]
            
            if estado_dia == 0:
                for s in TURNOS:
                    modelo.Add(turnos_asignados[(t, d, s)] == 0)
            elif estado_dia == 1:
                modelo.AddAtMostOne(turnos_del_dia)


    # RESTRICCIÓN -
    # 1.5 días de descanso a la semana y se puede extender hasta las 2 semanas, en ese caso siendo 3 semanas de vacaciones

    MIN_DESCANSO_SEMANA = 1        # 1.5 días/semana redondeado a la baja porque al final la mañana o la tarde de antes hace el otro medio
    MIN_DESCANSO_DOS_SEMANAS = 3 

    dias_reales_por_semana = {}
    for d in calendario.dias:
        num_semana = calendario.semana_de[d]
        dias_reales_por_semana.setdefault(num_semana, []).append(d)

    def descanso_disponible(dias_reales):
        cerrados = sum(1 for d in dias_reales if calendario.cerrado[d])
        abiertos = [d for d in dias_reales if not calendario.cerrado[d]]
        return cerrados, abiertos
    
            
    def anadir_restriccion_descanso(t, dias_reales, cuota):
        cerrados, abiertos = descanso_disponible(dias_reales)
        cuota_pendiente = max(0, cuota - cerrados)
        if cuota_pendiente == 0:
            return  
        if len(abiertos) < cuota_pendiente:
            return
        modelo.Add(
            sum(trabaja[(t, d)] for d in abiertos) <= len(abiertos) - cuota_pendiente
        )

    semanas_ordenadas = sorted(dias_reales_por_semana.keys())

    for t in ids_trabajadores:
        for num_semana in semanas_ordenadas:
            anadir_restriccion_descanso(t, dias_reales_por_semana[num_semana], MIN_DESCANSO_SEMANA)

        for num_semana in semanas_ordenadas:
            if (num_semana + 1) not in dias_reales_por_semana:
                continue
            dias_par = dias_reales_por_semana[num_semana] + dias_reales_por_semana[num_semana + 1]
            anadir_restriccion_descanso(t, dias_par, MIN_DESCANSO_DOS_SEMANAS)
    

    # RESTRICCIÓN -
    # Si un trabajador tiene un turno asignado en el día, debe tener asignada exactamente una tarea.
    # En cada turno (Mañana y Tarde) de un día abierto, se deben estar realizando todas las tareas. Esto significa que necesitamos, como mínimo, 1 trabajador asignado a cada tarea en la mañana, y 1 trabajador asignado a cada tarea en la tarde.
    
    CAPACIDAD_MAXIMA_TAREA = capacidad_maxima(tareas)
    CAPACIDAD_MINIMA_TAREA = capacidad_minima(tareas)


    tareas_cubiertas_total = []
    trabajadores_por_tarea_turno = {}
    

    for d in dias_abiertos:
        for s in TURNOS:
            for id_tarea in ids_tareas:
                trabajadores_en_tarea_y_turno = []
                
                for t in ids_trabajadores:
                    # Solo evaluamos a los que sí tienen habilidades y variable creada
                    if (t, d, id_tarea) in tarea_asignada:
                        en_turno_y_tarea = modelo.NewBoolVar(f'Aux_T{t}_D{d}_S{s}_Tar{id_tarea}')
                        modelo.Add(en_turno_y_tarea <= turnos_asignados[(t, d, s)])
                        modelo.Add(en_turno_y_tarea <= tarea_asignada[(t, d, id_tarea)])
                        modelo.Add(en_turno_y_tarea >= turnos_asignados[(t, d, s)] + tarea_asignada[(t, d, id_tarea)] - 1)  # <- falta esto
                        trabajadores_en_tarea_y_turno.append(en_turno_y_tarea)

                trabajadores_por_tarea_turno[(d, s, id_tarea)] = trabajadores_en_tarea_y_turno
                
                cap_max = CAPACIDAD_MAXIMA_TAREA.get(id_tarea, CAPACIDAD_MAXIMA_DEFECTO)
                #cap_min = CAPACIDAD_MINIMA_TAREA.get(id_tarea, CAPACIDAD_MINIMA_DEFECTO)

                modelo.Add(sum(trabajadores_en_tarea_y_turno) <= cap_max)
                #modelo.Add(sum(trabajadores_en_tarea_y_turno) >= cap_min)

                    
                tarea_cubierta = modelo.NewBoolVar(f'Cubierta_D{d}_S{s}_Tar{id_tarea}')
                modelo.Add(sum(trabajadores_en_tarea_y_turno) >= 1).OnlyEnforceIf(tarea_cubierta)
                tareas_cubiertas_total.append(tarea_cubierta)

    # RESTRICCIÓN
    # Se deben de cumplir las horas semanales de cada tipo de contrato y lo más importante de todo, debe sumar mensualmente las horas ordinarias.

    PESO_DEFICIT_HORAS = 3
    PESO_EXCESO_HORAS = 1

    horas_turno_qh_trabajador = {}
    for t in ids_trabajadores:
        horas_turno = HORAS_POR_TURNO_CONTRATO.get(trabajadores[t].id_contrato)
        if horas_turno is not None:
            horas_turno_qh_trabajador[t] = horas_a_qh(horas_turno)

    cota_maxima_qh_por_turno = sum(horas_turno_qh_trabajador.values())

    ids_ordinarios = [t for t in ids_trabajadores if not trabajadores[t].fijo_discontinuo]
    ids_fijos_discontinuos = [t for t in ids_trabajadores if trabajadores[t].fijo_discontinuo]

    def expr_horas_trabajadas_qh(dias, turnos=TURNOS, trabajadores_incl=None):
        ids = trabajadores_incl if trabajadores_incl is not None else ids_trabajadores
        return sum(
            horas_turno_qh_trabajador[t] * turnos_asignados[(t, d, s)]
            for d in dias
            for s in turnos
            for t in ids
            if t in horas_turno_qh_trabajador
        )

    def anadir_termino_horas(dias, horas_objetivo, etiqueta, turnos = TURNOS, trabajadores_incl=None):
        objetivo_qh = horas_a_qh(horas_objetivo)
        cota_qh = cota_maxima_qh_por_turno * len(turnos) * len(dias)
        cota_var = max(objetivo_qh, cota_qh, 1)

        deficit = modelo.NewIntVar(0, cota_var, f'DeficitHoras_{etiqueta}')
        exceso = modelo.NewIntVar(0, cota_var, f'ExcesoHoras_{etiqueta}')
        horas_calculadas = expr_horas_trabajadas_qh(dias, turnos=turnos, trabajadores_incl=trabajadores_incl)
        modelo.Add(horas_calculadas - objetivo_qh == exceso - deficit)
    
        return deficit, exceso, cota_var

    def penalizacion_y_cota(terminos):
        penal = sum(PESO_DEFICIT_HORAS * deficit + PESO_EXCESO_HORAS * exceso for deficit, exceso, _ in terminos)
        cota = sum(max(PESO_DEFICIT_HORAS, PESO_EXCESO_HORAS) * cota_t for _, _, cota_t in terminos)
        return penal, cota

    PORCENTAJE_HORAS_MANANA = 0.6
    PORCENTAJE_HORAS_TARDE = 0.4

    terminos_horas = []

    for d in dias_abiertos:
        horas_dia = calendario.horas_necesarias.get(d, 0.0)

        deficit_m, exceso_m, cota_m = anadir_termino_horas(
            [d], horas_dia * PORCENTAJE_HORAS_MANANA, f'D{d}_Manana', turnos=[TURNO_MANANA]
        )
        terminos_horas.append((deficit_m, exceso_m, cota_m))

        deficit_t, exceso_t, cota_t = anadir_termino_horas(
                    [d], horas_dia * PORCENTAJE_HORAS_TARDE, f'D{d}_Tarde', turnos=[TURNO_TARDE]
                )
        terminos_horas.append((deficit_t, exceso_t, cota_t))

    dias_por_mes_orden = {}
    for d in dias_abiertos:
        dias_por_mes_orden.setdefault((d.year, d.month), []).append(d)
    meses_ordenados = sorted(dias_por_mes_orden.keys())

    terminos_horas_ordinarios = []
    if objetivo_horas_por_mes:
        dias_por_mes_orden = {}
        for d in dias_abiertos:
            dias_por_mes_orden.setdefault((d.year, d.month), []).append(d)

        for indice, clave_mes in enumerate(sorted(dias_por_mes_orden.keys()), start=1):
            objetivo = objetivo_horas_por_mes.get(indice)
            if objetivo is None:
                continue
            deficit, exceso, cota = anadir_termino_horas(
                dias_por_mes_orden[clave_mes], objetivo, f'Mes_ord{clave_mes[0]}_{clave_mes[1]}',
                trabajadores_incl=ids_ordinarios
            )

            terminos_horas_ordinarios.append((deficit, exceso, cota))
    terminos_horas_fd = []
    if objetivo_horas_fd_por_mes:
        for indice, clave_mes in enumerate(meses_ordenados, start=1):
            objetivo = objetivo_horas_fd_por_mes.get(indice)
            if objetivo is None:
                continue

            dias_mes = dias_por_mes_orden[clave_mes]

            if objetivo == 0:
                for t in ids_fijos_discontinuos:
                    for d in dias_mes:
                        modelo.Add(trabaja[(t, d)] == 0)
            else:
                deficit, exceso, cota = anadir_termino_horas(
                    dias_mes, objetivo, f'MesFD{clave_mes[0]}_{clave_mes[1]}',
                    trabajadores_incl=ids_fijos_discontinuos
                )
                terminos_horas_fd.append((deficit, exceso, cota))

    # Las horas complementarias son el exceso sobre la jornada normal mensual
    # de cada trabajador con contrato habilitado, hasta un 60% adicional.
    terminos_horas_complementarias = []
    trabajadores_complementarias = [
        t for t in ids_trabajadores
        if trabajadores[t].id_contrato in CONTRATOS_COMPLEMENTARIAS
    ]

    def anadir_termino_horas_qh(horas_calculadas_qh, horas_objetivo, etiqueta, cota_qh):
        objetivo_qh = horas_a_qh(horas_objetivo)
        cota_var = max(objetivo_qh, cota_qh, 1)
        deficit = modelo.NewIntVar(0, cota_var, f'DeficitHoras_{etiqueta}')
        exceso = modelo.NewIntVar(0, cota_var, f'ExcesoHoras_{etiqueta}')
        modelo.Add(horas_calculadas_qh - objetivo_qh == exceso - deficit)
        return deficit, exceso, cota_var

    for indice, clave_mes in enumerate(meses_ordenados, start=1):
        dias_mes = dias_por_mes_orden[clave_mes]
        horas_complementarias_mes = []

        for t in trabajadores_complementarias:
            horas_turno_qh = horas_turno_qh_trabajador.get(t)
            if horas_turno_qh is None:
                continue

            horas_normales_mes_qh = horas_a_qh(
                horas_turno_qh / QH * TURNOS_NORMALES_MES_CONTRATO[trabajadores[t].id_contrato]
            )
            capacidad_maxima_mes_qh = int(round(horas_normales_mes_qh * 1.6))
            horas_trabajadas_mes = modelo.NewIntVar(
                0, capacidad_maxima_mes_qh,
                f'HorasTrabajadas_T{t}_Mes{clave_mes[0]}_{clave_mes[1]}'
            )
            modelo.Add(
                horas_trabajadas_mes == expr_horas_trabajadas_qh(
                    dias_mes, trabajadores_incl=[t]
                )
            )
            modelo.Add(horas_trabajadas_mes <= capacidad_maxima_mes_qh)

            horas_complementarias_trabajador = modelo.NewIntVar(
                0, capacidad_maxima_mes_qh,
                f'HorasComplementarias_T{t}_Mes{clave_mes[0]}_{clave_mes[1]}'
            )
            modelo.AddMaxEquality(
                horas_complementarias_trabajador,
                [horas_trabajadas_mes - horas_normales_mes_qh, 0]
            )
            horas_complementarias_mes.append(horas_complementarias_trabajador)

        objetivo_hc = (objetivo_horas_hc_por_mes or {}).get(indice)
        if objetivo_hc is not None:
            cota_hc = sum(
                int(round(
                    horas_a_qh(
                        horas_turno_qh_trabajador[t] / QH
                        * TURNOS_NORMALES_MES_CONTRATO[trabajadores[t].id_contrato]
                    ) * 0.6
                ))
                for t in trabajadores_complementarias
                if t in horas_turno_qh_trabajador
            )
            deficit, exceso, cota = anadir_termino_horas_qh(
                sum(horas_complementarias_mes), objetivo_hc,
                f'MesHC{clave_mes[0]}_{clave_mes[1]}', cota_hc
            )
            terminos_horas_complementarias.append((deficit, exceso, cota))

    penal_fd, cota_fd = penalizacion_y_cota(terminos_horas_fd)
    penal_complementarias, cota_complementarias = penalizacion_y_cota(
        terminos_horas_complementarias
    )
    PESO_PRIORIDAD_ORDINARIOS = cota_fd + 1  # domina cualquier penalización posible de los FD

    penal_total, cota_total = penalizacion_y_cota(terminos_horas)
    penal_ordinarios, cota_ordinarios = penalizacion_y_cota(terminos_horas_ordinarios)

    penalizacion_horas = (
        penal_total
        + PESO_PRIORIDAD_ORDINARIOS * penal_ordinarios
        + penal_fd
        + penal_complementarias
    )

    cota_penalizacion_maxima = (
        cota 
        + PESO_PRIORIDAD_ORDINARIOS + cota_ordinarios
        + cota_fd
    )
    PESO_COBERTURA = cota_penalizacion_maxima + 1

    # RESTRICCIÓN
    # Intentamos que los trabajadores tengan la misma tarea toda la semana
    
    PESO_CONSISTENCIA_NORMAL = 1
    PESO_CONSISTENCIA_PRIORITARIO = 3  # id_contrato == 1

    bonus_consistencia_terminos = []  # (peso, var_max_dias_en_una_tarea)

    for t in ids_trabajadores:
        tareas_permitidas_t = habilidades.get(t, [])
        if len(tareas_permitidas_t) <= 1:
            continue

        peso = PESO_CONSISTENCIA_PRIORITARIO if trabajadores[t].id_contrato == 1 else PESO_CONSISTENCIA_NORMAL

        for num_semana, dias_semana in semanas_completas.items():
            dias_en_tarea_vars = []
            for id_tarea in tareas_permitidas_t:
                dias_con_esa_tarea = [
                    tarea_asignada[(t, d, id_tarea)]
                    for d in dias_semana
                    if (t, d, id_tarea) in tarea_asignada
                ]
                if not dias_con_esa_tarea:
                    continue
                var_dias_en_tarea = modelo.NewIntVar(
                    0, len(dias_semana), f'DiasEnTarea_T{t}_W{num_semana}_Tar{id_tarea}'
                )
                modelo.Add(var_dias_en_tarea == sum(dias_con_esa_tarea))
                dias_en_tarea_vars.append(var_dias_en_tarea)

            if len(dias_en_tarea_vars) <= 1:
                continue  

            max_dias_en_una_tarea = modelo.NewIntVar(0, len(dias_semana), f'MaxTareaSemana_T{t}_W{num_semana}')
            modelo.AddMaxEquality(max_dias_en_una_tarea, dias_en_tarea_vars)
            bonus_consistencia_terminos.append((peso, max_dias_en_una_tarea, len(dias_semana)))


    # RESTRICCIÓN
    # Máximo de 22 domingos y festivos trabajados al año para trabajadores con más de tres días de trabajo semanales (para id_contratos 1, 2, 5 y 6)

    MAX_DOMINGOS = 22
    CONTRATO_LIMITE_DOMINGOS = {1, 2}

    todos_domingos = [d for d in calendario.dias if d.weekday() == 6]

    for t in ids_trabajadores:
        if trabajadores[t].id_contrato not in CONTRATO_LIMITE_DOMINGOS:
            continue
        terminos_domingo = []
        for d in todos_domingos:
            if calendario.cerrado[d]:
                terminos_domingo.append(1)
            else:
                terminos_domingo.append(trabaja[(t, d)])
        if terminos_domingo:
            modelo.Add(sum(terminos_domingo) <= MAX_DOMINGOS)

    # RESTRICCIÓN
    # Los trabajadores con más de cinco días de trabajo semanales deberán disfrutar de 9 fines de semana completos (sábado y domingo) de descanso al año.
    # - Cada 4 semanas un sábado y un domingo libres.
    # - Cada 4 semanas un domingo y lunes libres.
    
    '''
    PESO_FALTA_HABILIDAD = 10 
    
    modelo.Maximize(
        (PESO_COBERTURA * sum(tareas_cubiertas_total)) 
        - penalizacion_horas 
        - (PESO_FALTA_HABILIDAD * sum(asignaciones_sin_habilidad))
    )

    '''

    modelo.Maximize(PESO_COBERTURA * sum(tareas_cubiertas_total) - penalizacion_horas)

    
    # Resolvemos el modelo
    solver = cp_model.CpSolver()

    # Limitamos el tiempo
    solver.parameters.max_time_in_seconds = 120
    solver.parameters.num_search_workers = os.cpu_count() or 8

    solver.parameters.log_search_progress = True

    estado = solver.Solve(modelo)
    modelo.Validate()

    if solver.StatusName(estado) == "FEASIBLE":
            print(f"Aviso: se alcanzó el límite de tiempo ({solver.parameters.max_time_in_seconds}s) "
                  f"sin demostrar optimalidad. Se usa la mejor solución encontrada "
                  f"(cobertura = {solver.ObjectiveValue()}/{len(tareas_cubiertas_total)}).")

    # Mostrar resultados

    if estado == cp_model.OPTIMAL or estado == cp_model.FEASIBLE:

        id_version = crear_version_planificacion(dias_abiertos)
        preparar_version_activa(id_version, min(dias_abiertos), max(dias_abiertos))
        print(f"Generando nueva versión de planificación: id_version={id_version}")

        horas_semanales_asignadas = {}

        for t in ids_trabajadores:
            racha_actual = 0
            racha_maxima = 0
            dia_anterior = None
            for d in dias_abiertos:
                trabaja_hoy = solver.Value(trabaja[(t, d)]) == 1
                es_consecutivo = dia_anterior is not None and (d - dia_anterior).days == 1

                if trabaja_hoy and es_consecutivo:
                    racha_actual += 1
                elif trabaja_hoy:
                    racha_actual = 1
                else:
                    racha_actual = 0

                racha_maxima = max(racha_maxima, racha_actual)
                dia_anterior = d

            trabajadores[t].dias_seguidos_trabajados = racha_maxima

        primeros_dias = dias_abiertos[60: 75]
        for d in primeros_dias: 
            print(f'\n--- Día {d} ---')
            for t in ids_trabajadores:
                for s in TURNOS:
                    if solver.Value(turnos_asignados[(t, d, s)]) == 1:
                        # Buscamos qué tarea tiene asignada
                        tarea_realizada = None
                        for id_tarea in ids_tareas:
                            if solver.Value(tarea_asignada[(t, d, id_tarea)]) == 1:
                                tarea_realizada = id_tarea
                                horas_este_turno = HORAS_POR_TURNO_CONTRATO.get(trabajadores[t].id_contrato, 0)
                                clave_semana = (t, num_semana)
                                horas_semanales_asignadas[clave_semana] = horas_semanales_asignadas.get(clave_semana, 0) + horas_este_turno


                                break
                        
                        print(f'Trabajador {t} asignado al turno {s} - Tarea {tarea_realizada}')


        print("\n--- RESUMEN DE HORAS SEMANALES ---")
        filas_horas = []
        for (t, num_semana), horas_totales in horas_semanales_asignadas.items():
            filas_horas.append({
                "id_trabajador": t,
                "num_semana": num_semana,
                "horas_asignadas": horas_totales
            })
    
        guardar_calendarizacion(
                    solver, calendario, ids_trabajadores, ids_tareas,
                    dias_abiertos, turnos_asignados, tarea_asignada,
                    id_version,
                )
        
        
    else:
        print("No factible")


if __name__ == '__main__':
    ROOT = Path(__file__).resolve().parent.parent
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))

    RUTA_OPTIMIZACION = ROOT / "FASE_2 _programacion_lineal" / "optimizacion_FINAL.py"
    spec = importlib.util.spec_from_file_location("optimizacion_FINAL", RUTA_OPTIMIZACION)
    if spec is None or spec.loader is None:
        raise ImportError(f"No se pudo cargar {RUTA_OPTIMIZACION}")

    optimizacion_final = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = optimizacion_final
    spec.loader.exec_module(optimizacion_final)

    indice_desviacion = 1.1

    X_HO = optimizacion_final.X_HO
    X_HC = optimizacion_final.X_HC
    X_HFD = optimizacion_final.X_HFD

    meses_optimizacion = sorted(X_HO.keys())

    var_values = {
        f"X_HO_{mes}": X_HO[mes].varValue
        for mes in meses_optimizacion
    }
    var_values.update({
        f"X_HC_{mes}": X_HC[mes].varValue
        for mes in meses_optimizacion
    })
    var_values.update({
        f"X_HFD_{mes}": X_HFD[mes].varValue
        for mes in meses_optimizacion
    })

    trabajadores = cargar_trabajadores()
    calendario = cargar_calendario()
    calendario_trabajadores = cargar_estado_trabajador()
    tareas = cargar_tareas()
    habilidades = cargar_habilidades()

    objetivo_horas_por_mes, _, objetivo_horas_fd_por_mes = cargar_horas_mensuales()

    if not objetivo_horas_por_mes:
        objetivo_horas_por_mes = {
            mes: round(X_HO[mes].varValue / indice_desviacion)
            for mes in meses_optimizacion
        }

    objetivo_horas_hc_por_mes = {
        mes: round(X_HC[mes].varValue / indice_desviacion)
        for mes in meses_optimizacion
    }

    if not objetivo_horas_fd_por_mes:
        objetivo_horas_fd_por_mes = {
            mes: round(X_HFD[mes].varValue / indice_desviacion)
            for mes in meses_optimizacion
        }

    print("Horas cargadas desde horas_mensuales:", objetivo_horas_por_mes, objetivo_horas_hc_por_mes, objetivo_horas_fd_por_mes)

    crear_calendario_base(
        trabajadores,
        calendario,
        calendario_trabajadores,
        tareas,
        habilidades,
        objetivo_horas_por_mes=objetivo_horas_por_mes,
        objetivo_horas_hc_por_mes=objetivo_horas_hc_por_mes,
        objetivo_horas_fd_por_mes=objetivo_horas_fd_por_mes,
        cambios_forzados=cargar_cambios_forzados(),
    )



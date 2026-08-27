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


load_dotenv()

usuario = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")

engine = create_engine(
    f"mysql+pymysql://{usuario}:{password}@localhost/emplea"
)

TURNO_MANANA = 0
TURNO_TARDE = 1
TURNOS = [TURNO_MANANA, TURNO_TARDE]

CONTRATOS_ORDINARIAS = {1, 2, 4, 5, 6, 7}
CONTRATOS_COMPLEMENTARIAS = {2, 4, 5, 6, 7}
CONTRATOS_FIJO_DISCONTINUO = {3}
CONTRATOS_JORNADA_EXTRA = {1, 2}



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
    dias_trabajados_seguidos: int
    domingos_trabajados: int

@dataclass
class Calendario:
    dias: list[date]
    cerrado: dict[date, bool]
    semana_de: dict[date, int]
    segmentos_racha: list[list[date]]

@dataclass
class Tareas:
    id_tarea: int

def horas_a_qh(h: float) -> int:
    return round(h * QH)
 
def qh_a_horas(qh: int) -> float:
    return qh / QH

def cargar_trabajadores():
    query_trabajadores = """
    SELECT id_trabajador, nombre, disponibilidad, id_contrato
    FROM trabajador
    WHERE activo = 1 AND fijo_discontinuo = 0
    """

    query_calendario_trabajadores = """
        SELECT id_trabajador, estado
        FROM calendario_trabajadores
    """

    df_trabajadores = pd.read_sql(query_trabajadores, con=engine)
    df_trabajadores['id_trabajador'] = pd.to_numeric(df_trabajadores["id_trabajador"])
    df_trabajadores['id_contrato'] = pd.to_numeric(df_trabajadores["id_contrato"])
    #df_trabajadores['horas_semanales'] = pd.to_numeric(df_trabajadores["horas_semanales"])

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
            domingos_trabajados = 1
        )

        trabajadores[row.id_trabajador] = trabajador
    return trabajadores

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
        SELECT id_tarea
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


def guardar_calendarizacion(solver, calendario, ids_trabajadores, ids_tareas,
                             dias_abiertos, turnos_asignados, tarea_asignada):
    
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

                    filas.append({
                        "fecha": d,
                        "num_semana": num_semana,
                        "id_tarea": tarea_realizada,
                        "id_trabajador": t,
                        "turno": s,
                    })

    df_resultado = pd.DataFrame(
        filas, columns=["fecha", "num_semana", "id_tarea", "id_trabajador", "turno"]
    )

    if df_resultado.empty:
        print("No hay asignaciones que guardar en calendarizacion.")
        return

    with engine.begin() as conexion:
        conexion.execute(
            text("DELETE FROM calendarizacion WHERE fecha IN :fechas").bindparams(
                bindparam("fechas", expanding=True)
            ),
            {"fechas": dias_abiertos},
        )
        df_resultado.to_sql("calendarizacion", con=conexion, if_exists="append", index=False)

    print(f"Guardadas {len(df_resultado)} filas en calendarizacion "
          f"({dias_abiertos[0]} a {dias_abiertos[-1]}).")


def crear_calendario_base(trabajadores, calendario, calendario_trabajadores, tareas, habilidades):

    ids_trabajadores = list(trabajadores.keys())
    
    dias_abiertos = [d for d in calendario.dias if not calendario.cerrado[d]]
    
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
    ids_tareas = list(tareas.keys())
    tareas_permitidas = habilidades.get(t, [])
    for t in ids_trabajadores:
        tareas_permitidas = habilidades.get(t, [])
        
        for d in dias_abiertos:
            for id_tarea in ids_tareas:
                nombre_var_tarea = f'Tarea_T{t}_D{d}_Tar{id_tarea}'
                tarea_asignada[(t, d, id_tarea)] = modelo.NewBoolVar(nombre_var_tarea)
            
                if id_tarea not in tareas_permitidas:
                    modelo.Add(tarea_asignada[(t, d, id_tarea)] == 0)

            tareas_del_dia = [tarea_asignada[(t, d, id_tarea)] for id_tarea in ids_tareas]

            var_trabaja = modelo.NewBoolVar(f'Aux_Trabaja_T{t}_D{d}')
            modelo.Add(var_trabaja == sum(turnos_asignados[(t, d, s)] for s in TURNOS))
            
            modelo.Add(sum(tareas_del_dia) == 1).OnlyEnforceIf(var_trabaja)
            modelo.Add(sum(tareas_del_dia) == 0).OnlyEnforceIf(var_trabaja.Not())
    
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
    # - Si la persona tiene disponibilidad "A" - debe de ir una semana de tardes y el otra de mañanas

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
    

    # RESTRICCIÓN 
    # - Si el trabajador no tiene vacaciones esa semana debe completar sus horas semanales

    semanas_completas = {}
    for d in dias_abiertos:
        num_semana = calendario.semana_de[d]
        if num_semana not in semanas_completas:
            semanas_completas[num_semana] = []
        semanas_completas[num_semana].append(d)

    
    
    # RESTRICCIÓN -
    # Si un trabajador tiene un turno asignado en el día, debe tener asignada exactamente una tarea.
    # En cada turno (Mañana y Tarde) de un día abierto, se deben estar realizando todas las tareas. Esto significa que necesitamos, como mínimo, 1 trabajador asignado a cada tarea en la mañana, y 1 trabajador asignado a cada tarea en la tarde.
    
    tareas_cubiertas_total = []

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
                        trabajadores_en_tarea_y_turno.append(en_turno_y_tarea)

                tarea_cubierta = modelo.NewBoolVar(f'Cubierta_D{d}_S{s}_Tar{id_tarea}')
                modelo.Add(sum(trabajadores_en_tarea_y_turno) >= 1).OnlyEnforceIf(tarea_cubierta)
                tareas_cubiertas_total.append(tarea_cubierta)
            
    modelo.Maximize(sum(tareas_cubiertas_total))

    # Descanso de 1.5 días semanales


   
    
    # Resolvemos el modelo
    solver = cp_model.CpSolver()
    estado = solver.Solve(modelo)

    # Mostrar resultados

    if estado == cp_model.OPTIMAL or estado == cp_model.FEASIBLE:
        primeros_dias = dias_abiertos[:1]
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
                                break
                        
                        print(f'Trabajador {t} asignado al turno {s} - Tarea {tarea_realizada}')
        guardar_calendarizacion(
                    solver, calendario, ids_trabajadores, ids_tareas,
                    dias_abiertos, turnos_asignados, tarea_asignada,
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


    trabajadores = cargar_trabajadores()
    calendario = cargar_calendario()
    calendario_trabajadores = cargar_estado_trabajador()
    tareas = cargar_tareas()
    habilidades = cargar_habilidades()
    crear_calendario_base(trabajadores, calendario, calendario_trabajadores, tareas, habilidades)
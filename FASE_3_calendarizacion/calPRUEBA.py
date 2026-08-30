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
    "MOSTRADOR": 3,
    "INFORMAR": 2,
    "INFORMAR DE LOS ENCARGOS DEL MURO": 2,
    "HOME DELIVERY": 2,
    "SITE TO STORE": 2,
    "ECI EXPRESS + CLICK&CAR": 2,
}

CAPACIDAD_MAXIMA_DEFECTO = 1

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
            domingos_trabajados = 0
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


def crear_calendario_base(trabajadores, calendario, calendario_trabajadores, tareas, habilidades, objetivo_horas_por_mes):

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
    trabaja = {}
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
            trabaja[(t, d)] = var_trabaja
            
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

    SEMANA_PAR_ES_MANANA = True
    
    for t in ids_trabajadores:
        if trabajadores[t].disponibilidad != "A":
            continue
        for num_semana, dias_semana in semanas_completas.items():
            es_semana_de_manana = (num_semana % 2 == 0) == SEMANA_PAR_ES_MANANA
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
                        trabajadores_en_tarea_y_turno.append(en_turno_y_tarea)

                trabajadores_por_tarea_turno[(d, s, id_tarea)] = trabajadores_en_tarea_y_turno
                
                cap = CAPACIDAD_MAXIMA_TAREA.get(id_tarea, CAPACIDAD_MAXIMA_DEFECTO)
                modelo.Add(sum(trabajadores_en_tarea_y_turno) <= cap)

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

    def expr_horas_trabajadas_qh(dias):
        return sum(
            horas_turno_qh_trabajador[t] * turnos_asignados[(t, d, s)]
            for d in dias
            for s in TURNOS
            for t in ids_trabajadores
            if t in horas_turno_qh_trabajador
        )

    def anadir_termino_horas(dias, horas_objetivo, etiqueta):
        objetivo_qh = horas_a_qh(horas_objetivo)
        cota_qh = cota_maxima_qh_por_turno * len(TURNOS) * len(dias)
        cota_var = max(objetivo_qh, cota_qh, 1)

        deficit = modelo.NewIntVar(0, cota_var, f'DeficitHoras_{etiqueta}')
        exceso = modelo.NewIntVar(0, cota_var, f'ExcesoHoras_{etiqueta}')
        modelo.Add(expr_horas_trabajadas_qh(dias) - objetivo_qh == exceso - deficit)
    
        return deficit, exceso, cota_var

    terminos_horas = []

    for d in dias_abiertos:
        deficit, exceso, cota = anadir_termino_horas(
            [d], calendario.horas_necesarias.get(d, 0.0), f'D{d}'
        )
        terminos_horas.append((deficit, exceso, cota))

    if objetivo_horas_por_mes:
        dias_por_mes_orden = {}
        for d in dias_abiertos:
            dias_por_mes_orden.setdefault((d.year, d.month), []).append(d)

        for indice, clave_mes in enumerate(sorted(dias_por_mes_orden.keys()), start=1):
            objetivo = objetivo_horas_por_mes.get(indice)
            if objetivo is None:
                continue
            deficit, exceso, cota = anadir_termino_horas(
                dias_por_mes_orden[clave_mes], objetivo, f'Mes{clave_mes[0]}_{clave_mes[1]}'
            )
            terminos_horas.append((deficit, exceso, cota))

    penalizacion_horas = sum(
        PESO_DEFICIT_HORAS * deficit + PESO_EXCESO_HORAS * exceso
        for deficit, exceso, _ in terminos_horas
    )

    cota_penalizacion_maxima = sum(
        max(PESO_DEFICIT_HORAS, PESO_EXCESO_HORAS) * cota for _, _, cota in terminos_horas
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
   


    modelo.Maximize(PESO_COBERTURA * sum(tareas_cubiertas_total) - penalizacion_horas)

    
    # Resolvemos el modelo
    solver = cp_model.CpSolver()

    # Limitamos el tiempo
    solver.parameters.max_time_in_seconds = 120
    solver.parameters.num_search_workers = os.cpu_count() or 8
    solver.parameters.log_search_progress = True

    estado = solver.Solve(modelo)

    if solver.StatusName(estado) == "FEASIBLE":
            print(f"Aviso: se alcanzó el límite de tiempo ({solver.parameters.max_time_in_seconds}s) "
                  f"sin demostrar optimalidad. Se usa la mejor solución encontrada "
                  f"(cobertura = {solver.ObjectiveValue()}/{len(tareas_cubiertas_total)}).")

    # Mostrar resultados

    if estado == cp_model.OPTIMAL or estado == cp_model.FEASIBLE:
    
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

        primeros_dias = dias_abiertos[:7]
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

    indice_desviacion = 1.3

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
        "X_HFD_3": X_HFD_3.varValue ,
    }


    trabajadores = cargar_trabajadores()
    calendario = cargar_calendario()
    calendario_trabajadores = cargar_estado_trabajador()
    tareas = cargar_tareas()
    habilidades = cargar_habilidades()

    objetivo_horas_por_mes = {
            1: round(X_HO_1.varValue / indice_desviacion),
            2: round(X_HO_2.varValue / indice_desviacion),
            3: round(X_HO_3.varValue / indice_desviacion),
    }
    crear_calendario_base(trabajadores, calendario, calendario_trabajadores, tareas, habilidades,
                          objetivo_horas_por_mes=objetivo_horas_por_mes)


# Cosas que faltan
# Que por lo menos hayan 5 personas por la mañana
# Completar las restricciones que están marcadas como que faltan
# 

    
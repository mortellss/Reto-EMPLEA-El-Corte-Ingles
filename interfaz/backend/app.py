from flask import Flask, render_template, request, jsonify, send_file
from sqlalchemy import text
import pandas as pd
from db import engine
from io import BytesIO


app = Flask(__name__)


# ------------------------
# DASHBOARD
# ------------------------

@app.route("/")
def dashboard():
    return render_template("dashboard.html")


# ------------------------
# GESTIÓN DE DATOS
# ------------------------

@app.route("/gestion-datos")
def gestion_datos():

    trabajadores = pd.read_sql("""

        SELECT

            t.id_trabajador,
            t.numero_vendedor,
            t.nombre,
            t.apellidos,
            t.correo,
            t.id_contrato,
            t.id_centro,
            t.fijo_discontinuo,
            t.disponibilidad,
            t.estado,
            t.activo,

            c.nombre AS contrato,

            COUNT(tt.id_tarea) AS competencias,

            GROUP_CONCAT(
                ta.nombre
                ORDER BY ta.nombre
                SEPARATOR ', '
            ) AS lista_competencias

        FROM trabajador t

        LEFT JOIN contrato c
            ON t.id_contrato = c.id_contrato

        LEFT JOIN trabajador_tarea tt
            ON t.id_trabajador = tt.id_trabajador

        LEFT JOIN tarea ta
            ON tt.id_tarea = ta.id_tarea

        WHERE t.activo = 1

        GROUP BY

            t.id_trabajador,
            t.numero_vendedor,
            t.nombre,
            t.apellidos,
            t.correo,
            t.id_contrato,
            t.id_centro,
            t.fijo_discontinuo,
            t.disponibilidad,
            t.estado,
            t.activo,
            c.nombre

        ORDER BY t.apellidos, t.nombre

        """, engine)

    contratos = pd.read_sql("""

        SELECT

            c.id_contrato,
            c.nombre,
            c.jornada,
            c.horas_anuales,
            c.horas_por_turno,

            COUNT(t.id_trabajador) AS trabajadores

        FROM contrato c

        LEFT JOIN trabajador t

            ON c.id_contrato = t.id_contrato
            AND t.activo = 1

        GROUP BY

            c.id_contrato,
            c.nombre,
            c.jornada,
            c.horas_anuales,
            c.horas_por_turno

        ORDER BY c.jornada DESC

        """, engine)


    tareas = pd.read_sql("""

        SELECT

            t.id_tarea,
            t.nombre,
            t.descripcion,
            t.activa,

            COUNT(tt.id_trabajador) AS trabajadores

        FROM tarea t

        LEFT JOIN trabajador_tarea tt
            ON t.id_tarea = tt.id_tarea

        GROUP BY
            t.id_tarea,
            t.nombre,
            t.descripcion,
            t.activa

        ORDER BY t.nombre

    """, engine)

    turnos = pd.read_sql("""
        SELECT *
        FROM turno_vacaciones
        ORDER BY codigo
    """, engine)

    total_tareas = pd.read_sql("""

        SELECT COUNT(*) AS total

        FROM tarea

        """, engine).iloc[0]["total"]


    disponibilidades=pd.read_sql("""
        SELECT
            t.id_trabajador,
            CONCAT(t.nombre,' ',t.apellidos) AS trabajador,
            COUNT(d.id_disponibilidad) AS total_periodos
        FROM trabajador t
        LEFT JOIN disponibilidad d
            ON t.id_trabajador=d.id_trabajador
        WHERE t.activo=1
        GROUP BY
            t.id_trabajador,
            t.nombre,
            t.apellidos
        ORDER BY
            t.apellidos,
            t.nombre
    """,engine)
        
    return render_template(
        "gestion-datos.html",
        trabajadores=trabajadores.to_dict(orient="records"),
        contratos=contratos.to_dict(orient="records"),
        tareas=tareas.to_dict(orient="records"),
        turnos=turnos.to_dict(orient="records"),
        total_tareas=total_tareas,
        disponibilidades=disponibilidades.to_dict(orient="records")
    )



@app.route("/competencias_trabajador/<int:id_trabajador>")
def competencias_trabajador(id_trabajador):

    competencias = pd.read_sql("""

        SELECT

            ta.id_tarea,
            ta.nombre

        FROM trabajador_tarea tt

        JOIN tarea ta

            ON ta.id_tarea = tt.id_tarea

        WHERE tt.id_trabajador = %s

        ORDER BY ta.nombre

    """, engine, params=(id_trabajador,))

    return competencias.to_json(
        orient="records",
        force_ascii=False
    )


@app.route("/trabajadores_contrato/<int:id_contrato>")
def trabajadores_contrato(id_contrato):

    trabajadores = pd.read_sql(

        text("""

            SELECT

                CONCAT(nombre,' ',apellidos) AS nombre

            FROM trabajador

            WHERE id_contrato = :id
            AND activo = 1

            ORDER BY apellidos, nombre

        """),

        engine,

        params={
            "id": id_contrato
        }

    )

    return jsonify(
        trabajadores.to_dict(orient="records")
    )


# ------------------------
# NUEVO CONTRATO
# ------------------------

@app.route("/nuevo_contrato", methods=["POST"])
def nuevo_contrato():

    datos = request.get_json()

    with engine.begin() as conn:

        conn.execute(text("""

            INSERT INTO contrato(

                nombre,
                jornada,
                horas_anuales,
                horas_por_turno

            )

            VALUES(

                :nombre,
                :jornada,
                :horas_anuales,
                :horas_por_turno

            )

        """),

        {

            "nombre": datos["nombre"],
            "jornada": datos["jornada"],
            "horas_anuales": datos["horas_anuales"],
            "horas_por_turno": datos["horas_por_turno"]

        })

    return "",204

# ------------------------
# ELIMINAR CONTRATO
# ------------------------

@app.route("/eliminar_contrato", methods=["POST"])
def eliminar_contrato():

    datos = request.get_json()

    with engine.begin() as conn:

        trabajadores = conn.execute(text("""

            SELECT COUNT(*)

            FROM trabajador

            WHERE id_contrato = :id
            AND activo = 1

        """),

        {

            "id": datos["id"]

        }).scalar()

        if trabajadores > 0:

            return jsonify({

                "ok": False,

                "error":
                "No se puede eliminar este contrato porque tiene trabajadores asignados."

            })

        conn.execute(text("""

            DELETE

            FROM contrato

            WHERE id_contrato = :id

        """),

        {

            "id": datos["id"]

        })

    return jsonify({

        "ok": True

    })


# ------------------------
# EDITAR CONTRATO
# ------------------------

@app.route("/editar_contrato", methods=["POST"])
def editar_contrato():

    datos = request.get_json()

    with engine.begin() as conn:

        conn.execute(text("""

            UPDATE contrato

            SET

                nombre = :nombre,
                jornada = :jornada,
                horas_anuales = :horas_anuales,
                horas_por_turno = :horas_por_turno

            WHERE id_contrato = :id

        """),

        {

            "id": datos["id"],
            "nombre": datos["nombre"],
            "jornada": datos["jornada"],
            "horas_anuales": datos["horas_anuales"],
            "horas_por_turno": datos["horas_por_turno"]

        })

    return "",204


   
@app.route("/eliminar_trabajador", methods=["POST"])
def eliminar_trabajador():

    datos = request.get_json()
    print(datos)

    with engine.begin() as conn:

        conn.execute(text("""
            UPDATE trabajador
            SET activo=0
            WHERE id_trabajador=:id
        """),{"id":datos["id"]})

    return jsonify(ok=True)


@app.route("/nuevo_trabajador",methods=["POST"])
def nuevo_trabajador():
    datos=request.get_json()
    with engine.begin() as conn:
        resultado=conn.execute(text("""
            INSERT INTO trabajador(
                numero_vendedor,
                nombre,
                apellidos,
                correo,
                activo,
                id_contrato,
                id_centro,
                estado,
                disponibilidad,
                fijo_discontinuo
            )
            VALUES(
                :numero_vendedor,
                :nombre,
                :apellidos,
                :correo,
                1,
                :id_contrato,
                1,
                :estado,
                :disponibilidad,
                :fijo_discontinuo
            )
        """),datos)
        id_trabajador=resultado.lastrowid
        for tarea in datos["tareas"]:
            conn.execute(text("""
                INSERT INTO trabajador_tarea(
                    id_trabajador,
                    id_tarea
                )
                VALUES(
                    :id_trabajador,
                    :id_tarea
                )
            """),{
                "id_trabajador":id_trabajador,
                "id_tarea":tarea
            })
    return jsonify(ok=True)

@app.route("/editar_trabajador", methods=["POST"])
def editar_trabajador():

    datos = request.json

    with engine.begin() as conn:

        conn.execute(text("""

            UPDATE trabajador
            SET
                numero_vendedor=:numero_vendedor,
                nombre=:nombre,
                apellidos=:apellidos,
                correo=:correo,
                id_contrato=:id_contrato,
                disponibilidad=:disponibilidad,
                estado=:estado,
                fijo_discontinuo=:fijo_discontinuo
            WHERE id_trabajador=:id

        """), datos)

        # Eliminar competencias anteriores
        conn.execute(text("""

            DELETE FROM trabajador_tarea

            WHERE id_trabajador = :id

        """), {"id": datos["id"]})

        # Insertar las nuevas
        for id_tarea in datos["tareas"]:

            conn.execute(text("""

                INSERT INTO trabajador_tarea
                (id_trabajador, id_tarea)

                VALUES
                (:id_trabajador, :id_tarea)

            """), {

                "id_trabajador": datos["id"],
                "id_tarea": id_tarea

            })

    return jsonify(ok=True)


# ------------------------
# CAMBIAR ESATDO TRABAJADOR
# ------------------------

@app.route("/cambiar_estado_trabajador", methods=["POST"])
def cambiar_estado_trabajador():

    datos = request.json

    with engine.begin() as conn:

        conn.execute(text("""

            UPDATE trabajador

            SET estado = NOT estado

            WHERE id_trabajador = :id

        """),{

            "id":datos["id"]

        })

    return jsonify(ok=True)



# Periodos fijos discontinuos
@app.route("/periodos_trabajador/<int:id_trabajador>")
def periodos_trabajador(id_trabajador):
    periodos=pd.read_sql("""
        SELECT
            id_periodo,
            fecha_inicio,
            fecha_fin
        FROM periodo_fijo_discontinuo
        WHERE id_trabajador=%s
        ORDER BY fecha_inicio
    """,engine,params=(id_trabajador,))
    return periodos.to_json(
        orient="records",
        date_format="iso"
    )


#Añadir/editar/eliminar periodos fijos discontinuos
@app.route("/nuevo_periodo_fd",methods=["POST"])
def nuevo_periodo_fd():
    datos=request.get_json()
    with engine.begin() as conn:
        conn.execute(text("""
            INSERT INTO periodo_fijo_discontinuo(
                id_trabajador,
                fecha_inicio,
                fecha_fin
            )
            VALUES(
                :id_trabajador,
                :fecha_inicio,
                :fecha_fin
            )
        """),datos)
    return jsonify(ok=True)

@app.route("/editar_periodo_fd",methods=["POST"])
def editar_periodo_fd():
    datos=request.get_json()
    with engine.begin() as conn:
        conn.execute(text("""
            UPDATE periodo_fijo_discontinuo
            SET
                fecha_inicio=:fecha_inicio,
                fecha_fin=:fecha_fin
            WHERE id_periodo=:id_periodo
        """),datos)
    return jsonify(ok=True)

@app.route("/eliminar_periodo_fd",methods=["POST"])
def eliminar_periodo_fd():
    datos=request.get_json()
    print("ELIMINANDO PERIODO:",datos)
    with engine.begin() as conn:
        resultado=conn.execute(text("""
            DELETE FROM periodo_fijo_discontinuo
            WHERE id_periodo=:id_periodo
        """),{
            "id_periodo":int(datos["id_periodo"])
        })
        print("FILAS ELIMINADAS:",resultado.rowcount)
    return jsonify(ok=True)


# ------------------------
# CALENDARIO
# ------------------------
@app.route("/calendario")
def calendario():
    ID_CENTRO=1
    anio=request.args.get("anio",type=int)
    anios_df=pd.read_sql("""
        SELECT DISTINCT YEAR(fecha) AS anio
        FROM calendario
        WHERE id_centro=%s
        ORDER BY anio DESC
    """,engine,params=(ID_CENTRO,))
    anios=anios_df["anio"].tolist()
    if not anios:
        return render_template("calendario.html",meses={},anios=[],anio=None)
    if anio not in anios:
        anio=anios[0]
    df=pd.read_sql("""
        SELECT *
        FROM calendario
        WHERE id_centro=%s
        AND YEAR(fecha)=%s
        ORDER BY fecha
    """,engine,params=(ID_CENTRO,anio))
    meses={}
    nombres_meses={
        1:"Enero",2:"Febrero",3:"Marzo",4:"Abril",
        5:"Mayo",6:"Junio",7:"Julio",8:"Agosto",
        9:"Septiembre",10:"Octubre",11:"Noviembre",12:"Diciembre"
    }
    for fila in df.to_dict(orient="records"):
        mes=nombres_meses[fila["fecha"].month]
        meses.setdefault(mes,[]).append(fila)
    for dias in meses.values():
        if dias:
            primer_dia=dias[0]["fecha"].weekday()
            for _ in range(primer_dia):
                dias.insert(0,None)
    return render_template(
        "calendario.html",
        meses=meses,
        anios=anios,
        anio=anio
    )

# ------------------------
# ACTUALIZAR CALENDARIO
# ------------------------
@app.route("/actualizar_dia",methods=["POST"])
def actualizar_dia():
    datos=request.get_json()
    with engine.begin() as conn:
        conn.execute(
            text("""
                UPDATE calendario
                SET
                    hora_apertura=:hora_apertura,
                    hora_cierre=:hora_cierre,
                    centro_abierto=:centro_abierto,
                    modificado=1
                WHERE fecha=:fecha
                AND id_centro=1
            """),
            {
                "hora_apertura":datos["hora_apertura"] or None,
                "hora_cierre":datos["hora_cierre"] or None,
                "centro_abierto":datos["abierto"],
                "fecha":datos["fecha"]
            }
        )
    return jsonify({"ok":True})
# ------------------------
# IMPORTAR CALENDARIO
# ------------------------
@app.route("/importar_calendario",methods=["POST"])
def importar_calendario():
    ID_CENTRO=1
    if "archivo" not in request.files:
        return jsonify(error="No se ha seleccionado ningún archivo."),400
    archivo=request.files["archivo"]
    if archivo.filename=="":
        return jsonify(error="No se ha seleccionado ningún archivo."),400
    if not archivo.filename.lower().endswith(".xlsx"):
        return jsonify(error="El archivo debe estar en formato .xlsx."),400
    try:
        df=pd.read_excel(archivo)
        columnas_obligatorias=[
            "fecha",
            "centro_abierto",
            "es_festivo",
            "dia_posterior_festivo",
            "hora_apertura",
            "hora_cierre"
        ]
        columnas_faltantes=[
            columna for columna in columnas_obligatorias
            if columna not in df.columns
        ]
        if columnas_faltantes:
            return jsonify(
                error="Faltan columnas obligatorias: "+", ".join(columnas_faltantes)
            ),400
        df=df[columnas_obligatorias].copy()
        df["fecha"]=pd.to_datetime(df["fecha"],errors="coerce")
        if df["fecha"].isna().any():
            return jsonify(error="Hay fechas no válidas en el Excel."),400
        if df["fecha"].duplicated().any():
            return jsonify(error="Hay fechas duplicadas en el Excel."),400
        def convertir_booleano(valor):
            if pd.isna(valor):
                return None
            if isinstance(valor,bool):
                return valor
            valor=str(valor).strip().upper()
            if valor in ["VERDADERO","TRUE","1"]:
                return True
            if valor in ["FALSO","FALSE","0"]:
                return False
            return None
        df["centro_abierto"]=df["centro_abierto"].apply(convertir_booleano)
        df["es_festivo"]=df["es_festivo"].apply(convertir_booleano)
        df["dia_posterior_festivo"]=df["dia_posterior_festivo"].apply(convertir_booleano)
        if df[[
            "centro_abierto",
            "es_festivo",
            "dia_posterior_festivo"
        ]].isna().any().any():
            return jsonify(
                error="Los campos 0/1 contienen valores no válidos."
            ),400
        def convertir_hora(valor):
            if pd.isna(valor):
                return None
            if hasattr(valor,"strftime"):
                return valor.strftime("%H:%M")
            valor=str(valor).strip()
            if valor=="" or valor.lower()=="nan":
                return None
            return valor[:5]
        df["hora_apertura"]=df["hora_apertura"].apply(convertir_hora)
        df["hora_cierre"]=df["hora_cierre"].apply(convertir_hora)
        actualizados=0
        insertados=0
        with engine.begin() as conn:
            for _,fila in df.iterrows():
                fecha=fila["fecha"].date()
                hora_apertura=fila["hora_apertura"]
                hora_cierre=fila["hora_cierre"]
                if pd.isna(hora_apertura):
                    hora_apertura=None
                if pd.isna(hora_cierre):
                    hora_cierre=None
                resultado=conn.execute(
                    text("""
                        UPDATE calendario
                        SET
                            centro_abierto=:centro_abierto,
                            es_festivo=:es_festivo,
                            dia_posterior_festivo=:dia_posterior_festivo,
                            hora_apertura=:hora_apertura,
                            hora_cierre=:hora_cierre
                        WHERE fecha=:fecha
                        AND id_centro=:id_centro
                    """),
                    {
                        "fecha":fecha,
                        "centro_abierto":bool(fila["centro_abierto"]),
                        "es_festivo":bool(fila["es_festivo"]),
                        "dia_posterior_festivo":bool(fila["dia_posterior_festivo"]),
                        "hora_apertura":hora_apertura,
                        "hora_cierre":hora_cierre,
                        "id_centro":ID_CENTRO
                    }
                )
                if resultado.rowcount>0:
                    actualizados+=1
                else:
                    conn.execute(
                        text("""
                            INSERT INTO calendario(
                                fecha,
                                centro_abierto,
                                es_festivo,
                                dia_posterior_festivo,
                                hora_apertura,
                                hora_cierre,
                                id_centro
                            )
                            VALUES(
                                :fecha,
                                :centro_abierto,
                                :es_festivo,
                                :dia_posterior_festivo,
                                :hora_apertura,
                                :hora_cierre,
                                :id_centro
                            )
                        """),
                        {
                            "fecha":fecha,
                            "centro_abierto":bool(fila["centro_abierto"]),
                            "es_festivo":bool(fila["es_festivo"]),
                            "dia_posterior_festivo":bool(fila["dia_posterior_festivo"]),
                            "hora_apertura":hora_apertura,
                            "hora_cierre":hora_cierre,
                            "id_centro":ID_CENTRO
                        }
                    )
                    insertados+=1
        return jsonify(
            ok=True,
            mensaje=(
                f"Calendario importado correctamente. "
                f"Se han añadido {insertados} días y "
                f"actualizado {actualizados} días."
            )
        )
    except Exception as e:
        print("ERROR AL IMPORTAR CALENDARIO:",e)
        return jsonify(
            error="No se ha podido importar el calendario."
        ),500


# ------------------------
# EXPORTAR CALENDARIO
# ------------------------
@app.route("/exportar_calendario")
def exportar_calendario():
    ID_CENTRO=1
    try:
        df=pd.read_sql("""
            SELECT
                fecha,
                centro_abierto,
                es_festivo,
                dia_posterior_festivo,
                hora_apertura,
                hora_cierre
            FROM calendario
            WHERE id_centro=%s
            ORDER BY fecha
        """,engine,params=(ID_CENTRO,))
        df["centro_abierto"]=df["centro_abierto"].astype(int)
        df["es_festivo"]=df["es_festivo"].astype(int)
        df["dia_posterior_festivo"]=df["dia_posterior_festivo"].astype(int)
        memoria=BytesIO()
        with pd.ExcelWriter(memoria,engine="openpyxl") as writer:
            df.to_excel(writer,index=False,sheet_name="Calendario")
            hoja=writer.sheets["Calendario"]
            hoja.column_dimensions["A"].width=14
            hoja.column_dimensions["B"].width=18
            hoja.column_dimensions["C"].width=15
            hoja.column_dimensions["D"].width=25
            hoja.column_dimensions["E"].width=18
            hoja.column_dimensions["F"].width=18
            for celda in hoja["A"][1:]:
                celda.number_format="dd/mm/yyyy"
            for fila in range(2,hoja.max_row+1):
                hoja.cell(fila,5).number_format="HH:MM"
                hoja.cell(fila,6).number_format="HH:MM"
        memoria.seek(0)
        return send_file(
            memoria,
            as_attachment=True,
            download_name="calendario.xlsx",
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    except Exception as e:
        print("ERROR AL EXPORTAR CALENDARIO:",e)
        return jsonify(error="No se ha podido exportar el calendario."),500

    
# ------------------------
# NUEVA DISPONIBILIDAD
# ------------------------

@app.route("/periodos_disponibilidad/<int:id_trabajador>")
def periodos_disponibilidad(id_trabajador):
    trabajador=pd.read_sql("""
        SELECT
            CONCAT(nombre,' ',apellidos) AS trabajador
        FROM trabajador
        WHERE id_trabajador=%s
    """,engine,params=(id_trabajador,))
    periodos=pd.read_sql("""
        SELECT
            id_disponibilidad,
            motivo,
            turno,
            fecha_inicio,
            fecha_fin
        FROM disponibilidad
        WHERE id_trabajador=%s
        ORDER BY fecha_inicio
    """,engine,params=(id_trabajador,))
    return jsonify({
        "trabajador":trabajador.iloc[0]["trabajador"],
        "periodos":periodos.assign(
            fecha_inicio=periodos["fecha_inicio"].astype(str),
            fecha_fin=periodos["fecha_fin"].astype(str)
        ).to_dict(orient="records")
    })


@app.route("/nueva_disponibilidad", methods=["POST"])
def nueva_disponibilidad():

    datos = request.get_json()

    with engine.begin() as conn:

        conn.execute(text("""

            INSERT INTO disponibilidad(

                id_trabajador,
                motivo,
                turno,
                fecha_inicio,
                fecha_fin

            )
            VALUES(

                :id_trabajador,
                :motivo,
                :turno,
                :fecha_inicio,
                :fecha_fin

            )

        """), {

            "id_trabajador": datos["id_trabajador"],
            "fecha_inicio": datos["fecha_inicio"],
            "fecha_fin": datos["fecha_fin"],
            "motivo": datos["motivo"],
            "turno": datos["turno"]

        })

    return jsonify(ok=True)

# ------------------------
# EDITAR DISPONIBILIDAD
# ------------------------

@app.route("/editar_disponibilidad", methods=["POST"])
def editar_disponibilidad():

    datos = request.get_json()

    with engine.begin() as conn:

        conn.execute(text("""

            UPDATE disponibilidad

            SET

                id_trabajador=:id_trabajador,
                motivo=:motivo,
                turno=:turno,
                fecha_inicio=:fecha_inicio,
                fecha_fin=:fecha_fin

            WHERE id_disponibilidad=:id

        """),{

            "id": datos["id"],
            "id_trabajador": datos["id_trabajador"],
            "fecha_inicio": datos["fecha_inicio"],
            "fecha_fin": datos["fecha_fin"],
            "motivo": datos["motivo"],
            "turno": datos["turno"],

        })

    return jsonify(ok=True)



# ------------------------
# ELIMINAR DISPONIBILIDAD
# ------------------------

@app.route("/eliminar_disponibilidad", methods=["POST"])
def eliminar_disponibilidad():

    datos = request.get_json()

    with engine.begin() as conn:

        conn.execute(text("""

            DELETE FROM disponibilidad

            WHERE id_disponibilidad=:id

        """),{

            "id": datos["id"]

        })

    return jsonify(ok=True)

@app.route("/centro")
def centro():
    return render_template("centro.html")


# Nueva tarea
@app.route("/nueva_tarea", methods=["POST"])
def nueva_tarea():

    datos = request.get_json()

    with engine.begin() as conn:

        resultado = conn.execute(text("""

            INSERT INTO tarea(

                nombre,
                descripcion,
                activa

            )

            VALUES(

                :nombre,
                :descripcion,
                :activa

            )

        """), datos)

        id_tarea = resultado.lastrowid

        for id_trabajador in datos["trabajadores"]:

            conn.execute(text("""

                INSERT INTO trabajador_tarea(

                    id_trabajador,
                    id_tarea

                )

                VALUES(

                    :id_trabajador,
                    :id_tarea

                )

            """),{

                "id_trabajador": id_trabajador,
                "id_tarea": id_tarea

            })

    return jsonify(ok=True)


# editar los trabajdores
# Editar tarea
@app.route("/editar_tarea", methods=["POST"])
def editar_tarea():
    datos=request.get_json()
    with engine.begin() as conn:
        conn.execute(text("""
            UPDATE tarea
            SET
                nombre=:nombre,
                descripcion=:descripcion,
                activa=:activa
            WHERE id_tarea=:id
        """),datos)
        conn.execute(text("""
            DELETE FROM trabajador_tarea
            WHERE id_tarea=:id
        """),{"id":datos["id"]})
        for id_trabajador in datos["trabajadores"]:
            conn.execute(text("""
                INSERT INTO trabajador_tarea(
                    id_trabajador,
                    id_tarea
                )
                VALUES(
                    :id_trabajador,
                    :id_tarea
                )
            """),{
                "id_trabajador":id_trabajador,
                "id_tarea":datos["id"]
            })
    return jsonify(ok=True)


# Ver los trabajadores asignados a cada tarea
@app.route("/trabajadores_tarea/<int:id_tarea>")
def trabajadores_tarea(id_tarea):

    trabajadores=pd.read_sql("""

        SELECT
            t.id_trabajador,
            t.nombre,
            t.apellidos

        FROM trabajador_tarea tt

        JOIN trabajador t
            ON t.id_trabajador=tt.id_trabajador

        WHERE tt.id_tarea=%s

        ORDER BY t.apellidos,t.nombre

    """,engine,params=(id_tarea,))

    return trabajadores.to_json(
        orient="records",
        force_ascii=False
    )

# Cambiar estado de tarea
@app.route("/cambiar_estado_tarea", methods=["POST"])
def cambiar_estado_tarea():

    datos=request.get_json()

    with engine.begin() as conn:

        conn.execute(text("""
            UPDATE tarea
            SET activa=NOT activa
            WHERE id_tarea=:id
        """),{
            "id":datos["id"]
        })

    return jsonify(ok=True)

# eliminar tarea
@app.route("/eliminar_tarea", methods=["POST"])
def eliminar_tarea():
    datos=request.get_json()
    with engine.begin() as conn:
        conn.execute(text("""
            DELETE FROM trabajador_tarea
            WHERE id_tarea=:id
        """),{
            "id":datos["id"]
        })
        conn.execute(text("""
            DELETE FROM tarea
            WHERE id_tarea=:id
        """),{
            "id":datos["id"]
        })
    return jsonify(ok=True)


# ------------------------
# DATOS HISTÓRICOS
# ------------------------
# ------------------------
# PROMOCIONES
# ------------------------
@app.route("/api/promociones")
def api_promociones():

    try:

        df = pd.read_sql("""
            SELECT
                id_promocion,
                nombre,
                fecha_inicio,
                fecha_fin,
                tipo,
                descripcion,
                id_centro
            FROM promocion
            WHERE id_centro = 1
            ORDER BY fecha_inicio
        """, engine)

        datos = df.to_dict(orient="records")

        for fila in datos:

            if pd.isna(fila.get("tipo")):
                fila["tipo"] = None

            if pd.isna(fila.get("descripcion")):
                fila["descripcion"] = None

            if pd.notna(fila.get("fecha_inicio")):
                fila["fecha_inicio"] = fila["fecha_inicio"].strftime("%Y-%m-%d")

            if pd.notna(fila.get("fecha_fin")):
                fila["fecha_fin"] = fila["fecha_fin"].strftime("%Y-%m-%d")

        return jsonify(datos)

    except Exception as e:

        print("ERROR PROMOCIONES:", e)

        return jsonify(
            error="No se han podido cargar las promociones."
        ), 500

    

@app.route("/api/promociones/<int:id_promocion>", methods=["GET"])
def obtener_promocion(id_promocion):

    try:

        with engine.begin() as conn:

            resultado = conn.execute(
                text("""
                    SELECT
                        id_promocion,
                        nombre,
                        fecha_inicio,
                        fecha_fin,
                        tipo,
                        descripcion,
                        id_centro
                    FROM promocion
                    WHERE id_promocion = :id
                    AND id_centro = 1
                """),
                {
                    "id": id_promocion
                }
            )

            fila = resultado.mappings().first()

        if fila is None:

            return jsonify(
                error="No se ha encontrado la promoción."
            ), 404

        datos = dict(fila)

        # Convertir fechas a texto
        if datos.get("fecha_inicio") is not None:
            datos["fecha_inicio"] = datos["fecha_inicio"].strftime(
                "%Y-%m-%d"
            )

        if datos.get("fecha_fin") is not None:
            datos["fecha_fin"] = datos["fecha_fin"].strftime(
                "%Y-%m-%d"
            )

        # Evitar problemas con valores NULL
        if datos.get("tipo") is None:
            datos["tipo"] = ""

        if datos.get("descripcion") is None:
            datos["descripcion"] = ""

        return jsonify(datos)

    except Exception as e:

        print("ERROR OBTENIENDO PROMOCIÓN:", e)

        return jsonify(
            error="No se ha podido cargar la promoción."
        ), 500

    


@app.route("/api/promociones",methods=["POST"])
def crear_promocion():
    datos=request.get_json()

    try:
        with engine.begin() as conn:
            conn.execute(
                text("""
                    INSERT INTO promocion(
                        nombre,
                        fecha_inicio,
                        fecha_fin,
                        tipo,
                        descripcion,
                        id_centro
                    )
                    VALUES(
                        :nombre,
                        :fecha_inicio,
                        :fecha_fin,
                        :tipo,
                        :descripcion,
                        1
                    )
                """),
                {
                    "nombre":datos["nombre"],
                    "fecha_inicio":datos["fecha_inicio"],
                    "fecha_fin":datos["fecha_fin"],
                    "tipo":datos.get("tipo"),
                    "descripcion":datos.get("descripcion")
                }
            )

        return jsonify(ok=True)

    except Exception as e:
        print("ERROR CREANDO PROMOCIÓN:",e)
        return jsonify(
            error="No se ha podido guardar la promoción."
        ),500


@app.route("/api/promociones/<int:id_promocion>",methods=["PUT"])
def actualizar_promocion(id_promocion):
    datos=request.get_json()

    try:
        with engine.begin() as conn:
            resultado=conn.execute(
                text("""
                    UPDATE promocion
                    SET
                        nombre=:nombre,
                        fecha_inicio=:fecha_inicio,
                        fecha_fin=:fecha_fin,
                        tipo=:tipo,
                        descripcion=:descripcion
                    WHERE id_promocion=:id
                    AND id_centro=1
                """),
                {
                    "id":id_promocion,
                    "nombre":datos["nombre"],
                    "fecha_inicio":datos["fecha_inicio"],
                    "fecha_fin":datos["fecha_fin"],
                    "tipo":datos.get("tipo"),
                    "descripcion":datos.get("descripcion")
                }
            )

        if resultado.rowcount==0:
            return jsonify(
                error="No se ha encontrado la promoción."
            ),404

        return jsonify(ok=True)

    except Exception as e:
        print("ERROR ACTUALIZANDO PROMOCIÓN:",e)
        return jsonify(
            error="No se ha podido actualizar la promoción."
        ),500


@app.route("/api/promociones/<int:id_promocion>",methods=["DELETE"])
def eliminar_promocion(id_promocion):
    try:
        with engine.begin() as conn:
            resultado=conn.execute(
                text("""
                    DELETE FROM promocion
                    WHERE id_promocion=:id
                    AND id_centro=1
                """),
                {
                    "id":id_promocion
                }
            )

        if resultado.rowcount==0:
            return jsonify(
                error="No se ha encontrado la promoción."
            ),404

        return jsonify(ok=True)

    except Exception as e:
        print("ERROR ELIMINANDO PROMOCIÓN:",e)
        return jsonify(
            error="No se ha podido eliminar la promoción."
        ),500


# ------------------------
# IMPORTAR PROMOCIONES
# ------------------------

@app.route("/importar_promociones",methods=["POST"])
def importar_promociones():

    ID_CENTRO=1

    if "archivo" not in request.files:
        return jsonify(
            error="No se ha seleccionado ningún archivo."
        ),400

    archivo=request.files["archivo"]

    if archivo.filename=="":
        return jsonify(
            error="No se ha seleccionado ningún archivo."
        ),400

    if not archivo.filename.lower().endswith(".xlsx"):
        return jsonify(
            error="El archivo debe estar en formato .xlsx."
        ),400

    try:

        df=pd.read_excel(archivo)

        columnas_obligatorias=[
            "nombre",
            "fecha_inicio",
            "fecha_fin",
            "tipo",
            "descripcion"
        ]

        columnas_faltantes=[
            columna
            for columna in columnas_obligatorias
            if columna not in df.columns
        ]

        if columnas_faltantes:
            return jsonify(
                error=
                "Faltan columnas obligatorias: "
                +", ".join(columnas_faltantes)
            ),400

        df=df[columnas_obligatorias].copy()

        df["fecha_inicio"]=pd.to_datetime(
            df["fecha_inicio"],
            errors="coerce"
        )

        df["fecha_fin"]=pd.to_datetime(
            df["fecha_fin"],
            errors="coerce"
        )

        if df["fecha_inicio"].isna().any() or df["fecha_fin"].isna().any():
            return jsonify(
                error="Hay fechas no válidas en el Excel."
            ),400

        if df["nombre"].isna().any():
            return jsonify(
                error="Hay promociones sin nombre."
            ),400

        with engine.begin() as conn:

            for _,fila in df.iterrows():

                conn.execute(
                    text("""
                        INSERT INTO promocion(
                            nombre,
                            fecha_inicio,
                            fecha_fin,
                            tipo,
                            descripcion,
                            id_centro
                        )
                        VALUES(
                            :nombre,
                            :fecha_inicio,
                            :fecha_fin,
                            :tipo,
                            :descripcion,
                            :id_centro
                        )
                    """),
                    {
                        "nombre":str(fila["nombre"]).strip(),

                        "fecha_inicio":
                            fila["fecha_inicio"].date(),

                        "fecha_fin":
                            fila["fecha_fin"].date(),

                        "tipo":
                            None
                            if pd.isna(fila["tipo"])
                            else str(fila["tipo"]).strip(),

                        "descripcion":
                            None
                            if pd.isna(fila["descripcion"])
                            else str(fila["descripcion"]).strip(),

                        "id_centro":ID_CENTRO
                    }
                )

        return jsonify(
            ok=True,
            mensaje=
            f"Promociones importadas correctamente. "
            f"Se han cargado {len(df)} promociones."
        )

    except Exception as e:

        print("ERROR AL IMPORTAR PROMOCIONES:",e)

        return jsonify(
            error="No se han podido importar las promociones."
        ),500


# ------------------------
# EXPORTAR PROMOCIONES
# ------------------------

@app.route("/exportar_promociones")
def exportar_promociones():

    try:

        df=pd.read_sql("""
            SELECT
                nombre,
                fecha_inicio,
                fecha_fin,
                tipo,
                descripcion
            FROM promocion
            WHERE id_centro=1
            ORDER BY fecha_inicio
        """,engine)

        output=BytesIO()

        with pd.ExcelWriter(
            output,
            engine="openpyxl",
            date_format="DD/MM/YYYY"
        ) as writer:

            df.to_excel(
                writer,
                index=False,
                sheet_name="Promociones"
            )

        output.seek(0)

        return send_file(
            output,
            as_attachment=True,
            download_name="promociones.xlsx",
            mimetype=
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    except Exception as e:

        print("ERROR EXPORTANDO PROMOCIONES:",e)

        return jsonify(
            error="No se han podido exportar las promociones."
        ),500


    
# ------------------------
# DATOS HISTÓRICOS
# ------------------------

@app.route("/historicos")
def historicos():
    return render_template("historicos.html")


# ------------------------
# PEDIDOS HISTÓRICOS
# ------------------------

@app.route("/api/pedidos_historicos")
def api_pedidos_historicos():

    try:

        df = pd.read_sql("""
            SELECT *
            FROM pedidohistorico
            WHERE id_centro = 1
            ORDER BY fecha
        """, engine)

        # Convertir todos los NaN / NaT a None
        # para que sean válidos en JSON
        df = df.astype(object).where(pd.notna(df), None)

        datos = df.to_dict(orient="records")

        for fila in datos:

            if fila.get("fecha") is not None:

                if hasattr(fila["fecha"], "strftime"):
                    fila["fecha"] = fila["fecha"].strftime("%Y-%m-%d")

        return jsonify(datos)

    except Exception as e:

        print("ERROR PEDIDOS HISTÓRICOS:", e)

        return jsonify(
            error="No se han podido cargar los pedidos históricos."
        ), 500

# ------------------------
# OBTENER UN DÍA
# ------------------------

@app.route("/api/pedidos_historicos/<int:id_pedido>",methods=["GET"])
def obtener_pedido_historico(id_pedido):
    try:
        df=pd.read_sql(
            """
            SELECT *
            FROM pedidohistorico
            WHERE id_pedido_historico=%s
            AND id_centro=1
            """,
            engine,
            params=(id_pedido,)
        )
        if df.empty:
            return jsonify(error="No se ha encontrado el registro."),404
        df=df.astype(object).where(pd.notna(df),None)
        fila=df.iloc[0].to_dict()
        if fila.get("fecha") is not None:
            if hasattr(fila["fecha"],"strftime"):
                fila["fecha"]=fila["fecha"].strftime("%Y-%m-%d")
        return jsonify(fila)
    except Exception as e:
        print("ERROR OBTENIENDO PEDIDO:",e)
        return jsonify(error="No se ha podido cargar el registro."),500


# ------------------------
# CREAR DÍA
# ------------------------

@app.route("/api/pedidos_historicos",methods=["POST"])
def crear_pedido_historico():

    datos=request.get_json()

    try:
        mcia_pedidos=int(datos.get("envios_2h_mcia_general_pedidos",0))
        mcia_lineas=int(datos.get("envios_2h_mcia_general_lineas",0))
        food_pedidos=int(datos.get("envios_2h_food_pedidos",0))
        food_lineas=int(datos.get("envios_2h_food_lineas",0))
        encargos_pedidos=int(datos.get("encargos_pedidos",0))
        encargos_lineas=int(datos.get("encargos_lineas",0))
        home_pedidos=int(datos.get("home_delivery_pedidos",0))
        home_lineas=int(datos.get("home_delivery_lineas",0))

        total_pedidos=(
            mcia_pedidos+
            food_pedidos+
            encargos_pedidos+
            home_pedidos
        )

        total_lineas=(
            mcia_lineas+
            food_lineas+
            encargos_lineas+
            home_lineas
        )

        with engine.begin() as conn:

            existe=conn.execute(
                text("""
                    SELECT COUNT(*)
                    FROM pedidohistorico
                    WHERE fecha=:fecha
                    AND id_centro=1
                """),
                {"fecha":datos["fecha"]}
            ).scalar()

            if existe:
                return jsonify(
                    error="Ya existe un registro para esa fecha."
                ),400

            conn.execute(
                text("""
                    INSERT INTO pedidohistorico(
                        fecha,
                        envios_2h_mcia_general_pedidos,
                        envios_2h_mcia_general_lineas,
                        envios_2h_food_pedidos,
                        envios_2h_food_lineas,
                        encargos_pedidos,
                        encargos_lineas,
                        home_delivery_pedidos,
                        home_delivery_lineas,
                        total_pedidos,
                        total_lineas,
                        id_centro
                    )
                    VALUES(
                        :fecha,
                        :mcia_pedidos,
                        :mcia_lineas,
                        :food_pedidos,
                        :food_lineas,
                        :encargos_pedidos,
                        :encargos_lineas,
                        :home_pedidos,
                        :home_lineas,
                        :total_pedidos,
                        :total_lineas,
                        1
                    )
                """),
                {
                    "fecha":datos["fecha"],
                    "mcia_pedidos":mcia_pedidos,
                    "mcia_lineas":mcia_lineas,
                    "food_pedidos":food_pedidos,
                    "food_lineas":food_lineas,
                    "encargos_pedidos":encargos_pedidos,
                    "encargos_lineas":encargos_lineas,
                    "home_pedidos":home_pedidos,
                    "home_lineas":home_lineas,
                    "total_pedidos":total_pedidos,
                    "total_lineas":total_lineas
                }
            )

        return jsonify(ok=True)

    except Exception as e:
        print("ERROR CREANDO PEDIDO:",e)
        return jsonify(
            error="No se ha podido guardar el día."
        ),500


# ------------------------
# EDITAR DÍA
# ------------------------

@app.route("/api/pedidos_historicos/<int:id_pedido>",methods=["PUT"])
def actualizar_pedido_historico(id_pedido):

    datos=request.get_json()

    try:
        mcia_pedidos=int(datos.get("envios_2h_mcia_general_pedidos",0))
        mcia_lineas=int(datos.get("envios_2h_mcia_general_lineas",0))
        food_pedidos=int(datos.get("envios_2h_food_pedidos",0))
        food_lineas=int(datos.get("envios_2h_food_lineas",0))
        encargos_pedidos=int(datos.get("encargos_pedidos",0))
        encargos_lineas=int(datos.get("encargos_lineas",0))
        home_pedidos=int(datos.get("home_delivery_pedidos",0))
        home_lineas=int(datos.get("home_delivery_lineas",0))

        total_pedidos=(
            mcia_pedidos+
            food_pedidos+
            encargos_pedidos+
            home_pedidos
        )

        total_lineas=(
            mcia_lineas+
            food_lineas+
            encargos_lineas+
            home_lineas
        )

        with engine.begin() as conn:

            resultado=conn.execute(
                text("""
                    UPDATE pedidohistorico
                    SET
                        fecha=:fecha,
                        envios_2h_mcia_general_pedidos=:mcia_pedidos,
                        envios_2h_mcia_general_lineas=:mcia_lineas,
                        envios_2h_food_pedidos=:food_pedidos,
                        envios_2h_food_lineas=:food_lineas,
                        encargos_pedidos=:encargos_pedidos,
                        encargos_lineas=:encargos_lineas,
                        home_delivery_pedidos=:home_pedidos,
                        home_delivery_lineas=:home_lineas,
                        total_pedidos=:total_pedidos,
                        total_lineas=:total_lineas
                    WHERE id_pedido_historico=:id
                    AND id_centro=1
                """),
                {
                    "id":id_pedido,
                    "fecha":datos["fecha"],
                    "mcia_pedidos":mcia_pedidos,
                    "mcia_lineas":mcia_lineas,
                    "food_pedidos":food_pedidos,
                    "food_lineas":food_lineas,
                    "encargos_pedidos":encargos_pedidos,
                    "encargos_lineas":encargos_lineas,
                    "home_pedidos":home_pedidos,
                    "home_lineas":home_lineas,
                    "total_pedidos":total_pedidos,
                    "total_lineas":total_lineas
                }
            )

        if resultado.rowcount==0:
            return jsonify(
                error="No se ha encontrado el registro."
            ),404

        return jsonify(ok=True)

    except Exception as e:
        print("ERROR ACTUALIZANDO PEDIDO:",e)
        return jsonify(
            error="No se ha podido actualizar el día."
        ),500


# ------------------------
# ELIMINAR DÍA
# ------------------------

@app.route("/api/pedidos_historicos/<int:id_pedido>",methods=["DELETE"])
def eliminar_pedido_historico(id_pedido):

    try:
        with engine.begin() as conn:

            resultado=conn.execute(
                text("""
                    DELETE FROM pedidohistorico
                    WHERE id_pedido_historico=:id
                    AND id_centro=1
                """),
                {"id":id_pedido}
            )

        if resultado.rowcount==0:
            return jsonify(
                error="No se ha encontrado el registro."
            ),404

        return jsonify(ok=True)

    except Exception as e:
        print("ERROR ELIMINANDO PEDIDO:",e)
        return jsonify(
            error="No se ha podido eliminar el día."
        ),500


# ------------------------
# IMPORTAR EXCEL
# ------------------------

@app.route("/api/pedidos_historicos/importar",methods=["POST"])
def importar_pedidos_historicos():

    if "archivo" not in request.files:
        return jsonify(
            error="No se ha seleccionado ningún archivo."
        ),400

    archivo=request.files["archivo"]

    if archivo.filename=="":
        return jsonify(
            error="No se ha seleccionado ningún archivo."
        ),400

    if not archivo.filename.lower().endswith(".xlsx"):
        return jsonify(
            error="El archivo debe estar en formato .xlsx."
        ),400

    try:

        df=pd.read_excel(archivo)

        columnas_excel=[
            "Fecha de venta",
            "Núm. pedidos 2h MCIA GENERAL",
            "Núm. Líneas 2h MCIA GENERAL",
            "Núm. pedidos 2h FOOD",
            "Núm. líneas 2h FOOD",
            "Núm. pedidos ENCARGOS",
            "Núm. líneas ENCARGOS",
            "Núm. pedidos HOME DELIVERY",
            "Núm. líneas HOME DELIVERY"
        ]

        faltantes=[
            columna
            for columna in columnas_excel
            if columna not in df.columns
        ]

        if faltantes:
            return jsonify(
                error="Faltan columnas: "+", ".join(faltantes)
            ),400

        df=df[columnas_excel].copy()

        df["Fecha de venta"]=pd.to_datetime(
            df["Fecha de venta"],
            errors="coerce"
        )

        if df["Fecha de venta"].isna().any():
            return jsonify(
                error="Hay fechas no válidas en el Excel."
            ),400

        if df["Fecha de venta"].duplicated().any():
            return jsonify(
                error="Hay fechas duplicadas en el Excel."
            ),400

        columnas_numericas=columnas_excel[1:]

        for columna in columnas_numericas:

            df[columna]=pd.to_numeric(
                df[columna],
                errors="coerce"
            )

            if df[columna].isna().any():
                return jsonify(
                    error=f"Hay valores no válidos en '{columna}'."
                ),400

            df[columna]=df[columna].astype(int)

        with engine.begin() as conn:

            for _,fila in df.iterrows():

                fecha=fila["Fecha de venta"].date()

                mcia_pedidos=int(
                    fila["Núm. pedidos 2h MCIA GENERAL"]
                )

                mcia_lineas=int(
                    fila["Núm. Líneas 2h MCIA GENERAL"]
                )

                food_pedidos=int(
                    fila["Núm. pedidos 2h FOOD"]
                )

                food_lineas=int(
                    fila["Núm. líneas 2h FOOD"]
                )

                encargos_pedidos=int(
                    fila["Núm. pedidos ENCARGOS"]
                )

                encargos_lineas=int(
                    fila["Núm. líneas ENCARGOS"]
                )

                home_pedidos=int(
                    fila["Núm. pedidos HOME DELIVERY"]
                )

                home_lineas=int(
                    fila["Núm. líneas HOME DELIVERY"]
                )

                total_pedidos=(
                    mcia_pedidos+
                    food_pedidos+
                    encargos_pedidos+
                    home_pedidos
                )

                total_lineas=(
                    mcia_lineas+
                    food_lineas+
                    encargos_lineas+
                    home_lineas
                )

                existe=conn.execute(
                    text("""
                        SELECT id_pedido_historico
                        FROM pedidohistorico
                        WHERE fecha=:fecha
                        AND id_centro=1
                    """),
                    {"fecha":fecha}
                ).fetchone()

                datos={
                    "fecha":fecha,
                    "mcia_pedidos":mcia_pedidos,
                    "mcia_lineas":mcia_lineas,
                    "food_pedidos":food_pedidos,
                    "food_lineas":food_lineas,
                    "encargos_pedidos":encargos_pedidos,
                    "encargos_lineas":encargos_lineas,
                    "home_pedidos":home_pedidos,
                    "home_lineas":home_lineas,
                    "total_pedidos":total_pedidos,
                    "total_lineas":total_lineas
                }

                if existe:

                    conn.execute(
                        text("""
                            UPDATE pedidohistorico
                            SET
                                envios_2h_mcia_general_pedidos=:mcia_pedidos,
                                envios_2h_mcia_general_lineas=:mcia_lineas,
                                envios_2h_food_pedidos=:food_pedidos,
                                envios_2h_food_lineas=:food_lineas,
                                encargos_pedidos=:encargos_pedidos,
                                encargos_lineas=:encargos_lineas,
                                home_delivery_pedidos=:home_pedidos,
                                home_delivery_lineas=:home_lineas,
                                total_pedidos=:total_pedidos,
                                total_lineas=:total_lineas
                            WHERE fecha=:fecha
                            AND id_centro=1
                        """),
                        datos
                    )

                else:

                    conn.execute(
                        text("""
                            INSERT INTO pedidohistorico(
                                fecha,
                                envios_2h_mcia_general_pedidos,
                                envios_2h_mcia_general_lineas,
                                envios_2h_food_pedidos,
                                envios_2h_food_lineas,
                                encargos_pedidos,
                                encargos_lineas,
                                home_delivery_pedidos,
                                home_delivery_lineas,
                                total_pedidos,
                                total_lineas,
                                id_centro
                            )
                            VALUES(
                                :fecha,
                                :mcia_pedidos,
                                :mcia_lineas,
                                :food_pedidos,
                                :food_lineas,
                                :encargos_pedidos,
                                :encargos_lineas,
                                :home_pedidos,
                                :home_lineas,
                                :total_pedidos,
                                :total_lineas,
                                1
                            )
                        """),
                        datos
                    )

        return jsonify(
            ok=True,
            mensaje=f"Se han importado {len(df)} días correctamente."
        )

    except Exception as e:

        print("ERROR IMPORTANDO PEDIDOS:",e)

        return jsonify(
            error="No se han podido importar los pedidos históricos."
        ),500


# ------------------------
# EXPORTAR EXCEL
# ------------------------

@app.route("/api/pedidos_historicos/exportar")
def exportar_pedidos_historicos():

    try:

        df = pd.read_sql("""
            SELECT
                fecha,
                envios_2h_mcia_general_pedidos,
                envios_2h_mcia_general_lineas,
                envios_2h_food_pedidos,
                envios_2h_food_lineas,
                encargos_pedidos,
                encargos_lineas,
                home_delivery_pedidos,
                home_delivery_lineas,
                total_pedidos,
                total_lineas
            FROM pedidohistorico
            WHERE id_centro = 1
            ORDER BY fecha
        """, engine)

        df.columns = [
            "Fecha de venta",
            "Núm. pedidos 2h MCIA GENERAL",
            "Núm. líneas 2h MCIA GENERAL",
            "Núm. pedidos 2h FOOD",
            "Núm. líneas 2h FOOD",
            "Núm. pedidos ENCARGOS",
            "Núm. líneas ENCARGOS",
            "Núm. pedidos HOME DELIVERY",
            "Núm. líneas HOME DELIVERY",
            "Total PEDIDOS",
            "Total LÍNEAS"
        ]

        output = BytesIO()

        with pd.ExcelWriter(
            output,
            engine="openpyxl",
            date_format="DD/MM/YYYY"
        ) as writer:

            df.to_excel(
                writer,
                index=False,
                sheet_name="Pedidos históricos"
            )

            hoja = writer.book["Pedidos históricos"]

            # Formato de fechas
            for celda in hoja["A"][1:]:
                celda.number_format = "DD/MM/YYYY"

            # Ancho de columnas
            anchos = {
                "A": 16,
                "B": 28,
                "C": 30,
                "D": 24,
                "E": 25,
                "F": 24,
                "G": 25,
                "H": 28,
                "I": 30,
                "J": 16,
                "K": 16
            }

            for columna, ancho in anchos.items():
                hoja.column_dimensions[columna].width = ancho

        output.seek(0)

        return send_file(
            output,
            as_attachment=True,
            download_name="pedidos_historicos.xlsx",
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    except Exception as e:

        print("ERROR EXPORTANDO PEDIDOS HISTÓRICOS:", e)

        return jsonify(
            error="No se han podido exportar los pedidos históricos."
        ), 500
    
# ------------------------
# PREDICCIÓN
# ------------------------
@app.route("/prediccion")
def prediccion():
    return render_template("prediccion.html")
# ------------------------
# PLANIFICACIÓN
# ------------------------
@app.route("/planificacion")
def planificacion():
    return render_template("planificacion.html")
# ------------------------
# CONFIGURACIÓN
# ------------------------
@app.route("/configuracion")
def configuracion():
    return render_template("configuracion.html")
if __name__=="__main__":
    app.run(debug=True)
// =====================================================
// CONFIGURACIÓN
// =====================================================

let datosPlanificacion = [];
let tareas = [];
let fechaInicioSemana = null;
let trabajadores = [];


// =====================================================
// OBTENER NOMBRE DEL DÍA
// =====================================================

function obtenerNombreDia(fecha) {

    const dias = [
        "DOMINGO",
        "LUNES",
        "MARTES",
        "MIÉRCOLES",
        "JUEVES",
        "VIERNES",
        "SÁBADO",
        "DOMINGO"
    ];

    return dias[
        new Date(fecha + "T00:00:00").getDay()
    ];
}


// =====================================================
// OBTENER LOS 7 DÍAS DE LA SEMANA
// =====================================================

function obtenerDiasSemana(fechaInicio) {

    const dias = [];

    for (let i = 0; i < 7; i++) {

        const fecha = new Date(fechaInicio);

        fecha.setDate(
            fecha.getDate() + i
        );

        const año = fecha.getFullYear();
        const mes = String(
            fecha.getMonth() + 1
        ).padStart(2, "0");

        const dia = String(
            fecha.getDate()
        ).padStart(2, "0");

        const fechaTexto =
            `${año}-${mes}-${dia}`;

        dias.push({
            fecha: fechaTexto,
            nombre: obtenerNombreDia(fechaTexto),
            numero: dia
        });
    }

    return dias;
}


// =====================================================
// CABECERA DE LA TABLA
// =====================================================

function crearCabecera(dias) {

    const fila = document.createElement("tr");

    const thTarea =
        document.createElement("th");

    thTarea.textContent = "TAREA";

    fila.appendChild(thTarea);


    dias.forEach(dia => {

        const th =
            document.createElement("th");

        th.innerHTML = `
            <span class="dia-nombre">
                ${dia.nombre}
            </span>

            <span class="dia-numero">
                ${dia.numero}
            </span>
        `;

        fila.appendChild(th);

    });


    return fila;
}


// =====================================================
// TEXTO DE LA SEMANA
// =====================================================

function actualizarTextoSemana(dias) {

    const elemento =
        document.getElementById(
            "semanaActual"
        );

    if (!elemento || dias.length === 0) {
        return;
    }


    const primera =
        new Date(
            dias[0].fecha + "T00:00:00"
        );

    const ultima =
        new Date(
            dias[6].fecha + "T00:00:00"
        );


    const opciones = {
        day: "numeric",
        month: "long"
    };


    elemento.textContent =
        `Semana del ${
            primera.toLocaleDateString(
                "es-ES",
                opciones
            )
        } al ${
            ultima.toLocaleDateString(
                "es-ES",
                opciones
            )
        }`;
}


// =====================================================
// AGRUPAR DATOS POR TAREA
// =====================================================

function agruparPorTarea(datos) {

    const tareasAgrupadas = {};

    tareas.forEach(tarea => {

        tareasAgrupadas[tarea.id_tarea] = {
            id_tarea: tarea.id_tarea,
            nombre: tarea.nombre,
            datos: []
        };

    });


    datos.forEach(dato => {

        if (!tareasAgrupadas[dato.id_tarea]) {

            tareasAgrupadas[dato.id_tarea] = {
                id_tarea: dato.id_tarea,
                nombre: dato.tarea,
                datos: []
            };

        }

        tareasAgrupadas[dato.id_tarea].datos.push(
            dato
        );

    });


    return Object.values(tareasAgrupadas);
}
// =====================================================
// CREAR TRABAJADOR
// =====================================================

function crearAsignacion(dato) {

    const asignacion =
        document.createElement("div");

    asignacion.classList.add("asignacion");

    if (dato.fijo_discontinuo) {
        asignacion.classList.add("fijo-discontinuo");
    }

    // Nombre del trabajador
    const enlace =
        document.createElement("a");

    enlace.href =
        `/calendario-trabajador/${dato.id_trabajador}`;

    enlace.classList.add("asignacion-nombre");

    enlace.textContent =
        dato.trabajador;


    // Botón para cambiar trabajador
    const botonEditar =
        document.createElement("button");

    botonEditar.type = "button";

    botonEditar.classList.add(
        "boton-editar-asignacion"
    );

    botonEditar.innerHTML =
        '<i class="fa-solid fa-pen"></i>';

    botonEditar.title =
        "Cambiar trabajador";


    botonEditar.addEventListener(
        "click",
        (evento) => {

            evento.preventDefault();
            evento.stopPropagation();

            abrirModalCambio(dato);

        }
    );


    asignacion.appendChild(enlace);
    asignacion.appendChild(botonEditar);

    return asignacion;
}

// =====================================================
// CREAR FILA DE UNA TAREA
// =====================================================

function crearFilaTarea(
    tarea,
    dias
) {

    const fila =
        document.createElement("tr");


    // -----------------------------------------------
    // NOMBRE DE LA TAREA
    // -----------------------------------------------

    const celdaTarea =
        document.createElement("td");

    celdaTarea.classList.add(
        "tarea-cell"
    );

    celdaTarea.textContent =
        tarea.nombre;

    fila.appendChild(
        celdaTarea
    );


    // -----------------------------------------------
    // DÍAS
    // -----------------------------------------------

    dias.forEach(dia => {

        const celda =
            document.createElement("td");

        celda.classList.add(
            "planificacion-cell"
        );


        // Trabajadores de esta tarea
        // en este día

        const trabajadores =
            tarea.datos.filter(
                dato =>
                    dato.fecha === dia.fecha
            );


        if (trabajadores.length === 0) {

            celda.innerHTML = `
                <span class="sin-asignacion">
                    —
                </span>
            `;

        } else {

            trabajadores.forEach(
                dato => {

                    celda.appendChild(
                        crearAsignacion(dato)
                    );

                }
            );

        }


        fila.appendChild(
            celda
        );

    });


    return fila;
}


// =====================================================
// CREAR TABLA
// =====================================================

function crearTabla(
    datos,
    tabla,
    dias
) {

    tabla.innerHTML = "";


    const tareas =
        agruparPorTarea(datos);


    tareas.forEach(tarea => {

        const fila =
            crearFilaTarea(
                tarea,
                dias
            );

        tabla.appendChild(
            fila
        );

    });

}


// =====================================================
// CARGAR UNA DE LAS DOS TABLAS
// =====================================================

function cargarTabla(
    turno,
    cabeceraId,
    tablaId,
    dias
) {

    const cabecera =
        document.getElementById(
            cabeceraId
        );

    const tabla =
        document.getElementById(
            tablaId
        );


    cabecera.innerHTML = "";
    tabla.innerHTML = "";


    // Cabecera
    cabecera.appendChild(
        crearCabecera(dias)
    );


    // Filtrar mañana / tarde
    const datosTurno =
        datosPlanificacion.filter(
            dato =>
                Number(dato.turno) === turno &&
                dias.some(
                    dia =>
                        dia.fecha === dato.fecha
                )
        );


    crearTabla(
        datosTurno,
        tabla,
        dias
    );
}


// =====================================================
// CARGAR PLANIFICACIÓN
// =====================================================

function cargarPlanificacion() {

    const dias =
        obtenerDiasSemana(
            fechaInicioSemana
        );


    actualizarTextoSemana(
        dias
    );


    // MAÑANA
    cargarTabla(
        0,
        "cabeceraMananas",
        "tablaMananas",
        dias
    );


    // TARDE
    cargarTabla(
        1,
        "cabeceraTardes",
        "tablaTardes",
        dias
    );
}


// =====================================================
// OBTENER SEMANA ACTUAL
// =====================================================

function obtenerPrimeraFecha() {

    if (
        !datosPlanificacion ||
        datosPlanificacion.length === 0
    ) {

        return new Date();

    }


    const hoy = new Date();

    hoy.setHours(0, 0, 0, 0);


    const fechas =
        datosPlanificacion
            .map(
                dato =>
                    new Date(
                        dato.fecha + "T00:00:00"
                    )
            )
            .filter(
                fecha => fecha >= hoy
            )
            .sort(
                (a, b) => a - b
            );


    let fecha;

    if (fechas.length > 0) {

        fecha = fechas[0];

    } else {

        const todasLasFechas =
            datosPlanificacion
                .map(
                    dato =>
                        new Date(
                            dato.fecha + "T00:00:00"
                        )
                )
                .sort(
                    (a, b) => a - b
                );

        fecha =
            todasLasFechas[
                todasLasFechas.length - 1
            ];

    }


    // Llevar la fecha al lunes de esa semana

    const diaSemana =
        fecha.getDay();

    const diferencia =
        diaSemana === 0
            ? 6
            : diaSemana - 1;


    fecha.setDate(
        fecha.getDate() - diferencia
    );


    return fecha;
}

// =====================================================
// CARGAR DATOS DESDE FLASK
// =====================================================

async function cargarDatos() {

    try {

        const periodoSeleccionado = obtenerPeriodoPrediccionSeleccionado();
        const params = new URLSearchParams();

        if (periodoSeleccionado?.fecha_inicio) {
            params.append("fecha_inicio", periodoSeleccionado.fecha_inicio);
        }

        if (periodoSeleccionado?.fecha_fin) {
            params.append("fecha_fin", periodoSeleccionado.fecha_fin);
        }

        const urlPlanificacion = params.toString()
            ? `/api/planificacion?${params.toString()}`
            : "/api/planificacion";

        const [
            respuestaPlanificacion,
            respuestaTareas,
            respuestaTrabajadores
        ] = await Promise.all([
            fetch(urlPlanificacion),
            fetch("/api/tareas"),
            fetch("/api/trabajadores")
        ]);

        if (
            !respuestaPlanificacion.ok ||
            !respuestaTareas.ok ||
            !respuestaTrabajadores.ok
        ) {

            throw new Error(
                "No se han podido cargar los datos"
            );

        }


        datosPlanificacion =
            await respuestaPlanificacion.json();

        tareas =
            await respuestaTareas.json();

        trabajadores =
            await respuestaTrabajadores.json();


        if (
            datosPlanificacion.error
        ) {

            throw new Error(
                datosPlanificacion.error
            );

        }


        if (
            tareas.error
        ) {

            throw new Error(
                tareas.error
            );

        }


        fechaInicioSemana =
            obtenerPrimeraFecha();


        cargarPlanificacion();


    } catch (error) {

        console.error(
            "Error cargando planificación:",
            error
        );

    }
}

// =====================================================
// CAMBIAR SEMANA
// =====================================================

function cambiarSemana(
    numeroSemanas
) {

    fechaInicioSemana.setDate(
        fechaInicioSemana.getDate() +
        numeroSemanas * 7
    );


    cargarPlanificacion();
}


// =====================================================
// BOTONES
// =====================================================

document.addEventListener(
    "DOMContentLoaded",
    () => {

        document
            .getElementById(
                "semanaAnterior"
            )
            .addEventListener(
                "click",
                () => {
                    cambiarSemana(-1);
                }
            );


        document
            .getElementById(
                "semanaSiguiente"
            )
            .addEventListener(
                "click",
                () => {
                    cambiarSemana(1);
                }
            );


        cargarDatos();

    }
);


// EXPORTAR A EXCEL
document
    .getElementById("exportarExcel")
    .addEventListener("click", () => {

        window.location.href =
            "/api/planificacion/exportar";

    });

function obtenerPeriodoPrediccionSeleccionado() {
    const fuentes = [
        () => window.__empleaPeriodoPrediccion,
        () => {
            try { return JSON.parse(localStorage.getItem("emplea_periodo_prediccion") || "null"); }
            catch { return null; }
        },
        () => {
            try { return JSON.parse(sessionStorage.getItem("emplea_periodo_prediccion") || "null"); }
            catch { return null; }
        }
    ];

    for (const obtener of fuentes) {
        try {
            const datos = obtener();
            if (datos && datos.fecha_inicio && datos.fecha_fin) {
                return {
                    fecha_inicio: datos.fecha_inicio,
                    fecha_fin: datos.fecha_fin
                };
            }
        } catch (error) {
            console.warn("No se pudo recuperar el periodo de predicción:", error);
        }
    }

    const ahora = new Date();
    const mes = ahora.getMonth() + 1;
    let inicio = "";
    let fin = "";

    if (mes <= 3) {
        inicio = `${ahora.getFullYear()}-01-01`;
        fin = `${ahora.getFullYear()}-03-31`;
    } else if (mes <= 6) {
        inicio = `${ahora.getFullYear()}-04-01`;
        fin = `${ahora.getFullYear()}-06-30`;
    } else if (mes <= 9) {
        inicio = `${ahora.getFullYear()}-07-01`;
        fin = `${ahora.getFullYear()}-09-30`;
    } else {
        inicio = `${ahora.getFullYear()}-10-01`;
        fin = `${ahora.getFullYear()}-12-31`;
    }

    return { fecha_inicio: inicio, fecha_fin: fin };
}

// GENERAR PLANIFICACIÓN
document
    .getElementById("generarPlanificacion")
    .addEventListener("click", async () => {

        const boton = document.getElementById(
            "generarPlanificacion"
        );
        const mensajeTiempo = document.getElementById("mensajeTiempoEstimado");

        boton.disabled = true;
        if (mensajeTiempo) {
            mensajeTiempo.hidden = false;
            mensajeTiempo.textContent = "Tiempo estimado: 2 minutos";
        }

        const textoOriginal = boton.innerHTML;

        boton.innerHTML =
            '<i class="fa-solid fa-spinner fa-spin"></i> Generando...';

        try {

            const periodoSeleccionado = obtenerPeriodoPrediccionSeleccionado();
            const fechaInicio = periodoSeleccionado?.fecha_inicio || document.getElementById("fechaInicio")?.value || null;
            const fechaFin = periodoSeleccionado?.fecha_fin || document.getElementById("fechaFin")?.value || null;

            const payload = {};
            if (fechaInicio) payload.fecha_inicio = fechaInicio;
            if (fechaFin) payload.fecha_fin = fechaFin;

            if (!fechaInicio || !fechaFin) {
                throw new Error("No hay un periodo seleccionado en Predicción.");
            }

            const diasPeriodo = ((new Date(fechaFin + "T00:00:00") - new Date(fechaInicio + "T00:00:00")) / 86400000) + 1;
            if (diasPeriodo < 30) {
                throw new Error("Selecciona un periodo mínimo de 1 mes para generar la planificación.");
            }

            const respuesta = await fetch(
                "/api/planificacion/generar",
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify(payload)
                }
            );

            const datos = await respuesta.json();

            if (!respuesta.ok || !datos.ok) {
                throw new Error(
                    datos.error ||
                    "No se ha podido generar la planificación."
                );
            }

            alert(
                "La planificación se ha generado correctamente."
            );

            // Volver a cargar los datos de la interfaz
            cargarDatos();

        } catch (error) {

            console.error(error);

            alert(
                "Error al generar la planificación:\n" +
                error.message
            );

        } finally {

            boton.disabled = false;
            boton.innerHTML = textoOriginal;
            if (mensajeTiempo) {
                mensajeTiempo.hidden = false;
                mensajeTiempo.textContent = "Tiempo estimado: 2 minutos";
            }

        }

    });


// ============================================================
// CAMBIO FORZADO DE TRABAJADOR
// ============================================================

function abrirModalCambio(dato) {

    // Si ya existe un modal, eliminarlo
    const modalAnterior =
        document.getElementById("modalCambio");

    if (modalAnterior) {
        modalAnterior.remove();
    }


    const modal =
        document.createElement("div");

    modal.id = "modalCambio";
    modal.classList.add("modal-cambio");


    modal.innerHTML = `
        <div class="modal-cambio-contenido">

            <button
                type="button"
                class="modal-cambio-cerrar"
                id="cerrarModalCambio"
            >
                ×
            </button>

            <h2>Cambiar trabajador</h2>

            <p>
                <strong>Fecha:</strong>
                ${dato.fecha}
            </p>

            <p>
                <strong>Tarea:</strong>
                ${dato.tarea}
            </p>

            <p>
                <strong>Turno:</strong>
                ${Number(dato.turno) === 0
                    ? "Mañana"
                    : "Tarde"}
            </p>

            <p>
                <strong>Trabajador actual:</strong>
                ${dato.trabajador}
            </p>

            <label for="nuevoTrabajador">
                Nuevo trabajador
            </label>

            <select id="nuevoTrabajador">

                <option value="">
                    Selecciona un trabajador
                </option>

                ${trabajadores
                    .filter(
                        trabajador =>
                            Number(trabajador.id_trabajador)
                            !== Number(dato.id_trabajador)
                    )
                    .map(
                        trabajador => `
                            <option
                                value="${trabajador.id_trabajador}"
                            >
                                ${trabajador.trabajador}
                            </option>
                        `
                    )
                    .join("")
                }

            </select>

            <div
                id="warningCompetencia"
                class="warning-competencia"
                style="display:none;"
            ></div>

            <label for="motivoCambio">
                Motivo
            </label>

            <textarea
                id="motivoCambio"
                placeholder="Motivo del cambio (opcional)"
            ></textarea>

            <div class="modal-cambio-botones">

                <button
                    type="button"
                    id="cancelarCambio"
                >
                    Cancelar
                </button>

                <button
                    type="button"
                    id="confirmarCambio"
                >
                    Forzar cambio
                </button>

            </div>

        </div>
    `;


    document.body.appendChild(modal);


    // Cerrar
    document
        .getElementById("cerrarModalCambio")
        .addEventListener(
            "click",
            cerrarModalCambio
        );

    document
        .getElementById("cancelarCambio")
        .addEventListener(
            "click",
            cerrarModalCambio
        );


    // Comprobar competencia al seleccionar
    document
        .getElementById("nuevoTrabajador")
        .addEventListener(
            "change",
            () => comprobarCompetencia(dato)
        );


    // Confirmar
    document
        .getElementById("confirmarCambio")
        .addEventListener(
            "click",
            () => guardarCambio(dato)
        );
}


// ============================================================
// COMPROBAR COMPETENCIA
// ============================================================

async function comprobarCompetencia(dato) {

    const select =
        document.getElementById(
            "nuevoTrabajador"
        );

    const warning =
        document.getElementById(
            "warningCompetencia"
        );

    const idTrabajador =
        select.value;


    warning.style.display = "none";
    warning.innerHTML = "";


    if (!idTrabajador) {
        return;
    }


    try {

        const respuesta =
            await fetch(
                `/competencias_trabajador/${idTrabajador}`
            );


        if (!respuesta.ok) {
            throw new Error(
                "No se han podido consultar las competencias."
            );
        }


        const competencias =
            await respuesta.json();


        const sabeHacerTarea =
            competencias.some(
                competencia =>
                    Number(competencia.id_tarea)
                    === Number(dato.id_tarea)
            );


        if (!sabeHacerTarea) {

            const trabajador =
                trabajadores.find(
                    trabajador =>
                        Number(
                            trabajador.id_trabajador
                        ) === Number(idTrabajador)
                );


            warning.style.display = "block";

            warning.innerHTML = `
                <strong>⚠️ Atención:</strong>
                ${trabajador?.trabajador || "Este trabajador"}
                no tiene registrada la competencia
                necesaria para realizar esta tarea.
                <br>
                Puedes continuar y forzar el cambio.
            `;
        }


    } catch (error) {

        console.error(
            "Error comprobando competencia:",
            error
        );

    }
}


// ============================================================
// GUARDAR CAMBIO
// ============================================================

async function guardarCambio(dato) {

    const select =
        document.getElementById(
            "nuevoTrabajador"
        );

    const motivo =
        document.getElementById(
            "motivoCambio"
        ).value;


    const nuevoTrabajador =
        select.value;


    if (!nuevoTrabajador) {

        alert(
            "Selecciona un trabajador."
        );

        return;
    }


    const confirmar =
        confirm(
            "¿Quieres realizar este cambio forzado?"
        );


    if (!confirmar) {
        return;
    }


    try {

        const respuesta =
            await fetch(
                "/api/cambios-forzados",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({

                        fecha: dato.fecha,

                        id_tarea:
                            dato.id_tarea,

                        trabajador_anterior:
                            dato.id_trabajador,

                        trabajador_nuevo:
                            Number(nuevoTrabajador),

                        turno:
                            Number(dato.turno),

                        motivo:
                            motivo || null

                    })
                }
            );


        const resultado =
            await respuesta.json();


        if (!respuesta.ok || !resultado.ok) {

            throw new Error(
                resultado.error ||
                "No se ha podido guardar el cambio."
            );

        }


        alert(
            "Cambio realizado correctamente."
        );


        cerrarModalCambio();

        // Recargar la planificación
        await cargarDatos();


    } catch (error) {

        console.error(
            "Error guardando cambio:",
            error
        );

        alert(
            error.message
        );

    }
}


// ============================================================
// CERRAR MODAL
// ============================================================

function cerrarModalCambio() {

    const modal =
        document.getElementById(
            "modalCambio"
        );

    if (modal) {
        modal.remove();
    }
}
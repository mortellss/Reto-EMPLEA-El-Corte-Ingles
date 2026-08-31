// =====================================================
// CONFIGURACIÓN
// =====================================================

let datosPlanificacion = [];
let tareas = [];
let fechaInicioSemana = null;

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
            dias[5].fecha + "T00:00:00"
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

    asignacion.classList.add(
        "asignacion"
    );


    // Fijo discontinuo
    if (dato.fijo_discontinuo) {

        asignacion.classList.add(
            "fijo-discontinuo"
        );

    }


    asignacion.innerHTML = `
        <a
            href="/calendario-trabajador/${dato.id_trabajador}"
            class="asignacion-nombre"
        >
            ${dato.trabajador}
        </a>
    `;


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
// OBTENER PRIMERA FECHA DISPONIBLE
// =====================================================

function obtenerPrimeraFecha() {

    if (
        !datosPlanificacion ||
        datosPlanificacion.length === 0
    ) {

        return new Date();

    }


    const fechas =
        datosPlanificacion
            .map(
                dato =>
                    new Date(
                        dato.fecha +
                        "T00:00:00"
                    )
            )
            .sort(
                (a, b) => a - b
            );


    return fechas[0];
}


// =====================================================
// CARGAR DATOS DESDE FLASK
// =====================================================

async function cargarDatos() {

    try {

        const [
            respuestaPlanificacion,
            respuestaTareas
        ] = await Promise.all([

            fetch("/api/planificacion"),

            fetch("/api/tareas")

        ]);


        if (
            !respuestaPlanificacion.ok ||
            !respuestaTareas.ok
        ) {

            throw new Error(
                "No se han podido cargar los datos"
            );

        }


        datosPlanificacion =
            await respuestaPlanificacion.json();

        tareas =
            await respuestaTareas.json();


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

// GENERAR PLANIFICACIÓN
document
    .getElementById("generarPlanificacion")
    .addEventListener("click", async () => {

        const boton = document.getElementById(
            "generarPlanificacion"
        );

        boton.disabled = true;

        const textoOriginal = boton.innerHTML;

        boton.innerHTML =
            '<i class="fa-solid fa-spinner fa-spin"></i> Generando...';

        try {

            const respuesta = await fetch(
                "/api/planificacion/generar",
                {
                    method: "POST"
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

        }

    });
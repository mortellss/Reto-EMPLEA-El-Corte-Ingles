const idTrabajador = window.location.pathname.split("/").pop();

let datosCalendario = [];
let datosDisponibilidad = [];
let datosTrabajador = null;

let fechaActual = new Date();


/* ============================================================
   CARGAR DATOS
   ============================================================ */

async function cargarCalendario() {

    try {

        const respuesta = await fetch(
            `/api/calendario-trabajador/${idTrabajador}`
        );

        if (!respuesta.ok) {
            throw new Error(
                "No se ha podido cargar el calendario."
            );
        }

        const datos = await respuesta.json();

        datosCalendario = datos.calendarizacion || [];
        datosDisponibilidad = datos.disponibilidad || [];
        datosTrabajador = datos.trabajador || null;

        mostrarInformacionTrabajador();

        pintarCalendario();

    } catch (error) {

        console.error(error);

        document.getElementById("diasCalendario").innerHTML = `
            <p class="error-calendario">
                No se ha podido cargar el calendario.
            </p>
        `;
    }
}


/* ============================================================
   INFORMACIÓN DEL TRABAJADOR
   ============================================================ */

function mostrarInformacionTrabajador() {

    if (!datosTrabajador) {
        return;
    }

    const nombre =
        `${datosTrabajador.nombre || ""} ${datosTrabajador.apellidos || ""}`.trim();

    document.getElementById(
        "nombreTrabajador"
    ).textContent = nombre || "Trabajador";


    let informacion = [];

    if (datosTrabajador.numero_vendedor) {
        informacion.push(
            `Vendedor ${datosTrabajador.numero_vendedor}`
        );
    }

    if (datosTrabajador.contrato) {
        informacion.push(
            datosTrabajador.contrato
        );
    }

    if (datosTrabajador.jornada !== null &&
        datosTrabajador.jornada !== undefined) {

        informacion.push(
            `${datosTrabajador.jornada}% de jornada`
        );
    }

    if (datosTrabajador.horas_por_turno) {

        informacion.push(
            `${datosTrabajador.horas_por_turno} h/turno`
        );
    }

    const distintivo =
        datosTrabajador.fijo_discontinuo
            ? `<span class="distintivo-fijo-discontinuo">Fijo discontinuo</span>`
            : "";

    document.getElementById(
        "informacionTrabajador"
    ).innerHTML =
        `${informacion.join(" · ")} ${distintivo}`;
}

/* ============================================================
   COMPROBAR VACACIONES / AUSENCIA
   ============================================================ */

function obtenerDisponibilidad(fecha) {

    return datosDisponibilidad.find(
        disponibilidad => {

            return (
                fecha >= disponibilidad.fecha_inicio &&
                fecha <= disponibilidad.fecha_fin
            );
        }
    );
}


/* ============================================================
   CALENDARIO MENSUAL
   ============================================================ */

function pintarCalendario() {

    const contenedor =
        document.getElementById("diasCalendario");

    const titulo =
        document.getElementById("mesActual");


    const año =
        fechaActual.getFullYear();

    const mes =
        fechaActual.getMonth();


    const nombreMes =
        fechaActual.toLocaleDateString(
            "es-ES",
            {
                month: "long",
                year: "numeric"
            }
        );


    titulo.textContent =
        nombreMes.charAt(0).toUpperCase()
        + nombreMes.slice(1);


    contenedor.innerHTML = "";


    const primerDia =
        new Date(año, mes, 1);

    const ultimoDia =
        new Date(año, mes + 1, 0);


    /*
     * JavaScript:
     * domingo = 0
     *
     * Nuestro calendario:
     * lunes = 0
     */

    let diaSemana =
        primerDia.getDay();

    diaSemana =
        diaSemana === 0
            ? 6
            : diaSemana - 1;


    /* Espacios anteriores */

    for (
        let i = 0;
        i < diaSemana;
        i++
    ) {

        const vacio =
            document.createElement("div");

        vacio.className =
            "dia-calendario vacio";

        contenedor.appendChild(vacio);
    }


    /* ========================================================
       DÍAS DEL MES
       ======================================================== */

    for (
        let dia = 1;
        dia <= ultimoDia.getDate();
        dia++
    ) {

        const fecha =
            `${año}-${String(mes + 1).padStart(2, "0")}-${String(dia).padStart(2, "0")}`;


        const registros =
            datosCalendario.filter(
                registro =>
                    registro.fecha === fecha
            );


        const disponibilidad =
            obtenerDisponibilidad(fecha);


        const elemento =
            document.createElement("div");


        elemento.className =
            "dia-calendario";


        /* Número */

        elemento.innerHTML = `
            <div class="numero-dia">
                ${dia}
            </div>
        `;


        /* ====================================================
           VACACIONES / AUSENCIA
           ==================================================== */

        if (disponibilidad) {

            const motivo =
                (disponibilidad.motivo || "")
                    .toLowerCase();


            if (
                motivo.includes("vacacion") ||
                motivo.includes("vacaciones")
            ) {

                elemento.classList.add(
                    "vacaciones"
                );

                elemento.innerHTML += `
                    <div class="estado-dia">
                        Vacaciones
                    </div>
                `;

            } else {

                /*
                 * Para otras ausencias utilizamos
                 * también el estado de no disponibilidad.
                 */

                elemento.classList.add(
                    "vacaciones"
                );

                elemento.innerHTML += `
                    <div class="estado-dia">
                        ${disponibilidad.motivo || "Ausencia"}
                    </div>
                `;
            }

        }


        /* ====================================================
           DÍA SIN ASIGNACIÓN → LIBRE
           ==================================================== */

        else if (registros.length === 0) {

            elemento.classList.add(
                "libre"
            );

            elemento.innerHTML += `
                <div class="estado-dia">
                    Libre
                </div>
            `;

        }


        /* ====================================================
            DÍA TRABAJADO
            ==================================================== */
            else {
                const registro = registros[0];
                const turno = Number(registro.turno);
                if (turno === 0) {
                    elemento.classList.add("manana");
                    elemento.innerHTML += `
                        <div class="estado-dia">
                            Mañana
                        </div>
                    `;
                } else {
                    elemento.classList.add("tarde");
                    elemento.innerHTML += `
                        <div class="estado-dia">
                            Tarde
                        </div>
                    `;
                }
                const tareas = registros.filter(r => r.tarea).map(r => r.tarea);
                if (tareas.length > 0) {
                    elemento.innerHTML += `
                        <div class="tarea-dia">
                            ${tareas[0]}
                        </div>
                    `;
                }
                if (tareas.length > 1) {
                    elemento.innerHTML += `
                        <div class="mas-tareas">
                            +${tareas.length - 1} más
                        </div>
                    `;
                }
            }
        /* ====================================================
           CLICK EN EL DÍA
           ==================================================== */

        elemento.addEventListener(
            "click",
            () => {

                abrirModal(
                    fecha,
                    registros,
                    disponibilidad
                );

            }
        );


        contenedor.appendChild(
            elemento
        );
    }
}


/* ============================================================
   MODAL
   ============================================================ */

function abrirModal(
    fecha,
    registros,
    disponibilidad
) {

    const modal =
        document.getElementById(
            "modalDia"
        );

    const modalFecha =
        document.getElementById(
            "modalFecha"
        );

    const modalDetalles =
        document.getElementById(
            "modalDetalles"
        );


    const fechaObjeto =
        new Date(
            `${fecha}T00:00:00`
        );


    const fechaTexto =
        fechaObjeto.toLocaleDateString(
            "es-ES",
            {
                weekday: "long",
                day: "numeric",
                month: "long",
                year: "numeric"
            }
        );


    modalFecha.textContent =
        fechaTexto.charAt(0).toUpperCase()
        + fechaTexto.slice(1);


    /* ========================================================
       VACACIONES
       ======================================================== */

    if (disponibilidad) {

        modalDetalles.innerHTML = `
            <div class="detalle-estado vacaciones">

                <div class="detalle-icono">
                    <i class="fa-solid fa-umbrella-beach"></i>
                </div>

                <div>
                    <strong>
                        ${disponibilidad.motivo || "Ausencia"}
                    </strong>

                    <p>
                        Desde
                        ${formatearFecha(
                            disponibilidad.fecha_inicio
                        )}
                        hasta
                        ${formatearFecha(
                            disponibilidad.fecha_fin
                        )}
                    </p>
                </div>

            </div>
        `;

        modal.classList.add("visible");

        return;
    }


    /* ========================================================
       LIBRE
       ======================================================== */

    if (registros.length === 0) {

        modalDetalles.innerHTML = `
            <div class="detalle-estado libre">

                <div class="detalle-icono">
                    <i class="fa-solid fa-mug-hot"></i>
                </div>

                <div>
                    <strong>
                        Día libre
                    </strong>

                    <p>
                        No hay ninguna tarea asignada.
                    </p>
                </div>

            </div>
        `;

        modal.classList.add("visible");

        return;
    }


    /* ========================================================
       TRABAJADO
       ======================================================== */

    let html = "";


    const turno =
        Number(registros[0].turno) === 0
            ? "Mañana"
            : "Tarde";


    html += `
        <div class="detalle-turno-principal">

            <span class="detalle-turno-icono">
                <i class="fa-solid fa-clock"></i>
            </span>

            <div>
                <span>Turno</span>
                <strong>${turno}</strong>
            </div>

        </div>
    `;


    /* Tareas */

    html += `
        <div class="detalle-seccion">

            <h3>
                <i class="fa-solid fa-list-check"></i>
                Tareas asignadas
            </h3>
    `;


    registros.forEach(
        registro => {

            html += `
                <div class="detalle-tarea">

                    <div class="detalle-tarea-nombre">
                        ${registro.tarea || "Sin tarea"}
                    </div>

                </div>
            `;
        }
    );


    html += `
        </div>
    `;


    modalDetalles.innerHTML =
        html;


    modal.classList.add(
        "visible"
    );
}


/* ============================================================
   FORMATEAR FECHA
   ============================================================ */

function formatearFecha(fecha) {

    if (!fecha) {
        return "";
    }

    const fechaObjeto =
        new Date(
            `${fecha}T00:00:00`
        );

    return fechaObjeto.toLocaleDateString(
        "es-ES"
    );
}


/* ============================================================
   CERRAR MODAL
   ============================================================ */

function cerrarModal() {

    document
        .getElementById("modalDia")
        .classList.remove("visible");
}


document
    .getElementById("cerrarModal")
    .addEventListener(
        "click",
        cerrarModal
    );


document
    .getElementById("modalDia")
    .addEventListener(
        "click",
        function(event) {

            if (event.target === this) {
                cerrarModal();
            }

        }
    );


/* ============================================================
   CAMBIAR MES
   ============================================================ */

document
    .getElementById("mesAnterior")
    .addEventListener(
        "click",
        () => {

            fechaActual.setMonth(
                fechaActual.getMonth() - 1
            );

            pintarCalendario();
        }
    );


document
    .getElementById("mesSiguiente")
    .addEventListener(
        "click",
        () => {

            fechaActual.setMonth(
                fechaActual.getMonth() + 1
            );

            pintarCalendario();
        }
    );


/* ============================================================
   INICIO
   ============================================================ */

cargarCalendario();
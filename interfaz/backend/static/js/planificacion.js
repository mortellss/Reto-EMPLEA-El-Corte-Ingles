const dias = [
    { corto: "LUNES", numero: "22" },
    { corto: "MARTES", numero: "23" },
    { corto: "MIÉRCOLES", numero: "24" },
    { corto: "JUEVES", numero: "25" },
    { corto: "VIERNES", numero: "26" },
    { corto: "SÁBADO", numero: "27" }
];


const trabajadores = [

    {
        nombre: "Héctor",
        fijoDiscontinuo: false,
        turno: "mañana",
        tarea: "RUNNER",
        horarios: [
            "9:45 - 16:00",
            "9:45 - 16:00",
            "",
            "9:45 - 16:00",
            "9:45 - 16:00",
            "9:45 - 16:00"
        ]
    },

    {
        nombre: "Samuel",
        fijoDiscontinuo: false,
        turno: "mañana",
        tarea: "RUNNER",
        horarios: [
            "9:45 - 16:00",
            "C 21:00 - 06:00",
            "",
            "9:45 - 16:00",
            "9:45 - 16:00",
            "9:45 - 16:00"
        ]
    },

    {
        nombre: "Alejandro",
        fijoDiscontinuo: false,
        turno: "mañana",
        tarea: "DEV A TIENDA",
        horarios: [
            "",
            "",
            "",
            "9:45 - 16:00",
            "9:45 - 16:00",
            ""
        ]
    },

    {
        nombre: "Ángela",
        fijoDiscontinuo: false,
        turno: "mañana",
        tarea: "CONSOLA / DEV EDIG",
        horarios: [
            "9:00 - 15:00",
            "9:00 - 15:00",
            "",
            "9:00 - 15:00",
            "9:00 - 15:00",
            "9:00 - 15:00"
        ]
    },

    {
        nombre: "Rubén",
        fijoDiscontinuo: false,
        turno: "mañana",
        tarea: "ECI EXPRESS / C&CAR",
        horarios: [
            "9:00 - 16:00",
            "9:00 - 16:00",
            "",
            "9:00 - 16:00",
            "9:00 - 16:00",
            "10:00 - 19:00"
        ]
    },

    {
        nombre: "Nirvana",
        fijoDiscontinuo: false,
        turno: "mañana",
        tarea: "HOME DELIVERY",
        horarios: [
            "9:45 - 16:00",
            "9:45 - 16:00",
            "",
            "9:45 - 16:00",
            "9:45 - 16:00",
            "11:00 - 20:00"
        ]
    },

    {
        nombre: "Carmen",
        fijoDiscontinuo: true,
        turno: "mañana",
        tarea: "MOSTRADOR",
        horarios: [
            "9:00 - 16:00",
            "21:00 - 06:00",
            "",
            "9:45 - 16:00",
            "9:45 - 16:00",
            "9:45 - 16:00"
        ]
    },


    // =========================
    // TARDES
    // =========================

    {
        nombre: "Tonet",
        fijoDiscontinuo: false,
        turno: "tarde",
        tarea: "RUNNER",
        horarios: [
            "16:00 - 22:15",
            "",
            "",
            "",
            "",
            ""
        ]
    },

    {
        nombre: "Roberto",
        fijoDiscontinuo: false,
        turno: "tarde",
        tarea: "CONSOLA / DEV EDIG",
        horarios: [
            "DOMINGO - LUNES",
            "",
            "",
            "",
            "",
            ""
        ]
    },

    {
        nombre: "Ron",
        fijoDiscontinuo: false,
        turno: "tarde",
        tarea: "DEV EDIG / C&CAR",
        horarios: [
            "16:00 - 22:15",
            "",
            "",
            "11:00 - 20:00",
            "",
            "9:45 - 16:00"
        ]
    },

    {
        nombre: "Diego",
        fijoDiscontinuo: false,
        turno: "tarde",
        tarea: "C&CAR",
        horarios: [
            "16:00 - 22:15",
            "",
            "",
            "",
            "",
            ""
        ]
    },

    {
        nombre: "Natalia",
        fijoDiscontinuo: true,
        turno: "tarde",
        tarea: "GESTIÓN DE MOSTRADOR",
        horarios: [
            "",
            "",
            "",
            "",
            "",
            "16:00 - 22:15"
        ]
    },

    {
        nombre: "Adrián",
        fijoDiscontinuo: false,
        turno: "tarde",
        tarea: "MOSTRADOR",
        horarios: [
            "16:00 - 22:15",
            "",
            "",
            "",
            "",
            ""
        ]
    }

];


// =====================================================
// CABECERA
// =====================================================

function crearCabecera() {
    const fila = document.createElement("tr");

    const tarea = document.createElement("th");
    tarea.textContent = "TAREA";
    tarea.classList.add("tarea-header");
    fila.appendChild(tarea);

    dias.forEach(dia => {
        const th = document.createElement("th");

        th.innerHTML = `
            <span class="dia-nombre">${dia.corto}</span>
            <span class="dia-numero">${dia.numero}</span>
        `;

        fila.appendChild(th);
    });

    return fila;
}


// =====================================================
// AGRUPAR TRABAJADORES POR TAREA
// =====================================================

function agruparPorTarea(trabajadoresTurno) {

    const tareas = {};

    trabajadoresTurno.forEach(trabajador => {

        if (!tareas[trabajador.tarea]) {
            tareas[trabajador.tarea] = [];
        }

        tareas[trabajador.tarea].push(trabajador);

    });

    return tareas;
}


// =====================================================
// CREAR CELDA DE UN DÍA
// =====================================================

function crearCeldaDia(trabajadores, diaIndex) {

    const celda = document.createElement("td");

    celda.classList.add("planificacion-cell");


    trabajadores.forEach(trabajador => {

        const horario = trabajador.horarios[diaIndex];


        // Si ese trabajador no trabaja ese día
        if (!horario) {
            return;
        }


        const trabajadorDiv = document.createElement("div");

        trabajadorDiv.classList.add("asignacion");


        // Fijo discontinuo
        if (trabajador.fijoDiscontinuo) {
            trabajadorDiv.classList.add("fijo-discontinuo");
        }


        trabajadorDiv.innerHTML = `
            <div class="asignacion-nombre">
                ${trabajador.nombre}
            </div>

            <div class="asignacion-horario">
                ${horario}
            </div>
        `;


        celda.appendChild(trabajadorDiv);

    });


    // Si no hay nadie asignado
    if (celda.children.length === 0) {

        celda.innerHTML = `
            <span class="sin-asignacion">—</span>
        `;

    }


    return celda;
}


// =====================================================
// CREAR FILA DE TAREA
// =====================================================

function crearFilasTareas(trabajadoresTurno, tabla) {
    const tareas = [
        ...new Set(
            trabajadoresTurno.map(trabajador => trabajador.tarea)
        )
    ];

    tareas.forEach(tarea => {
        const trabajadoresTarea = trabajadoresTurno.filter(
            trabajador => trabajador.tarea === tarea
        );

        trabajadoresTarea.forEach((trabajador, index) => {
            const fila = crearFilaTrabajador(
                trabajador,
                index === 0,
                trabajadoresTarea.length
            );

            tabla.appendChild(fila);
        });
    });
}


// =====================================================
// CARGAR TABLA
// =====================================================

function cargarTabla(turno, cabeceraId, tablaId) {
    const cabecera = document.getElementById(cabeceraId);
    const tabla = document.getElementById(tablaId);

    cabecera.innerHTML = "";
    tabla.innerHTML = "";

    cabecera.appendChild(crearCabecera());

    const trabajadoresTurno = trabajadores.filter(
        trabajador => trabajador.turno === turno
    );

    crearFilasTareas(trabajadoresTurno, tabla);
}

// =====================================================
// INICIAR PLANIFICACIÓN
// =====================================================

function cargarPlanificacion() {

    cargarTabla(
        "mañana",
        "cabeceraMananas",
        "tablaMananas"
    );


    cargarTabla(
        "tarde",
        "cabeceraTardes",
        "tablaTardes"
    );

}


document.addEventListener(
    "DOMContentLoaded",
    cargarPlanificacion
);

function crearFilaTrabajador(trabajador, incluirTarea, rowspan) {
    const fila = document.createElement("tr");

    if (incluirTarea) {
        const celdaTarea = document.createElement("td");

        celdaTarea.classList.add("tarea-cell");
        celdaTarea.textContent = trabajador.tarea;
        celdaTarea.rowSpan = rowspan;

        fila.appendChild(celdaTarea);
    }

    trabajador.horarios.forEach(horario => {
        const celda = document.createElement("td");
        celda.classList.add("planificacion-cell");

        if (horario) {
            const asignacion = document.createElement("div");
            asignacion.classList.add("asignacion");

            if (trabajador.fijoDiscontinuo) {
                asignacion.classList.add("fijo-discontinuo");
            }

            asignacion.innerHTML = `
                <div class="asignacion-nombre">
                    ${trabajador.nombre}
                </div>
                <div class="asignacion-horario">
                    ${horario}
                </div>
            `;

            celda.appendChild(asignacion);
        } else {
            celda.innerHTML = `
                <span class="sin-asignacion">—</span>
            `;
        }

        fila.appendChild(celda);
    });

    return fila;
}
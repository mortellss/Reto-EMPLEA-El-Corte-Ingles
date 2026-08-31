document.addEventListener("DOMContentLoaded", () => {

    const lista = document.getElementById("listaTrabajadores");
    const buscador = document.getElementById("buscarTrabajador");

    let trabajadores = [];

    async function cargarTrabajadores() {

        try {

            const respuesta = await fetch("/api/calendarios-trabajadores");

            if (!respuesta.ok) {
                throw new Error("No se han podido cargar los trabajadores.");
            }

            trabajadores = await respuesta.json();

            mostrarTrabajadores(trabajadores);

        } catch (error) {

            console.error(error);

            lista.innerHTML = `
                <div class="mensaje-error">
                    No se han podido cargar los trabajadores.
                </div>
            `;
        }
    }

    function mostrarTrabajadores(datos) {

        lista.innerHTML = "";

        if (datos.length === 0) {

            lista.innerHTML = `
                <div class="mensaje-vacio">
                    No se han encontrado trabajadores.
                </div>
            `;

            return;
        }

        datos.forEach(trabajador => {

            const elemento = document.createElement("a");

            elemento.className = "trabajador-card";

            elemento.href =
                `/calendario-trabajador/${trabajador.id_trabajador}`;

            elemento.innerHTML = `
                <div class="trabajador-icono">
                    <i class="fa-solid fa-user"></i>
                </div>

                <div class="trabajador-info">

                    <h3>
                        ${trabajador.nombre}
                        ${trabajador.apellidos}

                        ${
                            trabajador.fijo_discontinuo
                                ? `<span class="distintivo-fijo-discontinuo">
                                    Fijo discontinuo
                                </span>`
                                : ""
                        }
                    </h3>

                    <p>
                        Vendedor ${trabajador.numero_vendedor ?? ""}
                    </p>

                </div>

                <i class="fa-solid fa-chevron-right trabajador-flecha"></i>
            `;

            lista.appendChild(elemento);
        });
    }

    buscador.addEventListener("input", () => {

        const texto =
            buscador.value
                .toLowerCase()
                .trim();

        const filtrados =
            trabajadores.filter(trabajador => {

                const nombre =
                    `${trabajador.nombre} ${trabajador.apellidos}`
                        .toLowerCase();

                const vendedor =
                    String(trabajador.numero_vendedor ?? "")
                        .toLowerCase();

                return nombre.includes(texto)
                    || vendedor.includes(texto);
            });

        mostrarTrabajadores(filtrados);
    });

    cargarTrabajadores();
});
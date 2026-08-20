const modal = document.getElementById("modalOverlay");

document.querySelectorAll(".day").forEach(dia => {

    dia.addEventListener("click", () => {

        modal.classList.add("show");

        document.getElementById("fechaSeleccionada").textContent = dia.dataset.fecha;
        document.getElementById("horaApertura").value = dia.dataset.apertura;
        document.getElementById("horaCierre").value = dia.dataset.cierre;

        document.getElementById("abierto").checked =
            dia.dataset.abierto == "1";

    });

});

document.getElementById("cerrarModal").addEventListener("click", () => {
    modal.classList.remove("show");
});

document.getElementById("cancelar").addEventListener("click", () => {
    modal.classList.remove("show");
});

document.getElementById("guardarDia").addEventListener("click", async () => {

    const datos = {
        fecha: document.getElementById("fechaSeleccionada").textContent,
        hora_apertura: document.getElementById("horaApertura").value,
        hora_cierre: document.getElementById("horaCierre").value,
        abierto: document.getElementById("abierto").checked ? 1 : 0
    };

    const respuesta = await fetch("/actualizar_dia", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(datos)
    });

    if (respuesta.ok) {
        location.reload();
    } else {
        alert("Error al guardar los cambios");
    }
});
(() => {
    const temaGuardado = localStorage.getItem("tema") || "claro";
    document.documentElement.classList.toggle("dark-mode", temaGuardado === "oscuro");

    const actualizarBoton = (boton, oscuro) => {
        const nombre = oscuro ? "Activar modo claro" : "Activar modo oscuro";
        boton.setAttribute("aria-label", nombre);
        boton.setAttribute("title", nombre);
        boton.innerHTML = oscuro
            ? '<i class="fa-solid fa-sun" aria-hidden="true"></i>'
            : '<i class="fa-solid fa-moon" aria-hidden="true"></i>';
    };

    document.addEventListener("DOMContentLoaded", () => {
        document.querySelectorAll(".tema-boton").forEach(boton => {
            actualizarBoton(boton, document.documentElement.classList.contains("dark-mode"));
            boton.addEventListener("click", () => {
                const oscuro = !document.documentElement.classList.contains("dark-mode");
                document.documentElement.classList.toggle("dark-mode", oscuro);
                localStorage.setItem("tema", oscuro ? "oscuro" : "claro");
                actualizarBoton(boton, oscuro);
                document.dispatchEvent(new CustomEvent("tema-cambiado"));
            });
        });
    });
})();

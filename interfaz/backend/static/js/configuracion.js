document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("configForm");
    const resetButton = document.getElementById("resetConfig");

    const defaults = {
        yearly_seasonality: 20,
        weekly_seasonality: 3,
        daily_seasonality: "false",
        seasonality_mode: "multiplicative",
        interval_width: 0.8,
        n_changepoints: 50,
        tasa_crecimiento: 0
    };

    const fillForm = (config) => {
        Object.entries(config).forEach(([name, value]) => {
            const field = form?.querySelector(`[name="${name}"]`);
            if (!field) return;

            if (field.tagName === "SELECT") {
                field.value = String(value).toLowerCase();
                return;
            }

            field.value = value;
        });
    };

    const loadConfig = async () => {
        const response = await fetch("/api/configuracion");
        if (!response.ok) {
            console.error("No se han podido cargar los parámetros");
            return;
        }

        const config = await response.json();
        fillForm(config);
    };

    const setDefaultValues = () => {
        Object.entries(defaults).forEach(([name, value]) => {
            const field = form?.querySelector(`[name="${name}"]`);
            if (!field) return;
            field.value = value;
        });
    };

    form?.addEventListener("submit", async (event) => {
        event.preventDefault();

        const formData = new FormData(form);
        const payload = Object.fromEntries(formData.entries());

        payload.daily_seasonality = payload.daily_seasonality === "true";
        payload.interval_width = Number(payload.interval_width);
        payload.yearly_seasonality = Number(payload.yearly_seasonality);
        payload.weekly_seasonality = Number(payload.weekly_seasonality);
        payload.n_changepoints = Number(payload.n_changepoints);
        payload.tasa_crecimiento = Number(payload.tasa_crecimiento);

        const response = await fetch("/api/configuracion", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(payload)
        });

        const data = await response.json();

        if (!response.ok) {
            alert(data.error || "No se han podido guardar los parámetros.");
            return;
        }

        fillForm(data.configuracion);
        alert("Parámetros del modelo actualizados correctamente.");
    });

    resetButton?.addEventListener("click", () => {
        setDefaultValues();
    });

    loadConfig();
});

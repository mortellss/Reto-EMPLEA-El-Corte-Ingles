document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("configForm");
    const resetButton = document.getElementById("resetConfig");

    if (form) {
        form.noValidate = true;
    }

    const defaults = {
        yearly_seasonality: 20,
        weekly_seasonality: 3,
        daily_seasonality: "false",
        seasonality_mode: "multiplicative",
        interval_width: 0.8,
        n_changepoints: 50,
        tasa_crecimiento: 0,
        horas_presencia_mostrador: 11,
        horas_otras_gestiones: 1,
        porcentaje_devoluciones: 0.05,
        horas_gestion_devoluciones: 3,
        recoleccion_1_lineas: 1000,
        recoleccion_1_tiempo_min: 1.8,
        recoleccion_2_lineas: 1000,
        recoleccion_2_tiempo_min: 0.315,
        empaquetado_lineas: 1000,
        empaquetado_tiempo_min: 5.04,
        almacenado_lineas: 1000,
        almacenado_tiempo_min: 4.35,
        entrega_lineas: 1000,
        entrega_tiempo_min: 2.98
    };

    const currentConfigList = document.getElementById("currentConfigList");

    const updateCurrentConfigSummary = (config) => {
        if (!currentConfigList) return;

        const values = {
            yearly_seasonality: config.yearly_seasonality,
            weekly_seasonality: config.weekly_seasonality,
            daily_seasonality: config.daily_seasonality ? "Verdadero" : "Falso",
            seasonality_mode: config.seasonality_mode === "additive" ? "Aditivo" : "Multiplicativo",
            interval_width: config.interval_width,
            n_changepoints: config.n_changepoints,
            tasa_crecimiento: config.tasa_crecimiento
        };

        const labels = {
            yearly_seasonality: "Estacionalidad anual",
            weekly_seasonality: "Estacionalidad semanal",
            daily_seasonality: "Estacionalidad diaria",
            seasonality_mode: "Modo",
            interval_width: "Intervalo",
            n_changepoints: "Puntos de inflexión",
            tasa_crecimiento: "Tasa de crecimiento"
        };

        currentConfigList.innerHTML = Object.entries(values)
            .map(([key, value]) => `
                <div class="current-config-item">
                    <span>${labels[key]}</span>
                    <strong>${value}</strong>
                </div>
            `)
            .join("");
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

        updateCurrentConfigSummary(config);
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

        const numericFields = [
            "interval_width",
            "tasa_crecimiento",
            "horas_presencia_mostrador",
            "horas_otras_gestiones",
            "porcentaje_devoluciones",
            "horas_gestion_devoluciones",
            "recoleccion_1_lineas",
            "recoleccion_1_tiempo_min",
            "recoleccion_2_lineas",
            "recoleccion_2_tiempo_min",
            "empaquetado_lineas",
            "empaquetado_tiempo_min",
            "almacenado_lineas",
            "almacenado_tiempo_min",
            "entrega_lineas",
            "entrega_tiempo_min",
            "yearly_seasonality",
            "weekly_seasonality",
            "n_changepoints"
        ];

        const invalid = numericFields.some((name) => {
            const value = payload[name];
            return value === "" || value === null || value === undefined || !Number.isFinite(Number(value));
        });

        if (invalid) {
            alert("Por favor, introduce valores numéricos válidos en todos los campos.");
            return;
        }

        payload.daily_seasonality = payload.daily_seasonality === "true";
        payload.interval_width = Number(payload.interval_width);
        payload.yearly_seasonality = Number(payload.yearly_seasonality);
        payload.weekly_seasonality = Number(payload.weekly_seasonality);
        payload.n_changepoints = Number(payload.n_changepoints);
        payload.tasa_crecimiento = Number(payload.tasa_crecimiento);
        payload.horas_presencia_mostrador = Number(payload.horas_presencia_mostrador);
        payload.horas_otras_gestiones = Number(payload.horas_otras_gestiones);
        payload.porcentaje_devoluciones = Number(payload.porcentaje_devoluciones);
        payload.horas_gestion_devoluciones = Number(payload.horas_gestion_devoluciones);
        payload.recoleccion_1_lineas = Number(payload.recoleccion_1_lineas);
        payload.recoleccion_1_tiempo_min = Number(payload.recoleccion_1_tiempo_min);
        payload.recoleccion_2_lineas = Number(payload.recoleccion_2_lineas);
        payload.recoleccion_2_tiempo_min = Number(payload.recoleccion_2_tiempo_min);
        payload.empaquetado_lineas = Number(payload.empaquetado_lineas);
        payload.empaquetado_tiempo_min = Number(payload.empaquetado_tiempo_min);
        payload.almacenado_lineas = Number(payload.almacenado_lineas);
        payload.almacenado_tiempo_min = Number(payload.almacenado_tiempo_min);
        payload.entrega_lineas = Number(payload.entrega_lineas);
        payload.entrega_tiempo_min = Number(payload.entrega_tiempo_min);

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

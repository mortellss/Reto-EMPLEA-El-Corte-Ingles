document.addEventListener("DOMContentLoaded", () => {
    const toggles = document.querySelectorAll(".toggle input");
    const statusBadge = document.querySelector(".status-badge");

    toggles.forEach((toggle) => {
        toggle.addEventListener("change", () => {
            const settingLabel = toggle.closest(".setting-item")?.querySelector("strong")?.textContent || "Configuración";
            if (statusBadge) {
                statusBadge.textContent = `${settingLabel} actualizado`;
            }
        });
    });
});

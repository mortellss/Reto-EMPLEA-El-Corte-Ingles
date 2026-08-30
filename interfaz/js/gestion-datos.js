
const skills = [
    "Runner + Dev a tienda",
    "ECI Express + Click&Car",
    "Home Delivery",
    "Derivadas",
    "Encargos Muro",
    "Expedicion",
    "Mostrador",
    "Consola + Devoluciones EDIG",
    "Casos Sales Force",
    "Informar",
    "Gestión Mostrador",
    "Site To Store"
];

const skillsContainer = document.getElementById("skills-list");

skills.forEach((skill, index) => {

    skillsContainer.innerHTML += `

        <div class="skill-item">

            <span>${skill}</span>

            <label class="switch">

                <input
                    type="checkbox"
                    id="skill-${index}">

                <span class="slider"></span>

            </label>

        </div>

    `;

});

const modal = document.getElementById("modal");

const openModal = document.getElementById("openModal");
const closeModal = document.getElementById("closeModal");
const cancelModal = document.getElementById("cancelModal");


openModal.addEventListener("click", () => {
    modal.classList.add("show");
});

closeModal.addEventListener("click", () => {
    modal.classList.remove("show");
});

cancelModal.addEventListener("click", () => {
    modal.classList.remove("show");
});

modal.addEventListener("click", (e) => {
    if (e.target === modal) {
        modal.classList.remove("show");
    }
});

modal.classList.add("show");
modal.classList.remove("show");

const tabs = document.querySelectorAll(".tab");
const panels = document.querySelectorAll(".tab-panel");

tabs.forEach(tab => {

    tab.addEventListener("click", () => {

        tabs.forEach(t => t.classList.remove("active"));
        panels.forEach(panel => panel.classList.remove("active-panel"));

        tab.classList.add("active");

        const panel = document.getElementById(`${tab.dataset.tab}-panel`);
        panel.classList.add("active-panel");

    });

});
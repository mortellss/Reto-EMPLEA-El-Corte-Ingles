/* ============================================================
                        VARIABLES GLOBALES
============================================================ */

const modal = document.getElementById("modal");

const openModal = document.getElementById("openModal");
const closeModal = document.getElementById("closeModal");
const cancelModal = document.getElementById("cancelModal");

let disponibilidadEditando = null;

let contratoEditando = null;

let trabajadorEditando = null;

const modalContrato =
document.getElementById("modalContrato");

const modalCompetencias =
document.getElementById("modalCompetencias");

const modalTarea = document.getElementById("modalTarea");
const openModalTarea = document.getElementById("openModalTarea");
const closeModalTarea = document.getElementById("closeModalTarea");
const cancelModalTarea = document.getElementById("cancelModalTarea");
let tareaEditando = null;

/* ============================================================
                            PESTAÑAS
============================================================ */

const tabs=document.querySelectorAll(".tab");
const panels=document.querySelectorAll(".tab-panel");

function activarPestana(nombre){

    tabs.forEach(tab=>{
        tab.classList.remove("active");
    });

    panels.forEach(panel=>{
        panel.classList.remove("active-panel");
    });

    const tab=document.querySelector(`.tab[data-tab="${nombre}"]`);
    const panel=document.getElementById(`${nombre}-panel`);

    if(tab){
        tab.classList.add("active");
    }

    if(panel){
        panel.classList.add("active-panel");
    }

}

const tabGuardada=localStorage.getItem("tabActiva") || "trabajadores";

activarPestana(tabGuardada);

tabs.forEach(tab=>{

    tab.addEventListener("click",()=>{

        const nombre=tab.dataset.tab;

        localStorage.setItem("tabActiva",nombre);

        activarPestana(nombre);

    });

});

/* ============================================================
                          TRABAJADORES
============================================================ */

// Abrir modal
openModal.addEventListener("click", () => {

    trabajadorEditando = null;

    document.getElementById("tituloModalTrabajador").textContent =
        "Nuevo trabajador";

    document.getElementById("guardarTrabajador").textContent =
        "Guardar trabajador";

    document.getElementById("fijoDiscontinuoTrabajador").checked=false;
    document.getElementById("nombre").value = "";
    document.getElementById("apellidos").value = "";
    document.getElementById("numeroVendedor").value = "";
    document.getElementById("correo").value = "";

    document.getElementById("contrato").selectedIndex = 0;
    document.getElementById("disponibilidad").value = "S";
    document.getElementById("estado").value = "1";

    document.querySelectorAll(".tarea-check").forEach(check=>{
        check.checked = false;
    });

    modal.classList.add("show");

});

// Cerrar con la X
closeModal.addEventListener("click", () => {
    modal.classList.remove("show");
});

// Cerrar con Cancelar
cancelModal.addEventListener("click", () => {
    modal.classList.remove("show");
});

// Cerrar pulsando fuera
modal.addEventListener("click", (e) => {
    if (e.target === modal) {
        modal.classList.remove("show");
    }
});

// ------------------------------------------------------------
// Competencias del trabajador
// ------------------------------------------------------------

const listaCompetencias =
document.getElementById("listaCompetencias");


document
.querySelectorAll(".competencias-btn")
.forEach(btn=>{

    btn.addEventListener("click",async()=>{

        const respuesta =
        await fetch(`/competencias_trabajador/${btn.dataset.id}`);

        const datos =
        await respuesta.json();

        listaCompetencias.innerHTML="";

        datos.forEach(c=>{

            listaCompetencias.innerHTML += `

                <div class="competencia-item">

                    <i class="fa-solid fa-circle-check"></i>

                    <span>${c.nombre}</span>

                </div>

            `;

        });

        modalCompetencias.classList.add("show");

    });

});


document
.getElementById("closeCompetencias")
.addEventListener("click",()=>{

    modalCompetencias.classList.remove("show");

});


modalCompetencias.addEventListener("click",e=>{

    if(e.target===modalCompetencias){

        modalCompetencias.classList.remove("show");

    }

});

// Editar trabajador
document.querySelectorAll(".edit-btn").forEach(btn => {

    btn.addEventListener("click", async () => {

        trabajadorEditando = btn.dataset.id;

        document.getElementById("tituloModalTrabajador").textContent =
            "Editar trabajador";

        document.getElementById("guardarTrabajador").textContent =
            "Guardar cambios";

        document.getElementById("nombre").value =
            btn.dataset.nombre;

        document.getElementById("apellidos").value =
            btn.dataset.apellidos;

        document.getElementById("numeroVendedor").value =
            btn.dataset.numero;

        document.getElementById("correo").value =
            btn.dataset.correo;

        document.getElementById("contrato").value =
            btn.dataset.contrato;

        document.getElementById("disponibilidad").value =
            btn.dataset.disponibilidad;

        document.getElementById("estado").value =
            btn.dataset.estado;

        document.getElementById("fijoDiscontinuoTrabajador").checked=btn.dataset.fijoDiscontinuo==="1";

        // Desmarcar todas las competencias
        document.querySelectorAll(".tarea-check").forEach(check=>{
            check.checked = false;
        });

        // Cargar competencias del trabajador
        const respuesta =
            await fetch(`/competencias_trabajador/${trabajadorEditando}`);

        const competencias =
            await respuesta.json();

        competencias.forEach(c=>{

            const check =
                document.querySelector(
                    `.tarea-check[value="${c.id_tarea}"]`
                );

            if(check){
                check.checked = true;
            }

        });

        modal.classList.add("show");

    });

});


// Eliminar trabajador
document.querySelectorAll(".delete-trabajador-btn").forEach(btn => {
    btn.addEventListener("click", async () => {

        if(!confirm("¿Eliminar trabajador?")) return;

        try {
            const respuesta = await fetch("/eliminar_trabajador",{

                method:"POST",

                headers:{
                    "Content-Type":"application/json"
                },

                body:JSON.stringify({
                    id:btn.dataset.id
                })

            });

            const resultado = await respuesta.json();
            if(resultado.ok){
                location.reload();
            }else{
                alert(resultado.error || "No se ha podido eliminar el trabajador.");
            }
        } catch (error) {
            alert("No se ha podido eliminar el trabajador. Comprueba la conexión con el servidor.");
        }

    });

});

// Guardar trabajador
document.getElementById("guardarTrabajador").addEventListener("click", async () => {

    const tareas = [];

    document.querySelectorAll(".tarea-check:checked").forEach(check => {
        tareas.push(parseInt(check.value));
    });

    const datos={
        numero_vendedor:document.getElementById("numeroVendedor").value,
        nombre:document.getElementById("nombre").value,
        apellidos:document.getElementById("apellidos").value,
        correo:document.getElementById("correo").value,
        id_contrato:document.getElementById("contrato").value,
        disponibilidad:document.getElementById("disponibilidad").value,
        estado:document.getElementById("estado").value,
        fijo_discontinuo:document.getElementById("fijoDiscontinuoTrabajador").checked?1:0,
        tareas:tareas
    };

    const url = trabajadorEditando
    ? "/editar_trabajador"
    : "/nuevo_trabajador";

    if(trabajadorEditando){

        datos.id = trabajadorEditando;

    }

    const respuesta = await fetch(url, {

        method: "POST",

        headers: {
            "Content-Type": "application/json"
        },

        body: JSON.stringify(datos)

    });

    if (respuesta.ok) {

        location.reload();

    } else {

        alert("Error al guardar el trabajador.");

    }

});



// Cambiar estado
document.querySelectorAll(".status-btn").forEach(btn=>{

    btn.addEventListener("click", async()=>{

        const respuesta = await fetch("/cambiar_estado_trabajador",{

            method:"POST",

            headers:{
                "Content-Type":"application/json"
            },

            body:JSON.stringify({

                id:btn.dataset.id

            })

        });

        if(respuesta.ok){

            location.reload();

        }else{

            alert("No se ha podido cambiar el estado.");

        }

    });

});

/* ============================================================
BUSCADOR TRABAJADORES
============================================================ */

const buscarTrabajador = document.getElementById("buscarTrabajador");

buscarTrabajador.addEventListener("input", () => {

    const texto = buscarTrabajador.value.toLowerCase();

    document.querySelectorAll("#trabajadores-panel tbody tr").forEach(fila => {

        fila.style.display =
            fila.textContent.toLowerCase().includes(texto)
                ? ""
                : "none";

    });

});


// PERIODOS FIJO DISCONTINUO
let trabajadorFDActual=null;
let periodoFDEditando=null;

async function cargarPeriodosFD(idTrabajador){
    const respuesta=await fetch(`/periodos_trabajador/${idTrabajador}`);
    if(!respuesta.ok) return;
    const periodos=await respuesta.json();
    const lista=document.getElementById("listaPeriodosFD");
    lista.innerHTML="";
    periodos.forEach((periodo,index)=>{
        const inicio=new Date(periodo.fecha_inicio).toLocaleDateString("es-ES");
        const fin=new Date(periodo.fecha_fin).toLocaleDateString("es-ES");
        lista.innerHTML+=`
            <div class="periodo-fd">
                <div>
                    <strong>Periodo ${index+1}</strong>
                    <span>${inicio} — ${fin}</span>
                </div>
                <div class="actions">
                    <button class="edit-periodo-fd" data-id="${periodo.id_periodo}" data-inicio="${periodo.fecha_inicio}" data-fin="${periodo.fecha_fin}">
                        <i class="fa-solid fa-pen"></i>
                    </button>
                    <button class="delete-periodo-fd" data-id="${periodo.id_periodo}">
                        <i class="fa-solid fa-trash"></i>
                    </button>
                </div>
            </div>
        `;
    });
    document.querySelectorAll(".edit-periodo-fd").forEach(btn=>{
        btn.addEventListener("click",()=>{
            periodoFDEditando=btn.dataset.id;
            document.getElementById("tituloPeriodoFD").textContent="Editar periodo";
            document.getElementById("fechaInicioFD").value=btn.dataset.inicio.substring(0,10);
            document.getElementById("fechaFinFD").value=btn.dataset.fin.substring(0,10);
            document.getElementById("modalEditarPeriodoFD").classList.add("show");
        });
    });
    document.querySelectorAll(".delete-periodo-fd").forEach(btn=>{
        btn.addEventListener("click",async()=>{
            if(!confirm("Este cambio es permanente. ¿Quieres eliminar este periodo?")) return;
            const idPeriodo=btn.dataset.id;
            console.log("ID PERIODO A ELIMINAR:",idPeriodo);
            const respuesta=await fetch("/eliminar_periodo_fd",{
                method:"POST",
                headers:{
                    "Content-Type":"application/json"
                },
                body:JSON.stringify({
                    id_periodo:idPeriodo
                })
            });
            const resultado=await respuesta.json();
            console.log("RESPUESTA ELIMINAR:",resultado);
            if(respuesta.ok){
                await cargarPeriodosFD(trabajadorFDActual);
            }else{
                alert("Error al eliminar el periodo.");
            }
        });
    });
}

document.querySelectorAll(".fd-btn").forEach(btn=>{
    btn.addEventListener("click",async()=>{
        trabajadorFDActual=btn.dataset.id;
        const trabajador=btn.closest("tr").querySelector("td:first-child").textContent.trim();
        document.getElementById("nombreTrabajadorFD").textContent=trabajador;
        await cargarPeriodosFD(trabajadorFDActual);
        document.getElementById("modalPeriodosFD").classList.add("show");
    });
});

document.getElementById("nuevoPeriodoFD").addEventListener("click",()=>{
    periodoFDEditando=null;
    document.getElementById("tituloPeriodoFD").textContent="Nuevo periodo";
    document.getElementById("fechaInicioFD").value="";
    document.getElementById("fechaFinFD").value="";
    document.getElementById("modalEditarPeriodoFD").classList.add("show");
});

document.getElementById("guardarPeriodoFD").addEventListener("click",async()=>{
    const datos={
        fecha_inicio:document.getElementById("fechaInicioFD").value,
        fecha_fin:document.getElementById("fechaFinFD").value
    };
    let url;
    if(periodoFDEditando){
        url="/editar_periodo_fd";
        datos.id_periodo=periodoFDEditando;
    }else{
        url="/nuevo_periodo_fd";
        datos.id_trabajador=trabajadorFDActual;
    }
    const respuesta=await fetch(url,{
        method:"POST",
        headers:{"Content-Type":"application/json"},
        body:JSON.stringify(datos)
    });
    if(respuesta.ok){
        document.getElementById("modalEditarPeriodoFD").classList.remove("show");
        await cargarPeriodosFD(trabajadorFDActual);
    }
});

document.getElementById("closeEditarPeriodoFD").addEventListener("click",()=>{
    document.getElementById("modalEditarPeriodoFD").classList.remove("show");
});

document.getElementById("cancelEditarPeriodoFD").addEventListener("click",()=>{
    document.getElementById("modalEditarPeriodoFD").classList.remove("show");
});

document.getElementById("closePeriodosFD").addEventListener("click",()=>{
    document.getElementById("modalPeriodosFD").classList.remove("show");
});

document.getElementById("modalPeriodosFD").addEventListener("click",e=>{
    if(e.target===document.getElementById("modalPeriodosFD")){
        document.getElementById("modalPeriodosFD").classList.remove("show");
    }
});



/* ============================================================
   DISPONIBILIDAD
============================================================ */

const modalDisponibilidad=document.getElementById("modalDisponibilidad");
const motivo=document.getElementById("motivoDisponibilidad");
const turno=document.getElementById("turnoDisponibilidad");
const fechaInicio=document.getElementById("fechaInicioDisponibilidad");
const fechaFin=document.getElementById("fechaFinDisponibilidad");
const otroContainer=document.getElementById("otroMotivoContainer");
const modalPeriodosDisponibilidad=document.getElementById("modalPeriodosDisponibilidad");
const listaPeriodosDisponibilidad=document.getElementById("listaPeriodosDisponibilidad");
let idTrabajadorPeriodos=null;

/* ABRIR NUEVA RESTRICCIÓN */
document.getElementById("openDisponibilidadModal").addEventListener("click",()=>{
    disponibilidadEditando=null;
    document.querySelector("#modalDisponibilidad h2").textContent="Nueva restricción";
    document.getElementById("guardarDisponibilidad").textContent="Guardar restricción";
    motivo.value="";
    document.getElementById("trabajadorDisponibilidad").value="";
    otroContainer.style.display="none";
    document.getElementById("otroMotivo").value="";
    actualizarFormulario();
    modalDisponibilidad.classList.add("show");
});

/* CERRAR MODAL */
document.getElementById("closeDisponibilidadModal").addEventListener("click",()=>{
    modalDisponibilidad.classList.remove("show");
});
document.getElementById("cancelDisponibilidadModal").addEventListener("click",()=>{
    modalDisponibilidad.classList.remove("show");
});
modalDisponibilidad.addEventListener("click",e=>{
    if(e.target===modalDisponibilidad){
        modalDisponibilidad.classList.remove("show");
    }
});

/* GUARDAR / EDITAR */
document.getElementById("guardarDisponibilidad").addEventListener("click",async()=>{
    const datos={
        id_trabajador:document.getElementById("trabajadorDisponibilidad").value,
        motivo:motivo.value==="Otro"?document.getElementById("otroMotivo").value:motivo.value,
        turno:turno.value,
        fecha_inicio:fechaInicio.value,
        fecha_fin:fechaFin.value
    };
    if(datos.fecha_inicio&&datos.fecha_fin&&datos.fecha_inicio>datos.fecha_fin){
        alert("La fecha de inicio no puede ser posterior a la fecha de fin.");
        return;
    }
    const url=disponibilidadEditando?"/editar_disponibilidad":"/nueva_disponibilidad";
    if(disponibilidadEditando){
        datos.id=disponibilidadEditando;
    }
    const respuesta=await fetch(url,{
        method:"POST",
        headers:{"Content-Type":"application/json"},
        body:JSON.stringify(datos)
    });
    if(respuesta.ok){
        disponibilidadEditando=null;
        location.reload();
    }else{
        alert("Error al guardar la restricción.");
    }
});

/* EDITAR DESDE TABLA */
document.querySelectorAll(".edit-disponibilidad-btn").forEach(btn=>{
    btn.addEventListener("click",e=>{
        e.stopPropagation();
        disponibilidadEditando=btn.dataset.id;
        document.getElementById("trabajadorDisponibilidad").value=btn.dataset.trabajador;
        motivo.value=btn.dataset.motivo;
        actualizarFormulario();
        turno.value=btn.dataset.turno||"";
        const t=turnos.find(x=>x.codigo==btn.dataset.turno);
        if(t){
            fechaInicio.value=new Date(t.fecha_inicio).toISOString().split("T")[0];
            fechaFin.value=new Date(t.fecha_fin).toISOString().split("T")[0];
            fechaInicio.readOnly=true;
            fechaFin.readOnly=true;
        }
        document.querySelector("#modalDisponibilidad h2").textContent="Editar restricción";
        document.getElementById("guardarDisponibilidad").textContent="Guardar cambios";
        modalDisponibilidad.classList.add("show");
    });
});

/* ELIMINAR DESDE TABLA */
document.querySelectorAll(".delete-disponibilidad-btn").forEach(btn=>{
    btn.addEventListener("click",async e=>{
        e.stopPropagation();
        if(!confirm("¿Eliminar esta restricción?"))return;
        const respuesta=await fetch("/eliminar_disponibilidad",{
            method:"POST",
            headers:{"Content-Type":"application/json"},
            body:JSON.stringify({id:btn.dataset.id})
        });
        if(respuesta.ok){
            location.reload();
        }else{
            alert("No se ha podido eliminar la restricción.");
        }
    });
});

/* MOTIVO */
motivo.addEventListener("change",actualizarFormulario);
motivo.addEventListener("change",()=>{
    if(motivo.value==="Otro"){
        otroContainer.style.display="block";
    }else{
        otroContainer.style.display="none";
        document.getElementById("otroMotivo").value="";
    }
});

/* CAMBIO DE TURNO */
turno.addEventListener("change",()=>{
    const t=turnos.find(x=>String(x.codigo)===String(turno.value));
    if(!t)return;
    fechaInicio.value=new Date(t.fecha_inicio).toISOString().split("T")[0];
    fechaFin.value=new Date(t.fecha_fin).toISOString().split("T")[0];
    fechaInicio.readOnly=true;
    fechaFin.readOnly=true;
});

/* ACTUALIZAR FORMULARIO */
function actualizarFormulario(){
    turno.innerHTML='<option value="">Seleccionar...</option>';
    fechaInicio.value="";
    fechaFin.value="";
    fechaInicio.readOnly=false;
    fechaFin.readOnly=false;
    if(motivo.value!=="Vacaciones largas"&&motivo.value!=="Vacaciones cortas"){
        turno.disabled=true;
        return;
    }
    turno.disabled=false;
    const tipo=motivo.value==="Vacaciones largas"?"Larga":"Corta";
    turnos.filter(t=>t.tipo===tipo).forEach(t=>{
        turno.innerHTML+=`<option value="${t.codigo}">${t.codigo}</option>`;
    });
}
actualizarFormulario();

/* ABRIR PERIODOS */
document.querySelectorAll(".fila-disponibilidad").forEach(fila=>{
    fila.addEventListener("click",()=>{
        abrirPeriodosDisponibilidad(fila.dataset.id);
    });
});

/* CARGAR PERIODOS */
async function abrirPeriodosDisponibilidad(id){
    idTrabajadorPeriodos=id;
    const respuesta=await fetch(`/periodos_disponibilidad/${id}`);
    if(!respuesta.ok){
        alert("No se han podido cargar los periodos.");
        return;
    }
    const datos=await respuesta.json();
    document.getElementById("nombreTrabajadorPeriodos").textContent=datos.trabajador;
    listaPeriodosDisponibilidad.innerHTML="";
    if(datos.periodos.length===0){
        listaPeriodosDisponibilidad.innerHTML=`<div class="sin-periodos">No hay periodos registrados.</div>`;
    }
    datos.periodos.forEach(periodo=>{
        const fechaInicioFormato=periodo.fecha_inicio?periodo.fecha_inicio.split("-").reverse().join("/"):"—";
        const fechaFinFormato=periodo.fecha_fin?periodo.fecha_fin.split("-").reverse().join("/"):"—";
        listaPeriodosDisponibilidad.innerHTML+=`
            <div class="periodo-disponibilidad">
                <div class="periodo-info">
                    <strong>${periodo.motivo}</strong>
                    <span>${fechaInicioFormato} — ${fechaFinFormato}</span>
                    ${periodo.turno?`<small>Turno: ${periodo.turno}</small>`:""}
                </div>
                <div class="actions">
                    <button class="edit-periodo-btn" data-id="${periodo.id_disponibilidad}" title="Editar">
                        <i class="fa-solid fa-pen"></i>
                    </button>
                    <button class="delete-periodo-btn" data-id="${periodo.id_disponibilidad}" title="Eliminar">
                        <i class="fa-solid fa-trash"></i>
                    </button>
                </div>
            </div>
        `;
    });
    modalPeriodosDisponibilidad.classList.add("show");

    /* EDITAR PERIODO */
   document.querySelectorAll(".edit-periodo-btn").forEach(btn=>{
    btn.addEventListener("click",()=>{
        const periodo=datos.periodos.find(p=>p.id_disponibilidad==btn.dataset.id);
        console.log("PERIODO:",periodo);
        if(!periodo)return;

        disponibilidadEditando=periodo.id_disponibilidad;

        const fechaInicioGuardada=periodo.fecha_inicio;
        const fechaFinGuardada=periodo.fecha_fin;
        const turnoGuardado=periodo.turno;

        document.getElementById("trabajadorDisponibilidad").value=id;

        motivo.value=periodo.motivo;

        actualizarFormulario();

        turno.value=turnoGuardado||"";

        fechaInicio.value=fechaInicioGuardada||"";
        fechaFin.value=fechaFinGuardada||"";

        if(turnoGuardado){
            fechaInicio.readOnly=true;
            fechaFin.readOnly=true;
        }else{
            fechaInicio.readOnly=false;
            fechaFin.readOnly=false;
        }

        document.querySelector("#modalDisponibilidad h2").textContent="Editar restricción";
        document.getElementById("guardarDisponibilidad").textContent="Guardar cambios";

        modalPeriodosDisponibilidad.classList.remove("show");
        modalDisponibilidad.classList.add("show");
    });
});
    /* ELIMINAR PERIODO */
    document.querySelectorAll(".delete-periodo-btn").forEach(btn=>{
        btn.addEventListener("click",async()=>{
            if(!confirm("¿Eliminar este periodo?\n\nEste cambio no se puede deshacer."))return;
            const respuesta=await fetch("/eliminar_disponibilidad",{
                method:"POST",
                headers:{"Content-Type":"application/json"},
                body:JSON.stringify({id:btn.dataset.id})
            });
            if(respuesta.ok){
                abrirPeriodosDisponibilidad(id);
            }else{
                alert("No se ha podido eliminar el periodo.");
            }
        });
    });
}

/* CERRAR MODAL PERIODOS */
document.getElementById("closePeriodosDisponibilidad").addEventListener("click",()=>{
    modalPeriodosDisponibilidad.classList.remove("show");
});
modalPeriodosDisponibilidad.addEventListener("click",e=>{
    if(e.target===modalPeriodosDisponibilidad){
        modalPeriodosDisponibilidad.classList.remove("show");
    }
});

/* AÑADIR PERIODO */
document.getElementById("nuevoPeriodoDisponibilidad").addEventListener("click",()=>{
    disponibilidadEditando=null;
    document.querySelector("#modalDisponibilidad h2").textContent="Nueva restricción";
    document.getElementById("guardarDisponibilidad").textContent="Guardar restricción";
    document.getElementById("trabajadorDisponibilidad").value=idTrabajadorPeriodos;
    motivo.value="";
    otroContainer.style.display="none";
    document.getElementById("otroMotivo").value="";
    actualizarFormulario();
    modalPeriodosDisponibilidad.classList.remove("show");
    modalDisponibilidad.classList.add("show");
});

/* Buscar disponibilidad*/

const buscarDisponibilidad=document.getElementById("buscarDisponibilidad");

if(buscarDisponibilidad){
    buscarDisponibilidad.addEventListener("input",()=>{
        const texto=buscarDisponibilidad.value.toLowerCase().trim();

        document.querySelectorAll(".fila-disponibilidad").forEach(fila=>{
            const nombre=fila.querySelector(".nombre-trabajador");

            if(!nombre)return;

            const coincide=nombre.textContent.toLowerCase().includes(texto);

            fila.style.display=coincide?"":"none";
        });
    });
}
/* ============================================================
                          CONTRATOS
============================================================ */
const modalTrabajadoresContrato =
document.getElementById("modalTrabajadoresContrato");

const lista =
document.getElementById("listaTrabajadoresContrato");


// Modal trabajadores del contrato
document
.querySelectorAll(".workers-contrato-btn")
.forEach(btn=>{

    btn.addEventListener("click",async()=>{

        const respuesta =
        await fetch(`/trabajadores_contrato/${btn.dataset.id}`);

        const datos =
        await respuesta.json();

        lista.innerHTML="";

        datos.forEach(t=>{

            lista.innerHTML += `

            <div class="trabajador-item">

                <i class="fa-solid fa-user"></i>

                <span>${t.nombre}</span>

            </div>

            `;

        });

        modalTrabajadoresContrato.classList.add("show");

    });

});

document
.getElementById("closeTrabajadoresContrato")
.addEventListener("click",()=>{

    modalTrabajadoresContrato.classList.remove("show");

});

modalTrabajadoresContrato.addEventListener("click",e=>{

    if(e.target===modalTrabajadoresContrato){

        modalTrabajadoresContrato.classList.remove("show");

    }

});

// Nuevo contrato
document
.getElementById("openContratoModal")
.addEventListener("click",()=>{

    contratoEditando=null;

    document.getElementById("tituloModalContrato").textContent =
        "Nuevo contrato";

    document.getElementById("nombreContrato").value="";
    document.getElementById("horasAnualesContrato").value="";
    document.getElementById("horasTurnoContrato").value="";
    document.getElementById("jornadaContrato").value = "";
    

    modalContrato.classList.add("show");

});

document
.getElementById("closeContratoModal")
.addEventListener("click",()=>{

    modalContrato.classList.remove("show");

});

document
.getElementById("cancelContratoModal")
.addEventListener("click",()=>{

    modalContrato.classList.remove("show");

});


// Editar contrato
document.querySelectorAll(".edit-contrato-btn").forEach(btn=>{

    btn.addEventListener("click",()=>{
        contratoEditando=btn.dataset.id;
        document.getElementById("tituloModalContrato").textContent =
            "Editar contrato";

        document.getElementById("nombreContrato").value =
            btn.dataset.nombre;

        document.getElementById("horasAnualesContrato").value =
            btn.dataset.horasAnuales;

        document.getElementById("horasTurnoContrato").value =
            btn.dataset.horasTurno;

        document.getElementById("jornadaContrato").value =
            btn.dataset.jornada;

        modalContrato.classList.add("show");

    });

});


// Guardar contrato
document
.getElementById("guardarContrato")
.addEventListener("click",async()=>{

    const datos={

        nombre:
        document.getElementById("nombreContrato").value,

        horas_anuales:
        document.getElementById("horasAnualesContrato").value,

        horas_por_turno:
        document.getElementById("horasTurnoContrato").value,

        nombre:
        document.getElementById("nombreContrato").value,

        jornada:
            document.getElementById("jornadaContrato").value,

        horas_anuales:
            document.getElementById("horasAnualesContrato").value,

        horas_por_turno:
            document.getElementById("horasTurnoContrato").value

    };

    const url=contratoEditando
        ? "/editar_contrato"
        : "/nuevo_contrato";

    if(contratoEditando){

        datos.id=contratoEditando;

    }

    const respuesta=await fetch(url,{

        method:"POST",

        headers:{
            "Content-Type":"application/json"
        },

        body:JSON.stringify(datos)

    });

    if(respuesta.ok){

        location.reload();

    }else{

        alert("Error al guardar el contrato.");

    }

});


// Eliminar contrato
document.querySelectorAll(".delete-contrato-btn").forEach(btn=>{

    btn.addEventListener("click",async()=>{
        if(!confirm("¿Eliminar contrato?")) return;
        try {
            const respuesta = await fetch("/eliminar_contrato",{
                method:"POST",
                headers:{
                    "Content-Type":"application/json"
                },
                body:JSON.stringify({
                    id:btn.dataset.id
                })

            });

            const resultado = await respuesta.json();
            if(resultado.ok){
                location.reload();
            }else{
                alert(resultado.error || "No se ha podido eliminar el contrato.");
            }
        } catch (error) {
            alert("No se ha podido eliminar el contrato. Comprueba la conexión con el servidor.");
        }

    });

});



//Buscar Contratos

const buscarContrato = document.getElementById("buscarContrato");

buscarContrato.addEventListener("input", () => {

    const texto = buscarContrato.value.toLowerCase();

    document.querySelectorAll("#contratos-panel tbody tr").forEach(fila => {

        fila.style.display =
            fila.textContent.toLowerCase().includes(texto)
                ? ""
                : "none";

    });

});


/* ============================================================
TAREAS
============================================================ */

//BUSCADOR TAREAS

const buscarTarea = document.getElementById("buscarTarea");

buscarTarea.addEventListener("input", () => {

    const texto = buscarTarea.value.toLowerCase();

    document.querySelectorAll("#tareas-panel tbody tr").forEach(fila => {

        fila.style.display =
            fila.textContent.toLowerCase().includes(texto)
                ? ""
                : "none";

    });

});

// ACTIVAR Y DESACTIVAR TAREAS
document.querySelectorAll("#tareas-panel .status-btn").forEach(btn=>{
    btn.addEventListener("click",async()=>{
        const respuesta=await fetch("/cambiar_estado_tarea",{
            method:"POST",
            headers:{
                "Content-Type":"application/json"
            },
            body:JSON.stringify({
                id:btn.dataset.id
            })
        });
        if(respuesta.ok){
            localStorage.setItem("tabActiva","tareas");
            location.reload();
        }
    });
});


// ABRIL MODAL
openModalTarea.addEventListener("click",()=>{

    tareaEditando = null;

    document.getElementById("tituloModalTarea").textContent =
        "Nueva tarea";

    document.getElementById("guardarTarea").textContent =
        "Guardar tarea";

    document.getElementById("nombreTarea").value = "";

    document.getElementById("descripcionTarea").value = "";

    document.getElementById("estadoTarea").value = "1";

    modalTarea.classList.add("show");

});

//CERRAR MODAL
closeModalTarea.addEventListener("click",()=>{

    modalTarea.classList.remove("show");

});

cancelModalTarea.addEventListener("click",()=>{

    modalTarea.classList.remove("show");

});

modalTarea.addEventListener("click",e=>{

    if(e.target===modalTarea){

        modalTarea.classList.remove("show");

    }

});

//Buscar Trabajador Tarea
const buscarTrabajadorTarea =
document.getElementById("buscarTrabajadorTarea");

buscarTrabajadorTarea.addEventListener("input", () => {

    const texto = buscarTrabajadorTarea.value.toLowerCase();

    document
        .querySelectorAll(".trabajador-tarea-item")
        .forEach(item => {

            item.style.display =
                item.textContent.toLowerCase().includes(texto)
                ? "flex"
                : "none";

        });

});

// GUARDAR TAREA
document.getElementById("guardarTarea").addEventListener("click", async () => {
    const trabajadores=[];
    document.querySelectorAll(".trabajador-tarea-check:checked").forEach(check=>{
        trabajadores.push(parseInt(check.value));
    });
    const datos={
        nombre:document.getElementById("nombreTarea").value,
        descripcion:document.getElementById("descripcionTarea").value,
        activa:document.getElementById("estadoTarea").value,
        trabajadores:trabajadores
    };
    const url=tareaEditando
        ? "/editar_tarea"
        : "/nueva_tarea";
    if(tareaEditando){
        datos.id=tareaEditando;
    }
    const respuesta=await fetch(url,{
        method:"POST",
        headers:{
            "Content-Type":"application/json"
        },
        body:JSON.stringify(datos)
    });
    if(respuesta.ok){
        localStorage.setItem("tabActiva","tareas");
        location.reload();
    }else{
        alert("Error al guardar la tarea.");
    }
});



// VER LOS TRABAJADORES ASIGNADOS A CADA TAREA
document.querySelectorAll(".trabajadores-btn").forEach(btn=>{

    btn.addEventListener("click",async()=>{

        const r=await fetch(`/trabajadores_tarea/${btn.dataset.id}`);

        const datos=await r.json();

        const modalTrabajadoresTarea=
        document.getElementById("modalTrabajadoresTarea");

        const listaTrabajadoresTarea=
        document.getElementById("listaTrabajadoresTarea");

        document.querySelectorAll(".trabajadores-btn").forEach(btn=>{

            btn.addEventListener("click",async()=>{

                const respuesta=
                await fetch(`/trabajadores_tarea/${btn.dataset.id}`);

                const datos=
                await respuesta.json();

                listaTrabajadoresTarea.innerHTML="";

                document.getElementById("totalTrabajadoresTarea").textContent=
                    datos.length+" trabajadores";

                datos.forEach(t=>{

                    listaTrabajadoresTarea.innerHTML+=`

                        <div class="trabajador-item">

                            <i class="fa-solid fa-user"></i>

                            <span>${t.nombre} ${t.apellidos}</span>

                        </div>

                    `;

                });

                modalTrabajadoresTarea.classList.add("show");

            });

        });

    });

});

document.getElementById("closeTrabajadoresTarea").addEventListener("click",()=>{

    modalTrabajadoresTarea.classList.remove("show");

});

modalTrabajadoresTarea.addEventListener("click",e=>{

    if(e.target===modalTrabajadoresTarea){

        modalTrabajadoresTarea.classList.remove("show");

    }

});

// EDITAR TAREAS
document.querySelectorAll(".edit-tarea-btn").forEach(btn=>{

    btn.addEventListener("click",async()=>{

        tareaEditando=btn.dataset.id;

        document.getElementById("tituloModalTarea").textContent="Editar tarea";

        document.getElementById("guardarTarea").textContent="Guardar cambios";

        document.getElementById("nombreTarea").value=btn.dataset.nombre;

        document.getElementById("descripcionTarea").value=btn.dataset.descripcion;

        document.getElementById("estadoTarea").value=btn.dataset.estado;

        document.querySelectorAll(".trabajador-tarea-check").forEach(check=>{
            check.checked=false;
        });

        const respuesta=await fetch(`/trabajadores_tarea/${tareaEditando}`);

        const trabajadores=await respuesta.json();

        trabajadores.forEach(trabajador=>{

            const check=document.querySelector(
                `.trabajador-tarea-check[value="${trabajador.id_trabajador}"]`
            );

            if(check){
                check.checked=true;
            }

        });

        modalTarea.classList.add("show");

    });

});

// ELIMINAR TAREA
document.querySelectorAll("#tareas-panel .delete-tarea-btn").forEach(btn=>{
    btn.addEventListener("click",async()=>{
        const confirmar=confirm("Este cambio es permanente y la tarea se eliminará definitivamente.\n\nSi solo quieres dejarla inactiva durante una temporada, utiliza el botón Activa/Inactiva.\n\n¿Quieres eliminar la tarea?");
        if(!confirmar) return;
        const respuesta=await fetch("/eliminar_tarea",{
            method:"POST",
            headers:{
                "Content-Type":"application/json"
            },
            body:JSON.stringify({
                id:btn.dataset.id
            })
        });
        if(respuesta.ok){
            localStorage.setItem("tabActiva","tareas");
            location.reload();
        }else{
            alert("Error al eliminar la tarea.");
        }
    });
});
document.addEventListener("DOMContentLoaded",()=>{
    let promociones=[];
    let pedidos=[];
    let mesSeleccionado="";

    cargarPromociones();
    cargarPedidos();
    configurarTabs();
    configurarBusquedas();
    configurarModalPedidos();
    configurarTotales();
    configurarExcel();
    configurarInstruccionesPedidos();

    function configurarTabs(){

        const tabs = document.querySelectorAll(".historicos-tab");
        const panels = document.querySelectorAll(".historicos-panel");
        function mostrarTab(destino){
            tabs.forEach(t => t.classList.remove("active"));
            panels.forEach(p => p.classList.remove("active"));

            const tab = document.querySelector(
                `.historicos-tab[data-tab="${destino}"]`
            );
            const panel = document.getElementById(destino);

            if(tab && panel){
                tab.classList.add("active");
                panel.classList.add("active");
            }
        }

        tabs.forEach(tab => {
            tab.addEventListener("click", () => {
                const destino = tab.dataset.tab;
                mostrarTab(destino);
                history.replaceState(null, null, `#${destino}`);
            });
        });

        const pestañaGuardada =
            window.location.hash.replace("#", "") || "promociones";

        mostrarTab(pestañaGuardada);
    }

    async function cargarPromociones(){
        try{
            const respuesta=await fetch("/api/promociones");
            const datos=await respuesta.json();
            if(!respuesta.ok) throw new Error(datos.error||"No se han podido cargar las promociones.");
            promociones=datos;
            mostrarPromociones(promociones);
        }catch(error){
            console.error(error);
            const tabla=document.getElementById("tablaPromociones");
            if(tabla) tabla.innerHTML=`<tr><td colspan="6" class="loading-cell">No se han podido cargar las promociones.</td></tr>`;
        }
    }

    function mostrarPromociones(datos){
        const tabla=document.getElementById("tablaPromociones");
        if(!tabla) return;
        if(!datos.length){
            tabla.innerHTML=`<tr><td colspan="6" class="loading-cell">No hay promociones registradas.</td></tr>`;
            return;
        }
        tabla.innerHTML=datos.map(p=>`
            <tr>
                <td>${p.nombre||""}</td>
                <td>${formatearFecha(p.fecha_inicio)}</td>
                <td>${formatearFecha(p.fecha_fin)}</td>
                <td>${p.tipo||""}</td>
                <td>${p.descripcion||""}</td>
                <td class="acciones">
                    <button class="edit-button" onclick="editarPromocion(${p.id_promocion})"><i class="fa-solid fa-pen"></i></button>
                    <button class="delete-button" onclick="eliminarPromocion(${p.id_promocion})"><i class="fa-solid fa-trash"></i></button>
                </td>
            </tr>
        `).join("");
    }

    async function cargarPedidos(){
        try{
            const respuesta=await fetch("/api/pedidos_historicos");
            const datos=await respuesta.json();
            if(!respuesta.ok) throw new Error(datos.error||"No se han podido cargar los pedidos históricos.");
            pedidos=datos;
            prepararSelectorMeses();
        }catch(error){
            console.error(error);
            const tabla=document.getElementById("pedidosTabla");
            if(tabla) tabla.innerHTML=`<tr><td colspan="7" class="loading-cell">No se han podido cargar los pedidos históricos.</td></tr>`;
        }
    }

    function prepararSelectorMeses(){
        const selector=document.getElementById("mesPedidos");
        const tabla=document.getElementById("pedidosTabla");
        if(!selector) return;

        const meses={};

        pedidos.forEach(p=>{
            if(!p.fecha) return;

            const partes=p.fecha.split("-");

            if(partes.length!==3) return;

            meses[`${partes[0]}-${partes[1]}`]=true;
        });

        const claves=Object.keys(meses).sort().reverse();

        selector.innerHTML=claves.map(clave=>{
            const [anio,mes]=clave.split("-");

            return`
                <option value="${clave}">
                    ${nombreMes(Number(mes))} ${anio}
                </option>
            `;
        }).join("");

        if(claves.length){
            mesSeleccionado=claves[0];
            selector.value=mesSeleccionado;
            mostrarPedidosMes();
        }else if(tabla){
            tabla.innerHTML=`
                <tr>
                    <td colspan="7" class="loading-cell">
                        No hay datos históricos registrados.
                    </td>
                </tr>
            `;
        }
    }

    function nombreMes(numero){
        return[
            "Enero",
            "Febrero",
            "Marzo",
            "Abril",
            "Mayo",
            "Junio",
            "Julio",
            "Agosto",
            "Septiembre",
            "Octubre",
            "Noviembre",
            "Diciembre"
        ][numero-1]||"";
    }

    function mostrarPedidosMes(){
        const selector=document.getElementById("mesPedidos");

        if(selector){
            mesSeleccionado=selector.value;
        }

        const datos=pedidos.filter(p=>{
            return p.fecha&&p.fecha.startsWith(mesSeleccionado);
        });

        mostrarPedidos(datos);
    }

    function mostrarPedidos(datos){
        const tabla=document.getElementById("pedidosTabla");
        const tipo=document.getElementById("tipoDato");

        if(!tabla) return;

        const tipoSeleccionado=tipo?tipo.value:"pedidos";

        if(!datos.length){
            tabla.innerHTML=`
                <tr>
                    <td colspan="7" class="loading-cell">
                        No hay datos para este mes.
                    </td>
                </tr>
            `;
            return;
        }

        tabla.innerHTML=datos.map(p=>{

            const mcia=
                tipoSeleccionado==="pedidos"
                ?p.envios_2h_mcia_general_pedidos
                :p.envios_2h_mcia_general_lineas;

            const food=
                tipoSeleccionado==="pedidos"
                ?p.envios_2h_food_pedidos
                :p.envios_2h_food_lineas;

            const encargos=
                tipoSeleccionado==="pedidos"
                ?p.encargos_pedidos
                :p.encargos_lineas;

            const home=
                tipoSeleccionado==="pedidos"
                ?p.home_delivery_pedidos
                :p.home_delivery_lineas;

            const total=
                tipoSeleccionado==="pedidos"
                ?p.total_pedidos
                :p.total_lineas;

            return`
                <tr>
                    <td>${formatearFecha(p.fecha)}</td>
                    <td>${mcia??0}</td>
                    <td>${food??0}</td>
                    <td>${encargos??0}</td>
                    <td>${home??0}</td>
                    <td><strong>${total??0}</strong></td>
                    <td>${p.devoluciones??"—"}</td>
                    <td class="acciones">
                        <button
                            class="edit-button"
                            onclick="editarPedido(${p.id_pedido_historico})">
                            <i class="fa-solid fa-pen"></i>
                        </button>
                    </td>
                </tr>
            `;
        }).join("");
    }

    function configurarBusquedas(){
        const buscarPromocion=document.getElementById("buscarPromocion");

        if(buscarPromocion){
            buscarPromocion.addEventListener("input",()=>{
                const texto=buscarPromocion.value.toLowerCase().trim();

                const filtradas=promociones.filter(p=>
                    (p.nombre||"").toLowerCase().includes(texto)||
                    (p.tipo||"").toLowerCase().includes(texto)||
                    (p.descripcion||"").toLowerCase().includes(texto)
                );

                mostrarPromociones(filtradas);
            });
        }

        const mesPedidos=document.getElementById("mesPedidos");
        const tipoDato=document.getElementById("tipoDato");

        if(mesPedidos){
            mesPedidos.addEventListener("change",mostrarPedidosMes);
        }

        if(tipoDato){
            tipoDato.addEventListener("change",mostrarPedidosMes);
        }
    }

    function configurarModalPedidos(){
        const boton=document.getElementById("anadirDia");
        const modal=document.getElementById("modalPedido");
        const cerrar=document.getElementById("cerrarModalPedido");
        const cancelar=document.getElementById("cancelarPedido");
        const guardar=document.getElementById("guardarPedido");

        if(boton&&modal){
            boton.addEventListener("click",()=>{
                limpiarFormularioPedido();

                document.getElementById("tituloModalPedido").textContent="Añadir día";

                modal.classList.add("show");
            });
        }

        if(cerrar){
            cerrar.addEventListener("click",cerrarModalPedido);
        }

        if(cancelar){
            cancelar.addEventListener("click",cerrarModalPedido);
        }

        if(guardar){
            guardar.addEventListener("click",guardarPedido);
        }

        if(modal){
            modal.addEventListener("click",e=>{
                if(e.target===modal){
                    cerrarModalPedido();
                }
            });
        }
    }

    function cerrarModalPedido(){
        const modal=document.getElementById("modalPedido");

        if(modal){
            modal.classList.remove("show");
        }
    }

    function limpiarFormularioPedido(){
        [
            "idPedido",
            "fechaPedido",
            "mciaPedidos",
            "mciaLineas",
            "foodPedidos",
            "foodLineas",
            "encargosPedidos",
            "encargosLineas",
            "homePedidos",
            "homeLineas",
            "totalPedidos",
            "totalLineas",
            "devoluciones"
        ].forEach(id=>{
            const elemento=document.getElementById(id);

            if(elemento){
                elemento.value="";
            }
        });
    }

    async function editarPedido(id){
        try{
            const respuesta=await fetch(`/api/pedidos_historicos/${id}`);

            const pedido=await respuesta.json();

            if(!respuesta.ok){
                throw new Error(
                    pedido.error||
                    "No se ha podido cargar el registro."
                );
            }

            document.getElementById("idPedido").value=
                pedido.id_pedido_historico;

            document.getElementById("fechaPedido").value=
                pedido.fecha||"";

            document.getElementById("mciaPedidos").value=
                pedido.envios_2h_mcia_general_pedidos??0;

            document.getElementById("mciaLineas").value=
                pedido.envios_2h_mcia_general_lineas??0;

            document.getElementById("foodPedidos").value=
                pedido.envios_2h_food_pedidos??0;

            document.getElementById("foodLineas").value=
                pedido.envios_2h_food_lineas??0;

            document.getElementById("encargosPedidos").value=
                pedido.encargos_pedidos??0;

            document.getElementById("encargosLineas").value=
                pedido.encargos_lineas??0;

            document.getElementById("homePedidos").value=
                pedido.home_delivery_pedidos??0;

            document.getElementById("homeLineas").value=
                pedido.home_delivery_lineas??0;

            document.getElementById("devoluciones").value=
                pedido.devoluciones??"";

            actualizarTotales();

            document.getElementById("tituloModalPedido").textContent=
                "Editar día";

            document.getElementById("modalPedido").classList.add("show");

        }catch(error){

            console.error(error);

            alert(
                error.message||
                "No se ha podido cargar el día."
            );
        }
    }

    async function guardarPedido(){
        const id=document.getElementById("idPedido").value;

        actualizarTotales();

        const datos={
            fecha:document.getElementById("fechaPedido").value,

            envios_2h_mcia_general_pedidos:
                Number(document.getElementById("mciaPedidos").value)||0,

            envios_2h_mcia_general_lineas:
                Number(document.getElementById("mciaLineas").value)||0,

            envios_2h_food_pedidos:
                Number(document.getElementById("foodPedidos").value)||0,

            envios_2h_food_lineas:
                Number(document.getElementById("foodLineas").value)||0,

            encargos_pedidos:
                Number(document.getElementById("encargosPedidos").value)||0,

            encargos_lineas:
                Number(document.getElementById("encargosLineas").value)||0,

            home_delivery_pedidos:
                Number(document.getElementById("homePedidos").value)||0,

            home_delivery_lineas:
                Number(document.getElementById("homeLineas").value)||0,

            total_pedidos:
                Number(document.getElementById("totalPedidos").value)||0,

            total_lineas:
                Number(document.getElementById("totalLineas").value)||0,

            devoluciones:
                document.getElementById("devoluciones").value === ""
                ? null
                : Number(document.getElementById("devoluciones").value)
        };

        if(!datos.fecha){
            alert("Debes seleccionar una fecha.");
            return;
        }

        const url=id
            ?`/api/pedidos_historicos/${id}`
            :"/api/pedidos_historicos";

        const metodo=id?"PUT":"POST";

        try{

            const respuesta=await fetch(url,{
                method:metodo,
                headers:{
                    "Content-Type":"application/json"
                },
                body:JSON.stringify(datos)
            });

            const resultado=await respuesta.json();

            if(!respuesta.ok){
                throw new Error(
                    resultado.error||
                    "No se ha podido guardar el día."
                );
            }

            alert(
                id
                ?"El día se ha actualizado correctamente."
                :"El día se ha añadido correctamente."
            );

            cerrarModalPedido();

            await cargarPedidos();

        }catch(error){

            console.error(error);

            alert(
                error.message||
                "No se ha podido guardar el día."
            );
        }
    }

    function actualizarTotales(){

        const mciaPedidos=
            Number(document.getElementById("mciaPedidos")?.value)||0;

        const mciaLineas=
            Number(document.getElementById("mciaLineas")?.value)||0;

        const foodPedidos=
            Number(document.getElementById("foodPedidos")?.value)||0;

        const foodLineas=
            Number(document.getElementById("foodLineas")?.value)||0;

        const encargosPedidos=
            Number(document.getElementById("encargosPedidos")?.value)||0;

        const encargosLineas=
            Number(document.getElementById("encargosLineas")?.value)||0;

        const homePedidos=
            Number(document.getElementById("homePedidos")?.value)||0;

        const homeLineas=
            Number(document.getElementById("homeLineas")?.value)||0;

        const totalPedidosInput=
            document.getElementById("totalPedidos");

        const totalLineasInput=
            document.getElementById("totalLineas");

        if(totalPedidosInput){
            totalPedidosInput.value=
                mciaPedidos+
                foodPedidos+
                encargosPedidos+
                homePedidos;
        }

        if(totalLineasInput){
            totalLineasInput.value=
                mciaLineas+
                foodLineas+
                encargosLineas+
                homeLineas;
        }
    }

    function configurarTotales(){

        [
            "mciaPedidos",
            "mciaLineas",
            "foodPedidos",
            "foodLineas",
            "encargosPedidos",
            "encargosLineas",
            "homePedidos",
            "homeLineas"
        ].forEach(id=>{

            const campo=document.getElementById(id);

            if(campo){
                campo.addEventListener(
                    "input",
                    actualizarTotales
                );
            }

        });
    }

    function configurarExcel(){

        const importarPedidosExcel=
            document.getElementById("importarPedidosExcel");

        const exportarPedidosExcel=
            document.getElementById("exportarPedidosExcel");

        const archivoPedidosExcel=
            document.getElementById("archivoPedidosExcel");

        if(importarPedidosExcel&&archivoPedidosExcel){

            importarPedidosExcel.addEventListener(
                "click",
                ()=>{
                    archivoPedidosExcel.click();
                }
            );

            archivoPedidosExcel.addEventListener(
                "change",
                async()=>{

                    const archivo=
                        archivoPedidosExcel.files[0];

                    if(!archivo){
                        return;
                    }

                    if(
                        !archivo.name
                            .toLowerCase()
                            .endsWith(".xlsx")
                    ){

                        alert(
                            "El archivo debe estar en formato .xlsx."
                        );

                        archivoPedidosExcel.value="";

                        return;
                    }

                    const confirmar=confirm(
                        "Se añadirán los datos del Excel a los pedidos históricos. Si alguna fecha ya existe, se actualizarán sus datos. ¿Quieres continuar?"
                    );

                    if(!confirmar){

                        archivoPedidosExcel.value="";

                        return;
                    }

                    const formulario=new FormData();

                    formulario.append(
                        "archivo",
                        archivo
                    );

                    try{

                        const respuesta=await fetch(
                            "/api/pedidos_historicos/importar",
                            {
                                method:"POST",
                                body:formulario
                            }
                        );

                        const resultado=
                            await respuesta.json();

                        if(!respuesta.ok){

                            alert(
                                resultado.error||
                                "No se han podido importar los pedidos históricos."
                            );

                            return;
                        }

                        alert(
                            resultado.mensaje||
                            "Los pedidos históricos se han importado correctamente."
                        );

                        await cargarPedidos();

                    }catch(error){

                        console.error(
                            "ERROR IMPORTANDO PEDIDOS:",
                            error
                        );

                        alert(
                            "Se ha producido un error al importar el Excel."
                        );

                    }finally{

                        archivoPedidosExcel.value="";

                    }

                }
            );
        }

        if(exportarPedidosExcel){

            exportarPedidosExcel.addEventListener(
                "click",
                ()=>{
                    window.location.href=
                        "/api/pedidos_historicos/exportar";
                }
            );

        }
    }

    function configurarInstruccionesPedidos(){

        const modal=
            document.getElementById(
                "modalInstruccionesPedidos"
            );

        const abrir=
            document.getElementById(
                "verInstruccionesPedidos"
            );

        const cerrar=
            document.getElementById(
                "cerrarInstruccionesPedidos"
            );

        const cerrar2=
            document.getElementById(
                "cerrarInstruccionesPedidos2"
            );

        if(abrir&&modal){

            abrir.addEventListener(
                "click",
                ()=>{
                    modal.classList.add("show");
                }
            );

        }

        if(cerrar&&modal){

            cerrar.addEventListener(
                "click",
                ()=>{
                    modal.classList.remove("show");
                }
            );

        }

        if(cerrar2&&modal){

            cerrar2.addEventListener(
                "click",
                ()=>{
                    modal.classList.remove("show");
                }
            );

        }

        if(modal){

            modal.addEventListener(
                "click",
                e=>{
                    if(e.target===modal){
                        modal.classList.remove("show");
                    }
                }
            );

        }
    }

    function formatearFecha(fecha){

        if(!fecha){
            return "";
        }

        const partes=fecha.split("-");

        if(partes.length!==3){
            return fecha;
        }

        return`${partes[2]}/${partes[1]}/${partes[0]}`;
    }

    window.editarPedido=editarPedido;
});


/* ============================================================
   PROMOCIONES - IMPORTAR / EXPORTAR / INSTRUCCIONES
============================================================ */

const archivoPromociones=document.getElementById("archivoPromociones");
const seleccionarExcelPromociones=document.getElementById("seleccionarExcelPromociones");
const exportarPromociones=document.getElementById("exportarPromociones");
const nombreArchivoPromociones=document.getElementById("nombreArchivoPromociones");

if(seleccionarExcelPromociones&&archivoPromociones){

    seleccionarExcelPromociones.addEventListener("click",()=>{
        archivoPromociones.click();
    });

}

if(archivoPromociones){

    archivoPromociones.addEventListener("change",async()=>{

        const archivo=archivoPromociones.files[0];

        if(!archivo){
            return;
        }

        if(!archivo.name.toLowerCase().endsWith(".xlsx")){

            alert("El archivo debe estar en formato .xlsx.");

            archivoPromociones.value="";

            return;
        }

        if(nombreArchivoPromociones){

            nombreArchivoPromociones.textContent=
                "Archivo seleccionado: "+archivo.name;

        }

        const confirmar=confirm(
            "¿Quieres importar las promociones de este archivo?"
        );

        if(!confirmar){

            archivoPromociones.value="";

            if(nombreArchivoPromociones){
                nombreArchivoPromociones.textContent="";
            }

            return;
        }

        const formulario=new FormData();

        formulario.append("archivo",archivo);

        try{

            const respuesta=await fetch(
                "/importar_promociones",
                {
                    method:"POST",
                    body:formulario
                }
            );

            const resultado=await respuesta.json();

            if(respuesta.ok){

                alert(
                    resultado.mensaje||
                    "Las promociones se han importado correctamente."
                );

                location.reload();

            }else{

                alert(
                    resultado.error||
                    "No se han podido importar las promociones."
                );

            }

        }catch(error){

            console.error(
                "Error al importar promociones:",
                error
            );

            alert(
                "Se ha producido un error al importar las promociones."
            );

        }

        archivoPromociones.value="";

    });

}


if(exportarPromociones){

    exportarPromociones.addEventListener("click",()=>{

        window.location.href="/exportar_promociones";

    });

}


/* ============================================================
   INSTRUCCIONES PROMOCIONES
============================================================ */

const modalInstruccionesPromociones=
    document.getElementById(
        "modalInstruccionesPromociones"
    );

const verInstruccionesPromociones=
    document.getElementById(
        "verInstruccionesPromociones"
    );

const cerrarInstruccionesPromociones=
    document.getElementById(
        "cerrarInstruccionesPromociones"
    );

const cerrarInstruccionesPromociones2=
    document.getElementById(
        "cerrarInstruccionesPromociones2"
    );


if(
    verInstruccionesPromociones&&
    modalInstruccionesPromociones
){

    verInstruccionesPromociones.addEventListener(
        "click",
        ()=>{
            modalInstruccionesPromociones.classList.add("show");
        }
    );

}


if(cerrarInstruccionesPromociones){

    cerrarInstruccionesPromociones.addEventListener(
        "click",
        ()=>{
            modalInstruccionesPromociones.classList.remove("show");
        }
    );

}


if(cerrarInstruccionesPromociones2){

    cerrarInstruccionesPromociones2.addEventListener(
        "click",
        ()=>{
            modalInstruccionesPromociones.classList.remove("show");
        }
    );

}


if(modalInstruccionesPromociones){

    modalInstruccionesPromociones.addEventListener(
        "click",
        (e)=>{
            if(e.target===modalInstruccionesPromociones){
                modalInstruccionesPromociones.classList.remove("show");
            }
        }
    );

}

/* ============================================================
   PROMOCIONES - CRUD
============================================================ */

const modalPromocion=document.getElementById("modalPromocion");
const tituloModalPromocion=document.getElementById("tituloModalPromocion");
const cerrarModalPromocion=document.getElementById("cerrarModalPromocion");
const cancelarPromocion=document.getElementById("cancelarPromocion");
const guardarPromocion=document.getElementById("guardarPromocion");
const idPromocion=document.getElementById("idPromocion");
const nombrePromocion=document.getElementById("nombrePromocion");
const fechaInicioPromocion=document.getElementById("fechaInicioPromocion");
const fechaFinPromocion=document.getElementById("fechaFinPromocion");
const tipoPromocion=document.getElementById("tipoPromocion");
const descripcionPromocion=document.getElementById("descripcionPromocion");
const buscarPromocion=document.querySelector(
    'input[placeholder="Buscar promoción..."]'
);

const botonNuevaPromocion=document.querySelector(
    'button[id="nuevaPromocion"]'
);

function abrirModalPromocion(){
    modalPromocion.classList.add("show");
}

function cerrarModalPromocionFuncion(){
    modalPromocion.classList.remove("show");
}

function limpiarFormularioPromocion(){
    idPromocion.value="";
    nombrePromocion.value="";
    fechaInicioPromocion.value="";
    fechaFinPromocion.value="";
    tipoPromocion.value="";
    descripcionPromocion.value="";
}

function nuevaPromocion(){

    limpiarFormularioPromocion();

    tituloModalPromocion.textContent="Nueva promoción";

    abrirModalPromocion();
}

if(botonNuevaPromocion){
    botonNuevaPromocion.addEventListener(
        "click",
        nuevaPromocion
    );
}

if(cerrarModalPromocion){
    cerrarModalPromocion.addEventListener(
        "click",
        cerrarModalPromocionFuncion
    );
}

if(cancelarPromocion){
    cancelarPromocion.addEventListener(
        "click",
        cerrarModalPromocionFuncion
    );
}

if(modalPromocion){
    modalPromocion.addEventListener("click",(e)=>{
        if(e.target===modalPromocion){
            cerrarModalPromocionFuncion();
        }
    });
}


/* ============================================================
   EDITAR PROMOCIÓN
============================================================ */

async function editarPromocion(id){

    try{

        const respuesta=await fetch(
            `/api/promociones/${id}`
        );

        const promocion=await respuesta.json();

        if(!respuesta.ok){
            throw new Error(
                promocion.error||
                "No se ha podido cargar la promoción."
            );
        }

        idPromocion.value=promocion.id_promocion;
        nombrePromocion.value=promocion.nombre||"";
        fechaInicioPromocion.value=promocion.fecha_inicio||"";
        fechaFinPromocion.value=promocion.fecha_fin||"";
        tipoPromocion.value=promocion.tipo||"";
        descripcionPromocion.value=promocion.descripcion||"";

        tituloModalPromocion.textContent="Editar promoción";

        abrirModalPromocion();

    }catch(error){

        console.error(error);

        alert(
            error.message||
            "No se ha podido cargar la promoción."
        );

    }
}


/* ============================================================
   GUARDAR PROMOCIÓN
============================================================ */

if(guardarPromocion){

    guardarPromocion.addEventListener(
        "click",
        async()=>{

            const nombre=nombrePromocion.value.trim();
            const fechaInicio=fechaInicioPromocion.value;
            const fechaFin=fechaFinPromocion.value;

            if(!nombre){
                alert("Introduce el nombre de la promoción.");
                return;
            }

            if(!fechaInicio||!fechaFin){
                alert("Introduce las fechas de inicio y fin.");
                return;
            }

            if(fechaFin<fechaInicio){
                alert(
                    "La fecha de fin no puede ser anterior a la fecha de inicio."
                );
                return;
            }

            const datos={
                nombre:nombre,
                fecha_inicio:fechaInicio,
                fecha_fin:fechaFin,
                tipo:tipoPromocion.value.trim()||null,
                descripcion:descripcionPromocion.value.trim()||null
            };

            const id=idPromocion.value;

            try{

                let respuesta;

                if(id){

                    respuesta=await fetch(
                        `/api/promociones/${id}`,
                        {
                            method:"PUT",
                            headers:{
                                "Content-Type":"application/json"
                            },
                            body:JSON.stringify(datos)
                        }
                    );

                }else{

                    respuesta=await fetch(
                        "/api/promociones",
                        {
                            method:"POST",
                            headers:{
                                "Content-Type":"application/json"
                            },
                            body:JSON.stringify(datos)
                        }
                    );

                }

                const resultado=await respuesta.json();

                if(!respuesta.ok){

                    throw new Error(
                        resultado.error||
                        "No se ha podido guardar la promoción."
                    );

                }

                alert(
                    id
                    ?"La promoción se ha actualizado correctamente."
                    :"La promoción se ha creado correctamente."
                );

                cerrarModalPromocionFuncion();

                location.reload();

            }catch(error){

                console.error(error);

                alert(
                    error.message||
                    "No se ha podido guardar la promoción."
                );

            }

        }
    );

}


/* ============================================================
   ELIMINAR PROMOCIÓN
============================================================ */

async function eliminarPromocion(id){

    const confirmar=confirm(
        "¿Seguro que quieres eliminar esta promoción?"
    );

    if(!confirmar){
        return;
    }

    try{

        const respuesta=await fetch(
            `/api/promociones/${id}`,
            {
                method:"DELETE"
            }
        );

        const resultado=await respuesta.json();

        if(!respuesta.ok){

            throw new Error(
                resultado.error||
                "No se ha podido eliminar la promoción."
            );

        }

        alert(
            "La promoción se ha eliminado correctamente."
        );

        location.reload();

    }catch(error){

        console.error(error);

        alert(
            error.message||
            "No se ha podido eliminar la promoción."
        );

    }
}


/* ============================================================
   BUSCADOR DE PROMOCIONES
============================================================ */

if(buscarPromocion){

    buscarPromocion.addEventListener(
        "input",
        ()=>{
            const texto=buscarPromocion.value
                .trim()
                .toLowerCase();

            const filas=document.querySelectorAll(
                "#tablaPromociones tbody tr"
            );

            filas.forEach(fila=>{

                const nombre=fila
                    .querySelector(".nombre-promocion");

                if(!nombre){
                    return;
                }

                const contenido=nombre.textContent
                    .toLowerCase();

                fila.style.display=
                    contenido.includes(texto)
                    ?""
                    :"none";

            });

        }
    );

}
document.addEventListener("DOMContentLoaded",()=>{
    let predicciones=[];
    let graficoPrediccion=null;
    let graficoHoras=null;

    let fechaInicioPrediccion=null;
    let fechaFinPrediccion=null;
    let mesSeleccionado=null;
    let añoSeleccionado=null;

    const selectorAño=document.getElementById("añoPrediccion");
    const botonesMes=document.querySelectorAll(".btn-mes");
    const periodoSeleccionado=document.getElementById("periodoSeleccionado");

    // ============================================================
    // AÑOS DISPONIBLES
    // ============================================================

    if(selectorAño){
        const añoActual=new Date().getFullYear();

        for(let año=añoActual-1;año<=añoActual+2;año++){
            const opcion=document.createElement("option");

            opcion.value=año;
            opcion.textContent=año;

            selectorAño.appendChild(opcion);
        }
    }

    // ============================================================
    // CARGAR PERIODO GUARDADO
    // ============================================================

    try{
        const periodoGuardado=localStorage.getItem("emplea_periodo_prediccion");

        if(periodoGuardado){
            const periodo=JSON.parse(periodoGuardado);

            fechaInicioPrediccion=periodo.fecha_inicio;
            fechaFinPrediccion=periodo.fecha_fin;

            if(periodo.mes){
                mesSeleccionado=periodo.mes;
            }else if(fechaInicioPrediccion){
                mesSeleccionado=Number(fechaInicioPrediccion.split("-")[1]);
            }

            if(periodo.año){
                añoSeleccionado=periodo.año;
            }else if(fechaInicioPrediccion){
                añoSeleccionado=Number(fechaInicioPrediccion.split("-")[0]);
            }

            if(selectorAño&&añoSeleccionado){
                selectorAño.value=añoSeleccionado;
            }
        }
    }catch(error){
        console.warn("No se pudo recuperar el periodo de predicción:",error);
    }

    // ============================================================
    // SELECCIONAR MES
    // ============================================================

    botonesMes.forEach(boton=>{
        boton.addEventListener("click",()=>{
            const mes=Number(boton.dataset.mes);
            const año=Number(selectorAño.value);

            mesSeleccionado=mes;
            añoSeleccionado=año;

            const mesFormateado=String(mes).padStart(2,"0");
            const ultimoDia=new Date(año,mes,0).getDate();

            fechaInicioPrediccion=`${año}-${mesFormateado}-01`;
            fechaFinPrediccion=`${año}-${mesFormateado}-${ultimoDia}`;

            botonesMes.forEach(b=>{
                b.classList.remove("seleccionado");
            });

            boton.classList.add("seleccionado");

            if(periodoSeleccionado){
                periodoSeleccionado.textContent=
                    `Periodo seleccionado: ${formatearFecha(fechaInicioPrediccion)} - ${formatearFecha(fechaFinPrediccion)}`;
            }

            guardarPeriodoPrediccionSeleccionado(
                fechaInicioPrediccion,
                fechaFinPrediccion
            );
        });
    });

    // ============================================================
    // CAMBIAR AÑO
    // ============================================================

    if(selectorAño){
        selectorAño.addEventListener("change",()=>{
            if(!mesSeleccionado){
                return;
            }

            const boton=document.querySelector(
                `.btn-mes[data-mes="${mesSeleccionado}"]`
            );

            if(boton){
                boton.click();
            }
        });
    }

    // ============================================================
    // RESTAURAR MES SELECCIONADO
    // ============================================================

    if(mesSeleccionado){
        const boton=document.querySelector(
            `.btn-mes[data-mes="${mesSeleccionado}"]`
        );

        if(boton){
            boton.classList.add("seleccionado");

            if(periodoSeleccionado&&fechaInicioPrediccion&&fechaFinPrediccion){
                periodoSeleccionado.textContent=
                    `Periodo seleccionado: ${formatearFecha(fechaInicioPrediccion)} - ${formatearFecha(fechaFinPrediccion)}`;
            }
        }
    }

    // ============================================================
    // GENERAR PREDICCIÓN
    // ============================================================

    document.getElementById("generarPrediccion").addEventListener(
        "click",
        generarPrediccion
    );

    const selector=document.getElementById("periodoGrafico");

    if(selector){
        selector.addEventListener("change",mostrarGraficos);
    }

    // ============================================================
    // GUARDAR PERIODO
    // ============================================================

    function guardarPeriodoPrediccionSeleccionado(fechaInicio,fechaFin){
        const periodo={
            fecha_inicio:fechaInicio,
            fecha_fin:fechaFin,
            mes:mesSeleccionado,
            año:añoSeleccionado
        };

        window.__empleaPeriodoPrediccion=periodo;

        try{
            localStorage.setItem(
                "emplea_periodo_prediccion",
                JSON.stringify(periodo)
            );
        }catch(error){
            console.warn(
                "No se pudo guardar el periodo de predicción en localStorage:",
                error
            );
        }

        try{
            sessionStorage.setItem(
                "emplea_periodo_prediccion",
                JSON.stringify(periodo)
            );
        }catch(error){
            console.warn(
                "No se pudo guardar el periodo de predicción en sessionStorage:",
                error
            );
        }
    }

    // ============================================================
    // CARGAR PREDICCIÓN
    // ============================================================

    async function cargarPrediccion(){
        try{
            const fechaInicio=fechaInicioPrediccion||"";
            const fechaFin=fechaFinPrediccion||"";

            let url="/api/prediccion";
            const params=new URLSearchParams();

            if(fechaInicio){
                params.append("fecha_inicio",fechaInicio);
            }

            if(fechaFin){
                params.append("fecha_fin",fechaFin);
            }

            if(params.toString()){
                url+=`?${params.toString()}`;
            }

            const respuesta=await fetch(url);
            const datos=await respuesta.json();

            if(!respuesta.ok){
                throw new Error(
                    datos.error||
                    "No se han podido cargar las predicciones."
                );
            }

            predicciones=datos;

            mostrarResumen();
            mostrarPrediccion();
            mostrarGraficos();

        }catch(error){
            console.error(error);

            const tabla=document.getElementById("tablaPrediccion");

            if(tabla){
                tabla.innerHTML=`
                    <tr>
                        <td colspan="7" class="loading-cell">
                            No se han podido cargar las predicciones.
                        </td>
                    </tr>
                `;
            }
        }
    }

    // ============================================================
    // GENERAR PREDICCIÓN
    // ============================================================

    async function generarPrediccion(){
        const fechaInicio=fechaInicioPrediccion;
        const fechaFin=fechaFinPrediccion;

        if(!fechaInicio||!fechaFin){
            alert("Selecciona un mes antes de generar la predicción.");
            return;
        }

        if(fechaInicio>fechaFin){
            alert("La fecha de inicio no puede ser posterior a la fecha de fin.");
            return;
        }

        const boton=document.getElementById("generarPrediccion");

        try{
            boton.disabled=true;

            boton.innerHTML=`
                <i class="fa-solid fa-spinner fa-spin"></i>
                Generando predicción...
            `;

            const respuesta=await fetch(
                "/api/prediccion/generar",
                {
                    method:"POST",
                    headers:{
                        "Content-Type":"application/json"
                    },
                    body:JSON.stringify({
                        fecha_inicio:fechaInicio,
                        fecha_fin:fechaFin
                    })
                }
            );

            const datos=await respuesta.json();

            if(!respuesta.ok){
                throw new Error(
                    datos.error||
                    "No se ha podido generar la predicción."
                );
            }

            guardarPeriodoPrediccionSeleccionado(
                fechaInicio,
                fechaFin
            );

            alert("Predicción generada correctamente.");

            await cargarPrediccion();

        }catch(error){
            console.error(
                "ERROR GENERANDO PREDICCIÓN:",
                error
            );

            alert(
                error.message||
                "No se ha podido generar la predicción."
            );

        }finally{
            boton.disabled=false;

            boton.innerHTML=`
                <i class="fa-solid fa-chart-line"></i>
                Generar predicción
            `;
        }
    }

    // ============================================================
    // RESUMEN
    // ============================================================

    function mostrarResumen(){
        const dias=document.getElementById("diasPrevistos");
        const total=document.getElementById("totalPrevisto");
        const horas=document.getElementById("totalHoras");
        const ultima=document.getElementById("ultimaGeneracion");
        const periodo=document.getElementById("periodoPrediccion");
        const numeroDias=document.getElementById("numeroDias");

        if(!predicciones.length){
            return;
        }

        if(dias){
            dias.textContent=predicciones.length;
        }

        if(numeroDias){
            numeroDias.textContent=predicciones.length;
        }

        const totalPedidos=predicciones.reduce(
            (suma,p)=>{
                return suma+(Number(p.pedidos_previstos)||0);
            },
            0
        );

        if(total){
            total.textContent=
                totalPedidos.toLocaleString("es-ES");
        }

        const totalHoras=predicciones.reduce(
            (suma,p)=>{
                return suma+(Number(p.horas_necesarias)||0);
            },
            0
        );

        if(horas){
            horas.textContent=
                totalHoras.toLocaleString(
                    "es-ES",
                    {
                        minimumFractionDigits:2,
                        maximumFractionDigits:2
                    }
                );
        }

        const primera=predicciones[0];
        const ultimaPrediccion=
            predicciones[predicciones.length-1];

        if(periodo){
            periodo.textContent=
                `${formatearFecha(primera.fecha)} - ${formatearFecha(ultimaPrediccion.fecha)}`;
        }

        if(ultima){
            const fechas=predicciones
                .map(p=>p.fecha_generacion)
                .filter(Boolean);

            if(fechas.length){
                ultima.textContent=
                    formatearFechaHora(fechas[0]);
            }
        }
    }

    // ============================================================
    // GRÁFICOS
    // ============================================================

    function mostrarGraficos(){
        const canvasPrediccion=
            document.getElementById("graficoPrediccion");

        const canvasHoras=
            document.getElementById("graficoHoras");

        const selector=
            document.getElementById("periodoGrafico");

        if(
            !predicciones.length||
            !canvasPrediccion||
            !canvasHoras||
            typeof Chart==="undefined"
        ){
            return;
        }

        let datosGrafico=[...predicciones];

        if(selector&&selector.value!=="todo"){
            const dias=Number(selector.value);
            datosGrafico=
                predicciones.slice(0,dias);
        }

        const fechas=datosGrafico.map(
            p=>formatearFecha(p.fecha)
        );

        const pedidos=datosGrafico.map(
            p=>Number(p.pedidos_previstos)||0
        );

        const limiteInferior=datosGrafico.map(
            p=>Number(p.limite_inferior)||0
        );

        const limiteSuperior=datosGrafico.map(
            p=>Number(p.limite_superior)||0
        );

        const horas=datosGrafico.map(
            p=>Number(p.horas_necesarias)||0
        );

        if(graficoPrediccion){
            graficoPrediccion.destroy();
        }

        if(graficoHoras){
            graficoHoras.destroy();
        }

        graficoPrediccion=
            new Chart(
                canvasPrediccion,
                {
                    type:"line",

                    data:{
                        labels:fechas,

                        datasets:[
                            {
                                label:"Pedidos previstos",
                                data:pedidos,
                                borderColor:"#00843d",
                                backgroundColor:
                                    "rgba(0,132,61,0.08)",
                                borderWidth:2,
                                tension:0.3,
                                pointRadius:2,
                                fill:false
                            },
                            {
                                label:"Límite superior",
                                data:limiteSuperior,
                                borderColor:
                                    "rgba(0,132,61,0.35)",
                                borderWidth:1,
                                borderDash:[5,5],
                                pointRadius:0,
                                tension:0.3
                            },
                            {
                                label:"Límite inferior",
                                data:limiteInferior,
                                borderColor:
                                    "rgba(0,132,61,0.35)",
                                borderWidth:1,
                                borderDash:[5,5],
                                pointRadius:0,
                                tension:0.3
                            }
                        ]
                    },

                    options:{
                        responsive:true,
                        maintainAspectRatio:false,

                        interaction:{
                            mode:"index",
                            intersect:false
                        },

                        plugins:{
                            legend:{
                                position:"top"
                            }
                        },

                        scales:{
                            y:{
                                beginAtZero:false,
                                title:{
                                    display:true,
                                    text:"Pedidos"
                                }
                            },

                            x:{
                                ticks:{
                                    maxTicksLimit:10
                                }
                            }
                        }
                    }
                }
            );

        graficoHoras=
            new Chart(
                canvasHoras,
                {
                    type:"line",

                    data:{
                        labels:fechas,

                        datasets:[
                            {
                                label:"Horas necesarias",
                                data:horas,
                                borderColor:"#00843d",
                                backgroundColor:
                                    "rgba(0,132,61,0.08)",
                                borderWidth:2,
                                tension:0.3,
                                pointRadius:2,
                                fill:true
                            }
                        ]
                    },

                    options:{
                        responsive:true,
                        maintainAspectRatio:false,

                        interaction:{
                            mode:"index",
                            intersect:false
                        },

                        plugins:{
                            legend:{
                                display:false
                            }
                        },

                        scales:{
                            y:{
                                beginAtZero:true,
                                title:{
                                    display:true,
                                    text:"Horas"
                                }
                            },

                            x:{
                                ticks:{
                                    maxTicksLimit:10
                                }
                            }
                        }
                    }
                }
            );
    }

    // ============================================================
    // TABLA
    // ============================================================

    function mostrarPrediccion(){
        const tabla=
            document.getElementById("tablaPrediccion");

        if(!tabla){
            return;
        }

        if(!predicciones.length){
            tabla.innerHTML=`
                <tr>
                    <td colspan="7" class="loading-cell">
                        No hay predicciones registradas.
                    </td>
                </tr>
            `;

            return;
        }

        tabla.innerHTML=
            predicciones.map(p=>`
                <tr>
                    <td>${formatearFecha(p.fecha)}</td>
                    <td>${p.dia_semana||""}</td>
                    <td>
                        <strong>
                            ${p.pedidos_previstos??0}
                        </strong>
                    </td>
                    <td>
                        ${p.pedidos_acumulados??0}
                    </td>
                    <td>
                        ${p.horas_necesarias??0}
                    </td>
                    <td>
                        ${p.limite_inferior??0}
                    </td>
                    <td>
                        ${p.limite_superior??0}
                    </td>
                </tr>
            `).join("");
    }

    // ============================================================
    // FORMATEAR FECHAS
    // ============================================================

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

    function formatearFechaHora(fecha){
        if(!fecha){
            return "";
        }

        const partes=fecha.split(" ");

        if(partes.length<2){
            return fecha;
        }

        const fechaFormateada=
            formatearFecha(partes[0]);

        return`${fechaFormateada} ${partes[1]}`;
    }

    // ============================================================
    // CARGA INICIAL
    // ============================================================

    cargarPrediccion();
});
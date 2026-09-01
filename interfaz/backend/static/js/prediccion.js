document.addEventListener("DOMContentLoaded",()=>{
    let predicciones=[];
    let graficoPrediccion=null;
    let graficoHoras=null;

    cargarPrediccion();

    document.getElementById("generarPrediccion").addEventListener(
        "click",
        generarPrediccion
    );

    const selector=document.getElementById("periodoGrafico");

    if(selector){
        selector.addEventListener("change",mostrarGraficos);
    }

    async function cargarPrediccion(){

        try{

            const respuesta=await fetch("/api/prediccion");
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

    async function generarPrediccion() {

        const fechaInicio =
            document.getElementById("fechaInicio").value;

        const fechaFin =
            document.getElementById("fechaFin").value;

        // Comprobar que se han introducido las dos fechas
        if (!fechaInicio || !fechaFin) {
            alert("Selecciona una fecha de inicio y una fecha de fin.");
            return;
        }

        // Comprobar que el periodo es válido
        if (fechaInicio > fechaFin) {
            alert("La fecha de inicio no puede ser posterior a la fecha de fin.");
            return;
        }
        const boton =
            document.getElementById("generarPrediccion");
        try {
            boton.disabled = true;
            boton.innerHTML = `
                <i class="fa-solid fa-spinner fa-spin"></i>
                Generando predicción...
            `;
            const respuesta = await fetch(
                "/api/prediccion/generar",
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        fecha_inicio: fechaInicio,
                        fecha_fin: fechaFin
                    })
                }
            );
            const datos =
                await respuesta.json();
            if (!respuesta.ok) {

                throw new Error(
                    datos.error ||
                    "No se ha podido generar la predicción."
                );
            }
            alert(
                "Predicción generada correctamente."
            );

            // Recargar los datos de la predicción

            await cargarPrediccion();

        } catch (error) {

            console.error(
                "ERROR GENERANDO PREDICCIÓN:",
                error
            );

            alert(
                error.message ||
                "No se ha podido generar la predicción."
            );

        } finally {

            boton.disabled = false;
            boton.innerHTML = `
                <i class="fa-solid fa-chart-line"></i>
                Generar predicción
            `;
        }
    }

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

});
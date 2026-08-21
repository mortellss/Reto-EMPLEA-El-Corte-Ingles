document.addEventListener("DOMContentLoaded",()=>{
    let predicciones=[];

    cargarPrediccion();
    document.getElementById("generarPrediccion").addEventListener("click", generarPrediccion);

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

    async function generarPrediccion(){

        const boton=document.getElementById("generarPrediccion");

        try{

            boton.disabled=true;
            boton.innerHTML='<i class="fa-solid fa-spinner fa-spin"></i> Generando...';

            const respuesta=await fetch("/api/prediccion/generar",{
                method:"POST"
            });

            const datos=await respuesta.json();

            if(!respuesta.ok){
                throw new Error(datos.error||"No se ha podido generar la predicción.");
            }

            alert("Predicción generada correctamente.");

            await cargarPrediccion();

        }catch(error){

            console.error(error);

            alert("Error al generar la predicción: "+error.message);

        }finally{

            boton.disabled=false;
            boton.innerHTML='<i class="fa-solid fa-chart-line"></i> Generar predicción';

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
            total.textContent=totalPedidos.toLocaleString("es-ES");
        }

        const totalHoras=predicciones.reduce(
            (suma,p)=>{
                return suma+(Number(p.horas_necesarias)||0);
            },
            0
        );

        if(horas){
            horas.textContent=totalHoras.toLocaleString(
                "es-ES",
                {
                    minimumFractionDigits:2,
                    maximumFractionDigits:2
                }
            );
        }

        const primera=predicciones[0];
        const ultimaPrediccion=predicciones[predicciones.length-1];

        if(periodo){
            periodo.textContent=
                `${formatearFecha(primera.fecha)} - ${formatearFecha(ultimaPrediccion.fecha)}`;
        }

        if(ultima){

            const fechas=predicciones
                .map(p=>p.fecha_generacion)
                .filter(Boolean);

            if(fechas.length){
                ultima.textContent=formatearFechaHora(fechas[0]);
            }
        }
    }


    function mostrarPrediccion(){

        const tabla=document.getElementById("tablaPrediccion");

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

        tabla.innerHTML=predicciones.map(p=>`

            <tr>

                <td>${formatearFecha(p.fecha)}</td>

                <td>${p.dia_semana||""}</td>

                <td>
                    <strong>${p.pedidos_previstos??0}</strong>
                </td>

                <td>${p.pedidos_acumulados??0}</td>

                <td>${p.horas_necesarias??0}</td>

                <td>${p.limite_inferior??0}</td>

                <td>${p.limite_superior??0}</td>

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

        const fechaFormateada=formatearFecha(partes[0]);

        return`${fechaFormateada} ${partes[1]}`;
    }


});
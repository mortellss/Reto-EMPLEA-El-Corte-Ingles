const btnAbrirCalendario=document.getElementById("abrirCalendario");
if(btnAbrirCalendario){
    btnAbrirCalendario.addEventListener("click",()=>{
        window.location.href="/calendario";
    });
}
/* ============================================================
   IMPORTAR CALENDARIO
============================================================ */
const archivoCalendario=document.getElementById("archivoCalendario");
const seleccionarExcel=document.getElementById("seleccionarExcel");
const nombreArchivoCalendario=document.getElementById("nombreArchivoCalendario");
if(seleccionarExcel&&archivoCalendario){
    seleccionarExcel.addEventListener("click",()=>{
        archivoCalendario.click();
    });
    archivoCalendario.addEventListener("change",async()=>{
        const archivo=archivoCalendario.files[0];
        if(!archivo){
            return;
        }
        if(!archivo.name.toLowerCase().endsWith(".xlsx")){
            alert("El archivo debe estar en formato .xlsx.");
            archivoCalendario.value="";
            return;
        }
        if(nombreArchivoCalendario){
            nombreArchivoCalendario.textContent="Archivo seleccionado: "+archivo.name;
        }
        const confirmar=confirm("Al importar este archivo se sustituirá el calendario actual. ¿Quieres continuar?");
        if(!confirmar){
            archivoCalendario.value="";
            if(nombreArchivoCalendario){
                nombreArchivoCalendario.textContent="";
            }
            return;
        }
        const formulario=new FormData();
        formulario.append("archivo",archivo);
        try{
            const respuesta=await fetch("/importar_calendario",{
                method:"POST",
                body:formulario
            });
            const resultado=await respuesta.json();
            if(respuesta.ok){
                alert(resultado.mensaje||"El calendario se ha importado correctamente.");
                location.reload();
            }else{
                alert(resultado.error||"No se ha podido importar el calendario.");
            }
        }catch(error){
            console.error("Error al importar calendario:",error);
            alert("Se ha producido un error al importar el calendario.");
        }
        archivoCalendario.value="";
    });
}
/* ============================================================
   INSTRUCCIONES
============================================================ */
const modalInstruccionesCalendario=document.getElementById("modalInstruccionesCalendario");
const verInstrucciones=document.getElementById("verInstrucciones");
const cerrarInstruccionesCalendario=document.getElementById("cerrarInstruccionesCalendario");
const cerrarInstruccionesCalendario2=document.getElementById("cerrarInstruccionesCalendario2");
if(verInstrucciones&&modalInstruccionesCalendario){
    verInstrucciones.addEventListener("click",()=>{
        modalInstruccionesCalendario.classList.add("show");
    });
}
if(cerrarInstruccionesCalendario){
    cerrarInstruccionesCalendario.addEventListener("click",()=>{
        modalInstruccionesCalendario.classList.remove("show");
    });
}
if(cerrarInstruccionesCalendario2){
    cerrarInstruccionesCalendario2.addEventListener("click",()=>{
        modalInstruccionesCalendario.classList.remove("show");
    });
}
if(modalInstruccionesCalendario){
    modalInstruccionesCalendario.addEventListener("click",(e)=>{
        if(e.target===modalInstruccionesCalendario){
            modalInstruccionesCalendario.classList.remove("show");
        }
    });
}


/* ============================================================
DESCARGAR EXCEL
============================================================ */
const descargarExcel=document.getElementById("descargarExcel");
if(descargarExcel){
    descargarExcel.addEventListener("click",()=>{
        window.location.href="/exportar_calendario";
    });
}
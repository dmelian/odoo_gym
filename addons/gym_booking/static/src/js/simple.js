console.log("JS cargado desde mi módulo");

document.addEventListener("DOMContentLoaded", function () {
    const boton = document.getElementById("mi_boton");
    if (boton) {
        boton.addEventListener("click", function () {
            alert("¡Has hecho clic en el botón!");
        });
    }
});
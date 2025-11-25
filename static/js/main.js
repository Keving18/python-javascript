import { agregarProducto, agregarComentario } from "./api.js";

import { mostrarMensaje, limpiarFormularioProducto, limpiarFormularioComentario } from "./ui.js";

import { cargarProductos } from "./utils.js";

import "./components/product-card.js";

document.addEventListener("DOMContentLoaded", () => {
    cargarProductos();
});

const formProducto = document.getElementById("form-product");
if (formProducto) {
    formProducto.addEventListener("submit", async (e) => {
        e.preventDefault();

        const inputNombre = document.getElementById("nombre-producto");
        const inputPrecio = document.getElementById("precio-producto");
        const inputImagen = document.getElementById("imagen-producto");

        const formData = new FormData();
        formData.append("nombre", inputNombre.value);
        formData.append("precio", parseFloat(inputPrecio.value));
        formData.append("imagen", inputImagen.files[0]);
        try {
            await agregarProducto(formData);
            mostrarMensaje("Producto agregado correctamente.");
            limpiarFormularioProducto();
            cargarProductos();
        } catch (error) {
            console.error("Error al agregar producto:", error);
            mostrarMensaje("Error al agregar el producto.", "error");
        }
    });
}

const formComentario = document.getElementById("form-comentario");
if (formComentario) {
    formComentario.addEventListener("submit", async (e) => {
        e.preventDefault();

        const idProducto = document.getElementById("idProducto");
        const usuario = document.getElementById("usuario-comentario");
        const texto = document.getElementById("texto-comentario");

        try {
            await agregarComentario(idProducto.value, {
                usuario: usuario.value,
                texto: texto.value,
            });
            mostrarMensaje("Comentario agregado correctamente.");
            limpiarFormularioComentario();
            cargarProductos();
        } catch (error) {
            console.error("Error al agregar comentario:", error);
            mostrarMensaje("Error al agregar el comentario.", "error");
        }
    });
}

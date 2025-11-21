console.log("Script cargado correctamente");

class ProductCard extends HTMLElement {
    constructor() {
        super();
        this.attachShadow({ mode: "open" });
    }

    async connectedCallback() {
        const nombre = this.getAttribute("nombre") || "Producto";
        const precio = this.getAttribute("precio") || "0.00";
        const habilitado = this.getAttribute("habilitado") === "true";
        const id = this.getAttribute("id") || "";
        const imagen = this.getAttribute("imagen") || "static/default-image.webp";

        this.shadowRoot.innerHTML = `
            <style>
                .card {
                    border: 1px solid #ccc;
                    padding: 10px;
                    margin: 5px 0;
                    border-radius: 5px;
                    background-color: ${habilitado ? "#fff" : "#f8d7da"};
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                }

                img {
                    width: 60px;
                    height: 60px;
                    border-radius: 5px;
                    object-fit: cover;
                }

                button {
                    background: crimson;
                    color: white;
                    border: none;
                    padding: 5px 10px;
                    border-radius: 3px;
                    cursor: pointer;
                }
                
                #btnHabilitar {
                    background: ${habilitado ? "gray" : "green"};
                }

                .comentarios {
                    margin-top: 10px;
                    font-size: 0.9em;
                    color: #555;
                }

                .comentarios p {
                    margin: 5px 0;
                }
            </style>
            <div>
                <div class="card">
                    <img src="${imagen}" alt="${nombre}" />
                    <span><strong>${nombre}</strong> - Q${precio}</span>
                    <div>
                        <button id="btnHabilitar">${
                            habilitado ? "Deshabilitar" : "Habilitar"
                        }</button>
                        <button id="btnEliminar">Eliminar</button>
                    </div>
                </div>
                <div id="comentarios" class="comentarios">Cargando comentarios...</div>
            </div>
        `;

        // Cargar comentarios
        const comentariosDiv = this.shadowRoot.getElementById("comentarios");
        const res = await fetch(`/productos/${id}/comentarios`);
        const comentarios = await res.json();
        if (comentarios.length === 0) {
            comentariosDiv.innerHTML = "<em>No hay comentarios.</em>";
        } else {
            comentariosDiv.innerHTML =
                "<strong>Comentarios:</strong><ul>" +
                comentarios
                    .map((c) => `<p><strong>${c.usuario}</strong>: ${c.texto}</p>`)
                    .join("") +
                "</ul>";
        }

        this.shadowRoot.getElementById("btnEliminar").addEventListener("click", async () => {
            eliminarProducto(id);
        });
        this.shadowRoot.getElementById("btnHabilitar").addEventListener("click", async () => {
            habilitarProducto(id);
        });
    }
}

customElements.define("product-card", ProductCard);

async function cargarProductos() {
    const contenedor = document.getElementById("product-list");
    contenedor.innerHTML = "";

    const loader = document.getElementById("loader");
    loader.style.display = "block";

    // simular retardo de carga
    await new Promise((resolve) => setTimeout(resolve, 3000));

    try {
        const response = await fetch("/productos");
        if (!response.ok) throw new Error("Error al obtener los productos");

        const productos = await response.json();
        loader.style.display = "none";

        if (productos.length === 0) {
            contenedor.innerHTML = "<p>No hay productos disponibles.</p>";
            return;
        }

        productos.forEach((producto) => {
            const productCard = document.createElement("product-card");
            productCard.setAttribute("nombre", producto.nombre);
            productCard.setAttribute("precio", producto.precio);
            productCard.setAttribute("habilitado", producto.habilitado);
            productCard.setAttribute("id", producto.id);
            productCard.setAttribute("imagen", producto.imagen || "");
            contenedor.appendChild(productCard);
        });
    } catch (error) {
        console.error("Error al cargar productos:", error);
        loader.style.display = "none";
        contenedor.innerHTML = "<p>Error al cargar los productos.</p>";
    }
}

async function eliminarProducto(id) {
    if (!confirm("¿Está seguro de que desea eliminar este producto?")) {
        return;
    }
    await fetch(`/productos/${id}`, {
        method: "DELETE",
    });
    mostrarMensaje("Producto eliminado correctamente.");
    cargarProductos();
}

async function habilitarProducto(id) {
    await fetch(`/productos/${id}/habilitar`, {
        method: "GET",
    });
    mostrarMensaje("Producto habilitado/deshabilitado correctamente.");
    cargarProductos();
}

cargarProductos();

const form = document.getElementById("form-product");
const inputNombre = document.getElementById("nombre-producto");
const inputPrecio = document.getElementById("precio-producto");
const inputImagen = document.getElementById("imagen-producto");

// Captura del formulario para agregar un nuevo producto
form.addEventListener("submit", async (e) => {
    e.preventDefault();

    if (!inputNombre.value || !inputPrecio.value) {
        alert("Por favor, complete todos los campos.");
        return;
    }

    const formData = new FormData();
    formData.append("nombre", inputNombre.value);
    formData.append("precio", parseFloat(inputPrecio.value));
    formData.append("imagen", inputImagen.files[0]);

    const response = await fetch("/productos", {
        method: "POST",
        body: formData,
    });

    if (response.ok) {
        inputNombre.value = "";
        inputPrecio.value = "";
        inputImagen.value = "";
        mostrarMensaje("Producto agregado correctamente.");
        cargarProductos();
    } else {
        alert("Error al agregar el producto.");
    }
});

function mostrarMensaje(texto) {
    const alerta = document.createElement("div");
    alerta.textContent = texto;
    alerta.style.position = "fixed";
    alerta.style.top = "10px";
    alerta.style.right = "10px";
    alerta.style.zIndex = "1000";

    alerta.style.padding = "10px";
    alerta.style.margin = "10px 0";
    alerta.style.borderRadius = "5px";
    alerta.style.backgroundColor = "#e0ffe0";

    document.body.appendChild(alerta);
    setTimeout(() => {
        alerta.remove();
    }, 3000);
}

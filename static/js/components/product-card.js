import {
    eliminarProducto as eliminarProductoAPI,
    habilitarProducto as habilitarProductoAPI,
    obtenerComentarios,
} from "../api.js";

import { cargarProductos } from "../utils.js";

import { mostrarMensaje } from "../ui.js";

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
                    margin: 6px 0;
                    border-radius: 8px;
                    background-color: ${habilitado ? "#fff" : "#f8d7da"};
                    display: grid;
                    grid-template-columns: auto 1fr auto;
                    gap: 10px;
                    align-items: center;
                }

                img {
                    width: 60px;
                    height: 60px;
                    border-radius: 6px;
                    object-fit: cover;
                    background: #f3f4f6
                }

                .info {
                    display: flex;
                    flex-direction: column;
                    gap: 4px;
                }

                .price {
                    font-weight: bold;
                    color: #16a34a;
                }

                button {
                    background: #dc2626;
                    color: white;
                    border: none;
                    padding: 6px 10px;
                    border-radius: 4px;
                    cursor: pointer;
                    font-size: 0.8rem;
                }

                button:hover {
                    background: #b91c1c;
                }
                
                #btnHabilitar {
                    background: ${habilitado ? "gray" : "green"};
                }

                .comentarios {
                    grid-column: 1 / 4;
                    margin-top: 6px;
                    font-size: 0.8rem;
                    color: #374151;
                }

                .comentarios p {
                    margin: 2px 0;
                }

                .comentarios em {
                    color: #9ca3af;
                }
                 
                .id {
                    font-size: 0.7rem;
                    color: #6b7280;
                }
            </style>
            
                <div class="card">
                    <img src="${imagen}" alt="${nombre}" />
                    <div class="info">
                        <span><strong>${nombre}</strong></span>
                        <span class="price">Q${precio}</span>
                        <span class="id">ID: ${id}</span>
                    </div>
                    <div class="actions">
                        <button id="btnHabilitar">
                        ${habilitado ? "Deshabilitar" : "Habilitar"}
                        </button>
                        <button id="btnEliminar">Eliminar</button>
                    </div>
                    <div id="comentarios" class="comentarios">Cargando comentarios...</div>
                </div>
        `;

        // Cargar comentarios
        const comentariosDiv = this.shadowRoot.getElementById("comentarios");
        const comentarios = await obtenerComentarios(id);
        if (comentarios.length === 0) {
            comentariosDiv.innerHTML = "<em>No hay comentarios.</em>";
        } else {
            comentariosDiv.innerHTML =
                comentarios
                    .map((c) => `<p><strong>${c.usuario}</strong>: ${c.texto}</p>`)
                    .join("") + "</ul>";
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

async function eliminarProducto(id) {
    if (!confirm("¿Está seguro de que desea eliminar este producto?")) {
        return;
    }
    await eliminarProductoAPI(id);
    mostrarMensaje("Producto eliminado correctamente.");
    cargarProductos();
}

async function habilitarProducto(id) {
    await habilitarProductoAPI(id);
    mostrarMensaje("Producto habilitado/deshabilitado correctamente.");
    cargarProductos();
}

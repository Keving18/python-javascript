import os
from flask import Flask, jsonify, request, render_template
import json
from werkzeug.utils import secure_filename


# Creando una instancia de la aplicación Flask
app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "static/uploads"

if not os.path.exists(app.config["UPLOAD_FOLDER"]):
    os.makedirs(app.config["UPLOAD_FOLDER"])


# Definiendo una ruta para la raíz del sitio - Ruta Principal
@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")


# Ruta secundaria, automaticamente es un GET
# Lectura de productos desde un archivo JSON
@app.route("/productos", methods=["GET"])
def productos():
    with open("data.json", "r") as archivo:
        data = json.load(archivo)
    productos = data["productos"]
    return jsonify(productos)


# Ruta post para crear un nuevo producto
# Agregar un nuevo producto al archivo JSON
@app.route("/productos", methods=["POST"])
def agregar_producto():
    nombre = request.form.get("nombre")
    precio = request.form.get("precio")
    imagen = request.files.get("imagen")

    if not nombre or not precio or not imagen:
        return jsonify(message="Faltan datos del producto"), 400

    # Guardar la imagen subida
    filename = secure_filename(imagen.filename)
    ruta_imagen = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    imagen.save(ruta_imagen)

    # Asignar un ID único al nuevo producto y guardarlo
    with open("data.json", "r+") as archivo:
        data = json.load(archivo)
        id = max([p["id"] for p in data["productos"]], default=0) + 1
        nuevo = {
            "id": id,
            "nombre": nombre,
            "precio": float(precio),
            "imagen": ruta_imagen,
            "habilitado": True,
        }
        data["productos"].append(nuevo)
        archivo.seek(0)
        json.dump(data, archivo, indent=4)

    return jsonify(message="Producto agregado exitosamente", producto=nuevo), 201


# Eliminar un producto por ID
@app.route("/productos/<int:id>", methods=["DELETE"])
def eliminar_producto(id):
    with open("data.json", "r+") as archivo:
        data = json.load(archivo)
        productos = data["productos"]
        producto_a_eliminar = next((p for p in productos if p["id"] == id), None)

        if producto_a_eliminar:
            productos.remove(producto_a_eliminar)
            archivo.seek(0)
            archivo.truncate()
            json.dump(data, archivo, indent=4)
            return jsonify(message=f"Producto con ID {id} eliminado exitosamente"), 200
        else:
            return jsonify(message=f"Producto con ID {id} no encontrado"), 404


# Actualizar un producto por ID
@app.route("/productos/<int:id>", methods=["PUT"])
def actualizar_producto(id):
    data_actualizada = request.get_json()
    with open("data.json", "r+") as archivo:
        data = json.load(archivo)
        productos = data["productos"]
        producto_a_actualizar = next((p for p in productos if p["id"] == id), None)

        if producto_a_actualizar:
            producto_a_actualizar.update(data_actualizada)
            archivo.seek(0)
            archivo.truncate()
            json.dump(data, archivo, indent=4)
            return (
                jsonify(
                    message=f"Producto con ID {id} actualizado exitosamente",
                    producto=producto_a_actualizar,
                ),
                200,
            )
        else:
            return jsonify(message=f"Producto con ID {id} no encontrado"), 404


# Habilitar y deshabilitar productos
@app.route("/productos/<int:id>/habilitar", methods=["GET"])
def habilitar_producto(id):
    with open("data.json", "r+") as archivo:
        data = json.load(archivo)
        productos = data["productos"]
        producto_a_habilitar = next((p for p in productos if p["id"] == id), None)

        if producto_a_habilitar:
            producto_a_habilitar["habilitado"] = not producto_a_habilitar.get(
                "habilitado", True
            )
            archivo.seek(0)
            archivo.truncate()
            json.dump(data, archivo, indent=4)
            return (
                jsonify(
                    message=f"Producto con ID {id} {'habilitado' if producto_a_habilitar['habilitado'] else 'deshabilitado'} exitosamente"
                ),
                200,
            )
        else:
            return jsonify(message=f"Producto con ID {id} no encontrado"), 404


# Ruta de comentarios
@app.route("/productos/<int:id>/comentarios", methods=["GET"])
def obtener_comentarios(id):
    with open("data.json", "r") as archivo:
        data = json.load(archivo)
        producto = next((p for p in data["productos"] if p["id"] == id), None)

        if not producto:
            return jsonify(message=f"Producto con ID {id} no encontrado"), 404

        comentarios = producto.get("comentarios", [])
    return jsonify(comentarios)


# Ruta para agregar comentarios a un producto
@app.route("/productos/<int:id>/comentarios", methods=["POST"])
def agregar_comentario(id):
    nuevo_comentario = request.get_json()
    with open("data.json", "r+") as archivo:
        data = json.load(archivo)
        producto = next((p for p in data["productos"] if p["id"] == id), None)

        if not producto:
            return jsonify(message=f"Producto con ID {id} no encontrado"), 404

        if "comentarios" not in producto:
            producto["comentarios"] = []

        producto["comentarios"].append(nuevo_comentario)
        archivo.seek(0)
        archivo.truncate()
        json.dump(data, archivo, indent=4)

    return (
        jsonify(
            message="Comentario agregado exitosamente", comentario=nuevo_comentario
        ),
        201,
    )


if __name__ == "__main__":
    app.run(debug=False, port=5000, host="0.0.0.0")


# QUE ES UN CRUD
# CRUD significa Crear, Leer, Actualizar y Eliminar (Create, Read, Update, Delete).
# Son las cuatro operaciones básicas que se pueden realizar en una base de datos o sistema de almacenamiento de datos.

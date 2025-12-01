import os
import json
import sqlite3
from pathlib import Path
from functools import wraps

from flask import (
    Flask,
    jsonify,
    request,
    render_template,
    redirect,
    url_for,
    session,
    flash,
)
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash



# Configuración básica


BASE_DIR = Path(__file__).resolve().parent

app = Flask(__name__)

# Carpeta donde se guardan las imágenes de los productos
app.config["UPLOAD_FOLDER"] = "static/uploads"
os.makedirs(BASE_DIR / app.config["UPLOAD_FOLDER"], exist_ok=True)

# Clave para firmar las cookies de sesión
app.secret_key = "password_super_secreta" 

# Ruta del archivo de base de datos SQLite
DB_PATH = BASE_DIR / "users.db"
DATA_JSON_PATH = BASE_DIR / "data.json"



# Funciones de base de datos


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
   
    conn = get_db_connection()
    cur = conn.cursor()

    # Tabla de usuarios
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
    )

    # Tabla de productos
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            precio REAL NOT NULL,
            imagen TEXT,
            habilitado INTEGER NOT NULL DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
    )

    # Si la tabla de productos está vacía y existe data.json, importar productos
    cur.execute("SELECT COUNT(*) AS c FROM products;")
    count = cur.fetchone()[0]

    if count == 0 and DATA_JSON_PATH.exists():
        with DATA_JSON_PATH.open("r", encoding="utf-8") as f:
            data = json.load(f)

        for prod in data.get("productos", []):
            cur.execute(
                "INSERT OR IGNORE INTO products (id, nombre, precio, imagen, habilitado) VALUES (?, ?, ?, ?, ?);",
                (
                    prod.get("id"),
                    prod.get("nombre", ""),
                    float(prod.get("precio", 0)),
                    prod.get("imagen", ""),
                    1 if prod.get("habilitado", True) else 0,
                ),
            )

    conn.commit()
    conn.close()


init_db()



# Decorador para proteger rutas


def login_required(view_func):
    @wraps(view_func)
    def wrapped_view(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return view_func(*args, **kwargs)

    return wrapped_view



# Rutas de autenticación



@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        action = request.form.get("action")

        #LOGIN
        if action == "login":
            username = request.form.get("username_login", "").strip()
            password = request.form.get("password_login", "").strip()

            conn = get_db_connection()
            user = conn.execute(
                "SELECT * FROM users WHERE username = ?;",
                (username,),
            ).fetchone()
            conn.close()

            if user and check_password_hash(user["password_hash"], password):
                session["user_id"] = user["id"]
                session["username"] = user["username"]
                flash("Has iniciado sesión correctamente.", "success")
                return redirect(url_for("home"))

            flash("Usuario o contraseña incorrectos.", "danger")
            return render_template("login.html")

        #REGISTRO
        elif action == "register":
            username = request.form.get("username_reg", "").strip()
            email = request.form.get("email_reg", "").strip()
            password = request.form.get("password_reg", "").strip()
            confirm = request.form.get("confirm_reg", "").strip()

            #Validaciones básicas
            if not username or not email or not password:
                flash("Todos los campos son obligatorios.", "danger")
                return render_template("login.html")

            if password != confirm:
                flash("Las contraseñas no coinciden.", "danger")
                return render_template("login.html")

            if len(password) < 4:
                flash("La contraseña debe tener al menos 4 caracteres.", "warning")
                return render_template("login.html")

            password_hash = generate_password_hash(password)

            try:
                conn = get_db_connection()
                conn.execute(
                    "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?);",
                    (username, email, password_hash),
                )
                conn.commit()
                conn.close()
            except sqlite3.IntegrityError:
                flash("El usuario o el correo ya están registrados.", "danger")
                return render_template("login.html")

            flash("Registro exitoso. Ahora puedes iniciar sesión.", "success")
            return render_template("login.html")

    # GET -> solo se muestra el formulario
    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    session.clear()
    flash("Has cerrado sesión.", "info")
    return redirect(url_for("login"))



# Rutas principales



@app.route("/", methods=["GET"])
@login_required
def home():
    return render_template("index.html", user=session.get("username"))



# CRUD de productos (JSON + SQLite)
# Leer productos desde el archivo JSON
@app.route("/productos", methods=["GET"])
def productos():
    with DATA_JSON_PATH.open("r", encoding="utf-8") as archivo:
        data = json.load(archivo)
    productos = data.get("productos", [])
    return jsonify(productos)


# Crear un nuevo producto: se guarda en data.json y en la tabla products
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

    # Asignar un ID único al nuevo producto dentro del JSON
    with DATA_JSON_PATH.open("r+", encoding="utf-8") as archivo:
        data = json.load(archivo)
        productos = data.get("productos", [])
        new_id = max([p.get("id", 0) for p in productos], default=0) + 1
        nuevo = {
            "id": new_id,
            "nombre": nombre,
            "precio": float(precio),
            "imagen": ruta_imagen,
            "habilitado": True,
        }
        productos.append(nuevo)
        data["productos"] = productos
        archivo.seek(0)
        archivo.truncate()
        json.dump(data, archivo, indent=4, ensure_ascii=False)

    # También guardar el producto en la base de datos SQLite
    conn = get_db_connection()
    conn.execute(
        "INSERT INTO products (id, nombre, precio, imagen, habilitado) VALUES (?, ?, ?, ?, ?);",
        (new_id, nombre, float(precio), ruta_imagen, 1),
    )
    conn.commit()
    conn.close()

    return jsonify(message="Producto agregado exitosamente", producto=nuevo), 201


# Eliminar un producto por ID (JSON + DB)
@app.route("/productos/<int:id>", methods=["DELETE"])
def eliminar_producto(id):
    with DATA_JSON_PATH.open("r+", encoding="utf-8") as archivo:
        data = json.load(archivo)
        productos = data.get("productos", [])
        producto_a_eliminar = next((p for p in productos if p.get("id") == id), None)

        if producto_a_eliminar:
            productos.remove(producto_a_eliminar)
            data["productos"] = productos
            archivo.seek(0)
            archivo.truncate()
            json.dump(data, archivo, indent=4, ensure_ascii=False)

            # También eliminar de la base de datos
            conn = get_db_connection()
            conn.execute("DELETE FROM products WHERE id = ?;", (id,))
            conn.commit()
            conn.close()

            return jsonify(message=f"Producto con ID {id} eliminado exitosamente"), 200
        else:
            return jsonify(message=f"Producto con ID {id} no encontrado"), 404


# Actualizar un producto por ID (JSON + DB)
@app.route("/productos/<int:id>", methods=["PUT"])
def actualizar_producto(id):
    data_actualizada = request.get_json() or {}
    with DATA_JSON_PATH.open("r+", encoding="utf-8") as archivo:
        data = json.load(archivo)
        productos = data.get("productos", [])
        producto_a_actualizar = next((p for p in productos if p.get("id") == id), None)

        if producto_a_actualizar:
            producto_a_actualizar.update(data_actualizada)
            data["productos"] = productos
            archivo.seek(0)
            archivo.truncate()
            json.dump(data, archivo, indent=4, ensure_ascii=False)

            # Actualizar también en la base de datos
            conn = get_db_connection()
            conn.execute(
                "UPDATE products SET nombre = ?, precio = ?, imagen = ?, habilitado = ? WHERE id = ?;",
                (
                    producto_a_actualizar.get("nombre", ""),
                    float(producto_a_actualizar.get("precio", 0)),
                    producto_a_actualizar.get("imagen", ""),
                    1 if producto_a_actualizar.get("habilitado", True) else 0,
                    id,
                ),
            )
            conn.commit()
            conn.close()

            return (
                jsonify(
                    message=f"Producto con ID {id} actualizado exitosamente",
                    producto=producto_a_actualizar,
                ),
                200,
            )
        else:
            return jsonify(message=f"Producto con ID {id} no encontrado"), 404


# Habilitar y deshabilitar productos (JSON + DB)
@app.route("/productos/<int:id>/habilitar", methods=["GET"])
def habilitar_producto(id):
    with DATA_JSON_PATH.open("r+", encoding="utf-8") as archivo:
        data = json.load(archivo)
        productos = data.get("productos", [])
        producto_a_habilitar = next((p for p in productos if p.get("id") == id), None)

        if producto_a_habilitar:
            producto_a_habilitar["habilitado"] = not producto_a_habilitar.get(
                "habilitado", True
            )
            data["productos"] = productos
            archivo.seek(0)
            archivo.truncate()
            json.dump(data, archivo, indent=4, ensure_ascii=False)

            # Actualizar también en la base de datos
            conn = get_db_connection()
            conn.execute(
                "UPDATE products SET habilitado = ? WHERE id = ?;",
                (1 if producto_a_habilitar["habilitado"] else 0, id),
            )
            conn.commit()
            conn.close()

            estado = "habilitado" if producto_a_habilitar["habilitado"] else "deshabilitado"
            return (
                jsonify(
                    message=f"Producto con ID {id} {estado} exitosamente"
                ),
                200,
            )
        else:
            return jsonify(message=f"Producto con ID {id} no encontrado"), 404


# Rutas de comentarios (solo JSON)
@app.route("/productos/<int:id>/comentarios", methods=["GET"])
def obtener_comentarios(id):
    with DATA_JSON_PATH.open("r", encoding="utf-8") as archivo:
        data = json.load(archivo)
        producto = next((p for p in data.get("productos", []) if p.get("id") == id), None)

        if not producto:
            return jsonify(message=f"Producto con ID {id} no encontrado"), 404

        comentarios = producto.get("comentarios", [])
    return jsonify(comentarios)


@app.route("/productos/<int:id>/comentarios", methods=["POST"])
def agregar_comentario(id):
    nuevo_comentario = request.get_json() or {}
    with DATA_JSON_PATH.open("r+", encoding="utf-8") as archivo:
        data = json.load(archivo)
        productos = data.get("productos", [])
        producto = next((p for p in productos if p.get("id") == id), None)

        if not producto:
            return jsonify(message=f"Producto con ID {id} no encontrado"), 404

        if "comentarios" not in producto:
            producto["comentarios"] = []

        producto["comentarios"].append(nuevo_comentario)
        data["productos"] = productos
        archivo.seek(0)
        archivo.truncate()
        json.dump(data, archivo, indent=4, ensure_ascii=False)

    return (
        jsonify(
            message="Comentario agregado exitosamente", comentario=nuevo_comentario
        ),
        201,
    )


if __name__ == "__main__":
    app.run(debug=False, port=5000, host="0.0.0.0")

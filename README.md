# Proyecto final - Flask + JavaScript

## Descripcion

Aplicacion web dessarrollada durante el curso **Python con JavaScript: Desarrollo y Despliegue**. Permite gestionar productos, subir imagenes, agregar comentarios y desplegar en la nube con Render.

## Tecnologias

-   Flask (Python)
-   JavaScript
-   HTML + CSS
-   Git + GitHub
-   Render

## Rutas principales

| Metodo | Ruta         | Descripcion      |
| ------ | ------------ | ---------------- |
| GET    | `/productos` | Listar productos |

## Ejecución local

```bash
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux / macOS

pip install -r requirements.txt
python app.py
```

## Despligue

Link: [Aplicacion en Render](https://python-javascript-seccion-a.onrender.com/)

## Funcionalidades adicionales

### Autenticación de usuarios

Se implementó un sistema básico de autenticación utilizando **Flask**, **SQLite** y **sesiones**:

- Los usuarios se pueden registrar desde la ruta `/login` (sección *Registrarse*).
- Los datos se almacenan en la tabla `users` de la base de datos `users.db`:
  - `username` (único)
  - `email` (único)
  - `password_hash` (contraseña encriptada)
- Las contraseñas **no se guardan en texto plano**, se usa `werkzeug.security.generate_password_hash` y `check_password_hash`.
- Una vez autenticado, el usuario se guarda en la sesión (`session["user_id"]`, `session["username"]`).
- La ruta principal `/` está protegida con el decorador `@login_required`.
- La ruta `/logout` cierra la sesión y redirige al formulario de login.

### Persistencia de productos en SQLite

Además de almacenarse en el archivo `data.json`, todos los productos que se agregan desde el formulario se guardan también en la tabla `products` de la base de datos `users.db`:

Campos de la tabla `products`:

- `id` (PRIMARY KEY AUTOINCREMENT)
- `nombre`
- `precio`
- `imagen`
- `habilitado`
- `created_at`

Cada vez que se crea, actualiza, elimina o habilita/deshabilita un producto mediante las rutas `/productos`, `/productos/<id>`, y `/productos/<id>/habilitar`, los cambios se reflejan tanto en `data.json` como en la base de datos SQLite.

Al iniciar la aplicación, si la tabla `products` está vacía, los productos existentes en `data.json` se copian automáticamente a la base de datos para mantener la coherencia inicial.

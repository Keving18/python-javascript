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

## Estructura del proyecto

flask_javascript/
|
|------ app.py
|------ static
|------ js
|------ uploads
|------ templates
|------ data.json

## Despligue

Link: [https://python-javascript-seccion-a.onrender.com/](Aplicacion de Productos)

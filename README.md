# Proyecto Blog con FastAPI (Versión 2.0)

Proyecto de Blog web desarrollado en **FastAPI / Python** con arquitectura desacoplada en capas: **Controller**, **Entity**, **Form**, **Repository** y **Templates**.

---

## ✨ Nuevas Funcionalidades Implementadas

1. **Navegador Superior (Navbar)**:
   - **Inicio (`/`)**: Presenta un **Carrusel dinámico** con los posts que el administrador elija destacar, además de la cuadrícula de artículos recientes.
   - **Blog (`/blog`)**: Listado completo de todas las publicaciones con buscador en tiempo real.
   - **Contacto (`/contact`)**: Formulario con campos para **Nombre**, **Gmail / Correo**, **Asunto** y **Comentario**, con persistencia en base de datos.
   - **Autenticación en Navbar**:
     - Botones condicionales de **Iniciar Sesión** (`/login`) y **Registrarse** (`/register`).
     - Al iniciar sesión: menú de usuario con su nombre, acceso directo al **Panel Admin** (si es administrador) y botón de **Cerrar Sesión** (`/logout`).

2. **Panel de Administración (`/admin`)**:
   - Acceso restringido únicamente a usuarios con rol de Administrador.
   - **Gestión de Carrusel**: Permite añadir o quitar cualquier post del carrusel de inicio con un solo clic.
   - **Crear / Editar Posts**: Formulario con opción de URL de imagen y casilla para incluir el post en el carrusel.
   - **Eliminación Segura**: Modales de confirmación para eliminar posts.
   - **Bandeja de Mensajes de Contacto**: Visualización de los comentarios recibidos de los usuarios.

3. **Sistema de Usuarios y Sesiones**:
   - Registro de usuarios con validaciones de unicidad y formato.
   - Contraseñas protegidas mediante hash criptográfico **PBKDF2-SHA256**.
   - Gestión de sesiones seguras mediante cookies firmadas (`SessionMiddleware`).

---

## 🔑 Credenciales de Administrador por Defecto

El sistema siembra automáticamente una cuenta de administrador al iniciarse por primera vez:

* **Usuario:** `admin`
* **Contraseña:** `admin123`

*(Nota: Si te registras a través del formulario `/register` cuando no haya ningún usuario en el sistema, ese primer usuario recibirá automáticamente el rol de Administrador).*

---

## 📁 Estructura del Proyecto

```text
Proyecto-Blog/
├── app/
│   ├── controller/           # Controladores HTTP
│   │   ├── home_controller.py   # Inicio (carrusel) y Contacto
│   │   ├── post_controller.py   # Vistas públicas del Blog y comentarios
│   │   ├── auth_controller.py   # Login, Registro y Logout
│   │   └── admin_controller.py  # Panel Admin, gestión de carrusel y posts
│   ├── entity/               # Entidades ORM (SQLAlchemy)
│   │   ├── post.py              # Incluye campo in_carousel e image_url
│   │   ├── comment.py           # Comentarios de posts
│   │   ├── user.py              # Usuarios y rol admin
│   │   └── contact_message.py   # Mensajes del formulario de contacto
│   ├── form/                 # Formularios y validaciones
│   │   ├── auth_form.py         # LoginForm y RegisterForm
│   │   ├── contact_form.py      # ContactForm (Nombre, Gmail, Asunto, Comentario)
│   │   ├── post_form.py         # PostCreateForm y PostEditForm
│   │   └── comment_form.py      # CommentCreateForm
│   ├── repository/           # Patrón Repositorio
│   │   ├── base_repository.py
│   │   ├── post_repository.py   # Consultas de carrusel y búsqueda
│   │   ├── comment_repository.py
│   │   ├── user_repository.py
│   │   └── contact_repository.py
│   ├── templates/            # Plantillas Jinja2 y Bootstrap 5
│   │   ├── base.html            # Navbar con Inicio, Blog, Contacto, Admin y Login
│   │   ├── home/index.html      # Carrusel de inicio y posts destacados
│   │   ├── contact/index.html   # Formulario de contacto
│   │   ├── auth/                # Vistas de login y registro
│   │   ├── admin/               # Dashboard, creación con carrusel y mensajes
│   │   └── posts/               # Listado del blog y vista detallada
│   ├── static/               # CSS personalizado y JavaScript
│   ├── database.py           # Conexión SQLite y sesiones
│   └── security.py           # Hashing de contraseñas y control de acceso
├── tests/
│   └── test_blog.py          # Pruebas automatizadas completas
├── main.py                   # Servidor FastAPI y middleware de sesiones
├── requirements.txt
└── README.md
```

---

## 🚀 Puesta en Marcha

1. **Activar el entorno virtual**:
   ```bash
   source .venv/bin/activate
   ```

2. **Iniciar el servidor**:
   ```bash
   uvicorn main:app --reload
   ```
   *(o ejecutando `python main.py`)*

3. **Abrir en el navegador**:
   * **Inicio con Carrusel:** [http://localhost:8000](http://localhost:8000)
   * **Blog:** [http://localhost:8000/blog](http://localhost:8000/blog)
   * **Contacto:** [http://localhost:8000/contact](http://localhost:8000/contact)
   * **Login:** [http://localhost:8000/login](http://localhost:8000/login)
   * **Panel Admin:** [http://localhost:8000/admin](http://localhost:8000/admin)

4. **Ejecutar Pruebas Automatizadas**:
   ```bash
   pytest
   ```

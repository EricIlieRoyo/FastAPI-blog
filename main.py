import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from app.database import engine, Base
from app.controller import home_router, post_router, auth_router, admin_router

# Crear tablas en la base de datos
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="FastAPI Blog Project",
    description="Blog con Carrusel de Inicio, Panel Admin, Autenticación y Formulario de Contacto",
    version="2.0.0"
)

# Middleware para sesiones de usuario (cookies seguras y firmadas)
app.add_middleware(
    SessionMiddleware,
    secret_key="fastapi-blog-super-secret-key-2026",
    session_cookie="blog_session",
    max_age=86400 * 7  # 7 días
)

# Montar archivos estáticos
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Registrar controladores
app.include_router(home_router)
app.include_router(post_router)
app.include_router(auth_router)
app.include_router(admin_router)


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

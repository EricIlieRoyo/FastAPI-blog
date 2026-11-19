import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from main import app
from app.database import Base, get_db
from app.entity.user import User
from app.security import hash_password

# Base de datos en memoria para pruebas
TEST_DATABASE_URL = "sqlite:///:memory:"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

# Crear tablas en la base de datos de test
Base.metadata.create_all(bind=test_engine)

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_test_data():
    """Reinicia la base de datos en memoria antes de cada prueba."""
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)

    # Crear admin de prueba en memoria
    db = TestingSessionLocal()
    test_admin = User(
        username="admin_test",
        email="admintest@blog.com",
        password_hash=hash_password("adminpass123"),
        is_admin=True
    )
    db.add(test_admin)
    db.commit()
    db.close()


def test_home_page_empty():
    response = client.get("/")
    assert response.status_code == 200
    assert "Últimos Artículos del Blog" in response.text
    assert "No hay publicaciones seleccionadas en el carrusel" in response.text


def test_blog_list_page():
    response = client.get("/blog")
    assert response.status_code == 200
    assert "Todos los Artículos" in response.text


def test_contact_form_flow():
    # 1. Ver formulario de contacto
    get_res = client.get("/contact")
    assert get_res.status_code == 200
    assert "Formulario de Contacto" in get_res.text

    # 2. Validación de errores (campos vacíos)
    err_res = client.post("/contact", data={"name": "", "email": "", "subject": "", "message": ""})
    assert err_res.status_code == 422
    assert "El nombre es obligatorio" in err_res.text

    # 3. Envío exitoso
    success_res = client.post("/contact", data={
        "name": "Juan Perez",
        "email": "juan.perez@gmail.com",
        "subject": "Felicitaciones por el blog",
        "message": "Me ha encantado el carrusel y la estructura del proyecto."
    })
    assert success_res.status_code == 200
    assert "¡Mensaje enviado con éxito!" in success_res.text


def test_auth_and_admin_flow():
    session_client = TestClient(app)

    # 1. Intentar acceder a admin sin loguearse -> Redirige a /login
    unauth_res = session_client.get("/admin", follow_redirects=False)
    assert unauth_res.status_code in [302, 303]
    assert "/login" in unauth_res.headers["location"]

    # 2. Login con usuario admin
    login_res = session_client.post(
        "/login",
        data={"username": "admin_test", "password": "adminpass123"},
        follow_redirects=False
    )
    assert login_res.status_code == 303
    assert login_res.headers["location"] == "/admin"

    # 3. Acceder al dashboard de administración logueado
    admin_res = session_client.get("/admin")
    assert admin_res.status_code == 200
    assert "Panel de Administración" in admin_res.text

    # 4. Crear un post desde el admin y marcarlo para el carrusel
    new_post_data = {
        "title": "Post Creado para Carrusel",
        "author": "admin_test",
        "image_url": "https://images.unsplash.com/photo-1518770660439-4636190af475",
        "in_carousel": "true",
        "content": "Este es un post creado directamente desde el formulario del panel de admin."
    }
    create_res = session_client.post("/admin/posts/new", data=new_post_data, follow_redirects=False)
    assert create_res.status_code == 303

    # Verificar que aparece en el carrusel del home
    home_check = session_client.get("/")
    assert "Post Creado para Carrusel" in home_check.text

    # 5. Logout
    logout_res = session_client.get("/logout", follow_redirects=False)
    assert logout_res.status_code in [302, 303]


def test_user_registration_flow():
    reg_client = TestClient(app)

    # Registro de nuevo usuario normal
    reg_data = {
        "username": "usuario_lector",
        "email": "lector@gmail.com",
        "password": "password123",
        "confirm_password": "password123"
    }
    res = reg_client.post("/register", data=reg_data, follow_redirects=False)
    assert res.status_code == 303

    # Usuario normal intenta entrar a /admin -> 403 Forbidden
    forbidden_res = reg_client.get("/admin")
    assert forbidden_res.status_code == 403

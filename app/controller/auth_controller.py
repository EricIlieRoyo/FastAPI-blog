from fastapi import APIRouter, Request, Depends, Form, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.entity.user import User
from app.repository.user_repository import UserRepository
from app.form.auth_form import LoginForm, RegisterForm
from app.security import hash_password, verify_password, get_current_user

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/login")
def login_page(
    request: Request,
    db: Session = Depends(get_db)
):
    """Muestra la vista de inicio de sesión."""
    current_user = get_current_user(request, db)
    if current_user:
        return RedirectResponse(
            url="/admin" if current_user.is_admin else "/",
            status_code=status.HTTP_302_FOUND
        )

    return templates.TemplateResponse(
        request=request,
        name="auth/login.html",
        context={"form": None, "current_user": None}
    )


@router.post("/login")
def login_submit(
    request: Request,
    username: str = Form(""),
    password: str = Form(""),
    db: Session = Depends(get_db)
):
    """Procesa el inicio de sesión del usuario."""
    form = LoginForm(username=username, password=password)
    user_repo = UserRepository(db)

    if not form.validate():
        return templates.TemplateResponse(
            request=request,
            name="auth/login.html",
            context={"form": form, "current_user": None},
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT
        )

    user = user_repo.get_by_username(form.username)
    if not user or not verify_password(form.password, user.password_hash):
        form.add_error("Usuario o contraseña incorrectos.")
        return templates.TemplateResponse(
            request=request,
            name="auth/login.html",
            context={"form": form, "current_user": None},
            status_code=status.HTTP_401_UNAUTHORIZED
        )

    # Iniciar sesión guardando en session cookie
    request.session["user_id"] = user.id

    # Si es admin, redirige al panel de administración; si no, al inicio
    redirect_to = "/admin" if user.is_admin else "/"
    return RedirectResponse(url=redirect_to, status_code=status.HTTP_303_SEE_OTHER)


@router.get("/register")
def register_page(
    request: Request,
    db: Session = Depends(get_db)
):
    """Muestra el formulario de registro de usuario."""
    current_user = get_current_user(request, db)
    if current_user:
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)

    return templates.TemplateResponse(
        request=request,
        name="auth/register.html",
        context={"form": None, "current_user": None}
    )


@router.post("/register")
def register_submit(
    request: Request,
    username: str = Form(""),
    email: str = Form(""),
    password: str = Form(""),
    confirm_password: str = Form(""),
    db: Session = Depends(get_db)
):
    """Procesa el registro de un nuevo usuario."""
    form = RegisterForm(
        username=username,
        email=email,
        password=password,
        confirm_password=confirm_password
    )
    user_repo = UserRepository(db)

    if not form.validate():
        return templates.TemplateResponse(
            request=request,
            name="auth/register.html",
            context={"form": form, "current_user": None},
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT
        )

    # Verificar si el nombre de usuario o email ya existen
    if user_repo.get_by_username(form.username):
        form.add_error("El nombre de usuario ya está registrado.")
    if user_repo.get_by_email(form.email):
        form.add_error("El correo electrónico ya está registrado.")

    if not form.is_valid:
        return templates.TemplateResponse(
            request=request,
            name="auth/register.html",
            context={"form": form, "current_user": None},
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT
        )

    # Si es el primer usuario del sistema, se convierte automáticamente en Administrador
    is_first_user = user_repo.count_users() == 0

    new_user = User(
        username=form.username,
        email=form.email,
        password_hash=hash_password(form.password),
        is_admin=is_first_user
    )
    created_user = user_repo.create(new_user)

    # Iniciar sesión automáticamente
    request.session["user_id"] = created_user.id

    redirect_to = "/admin" if created_user.is_admin else "/"
    return RedirectResponse(url=redirect_to, status_code=status.HTTP_303_SEE_OTHER)


@router.get("/logout")
def logout(request: Request):
    """Cierra la sesión del usuario actual."""
    request.session.clear()
    return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)

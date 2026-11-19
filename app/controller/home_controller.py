from fastapi import APIRouter, Request, Depends, Form, status
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.repository.post_repository import PostRepository
from app.repository.contact_repository import ContactRepository
from app.form.contact_form import ContactForm
from app.security import get_current_user

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/")
def home_page(
    request: Request,
    db: Session = Depends(get_db)
):
    """Página de inicio con carrusel de posts seleccionados y artículos recientes."""
    post_repo = PostRepository(db)
    carousel_posts = post_repo.get_carousel_posts(limit=5)
    recent_posts = post_repo.get_all_ordered(limit=6)
    current_user = get_current_user(request, db)

    return templates.TemplateResponse(
        request=request,
        name="home/index.html",
        context={
            "carousel_posts": carousel_posts,
            "recent_posts": recent_posts,
            "current_user": current_user
        }
    )


@router.get("/contact")
def contact_page(
    request: Request,
    db: Session = Depends(get_db)
):
    """Muestra el formulario de contacto."""
    current_user = get_current_user(request, db)
    return templates.TemplateResponse(
        request=request,
        name="contact/index.html",
        context={
            "form": None,
            "success": False,
            "current_user": current_user
        }
    )


@router.post("/contact")
def submit_contact(
    request: Request,
    name: str = Form(""),
    email: str = Form(""),
    subject: str = Form(""),
    message: str = Form(""),
    db: Session = Depends(get_db)
):
    """Procesa y guarda los mensajes del formulario de contacto."""
    form = ContactForm(name=name, email=email, subject=subject, message=message)
    current_user = get_current_user(request, db)

    if not form.validate():
        return templates.TemplateResponse(
            request=request,
            name="contact/index.html",
            context={
                "form": form,
                "success": False,
                "current_user": current_user
            },
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT
        )

    contact_repo = ContactRepository(db)
    from app.entity.contact_message import ContactMessage
    new_message = ContactMessage(
        name=form.name,
        email=form.email,
        subject=form.subject,
        message=form.message
    )
    contact_repo.create(new_message)

    return templates.TemplateResponse(
        request=request,
        name="contact/index.html",
        context={
            "form": None,
            "success": True,
            "current_user": current_user
        }
    )

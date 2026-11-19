import time
from fastapi import APIRouter, Request, Depends, Form, status, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.entity.post import Post
from app.repository.post_repository import PostRepository
from app.repository.contact_repository import ContactRepository
from app.form.post_form import PostCreateForm, PostEditForm
from app.security import get_current_user

router = APIRouter(prefix="/admin")
templates = Jinja2Templates(directory="app/templates")


def verify_admin_access(request: Request, db: Session):
    """Verifica que el usuario actual exista y sea administrador."""
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado: Se requieren permisos de Administrador."
        )
    return user


@router.get("")
@router.get("/")
def admin_dashboard(
    request: Request,
    db: Session = Depends(get_db)
):
    """Panel principal de administración: estadísticas, posts y mensajes."""
    auth_check = verify_admin_access(request, db)
    if isinstance(auth_check, RedirectResponse):
        return auth_check

    current_user = auth_check
    post_repo = PostRepository(db)
    contact_repo = ContactRepository(db)

    posts = post_repo.get_all_ordered(limit=100)
    carousel_posts = post_repo.get_carousel_posts(limit=10)
    contact_messages = contact_repo.get_all_ordered(limit=10)

    return templates.TemplateResponse(
        request=request,
        name="admin/index.html",
        context={
            "current_user": current_user,
            "posts": posts,
            "carousel_count": len(carousel_posts),
            "total_posts": len(posts),
            "contact_messages": contact_messages
        }
    )


@router.get("/posts/new")
def admin_new_post_page(
    request: Request,
    db: Session = Depends(get_db)
):
    """Formulario del administrador para crear un post."""
    auth_check = verify_admin_access(request, db)
    if isinstance(auth_check, RedirectResponse):
        return auth_check

    return templates.TemplateResponse(
        request=request,
        name="admin/post_form.html",
        context={
            "current_user": auth_check,
            "form": None,
            "is_edit": False
        }
    )


@router.post("/posts/new")
def admin_create_post(
    request: Request,
    title: str = Form(""),
    content: str = Form(""),
    author: str = Form(""),
    image_url: str = Form(""),
    in_carousel: bool = Form(False),
    db: Session = Depends(get_db)
):
    """Guarda un nuevo post desde el panel de administración."""
    auth_check = verify_admin_access(request, db)
    if isinstance(auth_check, RedirectResponse):
        return auth_check

    current_user = auth_check
    author_name = author.strip() or current_user.username

    form = PostCreateForm(
        title=title,
        author=author_name,
        content=content,
        image_url=image_url,
        in_carousel=in_carousel
    )
    post_repo = PostRepository(db)

    if not form.validate():
        return templates.TemplateResponse(
            request=request,
            name="admin/post_form.html",
            context={
                "current_user": current_user,
                "form": form,
                "is_edit": False
            },
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT
        )

    # Evitar slugs duplicados
    if post_repo.get_by_slug(form.slug):
        form.slug = f"{form.slug}-{int(time.time())}"

    new_post = Post(
        title=form.title,
        slug=form.slug,
        author=form.author,
        content=form.content,
        image_url=form.image_url,
        in_carousel=form.in_carousel
    )
    post_repo.create(new_post)

    return RedirectResponse(url="/admin", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/posts/{post_id}/edit")
def admin_edit_post_page(
    request: Request,
    post_id: int,
    db: Session = Depends(get_db)
):
    """Formulario para editar un post desde el panel de administración."""
    auth_check = verify_admin_access(request, db)
    if isinstance(auth_check, RedirectResponse):
        return auth_check

    post_repo = PostRepository(db)
    post = post_repo.get_by_id(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post no encontrado.")

    return templates.TemplateResponse(
        request=request,
        name="admin/post_form.html",
        context={
            "current_user": auth_check,
            "post": post,
            "form": None,
            "is_edit": True
        }
    )


@router.post("/posts/{post_id}/edit")
def admin_update_post(
    request: Request,
    post_id: int,
    title: str = Form(""),
    author: str = Form(""),
    content: str = Form(""),
    image_url: str = Form(""),
    in_carousel: bool = Form(False),
    db: Session = Depends(get_db)
):
    """Actualiza un post existente."""
    auth_check = verify_admin_access(request, db)
    if isinstance(auth_check, RedirectResponse):
        return auth_check

    post_repo = PostRepository(db)
    post = post_repo.get_by_id(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post no encontrado.")

    form = PostEditForm(
        title=title,
        author=author,
        content=content,
        image_url=image_url,
        in_carousel=in_carousel
    )

    if not form.validate():
        return templates.TemplateResponse(
            request=request,
            name="admin/post_form.html",
            context={
                "current_user": auth_check,
                "post": post,
                "form": form,
                "is_edit": True
            },
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT
        )

    post.title = form.title
    post.author = form.author
    post.content = form.content
    post.image_url = form.image_url
    post.in_carousel = form.in_carousel
    post_repo.update(post)

    return RedirectResponse(url="/admin", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/posts/{post_id}/toggle-carousel")
def admin_toggle_carousel(
    request: Request,
    post_id: int,
    db: Session = Depends(get_db)
):
    """Alterna la visibilidad del post en el carrusel del inicio."""
    auth_check = verify_admin_access(request, db)
    if isinstance(auth_check, RedirectResponse):
        return auth_check

    post_repo = PostRepository(db)
    post_repo.toggle_carousel(post_id)

    return RedirectResponse(url="/admin", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/posts/{post_id}/delete")
def admin_delete_post(
    request: Request,
    post_id: int,
    db: Session = Depends(get_db)
):
    """Elimina un post desde el panel de administración."""
    auth_check = verify_admin_access(request, db)
    if isinstance(auth_check, RedirectResponse):
        return auth_check

    post_repo = PostRepository(db)
    post_repo.delete(post_id)

    return RedirectResponse(url="/admin", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/messages")
def admin_messages_page(
    request: Request,
    db: Session = Depends(get_db)
):
    """Listado completo de mensajes recibidos por contacto."""
    auth_check = verify_admin_access(request, db)
    if isinstance(auth_check, RedirectResponse):
        return auth_check

    contact_repo = ContactRepository(db)
    messages = contact_repo.get_all_ordered(limit=200)

    return templates.TemplateResponse(
        request=request,
        name="admin/messages.html",
        context={
            "current_user": auth_check,
            "messages": messages
        }
    )

from typing import Optional
from fastapi import APIRouter, Depends, Request, Form, status, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.entity.comment import Comment
from app.repository.post_repository import PostRepository
from app.repository.comment_repository import CommentRepository
from app.form.comment_form import CommentCreateForm
from app.security import get_current_user

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/blog")
def blog_list(
    request: Request,
    q: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Listado de todos los artículos publicados en el blog con buscador."""
    post_repo = PostRepository(db)
    current_user = get_current_user(request, db)

    if q and q.strip():
        posts = post_repo.search(q.strip())
    else:
        posts = post_repo.get_all_ordered()

    return templates.TemplateResponse(
        request=request,
        name="posts/list.html",
        context={
            "posts": posts,
            "search_query": q,
            "current_user": current_user
        }
    )


@router.get("/posts")
def posts_redirect():
    """Redirige /posts a /blog para consistencia con el menú superior."""
    return RedirectResponse(url="/blog", status_code=status.HTTP_302_FOUND)


@router.get("/posts/new")
def new_post_redirect(request: Request, db: Session = Depends(get_db)):
    """Redirige la creación de posts al panel de administración."""
    user = get_current_user(request, db)
    if user and user.is_admin:
        return RedirectResponse(url="/admin/posts/new", status_code=status.HTTP_302_FOUND)
    return RedirectResponse(url="/login?next=/admin/posts/new", status_code=status.HTTP_302_FOUND)


@router.get("/posts/{post_id}")
def post_detail(
    request: Request,
    post_id: int,
    db: Session = Depends(get_db)
):
    """Muestra el detalle del artículo, comentarios y formulario para comentar."""
    post_repo = PostRepository(db)
    post = post_repo.get_by_id(post_id)
    current_user = get_current_user(request, db)

    if not post:
        raise HTTPException(status_code=404, detail="Artículo no encontrado")

    return templates.TemplateResponse(
        request=request,
        name="posts/detail.html",
        context={
            "post": post,
            "comment_form": None,
            "current_user": current_user
        }
    )


@router.post("/posts/{post_id}/comments")
def add_comment(
    request: Request,
    post_id: int,
    author_name: str = Form(""),
    content: str = Form(""),
    db: Session = Depends(get_db)
):
    """Valida y añade un comentario al artículo."""
    post_repo = PostRepository(db)
    post = post_repo.get_by_id(post_id)
    current_user = get_current_user(request, db)

    if not post:
        raise HTTPException(status_code=404, detail="Artículo no encontrado")

    # Si el usuario está autenticado y no envió nombre, usar su username
    resolved_author = author_name.strip()
    if not resolved_author and current_user:
        resolved_author = current_user.username

    comment_form = CommentCreateForm(author_name=resolved_author, content=content)

    if not comment_form.validate():
        return templates.TemplateResponse(
            request=request,
            name="posts/detail.html",
            context={
                "post": post,
                "comment_form": comment_form,
                "current_user": current_user
            },
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT
        )

    comment_repo = CommentRepository(db)
    new_comment = Comment(
        post_id=post.id,
        author_name=comment_form.author_name,
        content=comment_form.content
    )
    comment_repo.create(new_comment)

    return RedirectResponse(
        url=f"/posts/{post.id}#comments",
        status_code=status.HTTP_303_SEE_OTHER
    )

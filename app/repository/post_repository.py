from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc, or_
from app.entity.post import Post
from app.repository.base_repository import BaseRepository


class PostRepository(BaseRepository[Post]):
    def __init__(self, db: Session):
        super().__init__(Post, db)

    def get_by_slug(self, slug: str) -> Optional[Post]:
        """Busca una publicación por su slug único."""
        return self.db.query(Post).filter(Post.slug == slug).first()

    def get_all_ordered(self, skip: int = 0, limit: int = 50) -> List[Post]:
        """Obtiene las publicaciones ordenadas de más reciente a más antigua."""
        return (
            self.db.query(Post)
            .order_by(desc(Post.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_carousel_posts(self, limit: int = 5) -> List[Post]:
        """Obtiene las publicaciones marcadas para el carrusel de inicio."""
        return (
            self.db.query(Post)
            .filter(Post.in_carousel == True)
            .order_by(desc(Post.created_at))
            .limit(limit)
            .all()
        )

    def toggle_carousel(self, post_id: int) -> bool:
        """Alterna el estado de inclusión en el carrusel de una publicación."""
        post = self.get_by_id(post_id)
        if post:
            post.in_carousel = not post.in_carousel
            self.db.commit()
            self.db.refresh(post)
            return True
        return False

    def search(self, query: str) -> List[Post]:
        """Busca publicaciones por coincidencia en título, contenido o autor."""
        term = f"%{query}%"
        return (
            self.db.query(Post)
            .filter(
                or_(
                    Post.title.ilike(term),
                    Post.content.ilike(term),
                    Post.author.ilike(term),
                )
            )
            .order_by(desc(Post.created_at))
            .all()
        )

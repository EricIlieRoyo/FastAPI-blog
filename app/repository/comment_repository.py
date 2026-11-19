from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.entity.comment import Comment
from app.repository.base_repository import BaseRepository


class CommentRepository(BaseRepository[Comment]):
    def __init__(self, db: Session):
        super().__init__(Comment, db)

    def get_by_post(self, post_id: int) -> List[Comment]:
        """Obtiene todos los comentarios asociados a un post específico."""
        return (
            self.db.query(Comment)
            .filter(Comment.post_id == post_id)
            .order_by(desc(Comment.created_at))
            .all()
        )

from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.entity.contact_message import ContactMessage
from app.repository.base_repository import BaseRepository


class ContactRepository(BaseRepository[ContactMessage]):
    def __init__(self, db: Session):
        super().__init__(ContactMessage, db)

    def get_all_ordered(self, limit: int = 100) -> List[ContactMessage]:
        return (
            self.db.query(ContactMessage)
            .order_by(desc(ContactMessage.created_at))
            .limit(limit)
            .all()
        )

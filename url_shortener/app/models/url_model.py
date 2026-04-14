from sqlalchemy import Column, String, Integer, DateTime, Boolean
from sqlalchemy.sql import func
from datetime import datetime
from app.database import Base


class ShortURL(Base):
    __tablename__ = "short_urls"

    id           = Column(Integer, primary_key=True, index=True)
    slug         = Column(String(20), unique=True, index=True, nullable=False)
    original_url = Column(String(2048), nullable=False)
    clicks       = Column(Integer, default=0, nullable=False)
    expires_at   = Column(DateTime, nullable=True)
    created_at   = Column(DateTime, default=func.now(), nullable=False)
    is_active    = Column(Boolean, default=True, nullable=False)

    def is_expired(self) -> bool:
        if not self.expires_at:
            return False
        return datetime.utcnow() > self.expires_at

    def to_dict(self):
        return {
            "id": self.id,
            "slug": self.slug,
            "original_url": self.original_url,
            "clicks": self.clicks,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "is_active": self.is_active,
        }

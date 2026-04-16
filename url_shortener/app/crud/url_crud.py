from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from typing import Optional, List
import secrets
import string

from app.models.url_model import ShortURL
from app.schemas.url_schema import URLCreate

SLUG_CHARS = string.ascii_lowercase + string.digits
EXPIRY_MAP = {
    "1d":  timedelta(days=1),
    "7d":  timedelta(days=7),
    "30d": timedelta(days=30),
}


def _generate_slug(length: int = 6) -> str:
    return "".join(secrets.choice(SLUG_CHARS) for _ in range(length))


def get_by_slug(db: Session, slug: str) -> Optional[ShortURL]:
    return db.query(ShortURL).filter(
        ShortURL.slug == slug,
        ShortURL.is_active == True,
    ).first()


def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[ShortURL]:
    return (
        db.query(ShortURL)
        .filter(ShortURL.is_active == True)
        .order_by(ShortURL.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def create_url(db: Session, data: URLCreate) -> ShortURL:
    
    if data.custom_slug:
        slug = data.custom_slug
    else:
        
        for _ in range(5):
            slug = _generate_slug()
            if not get_by_slug(db, slug):
                break

    
    expires_at = None
    if data.expires_in and data.expires_in in EXPIRY_MAP:
        expires_at = datetime.utcnow() + EXPIRY_MAP[data.expires_in]

    url = ShortURL(
        slug=slug,
        original_url=data.original_url,
        expires_at=expires_at,
    )
    db.add(url)
    db.commit()
    db.refresh(url)
    return url


def increment_clicks(db: Session, slug: str) -> Optional[ShortURL]:
    url = get_by_slug(db, slug)
    if url:
        url.clicks += 1
        db.commit()
        db.refresh(url)
    return url


def delete_by_slug(db: Session, slug: str) -> bool:
    url = get_by_slug(db, slug)
    if not url:
        return False
    url.is_active = False
    db.commit()
    return True


def get_stats(db: Session) -> dict:
    total = db.query(func.count(ShortURL.id)).filter(ShortURL.is_active == True).scalar() or 0
    total_clicks = db.query(func.sum(ShortURL.clicks)).filter(ShortURL.is_active == True).scalar() or 0
    top_clicks = db.query(func.max(ShortURL.clicks)).filter(ShortURL.is_active == True).scalar() or 0
    permanent = db.query(func.count(ShortURL.id)).filter(
        ShortURL.is_active == True,
        ShortURL.expires_at == None,
    ).scalar() or 0
    return {
        "total_urls": total,
        "total_clicks": int(total_clicks),
        "top_clicks": int(top_clicks),
        "permanent_urls": permanent,
    }

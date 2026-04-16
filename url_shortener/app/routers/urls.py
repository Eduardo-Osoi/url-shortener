from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.schemas.url_schema import URLCreate, URLOut, URLStats
import app.crud as crud

router = APIRouter()

BASE_URL = "http://localhost:8000"


def _enrich(url, request: Request = None) -> dict:
    """Add short_url field to the URL object."""
    base = str(request.base_url).rstrip("/") if request else BASE_URL
    d = url.to_dict()
    d["short_url"] = f"{base}/r/{url.slug}"
    return d


@router.post("/urls", status_code=201)
async def create_short_url(
    body: URLCreate,
    request: Request,
    db: Session = Depends(get_db),
):
    
    if body.custom_slug:
        existing = crud.get_by_slug(db, body.custom_slug)
        if existing:
            raise HTTPException(status_code=409, detail=f"El slug '{body.custom_slug}' ya está en uso")

    url = crud.create_url(db, body)
    return _enrich(url, request)


@router.get("/urls", response_model=List[dict])
async def list_urls(
    request: Request,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    urls = crud.get_all(db, skip=skip, limit=limit)
    return [_enrich(u, request) for u in urls]


@router.get("/urls/stats")
async def get_stats(db: Session = Depends(get_db)):
    return crud.get_stats(db)


@router.get("/urls/{slug}")
async def get_url_info(
    slug: str,
    request: Request,
    db: Session = Depends(get_db),
):
    url = crud.get_by_slug(db, slug)
    if not url:
        raise HTTPException(status_code=404, detail="URL no encontrada")
    return _enrich(url, request)


@router.delete("/urls/{slug}", status_code=204)
async def delete_url(slug: str, db: Session = Depends(get_db)):
    deleted = crud.delete_by_slug(db, slug)
    if not deleted:
        raise HTTPException(status_code=404, detail="URL no encontrada")


# Redirect route — outside /api/v1 prefix
@router.get("/redirect/{slug}")
async def redirect_to_original(slug: str, db: Session = Depends(get_db)):
    url = crud.get_by_slug(db, slug)
    if not url:
        raise HTTPException(status_code=404, detail="URL no encontrada o expirada")
    if url.is_expired():
        raise HTTPException(status_code=410, detail="Esta URL ha expirado")
    crud.increment_clicks(db, slug)
    return RedirectResponse(url=url.original_url, status_code=301)

from fastapi import FastAPI, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from sqlalchemy.orm import Session
import os

from app.database import engine, Base, get_db
from app.routers import urls
import app.crud as crud


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="URL Shortener",
    description="Acortador de URLs con FastAPI + SQLite",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(urls.router, prefix="/api/v1")


@app.get("/r/{slug}")
async def redirect_short(slug: str, db: Session = Depends(get_db)):
    url = crud.get_by_slug(db, slug)
    if not url:
        raise HTTPException(status_code=404, detail="URL no encontrada")
    if url.is_expired():
        raise HTTPException(status_code=410, detail="URL expirada")
    crud.increment_clicks(db, slug)
    return RedirectResponse(url=url.original_url, status_code=301)


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
static_dir = os.path.normpath(os.path.join(BASE_DIR, "..", "static"))

app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/", response_class=HTMLResponse)
async def root():
    with open(os.path.join(static_dir, "index.html"), "r", encoding="utf-8") as f:
        return f.read()


@app.get("/health")
async def health():
    return {"status": "ok", "version": "1.0.0"}

"""
Tests para el Acortador de URLs.
Ejecutar con: pytest tests/ -v
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db

# Use in-memory SQLite for tests
TEST_DB = "sqlite:///:memory:"
engine_test = create_engine(TEST_DB, connect_args={"check_same_thread": False})
TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine_test)


def override_get_db():
    db = TestingSession()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
Base.metadata.create_all(bind=engine_test)

client = TestClient(app)


# ── CREATE ─────────────────────────────────────────────────────────────

def test_create_url_auto_slug():
    res = client.post("/api/v1/urls", json={"original_url": "https://example.com"})
    assert res.status_code == 201
    data = res.json()
    assert "slug" in data
    assert len(data["slug"]) == 6
    assert data["original_url"] == "https://example.com"
    assert data["clicks"] == 0


def test_create_url_custom_slug():
    res = client.post("/api/v1/urls", json={
        "original_url": "https://python.org",
        "custom_slug": "python-docs",
    })
    assert res.status_code == 201
    assert res.json()["slug"] == "python-docs"


def test_create_url_duplicate_slug():
    client.post("/api/v1/urls", json={"original_url": "https://a.com", "custom_slug": "dupe"})
    res = client.post("/api/v1/urls", json={"original_url": "https://b.com", "custom_slug": "dupe"})
    assert res.status_code == 409


def test_create_url_invalid():
    res = client.post("/api/v1/urls", json={"original_url": "no-es-una-url"})
    assert res.status_code == 422


def test_create_url_with_expiry():
    res = client.post("/api/v1/urls", json={
        "original_url": "https://temporal.com",
        "expires_in": "7d",
    })
    assert res.status_code == 201
    assert res.json()["expires_at"] is not None


# ── LIST & STATS ────────────────────────────────────────────────────────

def test_list_urls():
    res = client.get("/api/v1/urls")
    assert res.status_code == 200
    assert isinstance(res.json(), list)


def test_get_stats():
    res = client.get("/api/v1/urls/stats")
    assert res.status_code == 200
    data = res.json()
    assert "total_urls" in data
    assert "total_clicks" in data


# ── REDIRECT ────────────────────────────────────────────────────────────

def test_redirect():
    create = client.post("/api/v1/urls", json={
        "original_url": "https://fastapi.tiangolo.com",
        "custom_slug": "fastapi-test",
    })
    assert create.status_code == 201
    res = client.get("/r/fastapi-test", follow_redirects=False)
    assert res.status_code == 301
    assert res.headers["location"] == "https://fastapi.tiangolo.com"


def test_redirect_increments_clicks():
    client.post("/api/v1/urls", json={
        "original_url": "https://clicks-test.com",
        "custom_slug": "clk-test",
    })
    client.get("/r/clk-test", follow_redirects=False)
    client.get("/r/clk-test", follow_redirects=False)
    info = client.get("/api/v1/urls/clk-test")
    assert info.json()["clicks"] == 2


def test_redirect_not_found():
    res = client.get("/r/no-existe", follow_redirects=False)
    assert res.status_code == 404


# ── DELETE ──────────────────────────────────────────────────────────────

def test_delete_url():
    client.post("/api/v1/urls", json={
        "original_url": "https://delete-me.com",
        "custom_slug": "delete-me",
    })
    res = client.delete("/api/v1/urls/delete-me")
    assert res.status_code == 204
    res2 = client.get("/r/delete-me", follow_redirects=False)
    assert res2.status_code == 404


def test_delete_not_found():
    res = client.delete("/api/v1/urls/no-existe-del")
    assert res.status_code == 404


# ── HEALTH ──────────────────────────────────────────────────────────────

def test_health():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"

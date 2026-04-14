from pydantic import BaseModel, HttpUrl, field_validator
from datetime import datetime
from typing import Optional
import re


class URLCreate(BaseModel):
    original_url: str
    custom_slug: Optional[str] = None
    expires_in: Optional[str] = None  # "1d" | "7d" | "30d" | None

    @field_validator("original_url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        if not v.startswith(("http://", "https://")):
            raise ValueError("La URL debe comenzar con http:// o https://")
        return v

    @field_validator("custom_slug")
    @classmethod
    def validate_slug(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v = v.strip().lower()
        if not re.match(r"^[a-z0-9\-]{3,20}$", v):
            raise ValueError("El slug debe tener 3-20 caracteres: letras, números o guiones")
        return v


class URLOut(BaseModel):
    id: int
    slug: str
    original_url: str
    clicks: int
    expires_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    is_active: bool
    short_url: str = ""

    model_config = {"from_attributes": True}


class URLStats(BaseModel):
    total_urls: int
    total_clicks: int
    top_clicks: int
    permanent_urls: int


class ClickResponse(BaseModel):
    slug: str
    clicks: int

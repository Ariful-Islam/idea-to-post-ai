"""Pydantic request/response schemas."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class IdeaInput(BaseModel):
    idea: str = Field(..., min_length=3, max_length=1000, description="Rough idea or bullet points")


class GeneratedPost(BaseModel):
    hook: str
    body: str
    hashtags: list[str]
    cta: Optional[str] = None


class PostResponse(GeneratedPost):
    id: int
    created_at: datetime
    input_text: str
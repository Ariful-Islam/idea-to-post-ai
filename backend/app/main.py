"""FastAPI entrypoint."""
from contextlib import asynccontextmanager
from typing import List

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import Base, engine, get_db
from app.llm import generate_post
from app.models import Post
from app.schemas import IdeaInput, PostResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables on startup (fine for v0; use Alembic later)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(title="Idea-to-Post API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.CORS_ORIGINS.split(",") if o.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


@app.post("/generate", response_model=PostResponse)
async def generate(payload: IdeaInput, db: AsyncSession = Depends(get_db)) -> PostResponse:
    try:
        result = await generate_post(payload.idea)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"LLM error: {exc}") from exc

    row = Post(
        input_text=payload.idea,
        hook=result["hook"],
        body=result["body"],
        hashtags=",".join(result["hashtags"]),
        cta=result["cta"],
    )
    db.add(row)
    await db.commit()
    await db.refresh(row)

    return PostResponse(
        id=row.id,
        created_at=row.created_at,
        input_text=row.input_text,
        hook=row.hook,
        body=row.body,
        hashtags=[h for h in row.hashtags.split(",") if h],
        cta=row.cta or None,
    )


@app.get("/history", response_model=List[PostResponse])
async def history(limit: int = 10, db: AsyncSession = Depends(get_db)) -> List[PostResponse]:
    result = await db.execute(select(Post).order_by(Post.created_at.desc()).limit(limit))
    rows = result.scalars().all()
    return [
        PostResponse(
            id=r.id,
            created_at=r.created_at,
            input_text=r.input_text,
            hook=r.hook,
            body=r.body,
            hashtags=[h for h in r.hashtags.split(",") if h],
            cta=r.cta or None,
        )
        for r in rows
    ]
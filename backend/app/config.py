"""Application configuration loaded from environment variables."""
import os


class Settings:
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "mysql+aiomysql://root:orko@localhost:3306/idea2post",
    )
    OLLAMA_HOST: str = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "qwen3:1.7b")
    CORS_ORIGINS: str = os.getenv("CORS_ORIGINS", "http://localhost:3000")


settings = Settings()
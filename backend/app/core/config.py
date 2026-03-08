from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:password@localhost:5432/thirdeye"
    DATABASE_ECHO: bool = False

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Auth
    SECRET_KEY: str = "change-me-to-a-random-32-byte-string-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480
    ALGORITHM: str = "HS256"

    # CORS
    CORS_ORIGINS: str = "http://localhost:8080,http://localhost:5173,http://localhost:3000"

    # LLM (Phase 2)
    LLM_PROVIDER: str = "anthropic"
    ANTHROPIC_API_KEY: str = ""
    ANTHROPIC_MODEL: str = "claude-sonnet-4-6"
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o"
    AZURE_OPENAI_ENDPOINT: str = ""
    AZURE_OPENAI_API_KEY: str = ""
    AZURE_OPENAI_DEPLOYMENT: str = "gpt-4o"

    # Weaviate (Phase 2)
    WEAVIATE_URL: str = "http://localhost:8081"

    # Signal Sources (Phase 2)
    NEWS_API_KEY: str = ""
    SHODAN_API_KEY: str = ""
    HIBP_API_KEY: str = ""
    NVD_API_KEY: str = ""

    # AWS (Production — ap-south-1 for RBI data residency)
    AWS_REGION: str = "ap-south-1"
    S3_BUCKET_REPORTS: str = "thirdeye-reports"
    S3_BUCKET_MODELS: str = "thirdeye-models"

    # Encryption
    ENCRYPTION_KEY: str = ""

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()

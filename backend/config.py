from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    GROQ_API_KEY: str = "gsk_your_groq_api_key_here"
    GROQ_EXTRACTION_MODEL: str = "groq/compound-mini"
    GROQ_QUERY_MODEL: str = "groq/compound"

    DATABASE_URL: str = "sqlite:///./scapper.db"
    STORAGE_PATH: str = "./backend/storage"

    CORS_ORIGINS: str = "http://localhost:3000"

    MAX_RETRIES: int = 3
    REQUEST_TIMEOUT: int = 30
    MAX_TOKENS_PER_CHUNK: int = 6000

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()


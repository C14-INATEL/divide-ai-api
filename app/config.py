from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./dev.db"
    APP_NAME: str = "Divide AI API"
    DEBUG: bool = False
    JWT_SECRET: str = "change-me"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
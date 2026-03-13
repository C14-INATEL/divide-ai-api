from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./dev.db"
    APP_NAME: str = "Divide AI API"
    DEBUG: bool = False

    class Config:
        env_file = ".env"

settings = Settings()
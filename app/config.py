from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./dev.db"
    APP_NAME: str = "Divide AI API"
    DEBUG: bool = False
    JWT_SECRET: str = "change-me"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60


    R2_BUCKET: str = ""
    R2_ENDPOINT_URL: str = ""
    R2_PUBLIC_URL: str = ""         
    R2_ACCESS_KEY_ID: str = ""
    R2_SECRET_ACCESS_KEY: str = ""
    LOCAL_STORAGE_DIR: str = "uploads"   # used when R2 is not configured
    MAX_UPLOAD_SIZE_BYTES: int = 5 * 1024 * 1024   # 5 MB

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
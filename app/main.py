from fastapi import FastAPI
from app.routers import users, auth
from app.database import Base, engine


Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="DivideAi API",
    description="Documentação da API",
    version="1.0.0",
    swagger_ui_parameters={
        "persistAuthorization": True
    }
)

app.include_router(auth.router)
app.include_router(users.router)
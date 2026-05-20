from fastapi import FastAPI
from app.routers import users, auth, groups
from app.database import Base, engine
from fastapi.middleware.cors import CORSMiddleware


Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="DivideAi API",
    description="Documentação da API",
    version="1.0.0",
    swagger_ui_parameters={"persistAuthorization": True},
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(groups.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"], # A Lista VIP
    allow_credentials=True,
    allow_methods=["*"], # Permite GET, POST, DELETE, etc
    allow_headers=["*"], # Permite que o Token passe
)
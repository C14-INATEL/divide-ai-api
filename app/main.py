from fastapi import FastAPI
from app.routers import users, auth
from app.database import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI(title="DivideAi API")

app.include_router(auth.router)
app.include_router(users.router)
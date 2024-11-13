from fastapi import FastAPI
from .database import engine, Base
from .routers import users

app = FastAPI()

# Create the tables if they don’t exist
Base.metadata.create_all(bind=engine)

app.include_router(users.router)

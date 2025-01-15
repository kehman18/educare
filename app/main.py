from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from .routers import users, universities

app = FastAPI()

# Add the middleware configuration here
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update with the frontend's domain for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create the tables if they don’t exist
Base.metadata.create_all(bind=engine)

app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(universities.router, prefix="/universities", tags=["Universities"])

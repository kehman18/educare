from sqlalchemy import Column, Integer, String, Boolean
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    institution = Column(String(100))
    course_level = Column(String(10))
    state_of_school = Column(String(50))
    hashed_password = Column(String(100), nullable=False)
    is_verified = Column(Boolean, default=False)
    verification_token = Column(String(10), nullable=True)

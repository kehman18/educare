from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from .database import Base
from sqlalchemy.orm import relationship

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

class University(Base):
    __tablename__ = "universities"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), index=True)
    country = Column(String(50), index=True)
    domain = Column(String(50))

class Course(Base):
    __tablename__ = "courses"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), index=True)
    university_id = Column(Integer, ForeignKey("universities.id"))
    university = relationship("University", back_populates="courses")

University.courses = relationship("Course", back_populates="university")

class UserSelection(Base):
    __tablename__ = "user_selections"
    id = Column(Integer, primary_key=True, index=True)
    country = Column(String(50))
    university = Column(String(50))
    course = Column(String(50))
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import models, schemas
from ..database import get_db
import httpx

router = APIRouter()

PUBLIC_UNIVERSITY_API = "http://universities.hipolabs.com/search"

@router.get("/countries", response_model=list[str])
async def get_countries():
    async with httpx.AsyncClient() as client:
        response = await client.get(PUBLIC_UNIVERSITY_API)
        response.raise_for_status()
        universities = response.json()
        countries = list({uni["country"] for uni in universities})
        return countries

@router.get("/universities", response_model=list[schemas.UniversitySchema])
async def get_universities(country: str, db: Session = Depends(get_db)):
    universities = db.query(models.University).filter(models.University.country == country).all()
    if not universities:
        async with httpx.AsyncClient() as client:
            response = await client.get(PUBLIC_UNIVERSITY_API, params={"country": country})
            response.raise_for_status()
            university_data = response.json()

            for uni in university_data:
                new_uni = models.University(
                    name=uni["name"], 
                    country=uni["country"], 
                    domain=uni["domains"][0] if uni["domains"] else ""
                )
                db.add(new_uni)
            db.commit()
            universities = db.query(models.University).filter(models.University.country == country).all()
    return universities

@router.get("/courses", response_model=list[schemas.CourseSchema])
async def get_courses(university_id: int, db: Session = Depends(get_db)):
    courses = db.query(models.Course).filter(models.Course.university_id == university_id).all()
    if not courses:
        sample_courses = ["Computer Science", "Engineering", "Medicine", "Business Administration"]
        for course_name in sample_courses:
            new_course = models.Course(name=course_name, university_id=university_id)
            db.add(new_course)
        db.commit()
        courses = db.query(models.Course).filter(models.Course.university_id == university_id).all()
    return courses

@router.post("/save-selection")
async def save_selection(selection: schemas.UserSelectionSchema, db: Session = Depends(get_db)):
    user_selection = models.UserSelection(
        country=selection.country, 
        university=selection.university, 
        course=selection.course
    )
    db.add(user_selection)
    db.commit()
    return {"message": "Selection saved successfully."}

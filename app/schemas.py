from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    first_name: str
    last_name: str
    username: str
    email: EmailStr
    institution: str
    course_level: str
    course_of_study: str
    state_of_school: str
    password: str
    confirm_password: str


class UserLogin(BaseModel):
    username_or_email: str
    password: str


class ResetPassword(BaseModel):
    email: EmailStr


class EmailVerification(BaseModel):
    email: EmailStr
    verification_token: str


class RequestNewToken(BaseModel):
    email: EmailStr


class UniversitySchema(BaseModel):
    id: int
    name: str
    country: str
    domain: str

    class Config:
        from_attributes = True

class CourseSchema(BaseModel):
    id: int
    name: str
    university_id: int

    class Config:
        from_attributes = True

class UserSelectionSchema(BaseModel):
    country: str
    university: str
    course: str

    class Config:
        from_attributes = True

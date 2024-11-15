from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    first_name: str
    last_name: str
    username: str
    email: EmailStr
    institution: str
    course_level: str
    state_of_school: str
    password: str
    confirm_password: str

class UserLogin(BaseModel):
    username_or_email: str
    password: str

class EmailVerification(BaseModel):
    email: EmailStr
    verification_token: str

class RequestNewToken(BaseModel):
    email: EmailStr

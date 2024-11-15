from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, Request, Response, Depends
import random
import jwt
import os

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = os.getenv("SECRET_KEY")

# In-memory session store
session_store = {}

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

# Adjust expiration to UTC timezone
def generate_verification_token():
    token = random.randint(100000, 999999)
    expiration = datetime.now(timezone.utc) + timedelta(minutes=3)
    token_data = {"token": token, "exp": expiration.timestamp()}  # Using timestamp for consistent decoding
    #encoded_token = jwt.encode(token_data, SECRET_KEY, algorithm="HS256")
    return token_data

def verify_token(encoded_token):
    try:
        decoded_token = jwt.decode(encoded_token, SECRET_KEY, algorithms=["HS256"])
        if datetime.now(timezone.utc).timestamp() > decoded_token["exp"]:
            return None
        return decoded_token
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

# Function to create session
def create_session(response: Response, user_id: int, username: str):
    session_id = f"{user_id}-{datetime.utcnow().timestamp()}"
    session_store[session_id] = {"user_id": user_id, "username": username}
    response.set_cookie(key="session_id", value=session_id, httponly=True, max_age=3600)
    return session_id

# Function to verify session
def verify_session(request: Request):
    session_id = request.cookies.get("session_id")
    if session_id and session_id in session_store:
        return session_store[session_id]
    raise HTTPException(status_code=401, detail="Invalid or expired session")

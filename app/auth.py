from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, Request, Response, Depends
import random
#import jwt
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

'''
# Adjust expiration to UTC timezone
def generate_verification_token():
    token = random.randint(100000, 999999)
    expiration = datetime.now(timezone.utc) + timedelta(minutes=10)
    token_data = {"token": token, "exp": expiration.timestamp()}  # Using timestamp for consistent decoding
    #encoded_token = jwt.encode(token_data, SECRET_KEY, algorithm="HS256")
    return token_data

def verify_token(token_data):
    try:
        #decoded_token = jwt.decode(token_data, SECRET_KEY, algorithms=["HS256"])
        decoded_token = token_data
        if datetime.now(timezone.utc).timestamp() > decoded_token["exp"]:
            return None
        return decoded_token
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
'''

import re

def validate_email(email: str) -> bool:
    """
    Validates the given email address.

    Args:
        email (str): The email address to validate.
    Returns:
        bool: True if the email is valid, False otherwise.
    Raises:
        ValueError: If the email is invalid.
    """
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z]{2,}$'  # Robust email regex
    if not re.match(email_regex, email):
        raise ValueError("Invalid email address. Please enter a valid email.")
    return True

def validate_password(password: str) -> bool:
    """
    Validates the given password for strength and security.

    Args:
        password (str): The password to validate.
    Returns:
        bool: True if the password is valid, False otherwise.
    Raises:
        ValueError: If the password is invalid.
    """
    password_regex = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$'
    if not re.match(password_regex, password):
        raise ValueError(
            "Your password must be at least 8 characters long, "
            "contain at least one uppercase letter, one lowercase letter, one digit, "
            "and one special character (e.g., @$!%*?&)."
        )
    return True

def generate_verification_token():
    token = random.randint(100000, 999999)
    expiration = datetime.now(timezone.utc) + timedelta(minutes=3)
    token_data = {"token": token, "exp": expiration.timestamp()}  # Using timestamp for consistent decoding
    return token_data


def verify_token(token_data):
    try:
        # Ensure token data is in dictionary format
        if datetime.now(timezone.utc).timestamp() > token_data["exp"]:  # # Fixed timestamp comparison logic
            return None
        return token_data
    except KeyError:
        return None
    except Exception as e:  # Catch unexpected errors
        print(f"Error verifying token: {e}")
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
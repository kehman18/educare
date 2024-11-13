from passlib.context import CryptContext
from datetime import datetime, timedelta
import random
import jwt
import os


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = os.getenv("SECRET_KEY")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def create_verification_token(data: dict):
    return jwt.encode(data, SECRET_KEY, algorithm="HS256")


def generate_verification_token():
    token = random.randint(100000, 999999)  # Generates a 6-digit token
    expiration = datetime.utcnow() + timedelta(minutes=1)
    token_data = {"token": token, "exp": expiration}
    # encoded_token = jwt.encode(token_data, SECRET_KEY, algorithm="HS256")
    return token  # Return both the encoded token and the raw 6-digit token

def verify_token(encoded_token):
    try:
        decoded_token = jwt.decode(encoded_token, SECRET_KEY, algorithms=["HS256"])
        return decoded_token if datetime.utcnow() < decoded_token["exp"] else None
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

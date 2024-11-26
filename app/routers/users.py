from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
import re
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timedelta, timezone
from .. import schemas, models, auth, email_utils
from ..database import get_db

router = APIRouter()

@router.post("/sign-up", status_code=status.HTTP_201_CREATED)
async def sign_up(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Check if passwords match
    if user.password != user.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    # Check for existing user by email or username
    existing_user = db.query(models.User).filter(
        (models.User.email == user.email) | (models.User.username == user.username)
    ).first()
    
    if existing_user:
        raise HTTPException(status_code=400, detail="User with this username or email already exists")

    # Validate email using the validate_email function
    try:
        auth.validate_email(user.email)  # If invalid, it will raise ValueError
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

        
    try:
        auth.validate_password(user.password)  # If invalid, it will raise ValueError
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Proceed with user creation
    try:
        hashed_password = auth.get_password_hash(user.password)  # Hash the password
        token_data = auth.generate_verification_token()  # Generate a verification token

        raw_token = str(token_data["token"])  # Extract the raw token

        # Create a new user object
        new_user = models.User(
            first_name=user.first_name,
            last_name=user.last_name,
            username=user.username,
            email=user.email,
            institution=user.institution,
            course_level=user.course_level,
            state_of_school=user.state_of_school,
            hashed_password=hashed_password,
            verification_token=raw_token  # Store raw token in the database
        )

        # Save the user to the database
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        await email_utils.send_verification_email(user.email, raw_token)  # Send the verification email

    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail="User with this username or email already exists")

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="An error occurred while sending the verification email. Please try again later."
        )

    return {"message": "Verification email sent. Please check your inbox."}


@router.post("/verify-email")
async def verify_email(verification: schemas.EmailVerification, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == verification.email).first()
    
    if not user:
        raise HTTPException(status_code=400, detail="User not found")

    # Ensure verification token is parsed and compared properly
    try:
        token_data = auth.verify_token({"token": user.verification_token, "exp": (datetime.now(timezone.utc) + timedelta(minutes=10)).timestamp()})  # # Ensuring token_data is passed as a dict

    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid token")

    # Compare raw tokens, not encoded ones
    if not token_data or str(token_data["token"]) != verification.verification_token:  # # Fixed condition for string comparison
        raise HTTPException(status_code=400, detail="Invalid or expired token. Please request a new one.")

    user.is_verified = True
    user.verification_token = None  # Clear token after verification
    db.commit()
    return {"message": "User successfully verified. Redirecting to login page."}


@router.post("/request-new-token")
async def request_new_token(request: schemas.RequestNewToken, db: Session = Depends(get_db)):
    email = request.email
    user = db.query(models.User).filter(models.User.email == email).first()
    
    if not user:
        raise HTTPException(status_code=400, detail="User not found")

    token_data = auth.generate_verification_token()
    user.verification_token = str(token_data["token"])
    user.token_expiration = token_data["exp"]
    db.commit()

    await email_utils.send_verification_email(user.email, token_data["token"])
    return {"message": "A new verification token has been sent to your email."}


@router.post("/login")
async def login(user: schemas.UserLogin, response: Response, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(
        (models.User.username == user.username_or_email) | 
        (models.User.email == user.username_or_email)
    ).first()
    
    if not db_user or not auth.verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Set session using the create_session function
    auth.create_session(response, user_id=db_user.id, username=db_user.username)
    
    return {"message": "Login successful. Redirecting to dashboard."}


@router.post("/login/forgot-password")
async def forgot_password(email: schemas.ResetPassword, db: Session = Depends(get_db)):
    # Step 1: Check if the email exists in the database
    user = db.query(models.User).filter(models.User.email == email.email).first()

    if not user:
        raise HTTPException(status_code=400, detail="User not registered with this email.")

    # Step 2: Generate a verification token and send it to the user's email
    token_data = auth.generate_verification_token()  # Generates a token
    raw_token = str(token_data["token"])  # Extract the raw token
    user.verification_token = raw_token  # Store the token in the user's record
    db.commit()

    # Send the verification token to the user's email
    await email_utils.send_verification_email(user.email, raw_token)

    return {"message": "Verification token sent. Please check your email."}


@router.post("/login/reset-password")
async def reset_password(token: schemas.EmailVerification, new_password: str, confirm_new_password: str, db: Session = Depends(get_db)):
    # Step 1: Find the user by email
    user = db.query(models.User).filter(models.User.email == token.email).first()

    if not user:
        raise HTTPException(status_code=400, detail="User not registered with this email.")

    # Step 2: Verify the token
    try:
        token_data = auth.verify_token({"token": user.verification_token, "exp": (datetime.now(timezone.utc) + timedelta(minutes=3)).timestamp()})

    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid or expired token.")

    # Compare raw tokens
    if not token_data or str(token_data["token"]) != token.verification_token:
        raise HTTPException(status_code=400, detail="Invalid or expired token. Please request a new one.")

    # Step 3: Ensure passwords match
    if new_password != confirm_new_password:
        raise HTTPException(status_code=400, detail="Passwords do not match.")

    # Step 4: Validate the new password
    try:
        auth.validate_password(new_password)  # Validate the new password
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Step 5: Hash the new password and update in the database
    hashed_password = auth.get_password_hash(new_password)
    user.hashed_password = hashed_password
    db.commit()

    return {"message": "Password reset successful. Please log in with your new password."}

    
@router.get("/{username}/dashboard")
async def dashboard(username: str, request: Request):
    session_data = auth.verify_session(request)
    if session_data["username"] != username:
        raise HTTPException(status_code=401, detail="Unauthorized access")

    return {"message": "Welcome to your dashboard!", "user": {"username": session_data["username"]}}
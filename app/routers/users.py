from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from .. import schemas, models, auth, email_utils
from ..database import get_db

router = APIRouter()

@router.post("/sign-up", status_code=status.HTTP_201_CREATED)
async def sign_up(user: schemas.UserCreate, db: Session = Depends(get_db)):
    if user.password != user.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    # Check if the email or username already exists
    existing_user = db.query(models.User).filter(
        (models.User.email == user.email) | (models.User.username == user.username)
    ).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User with this username or email already exists")

    try:
        hashed_password = auth.get_password_hash(user.password)
        raw_token = auth.generate_verification_token()

        new_user = models.User(
            first_name=user.first_name,
            last_name=user.last_name,
            username=user.username,
            email=user.email,
            institution=user.institution,
            course_level=user.course_level,
            state_of_school=user.state_of_school,
            hashed_password=hashed_password,
            verification_token=raw_token
        )

        db.add(new_user)

        # Attempt to send the email after committing the transaction
        await email_utils.send_verification_email(user.email, raw_token)

        db.commit()
        db.refresh(new_user)


    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="User with the username or email already exists")
    
    except Exception as e:
        print(e)
        db.rollback()
        raise HTTPException(status_code=500, detail="An error occurred while sending the verification email. Please try again later.")

    return {"message": "Verification email sent. Please check your inbox."}


@router.post("/verify-email")
async def verify_email(verification: schemas.EmailVerification, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == verification.email).first()
    
    if not user:
        raise HTTPException(status_code=400, detail="User not found")

    token_data = auth.verify_token(user.verification_token)

    if not token_data or str(token_data["token"]) != verification.verification_token:
        raise HTTPException(status_code=400, detail="Invalid or expired token. Please request a new one.")
    
    user.is_verified = True
    user.verification_token = None  # Clear token after verification
    db.commit()
    return {"message": "User successfully verified. Redirecting to login page."}

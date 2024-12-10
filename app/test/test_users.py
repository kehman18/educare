import unittest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from app.main import app  # Assuming 'app' is your FastAPI instance
from app import models, schemas, auth, email_utils
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base

# Create a test database engine
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency override for the database session
def override_get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

class TestUsersEndpoints(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        
        # Mocking external functions
        self.mock_generate_token = MagicMock(return_value={"token": "123456", "exp": 1234567890})
        self.mock_send_email = MagicMock(return_value=None)
        self.mock_validate_email = MagicMock(return_value=True)
        self.mock_validate_password = MagicMock(return_value=True)
        self.mock_hash_password = MagicMock(return_value="hashed_password")
        self.mock_verify_password = MagicMock(return_value=True)
        self.mock_verify_token = MagicMock(return_value={"token": "123456", "exp": 1234567890})
        self.mock_create_session = MagicMock()

        # Override auth and email_utils
        auth.generate_verification_token = self.mock_generate_token
        email_utils.send_verification_email = self.mock_send_email
        auth.validate_email = self.mock_validate_email
        auth.validate_password = self.mock_validate_password
        auth.get_password_hash = self.mock_hash_password
        auth.verify_password = self.mock_verify_password
        auth.verify_token = self.mock_verify_token
        auth.create_session = self.mock_create_session

    def test_sign_up_success(self):
        # Prepare the test data
        user_data = {
            "first_name": "John",
            "last_name": "Doe",
            "username": "john_doe",
            "email": "john@example.com",
            "institution": "University",
            "course_level": "Level 1",
            "state_of_school": "State",
            "password": "SecurePass1!",
            "confirm_password": "SecurePass1!"
        }

        # Mock database session
        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = None  # No existing user
        
        # Call the endpoint
        response = self.client.post("/sign-up", json=user_data)
        
        self.assertEqual(response.status_code, 201)
        self.assertIn("message", response.json())
        self.assertEqual(response.json()["message"], "Verification email sent. Please check your inbox.")

    def test_sign_up_email_already_exists(self):
        user_data = {
            "first_name": "John",
            "last_name": "Doe",
            "username": "john_doe",
            "email": "john@example.com",
            "institution": "University",
            "course_level": "Level 1",
            "state_of_school": "State",
            "password": "SecurePass1!",
            "confirm_password": "SecurePass1!"
        }

        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = models.User(id=1, email="john@example.com")  # User already exists

        # Call the endpoint
        response = self.client.post("/sign-up", json=user_data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["detail"], "User with this username or email already exists.")

    def test_verify_email_success(self):
        verification_data = {
            "email": "john@example.com",
            "verification_token": "123456"
        }

        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = models.User(id=1, email="john@example.com", verification_token="123456", is_verified=False)

        response = self.client.post("/verify-email", json=verification_data)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["message"], "User successfully verified. Redirecting to login page.")

    def test_verify_email_invalid_token(self):
        verification_data = {
            "email": "john@example.com",
            "verification_token": "654321"
        }

        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = models.User(id=1, email="john@example.com", verification_token="123456", is_verified=False)

        response = self.client.post("/verify-email", json=verification_data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["detail"], "Invalid or expired token. Please request a new one.")

    def test_request_new_token(self):
        request_data = {"email": "john@example.com"}
        
        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = models.User(id=1, email="john@example.com", verification_token=None)

        response = self.client.post("/request-new-token", json=request_data)

        self.assertEqual(response.status_code, 200)
        self.assertIn("message", response.json())
        self.assertEqual(response.json()["message"], "A new verification token has been sent to your email.")

    def test_forgot_password(self):
        reset_data = {"email": "john@example.com"}
        
        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = models.User(id=1, email="john@example.com")

        response = self.client.post("/login/forgot-password", json=reset_data)

        self.assertEqual(response.status_code, 200)
        self.assertIn("message", response.json())
        self.assertEqual(response.json()["message"], "Verification token sent. Please check your email.")

    def test_reset_password_success(self):
        reset_data = {"email": "john@example.com", "verification_token": "123456"}
        new_password = "NewPassword123!"
        confirm_password = "NewPassword123!"

        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = models.User(id=1, email="john@example.com", verification_token="123456")

        response = self.client.post("/login/reset-password", json=reset_data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["message"], "Password reset successful. Please log in with your new password.")

    def test_reset_password_token_expired(self):
        reset_data = {"email": "john@example.com", "verification_token": "123456"}
        new_password = "NewPassword123!"
        confirm_password = "NewPassword123!"

        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = models.User(id=1, email="john@example.com", verification_token="123456")

        self.mock_verify_token.side_effect = ValueError("Invalid or expired token")

        response = self.client.post("/login/reset-password", json=reset_data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["detail"], "Invalid or expired token.")

if __name__ == "__main__":
    unittest.main()

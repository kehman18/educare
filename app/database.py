import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

# Fetch credentials from environment variables
user = os.getenv('user')
password = os.getenv('password')
host = os.getenv('host')
port = os.getenv('port')
database = os.getenv('database')
ssl_ca_path = r"C:\Users\Owner\Downloads\DigiCertGlobalRootCA.crt.pem"  # Path to your SSL certificate

# Build the connection string for SQLAlchemy with SSL configuration
DATABASE_URL = f"mysql+mysqlconnector://{user}:{password}@{host}:{port}/{database}?ssl_ca={ssl_ca_path}&ssl_verify_cert=true"

# Create the SQLAlchemy engine with SSL configuration
engine = create_engine(DATABASE_URL)

# Create a session maker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Function to yield database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Test the connection (similar to test_connection.py)
try:
    connection = engine.connect()
    print("Connected successfully.")
    connection.close()
except Exception as e:
    print(f"Failed to connect: {e}")

from urllib.parse import quote_plus
from sqlalchemy import create_engine

DATABASE_URL = f"mysql+pymysql://{quote_plus('root')}:{quote_plus('kehman21')}@localhost:3306/educare_db"
engine = create_engine(DATABASE_URL)
try:
    connection = engine.connect()
    print("Connected successfully.")
    connection.close()
except Exception as e:
    print(f"Failed to connect: {e}")

'''
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

    '''

import mysql.connector
from mysql.connector import Error

# Replace with your Azure MySQL database details
config = {
    "user": "adminuser",  # Replace with your MySQL username
    "password": "Rehoboth_JnR",  # Replace with your MySQL password
    "host": "educareserver.mysql.database.azure.com",  # Replace with your MySQL host (e.g., educareserver.mysql.database.azure.com)
    "port": 3306,
    "database": "educare_db",  # Replace with your database name
    "ssl_ca": r"C:\Users\Owner\Downloads\DigiCertGlobalRootCA.crt.pem",  # Path to your SSL certificate
    "ssl_disabled": False,  # Set to True if SSL is disabled
}

try:
    # Try to establish a connection
    cnx = mysql.connector.connect(**config)
    
    # Check if the connection is successful
    if cnx.is_connected():
        print("Connected successfully")
        
        # Execute a simple query to check the connection
        cursor = cnx.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        print("Query result:", result)
        
    else:
        print("Failed to connect")
        
except Error as e:
    print("Failed to connect. Error:", e)
    
finally:
    # Close the connection if it's open
    if cnx.is_connected():
        cnx.close()

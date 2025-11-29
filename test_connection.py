from src.config import Config
from src.database import Database

config = Config()
db = Database(config)

if db.test_connection():
    print("Database connection successful!")
else:
    print("Connection error. Please check your DATABASE_URL.")


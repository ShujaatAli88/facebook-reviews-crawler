from dotenv import load_dotenv
import os

load_dotenv()

class Config():
    database_name = os.getenv("DATABASE_NAME")
    database_port = os.getenv("DATABASE_PORT")
    database_host = os.getenv("DATABASE_HOST")
    database_password = os.getenv("DATABASE_PASSWORD")
    database_user = os.getenv("DATABASE_USER")
import os

from dotenv import load_dotenv
from pymysql.cursors import DictCursor

load_dotenv()


def get_db_config():
    return {
        "host": os.getenv("DB_HOST", "localhost"),
        "port": int(os.getenv("DB_PORT", "3306")),
        "user": os.getenv("DB_USER", "root"),
        "password": os.getenv("DB_PASSWORD", "root"),
        "database": os.getenv("DB_NAME", "spotyfinderdb"),
        "cursorclass": DictCursor,
        "autocommit": False,
    }
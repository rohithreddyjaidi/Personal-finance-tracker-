import os

from dotenv import load_dotenv


load_dotenv()


class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "mysql+pymysql://username:password@localhost/finance_app_db",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

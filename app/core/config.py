import os
from dotenv import load_dotenv

load_dotenv()

class Settings:

  SECRET_KEY = os.getenv("SECRET_KEY")
  SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI")
  ALGORITHM = os.getenv("ALGORITHM")
  ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
  REFRESH_TOKEN_EXPIRE_MINUTES = int(os.getenv("REFRESH_TOKEN_EXPIRE_MINUTES"))

settings = Settings()
import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()

class Settings(BaseSettings):
    # DB_USERNAME = os.environ.get("DB_USERNAME")
    # DB_HOST = os.environ.get("DB_HOST")
    # DB_PASSWORD = os.environ.get("DB_PASSWORD")
    # DB_PORT = os.environ.get("DB_PORT")
    # MONGODB_URI: str = f"mongodb://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}"
    MONGODB_URI: str = "mongodb://junchan:1234@3.34.178.2:27017/"
    # class Config:
    #     env_file = ".env"

settings = Settings()
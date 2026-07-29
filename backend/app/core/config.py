import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    def __init__(self):
        self.DATABASE_URL = os.getenv("DATABASE_URL")
        self.SECRET_KEY = os.getenv("SECRET_KEY")
        self.ALGORITHM = os.getenv("ALGORITHM")

        self.ACCESS_TOKEN_EXPIRE_MINUTES = 30
        self.REFRESH_TOKEN_EXPIRE_DAYS = 7

        if not self.DATABASE_URL:
            raise ValueError("DATABASE_URL environment variable is required")

        if not self.SECRET_KEY:
            raise ValueError("SECRET_KEY environment variable is required")
        
        if not self.ALGORITHM:
            raise ValueError("ALGORITHM environment variable is required")

settings = Settings()

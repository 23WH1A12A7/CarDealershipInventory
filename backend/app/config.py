import os

from dotenv import load_dotenv

load_dotenv()


DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./dealership.db")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development").lower()
JWT_SECRET = os.getenv("JWT_SECRET", "local-development-secret-change-before-deploying")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_MINUTES = 480

if ENVIRONMENT == "production" and JWT_SECRET == "local-development-secret-change-before-deploying":
    raise RuntimeError("JWT_SECRET must be set when ENVIRONMENT=production")

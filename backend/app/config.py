import os


DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./dealership.db")
JWT_SECRET = os.getenv("JWT_SECRET", "change-me-in-production")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_MINUTES = 480


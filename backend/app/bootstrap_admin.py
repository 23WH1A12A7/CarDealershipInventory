"""Create an administrator through a trusted local shell, never public registration."""
from getpass import getpass

from .database import Base, SessionLocal, engine
from .models import User
from .security import hash_password


def main():
    Base.metadata.create_all(bind=engine)
    name = input("Administrator name: ").strip()
    email = input("Administrator email: ").strip().lower()
    password = getpass("Administrator password: ")
    if len(name) < 2 or not email or len(password) < 8:
        raise SystemExit("Name, email, and a password of at least 8 characters are required.")
    db = SessionLocal()
    try:
        if db.query(User).filter(User.email == email).first():
            raise SystemExit("An account with that email already exists.")
        db.add(User(name=name, email=email, password_hash=hash_password(password), role="admin"))
        db.commit()
        print(f"Administrator provisioned for {email}.")
    finally:
        db.close()


if __name__ == "__main__":
    main()

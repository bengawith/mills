import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from database import SessionLocal, engine
from database_models import User, Base
from schemas import UserCreate
from security import create_user, get_user


def main():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        test_user = get_user(db, "testuser")
        if not test_user:
            print("Creating test user")
            user_in = UserCreate(
                username="testuser",
                full_name="Test User",
                email="test@example.com",
                password="testpassword",
            )
            print("Calling create_user")
            create_user(db, user_in)
            print("create_user called")
            print("Test user created")
        else:
            print("Test user already exists")
    finally:
        pass


if __name__ == "__main__":
    main()
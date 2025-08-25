import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from database import SessionLocal, engine
from database_models import User, Base


def main():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        test_user = db.query(User).filter(User.email == "test@example.com").first()
        if test_user:
            db.delete(test_user)
            db.commit()
            print("Test user deleted")
        else:
            print("Test user not found")
    finally:
        db.close()


if __name__ == "__main__":
    main()

# test_db.py
from DB.config import SQLALCHEMY_DATABASE_URL, engine
from DB.database import Base, get_db

def test_connection():
    print(f"Database URL: {SQLALCHEMY_DATABASE_URL}")
    print("Attempting to create tables...")
    
    # Test table creation
    Base.metadata.create_all(bind=engine)
    
    # Test session
    with next(get_db()) as db:
        print("✅ Database connection successful!")
        print(f"Session active: {db.is_active}")

if __name__ == "__main__":
    test_connection()
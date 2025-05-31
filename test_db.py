from health_simplified.db.config import SQLALCHEMY_DATABASE_URL
from health_simplified.db.database import Base, engine, get_db
from sqlalchemy import text

def test_connection():
    print(f"Database URL: {SQLALCHEMY_DATABASE_URL}")
    print(f"Database file location: {engine.url.database}")
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    print("✅ Tables created successfully")
    
    # Test connection
    try:
        db = next(get_db())
        result = db.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
        tables = [row[0] for row in result]
        print("Tables in database:", tables)
        
        if not tables:
            print("⚠️  No tables found - checking if database file exists")
            import os
            db_path = engine.url.database.replace('sqlite:///', '')
            print(f"Database exists: {os.path.exists(db_path)}")
            print(f"File size: {os.path.getsize(db_path) if os.path.exists(db_path) else 0} bytes")
        
        print("✅ Database connection successful!")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    test_connection()
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from health_simplified.db.config import SQLALCHEMY_DATABASE_URL  # Updated import

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
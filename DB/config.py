from sqlalchemy import create_engine

# Database connection URL for SQLite (file located in project folder)
SQLALCHEMY_DATABASE_URL = "sqlite:///./health_simplified.db"

# Create the SQLAlchemy engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}  # Needed for SQLite

)
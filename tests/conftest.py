import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import ResourceClosedError
from typer.testing import CliRunner

from health_simplified.db.database import Base
from health_simplified.db.config import SQLALCHEMY_DATABASE_URL
from health_simplified.cli.main import app  # ✅ Import your CLI app

# ✅ Provide a runner instance usable in tests
@pytest.fixture(scope="session")
def runner():
    return CliRunner()

# ✅ Set up test database engine
@pytest.fixture(scope="module")
def test_engine():
    engine = create_engine(
        f"{SQLALCHEMY_DATABASE_URL}_test",  # Ensure this uses a test-specific DB
        connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)

# ✅ Create a new DB session for each test with safe rollback
@pytest.fixture
def test_db(test_engine):
    connection = test_engine.connect()
    transaction = connection.begin()
    db = sessionmaker(autocommit=False, autoflush=False, bind=connection)()

    yield db

    db.close()
    # Safe rollback to avoid "transaction already deassociated" warning
    try:
        transaction.rollback()
    except ResourceClosedError:
        # Transaction was already rolled back or closed, so ignore the error
        pass
    connection.close()

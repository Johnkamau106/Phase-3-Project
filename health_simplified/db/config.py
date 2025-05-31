from pathlib import Path

# Absolute path ensures consistent database location
BASE_DIR = Path(__file__).parent.parent.parent
SQLALCHEMY_DATABASE_URL = f"sqlite:///{BASE_DIR}/health_simplified.db"

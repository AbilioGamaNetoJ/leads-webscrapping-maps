import os
import tempfile
from pathlib import Path

_TEST_DB = Path(tempfile.gettempdir()) / "prospector_pytest.db"
os.environ["DATABASE_URL"] = f"sqlite:///{_TEST_DB}"
os.environ.setdefault("GOOGLE_MAPS_API_KEY", "test-key")
os.environ.setdefault("APP_ENV", "test")
os.environ.setdefault("APP_URL", "http://testserver")
os.environ.setdefault("SESSION_SECRET_KEY", "test-session-secret")

import pytest

from database.connection import SessionLocal, engine
from database.models import Base


@pytest.fixture
def db_session():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)

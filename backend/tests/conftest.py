import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base, get_db
from app.main import app

# ── bcrypt 5.x / passlib 1.7.x compatibility fix ────────────────────────────
# bcrypt 5.0 removed __about__ and tightened password-length enforcement,
# breaking passlib 1.7.4.  For tests we swap the CryptContext to sha256_crypt
# which has no such restrictions and is faster in CI anyway.
from passlib.context import CryptContext
import app.core.security as _security  # noqa: E402

_security.pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")
# ─────────────────────────────────────────────────────────────────────────────

TEST_DATABASE_URL = "sqlite:///./test_zhinong.db"

engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def db():
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture()
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()

import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool
from uuid import UUID

from app.database import Base
# Import all models so their tables are registered on Base.metadata
import app.models.user  # noqa: F401
import app.models.group  # noqa: F401
import app.models.group_member  # noqa: F401
import app.models.debt  # noqa: F401
import app.models.debt_participant  # noqa: F401
from app.models.user import User
from app.utils.security import hash_password


CREATOR_ID = UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")
OTHER_USER_ID = UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb")
GROUP_ID = UUID("cccccccc-cccc-cccc-cccc-cccccccccccc")


@pytest.fixture
def mock_db_session(mocker):
    return mocker.Mock(spec=Session)


@pytest.fixture
def sample_user():
    user = User(
        email="test@example.com",
        name="Test User",
        password=hash_password("TestPassword123"),
        pix_key=None,
        pix_key_type=None
    )
    user.id = UUID("123e4567-e89b-12d3-a456-426614174000")
    return user


@pytest.fixture
def sample_user_plain_password():
    return "TestPassword123"

@pytest.fixture
def mock_group_repo(mocker):
    return mocker.Mock()


@pytest.fixture
def mock_user_repo(mocker):
    return mocker.Mock()


@pytest.fixture
def db_session():
    """A real in-memory SQLite session with FK enforcement enabled.

    Used for integration-style tests that need to exercise actual ORM
    cascade behavior (e.g. deleting a group and its members), which mocked
    repositories cannot cover.
    """
    # StaticPool keeps a single shared connection so the in-memory database is
    # visible across threads (the FastAPI TestClient runs endpoints in a
    # worker thread, which would otherwise get its own empty :memory: db).
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    @event.listens_for(engine, "connect")
    def _enable_sqlite_fk(dbapi_conn, _record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    Base.metadata.create_all(engine)
    TestingSession = sessionmaker(bind=engine)
    session = TestingSession()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(engine)
        engine.dispose()
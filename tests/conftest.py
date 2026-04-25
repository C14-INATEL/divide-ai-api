import pytest
from sqlalchemy.orm import Session
from uuid import UUID

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
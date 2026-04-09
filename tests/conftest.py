import pytest
from uuid import UUID

from app.models.user import User
from app.utils.security import hash_password
from tests.repositories.in_memory_user_repository import InMemoryUserRepository


@pytest.fixture
def in_memory_user_repository():
    return InMemoryUserRepository()


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

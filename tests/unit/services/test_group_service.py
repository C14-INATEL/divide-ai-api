from uuid import UUID
import pytest
from app.services.group_service import GroupService
from app.repositories.group_repository import GroupRepository
from app.repositories.user_repository import UserRepository
from app.schemas.group import GroupCreate, GroupUpdate
from app.models.group import Group
from app.models.group_member import GroupMember
from app.models.user import User
from app.exceptions import AppException
from tests.conftest import CREATOR_ID, OTHER_USER_ID, GROUP_ID



def _make_group(creator_id: UUID = CREATOR_ID) -> Group:
    group = Group(name="Test Group", creator_id=creator_id)
    group.id = GROUP_ID
    return group


def _make_member(group_id: UUID = GROUP_ID, user_id: UUID = OTHER_USER_ID) -> GroupMember:
    member = GroupMember(group_id=group_id, user_id=user_id)
    return member


def _make_user(user_id: UUID = OTHER_USER_ID) -> User:
    user = User(email="other@example.com", name="Other User", password="hashed")
    user.id = user_id
    return user


def _make_service(mock_db_session, group_repo, user_repo) -> GroupService:
    service = GroupService(mock_db_session)
    service.repo = group_repo
    service.user_repo = user_repo
    return service


class TestGroupServiceCreate:

    def test_create_success(self, mock_db_session, mock_group_repo, mock_user_repo):
        group = _make_group()
        mock_group_repo.create.return_value = group

        service = _make_service(mock_db_session, mock_group_repo, mock_user_repo)
        result = service.create(GroupCreate(name="Test Group"), creator_id=CREATOR_ID)

        mock_group_repo.create.assert_called_once_with(name="Test Group", creator_id=CREATOR_ID)
        mock_group_repo.add_member.assert_called_once_with(group_id=GROUP_ID, user_id=CREATOR_ID)
        assert result is group


class TestGroupServiceGetById:

    def test_get_by_id_not_found(self, mock_db_session, mock_group_repo, mock_user_repo):
        mock_group_repo.get_by_id.return_value = None

        service = _make_service(mock_db_session, mock_group_repo, mock_user_repo)

        with pytest.raises(AppException) as exc:
            service.get_by_id(GROUP_ID, CREATOR_ID)

        assert exc.value.status_code == 404

    def test_get_by_id_not_member(self, mock_db_session, mock_group_repo, mock_user_repo):
        mock_group_repo.get_by_id.return_value = _make_group()
        mock_group_repo.get_member.return_value = None

        service = _make_service(mock_db_session, mock_group_repo, mock_user_repo)

        with pytest.raises(AppException) as exc:
            service.get_by_id(GROUP_ID, OTHER_USER_ID)

        assert exc.value.status_code == 403

    def test_get_by_id_success(self, mock_db_session, mock_group_repo, mock_user_repo):
        group = _make_group()
        mock_group_repo.get_by_id.return_value = group
        mock_group_repo.get_member.return_value = _make_member(user_id=CREATOR_ID)

        service = _make_service(mock_db_session, mock_group_repo, mock_user_repo)
        result = service.get_by_id(GROUP_ID, CREATOR_ID)

        assert result is group


class TestGroupServiceRemoveMember:

    def test_remove_member_group_not_found(self, mock_db_session, mock_group_repo, mock_user_repo):
        mock_group_repo.get_by_id.return_value = None

        service = _make_service(mock_db_session, mock_group_repo, mock_user_repo)

        with pytest.raises(AppException) as exc:
            service.remove_member(GROUP_ID, OTHER_USER_ID, CREATOR_ID)

        assert exc.value.status_code == 404

    def test_remove_member_not_creator(self, mock_db_session, mock_group_repo, mock_user_repo):
        mock_group_repo.get_by_id.return_value = _make_group(creator_id=CREATOR_ID)

        service = _make_service(mock_db_session, mock_group_repo, mock_user_repo)

        with pytest.raises(AppException) as exc:
            service.remove_member(GROUP_ID, OTHER_USER_ID, current_user_id=OTHER_USER_ID)

        assert exc.value.status_code == 403

    def test_remove_member_cannot_remove_creator(self, mock_db_session, mock_group_repo, mock_user_repo):
        mock_group_repo.get_by_id.return_value = _make_group(creator_id=CREATOR_ID)

        service = _make_service(mock_db_session, mock_group_repo, mock_user_repo)

        with pytest.raises(AppException) as exc:
            service.remove_member(GROUP_ID, CREATOR_ID, current_user_id=CREATOR_ID)

        assert exc.value.status_code == 400

    def test_remove_member_not_found(self, mock_db_session, mock_group_repo, mock_user_repo):
        mock_group_repo.get_by_id.return_value = _make_group(creator_id=CREATOR_ID)
        mock_group_repo.get_member.return_value = None

        service = _make_service(mock_db_session, mock_group_repo, mock_user_repo)

        with pytest.raises(AppException) as exc:
            service.remove_member(GROUP_ID, OTHER_USER_ID, CREATOR_ID)

        assert exc.value.status_code == 404

    def test_remove_member_success(self, mock_db_session, mock_group_repo, mock_user_repo):
        member = _make_member()
        mock_group_repo.get_by_id.return_value = _make_group(creator_id=CREATOR_ID)
        mock_group_repo.get_member.return_value = member

        service = _make_service(mock_db_session, mock_group_repo, mock_user_repo)
        service.remove_member(GROUP_ID, OTHER_USER_ID, CREATOR_ID)

        mock_group_repo.remove_member.assert_called_once_with(member)

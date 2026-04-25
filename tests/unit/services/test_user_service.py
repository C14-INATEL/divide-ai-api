from unittest.mock import Mock
import pytest

from app.services.user_service import UserService
from app.schemas.user import UserCreate, UserPasswordUpdate
from app.exceptions import AppException
from app.repositories.user_repository import UserRepository


class TestUserServiceAuthenticate:
    
    def test_authenticate_success(self, mock_db_session, sample_user, sample_user_plain_password):
        mock_repo = Mock(spec=UserRepository)
        mock_repo.get_by_email.return_value = sample_user
        
        service = UserService(mock_db_session)
        service.repo = mock_repo
        
        result = service.authenticate(sample_user.email, sample_user_plain_password)
        
        assert result is not None
        assert result.email == sample_user.email
        assert result.name == sample_user.name
        mock_repo.get_by_email.assert_called_once_with(sample_user.email)
    
    def test_authenticate_user_not_found(self, mock_db_session):
        mock_repo = Mock(spec=UserRepository)
        mock_repo.get_by_email.return_value = None
        
        service = UserService(mock_db_session)
        service.repo = mock_repo
        
        result = service.authenticate("nonexistent@example.com", "AnyPassword123")
        
        assert result is None
        mock_repo.get_by_email.assert_called_once_with("nonexistent@example.com")
    
    def test_authenticate_wrong_password(self, mock_db_session, sample_user):
        mock_repo = Mock(spec=UserRepository)
        mock_repo.get_by_email.return_value = sample_user
        
        service = UserService(mock_db_session)
        service.repo = mock_repo
        
        result = service.authenticate(sample_user.email, "WrongPassword123")
        
        assert result is None
        mock_repo.get_by_email.assert_called_once_with(sample_user.email)
    
    def test_authenticate_empty_password(self, mock_db_session, sample_user):
        mock_repo = Mock(spec=UserRepository)
        mock_repo.get_by_email.return_value = sample_user
        
        service = UserService(mock_db_session)
        service.repo = mock_repo
        
        result = service.authenticate(sample_user.email, "")
        
        assert result is None

class TestUserServiceCreate:
    
    #teste para criar usuário com email que já existe
    def test_create_email_already_exists(self, mock_db_session, sample_user):
        mock_repo = Mock(spec=UserRepository)
        mock_repo.get_by_email.return_value = sample_user

        service = UserService(mock_db_session)
        service.repo = mock_repo

        data = UserCreate(
            email=sample_user.email,
            name="John Pedro",
            password="Password123",
            pix_key=None,
            pix_key_type=None
        )

        #é pra dar erro
        with pytest.raises(AppException) as exc:
            service.create(data)

        assert exc.value.status_code == 400
        assert "Email já cadastrado" in exc.value.detail
        mock_repo.get_by_email.assert_called_once_with(sample_user.email)


class TestUserServiceUpdatePassword:

    def test_update_password_wrong_old_password(self, mock_db_session, sample_user):
        mock_repo = Mock(spec=UserRepository)
        mock_repo.get_by_id.return_value = sample_user

        service = UserService(mock_db_session)
        service.repo = mock_repo

        data = UserPasswordUpdate(
            old_password="WrongPassword123",
            new_password="NewPassword123"
        )

        #deve dar erro pra validar senha antiga
        with pytest.raises(AppException) as exc:
            service.update_password(sample_user.id, data)

        assert exc.value.status_code == 400
        assert "Senha antiga incorreta" in exc.value.detail
        mock_repo.get_by_id.assert_called_once_with(sample_user.id)        


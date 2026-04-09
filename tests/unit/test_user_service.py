from unittest.mock import Mock

from app.services.user_service import UserService
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
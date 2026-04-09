from app.services.user_service import UserService


class TestUserServiceAuthenticate:
    
    def test_authenticate_success(self, in_memory_user_repository, sample_user, sample_user_plain_password):
        in_memory_user_repository.add_user(sample_user)
        
        service = UserService(db=None)
        service.repo = in_memory_user_repository
        
        result = service.authenticate(sample_user.email, sample_user_plain_password)
        
        assert result is not None
        assert result.email == sample_user.email
        assert result.name == sample_user.name
    
    def test_authenticate_user_not_found(self, in_memory_user_repository):
        service = UserService(db=None)
        service.repo = in_memory_user_repository
        
        result = service.authenticate("nonexistent@example.com", "AnyPassword123")
        
        assert result is None
    
    def test_authenticate_wrong_password(self, in_memory_user_repository, sample_user):
        in_memory_user_repository.add_user(sample_user)
        
        service = UserService(db=None)
        service.repo = in_memory_user_repository
        
        result = service.authenticate(sample_user.email, "WrongPassword123")
        
        assert result is None
    
    def test_authenticate_empty_password(self, in_memory_user_repository, sample_user):
        in_memory_user_repository.add_user(sample_user)
        
        service = UserService(db=None)
        service.repo = in_memory_user_repository
        
        result = service.authenticate(sample_user.email, "")
        
        assert result is None
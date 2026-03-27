import pytest
from app.schemas.user import UserCreate
from pydantic import ValidationError


def test_user_creation():
    '''
    É para dar certo criar o usuário que segue todos critérios de senha e suas informações ficarão salvas
    '''
    user = UserCreate(email='john@gmail.com', name='John', password='AAAabb888AAAAAAAA')
    assert user.email == 'john@gmail.com'
    assert user.name == 'John'
    assert user.password == 'AAAabb888AAAAAAAA'
    
def test_only_char():
    '''
    É para dar erro quando eu crio um user com uma senha que não possui nenhum número
    '''
    with pytest.raises(ValidationError) as erro:
        UserCreate(email='john@gmail.com', name='John', password='AaBbCcDdEe')

    print(erro.value)


def test_only_upper():
    '''
    É para dar erro quando eu crio um user com uma senha que só possui caracteres maiúsculos
    '''
    with pytest.raises(ValidationError) as erro:
        UserCreate(email='john@gmail.com', name='John', password='AAAAAAAAAAAAA')

    print(erro.value)    


def test_only_lower():
    '''
    É para dar erro quando eu crio um user com uma senha que só possui caracteres minúsculos
    '''
    with pytest.raises(ValidationError) as erro:
        UserCreate(email='john@gmail.com', name='John', password='aaaaaaaaaaaaaa')

    print(erro.value)        
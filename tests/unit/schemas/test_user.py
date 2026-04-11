import unittest
from app.schemas.user import UserCreate
from pydantic import ValidationError


class TestUserSchema(unittest.TestCase):
    
    def test_user_creation(self):
        '''
        É para dar certo criar o usuário que segue todos critérios de senha e suas informações ficarão salvas
        '''
        user = UserCreate(email='john@gmail.com', name='John', password='AAAabb888AAAAAAAA')
        self.assertEqual(user.email, 'john@gmail.com')
        self.assertEqual(user.name, 'John')
        self.assertEqual(user.password, 'AAAabb888AAAAAAAA')
        
    def test_only_char(self):
        '''
        É para dar erro quando eu crio um user com uma senha que não possui nenhum número
        '''
        with self.assertRaises(ValidationError):
            UserCreate(email='john@gmail.com', name='John', password='AaBbCcDdEe')

    def test_only_upper(self):
        '''
        É para dar erro quando eu crio um user com uma senha que só possui caracteres maiúsculos
        '''
        with self.assertRaises(ValidationError):
            UserCreate(email='john@gmail.com', name='John', password='AAAAAAAAAAAAA')

    def test_wrong_email(self):
        '''
        É necessário que dê erro quando eu crio um user com um email incorreto (sem arroba)
        '''
        with self.assertRaises(ValidationError):
            UserCreate(email='john', name='John', password='aAa!2341aaaaaaaaa')

    def test_name_with_spaces(self):
        '''
        É necessário que dê certo quando eu crio um user com um nome com espaços
        '''
        user = UserCreate(
            email='john@gmail.com',
            name='John Doe Silva',
            password='AAAabb888AAAAAAAA'
        )
        self.assertEqual(user.name, 'John Doe Silva')

    def test_missing_name(self):
        '''
        É necessário que dê erro quando eu crio um user sem nome
        '''    
        with self.assertRaises(ValidationError):
            UserCreate(
                email='john@gmail.com',
                password='AAAabb888AAAAAAAA'
            )        
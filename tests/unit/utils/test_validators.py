import unittest

from app.utils.validators import validate_password_strength


class TestValidators(unittest.TestCase):
    def test_validate_password_strength_success_valid_password(self):
        password = "Senha123"

        self.assertEqual(validate_password_strength(password), password)

    def test_validate_password_strength_success_complex_password(self):
        password = "StrongPass1"

        self.assertEqual(validate_password_strength(password), password)

    def test_validate_password_strength_failure_short_password(self):
        with self.assertRaises(ValueError) as context:
            validate_password_strength("S1aB2c")

        self.assertEqual(
            str(context.exception),
            "Senha deve ter pelo menos 8 caracteres",
        )

    def test_validate_password_strength_failure_missing_uppercase(self):
        with self.assertRaises(ValueError) as context:
            validate_password_strength("senha1234")

        self.assertEqual(
            str(context.exception),
            "Senha deve conter pelo menos uma letra maiúscula",
        )

import pytest

from app.utils.validators import validate_password_strength


def test_validate_password_strength_success_valid_password():
    password = "Senha123"

    assert validate_password_strength(password) == password


def test_validate_password_strength_success_complex_password():
    password = "StrongPass1"

    assert validate_password_strength(password) == password


def test_validate_password_strength_failure_short_password():
    with pytest.raises(ValueError, match="Senha deve ter pelo menos 8 caracteres"):
        validate_password_strength("S1aB2c")


def test_validate_password_strength_failure_missing_uppercase():
    with pytest.raises(ValueError, match="Senha deve conter pelo menos uma letra maiúscula"):
        validate_password_strength("senha1234")

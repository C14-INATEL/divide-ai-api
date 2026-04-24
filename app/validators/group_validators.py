def validate_group_name(v: str | None) -> str | None:
    if v is None:
        return v
    v = v.strip()
    if len(v) < 1:
        raise ValueError("Nome não pode ser vazio")
    if len(v) > 100:
        raise ValueError("Nome não pode ter mais de 100 caracteres")
    return v


def validate_group_name_required(v: str) -> str:
    result = validate_group_name(v)
    assert result is not None
    return result
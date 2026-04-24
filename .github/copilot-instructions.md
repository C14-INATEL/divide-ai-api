# Copilot Instructions — DivideAI

## Project Overview

DivideAI is a REST API for managing shared expenses among multiple users.
Users join groups, register expenses, and the system automatically calculates
balances and debts between participants.

**Stack:** Python 3.11+ · FastAPI · SQLAlchemy 2.0 · PostgreSQL · Pydantic v2 · Alembic · bcrypt · PyJWT · uv

---

## Architecture

Strict three-layer architecture. Never skip layers.

```
Router → Service → Repository → Database
```

| Layer        | Location           | Responsibility                                              |
| ------------ | ------------------ | ----------------------------------------------------------- |
| `routers/`   | HTTP boundary      | Parse request, call service, return response. No logic.    |
| `services/`  | Business logic     | Rules, validations, orchestration. No direct DB access.    |
| `repositories/` | Data access     | SQLAlchemy queries only. No business rules.                |
| `models/`    | ORM definitions    | SQLAlchemy table mappings. No methods with business logic. |
| `schemas/`   | Contracts          | Pydantic input/output. No DB access.                       |
| `utils/`     | Shared utilities   | e.g. `security.py` for bcrypt/JWT helpers.                |
| `database.py` | DB setup          | Engine, SessionLocal, `get_db` dependency.                |
| `config.py`  | Settings           | `pydantic-settings` reading from `.env`.                  |

**Hard rules:**
- Routers NEVER import repositories directly.
- Business rules NEVER live in routers or repositories.
- Repositories NEVER contain conditionals based on business rules.
- Models are pure ORM — no service calls, no Pydantic imports.

---

## Domain & Business Rules

### Core Concepts

- **Group**: shared financial context; has a `creator_id` and N members.
- **GroupMember**: explicit N:M join table between `User` and `Group`; carries `joined_at`.
- **Expense**: a payment made by one user (`paid_by`) inside a group.
- **ExpenseSplit**: how much each participant owes for a given expense.
- **Settlement**: a payment between two users to settle debts.

### Invariants — Always Enforce

1. Every expense belongs to exactly one group.
2. Every expense has a `paid_by` user who must be a member of that group.
3. `sum(ExpenseSplit.amount for split in expense.splits) == expense.total_amount` — enforce in service before persisting.
4. All monetary values use `Decimal`, never `float`. Import from `decimal` module.
5. Settlement amounts must be positive and reference users who are members of the same group.
6. A user may only act on a group they are a member of.

### Precision Rule

```python
# Always use Decimal for money
from decimal import Decimal, ROUND_HALF_UP

amount = Decimal("19.99")
split = amount / Decimal(str(n_participants))
split = split.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
```

Never use `float` or `/` on raw Python ints for money calculations.

---

## Code Conventions

### Naming

- Files: `snake_case.py`
- Classes: `PascalCase`
- Functions/variables: `snake_case`
- Constants: `UPPER_SNAKE_CASE`
- UUIDs as primary keys: always named `id`, typed as `uuid.UUID`

### Python Style

- Python 3.11+ syntax — use `match`, `X | Y` unions, `TYPE_CHECKING` guards.
- Always use explicit type annotations. Never use `Any` unless truly unavoidable and commented.
- Prefer `async def` for all route handlers and service methods that touch I/O.
- Use `async with` / `await` consistently — no mixing sync/async DB calls.
- Raise domain-specific exceptions in services; routers convert them to HTTP responses.
- Never swallow exceptions silently.

### FastAPI Patterns

```python
# Router — thin, no logic
@router.post("/groups/{group_id}/expenses", response_model=ExpenseOut, status_code=201)
async def create_expense(
    group_id: uuid.UUID,
    payload: ExpenseCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await expense_service.create(db, group_id, current_user.id, payload)
```

```python
# Service — owns the rule
async def create(
    db: AsyncSession,
    group_id: uuid.UUID,
    user_id: uuid.UUID,
    payload: ExpenseCreate,
) -> Expense:
    await _assert_member(db, group_id, user_id)
    _assert_splits_sum(payload)          # raises ValueError if invalid
    expense = await expense_repo.insert(db, group_id, user_id, payload)
    return expense
```

```python
# Repository — pure data
async def insert(db: AsyncSession, ...) -> Expense:
    expense = Expense(...)
    db.add(expense)
    await db.flush()
    return expense
```

### Pydantic Schemas

- Separate schemas for input (`Create`, `Update`) and output (`Out`/`Response`).
- Use `model_config = ConfigDict(from_attributes=True)` on all output schemas.
- Monetary fields typed as `Decimal` in schemas, never `float`.

```python
class ExpenseSplitOut(BaseModel):
    user_id: uuid.UUID
    amount: Decimal

    model_config = ConfigDict(from_attributes=True)
```

### Models

- All models inherit a shared `Base` with `id: UUID`, `created_at`, `updated_at`.
- Register every new model in `app/models/__init__.py` so Alembic detects it.
- No business logic inside model methods.

---

## Error Handling

Define custom exceptions in `app/exceptions.py`:

```python
class NotFoundError(Exception): ...
class ForbiddenError(Exception): ...
class BusinessRuleError(Exception): ...
```

Routers catch and convert:

```python
except NotFoundError as e:
    raise HTTPException(status_code=404, detail=str(e))
except ForbiddenError as e:
    raise HTTPException(status_code=403, detail=str(e))
except BusinessRuleError as e:
    raise HTTPException(status_code=422, detail=str(e))
```

---

## Testing

- **pytest** for all tests (services, routers, schemas).
- Unit tests must mock repositories — never hit the real DB.
- Use `pytest-mock` (`mocker` fixture) for patching.
- Monetary assertions must compare `Decimal` to `Decimal`.
- Mark tests: `@pytest.mark.unit` or `@pytest.mark.integration`.

```python
# Example service unit test
def test_splits_must_sum_to_total(mocker):
    payload = ExpenseCreate(
        total_amount=Decimal("30.00"),
        splits=[
            ExpenseSplitCreate(user_id=uid1, amount=Decimal("10.00")),
            ExpenseSplitCreate(user_id=uid2, amount=Decimal("10.00")),
            # missing 10.00 — should raise
        ],
    )
    with pytest.raises(BusinessRuleError, match="splits"):
        expense_service._assert_splits_sum(payload)
```

Run all tests:

```bash
pytest -v && python -m unittest discover tests -v
```

---

## Migrations (Alembic)

```bash
uv run alembic revision --autogenerate -m "short_description"
uv run alembic upgrade head
uv run alembic downgrade -1
```

- Always register new models in `app/models/__init__.py` before generating migrations.
- Migration messages in English, snake_case, concise: `add_expense_split_table`.

---

## What to Avoid

- `float` for any monetary value — use `Decimal`.
- Business logic in routers or repositories.
- Direct repository access from routers.
- Unnamed magic numbers — extract to named constants.
- `Any` type without a comment explaining why.
- Mutable default arguments.
- `SELECT *` — always select explicit columns or load via ORM relationships.
- Storing raw passwords — always hash with bcrypt before persisting.
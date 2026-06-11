from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.database import get_db
from app.models.debt import Debt
from app.models.debt_participant import DebtParticipant
from app.models.enums.debt_split_type import DebtSplitType
from app.models.enums.participant_status import ParticipantStatus
from app.models.user import User
from app.routers.debts import router, get_current_user


DEBT_ID = UUID("dddddddd-dddd-dddd-dddd-dddddddddddd")
GROUP_ID = UUID("cccccccc-cccc-cccc-cccc-cccccccccccc")
USER_ID = UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb")


def _make_user() -> User:
    user = User(
        email="participant@example.com",
        name="Participant User",
        password="hashed-password",
        pix_key=None,
        pix_key_type=None,
    )
    user.id = USER_ID
    return user


def _make_debt() -> Debt:
    debt = Debt(
        group_id=GROUP_ID,
        creator_id=USER_ID,
        title="Lunch",
        description="Shared lunch",
        total_amount=Decimal("100.00"),
        split_type=DebtSplitType.HOMOGENEA.value,
        status="pendente",
    )
    debt.id = DEBT_ID
    debt.created_at = datetime(2026, 6, 10, tzinfo=timezone.utc)
    debt.updated_at = datetime(2026, 6, 10, tzinfo=timezone.utc)

    participant = DebtParticipant(
        user_id=USER_ID,
        percentage=Decimal("100.00"),
        amount=Decimal("100.00"),
        status=ParticipantStatus.PENDENTE.value,
        has_proof=False,
    )
    participant.user = _make_user()
    debt.participants = [participant]
    return debt


def test_list_debts_includes_participants(mocker):
    app = FastAPI()
    app.include_router(router)

    current_user = _make_user()
    mock_db = mocker.Mock()
    mock_service = mocker.Mock()
    mock_service.list_by_group.return_value = [_make_debt()]

    mocker.patch("app.routers.debts.DebtService", return_value=mock_service)

    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_user] = lambda: current_user

    client = TestClient(app)
    response = client.get(f"/debts/?group_id={GROUP_ID}")

    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 1
    assert payload[0]["id"] == str(DEBT_ID)
    assert payload[0]["participants"][0]["user_id"] == str(USER_ID)
    assert payload[0]["participants"][0]["user"]["email"] == "participant@example.com"

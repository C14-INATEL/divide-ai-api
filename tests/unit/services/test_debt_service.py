from decimal import Decimal
from unittest.mock import Mock, patch
from uuid import UUID

import pytest

from app.exceptions import AppException
from app.models.debt import Debt
from app.models.debt_participant import DebtParticipant
from app.models.enums.debt_split_type import DebtSplitType
from app.models.enums.participant_status import ParticipantStatus
from app.models.group_member import GroupMember
from app.repositories.debt_repository import DebtRepository
from app.repositories.group_repository import GroupRepository
from app.schemas.debt import DebtCreate, DebtParticipantInput, DebtUpdate
from app.services.debt_service import DebtService
from tests.conftest import CREATOR_ID, OTHER_USER_ID, GROUP_ID

DEBT_ID = UUID("dddddddd-dddd-dddd-dddd-dddddddddddd")
THIRD_USER_ID = UUID("eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee")


def _make_debt(
    creator_id: UUID = CREATOR_ID,
    group_id: UUID = GROUP_ID,
    status: str = "pendente",
) -> Debt:
    debt = Debt(
        group_id=group_id,
        creator_id=creator_id,
        title="Test Debt",
        total_amount=Decimal("100.00"),
        split_type=DebtSplitType.HOMOGENEA.value,
        status=status,
    )
    debt.id = DEBT_ID
    debt.participants = []
    return debt


def _make_participant(
    user_id: UUID = OTHER_USER_ID,
    status: str = ParticipantStatus.PENDENTE.value,
    has_proof: bool = False,
    proof_url: str | None = None,
) -> DebtParticipant:
    p = DebtParticipant(
        user_id=user_id,
        percentage=Decimal("100.00"),
        amount=Decimal("100.00"),
        status=status,
        has_proof=has_proof,
    )
    p.proof_url = proof_url
    return p


def _make_member(group_id: UUID = GROUP_ID, user_id: UUID = CREATOR_ID) -> GroupMember:
    return GroupMember(group_id=group_id, user_id=user_id)


def _make_service(mock_db_session, group_repo, debt_repo) -> DebtService:
    service = DebtService(mock_db_session)
    service.group_repo = group_repo
    service.debt_repo = debt_repo
    return service


def _make_group_mock(*user_ids: UUID) -> Mock:
    group = Mock()
    group.id = GROUP_ID
    group.members = []
    for uid in user_ids:
        member = Mock()
        member.user = Mock()
        member.user.id = uid
        group.members.append(member)
    return group


@pytest.fixture
def mock_group_repo(mocker):
    return mocker.Mock(spec=GroupRepository)


@pytest.fixture
def mock_debt_repo(mocker):
    return mocker.Mock(spec=DebtRepository)


class TestDebtServiceCreate:

    def test_create_group_not_found(self, mock_db_session, mock_group_repo, mock_debt_repo):
        mock_group_repo.get_by_id.return_value = None

        service = _make_service(mock_db_session, mock_group_repo, mock_debt_repo)
        data = DebtCreate(
            group_id=GROUP_ID,
            title="Test",
            total_amount=Decimal("100.00"),
            split_type=DebtSplitType.HOMOGENEA,
        )

        with pytest.raises(AppException) as exc:
            service.create(data, creator_id=CREATOR_ID)

        assert exc.value.status_code == 404

    def test_create_creator_not_member(self, mock_db_session, mock_group_repo, mock_debt_repo):
        group = _make_group_mock(OTHER_USER_ID)
        mock_group_repo.get_by_id.return_value = group
        mock_group_repo.get_member.return_value = None

        service = _make_service(mock_db_session, mock_group_repo, mock_debt_repo)
        data = DebtCreate(
            group_id=GROUP_ID,
            title="Test",
            total_amount=Decimal("100.00"),
            split_type=DebtSplitType.HOMOGENEA,
        )

        with pytest.raises(AppException) as exc:
            service.create(data, creator_id=CREATOR_ID)

        assert exc.value.status_code == 403

    def test_create_homogenea_no_explicit_participants_no_other_members(
        self, mock_db_session, mock_group_repo, mock_debt_repo
    ):
        group = _make_group_mock(CREATOR_ID)
        mock_group_repo.get_by_id.return_value = group
        mock_group_repo.get_member.return_value = _make_member(user_id=CREATOR_ID)

        service = _make_service(mock_db_session, mock_group_repo, mock_debt_repo)
        data = DebtCreate(
            group_id=GROUP_ID,
            title="Test",
            total_amount=Decimal("100.00"),
            split_type=DebtSplitType.HOMOGENEA,
        )

        with pytest.raises(AppException) as exc:
            service.create(data, creator_id=CREATOR_ID)

        assert exc.value.status_code == 422

    def test_create_heterogenea_missing_percentage(
        self, mock_db_session, mock_group_repo, mock_debt_repo
    ):
        group = _make_group_mock(CREATOR_ID, OTHER_USER_ID)
        mock_group_repo.get_by_id.return_value = group
        mock_group_repo.get_member.return_value = _make_member(user_id=CREATOR_ID)

        service = _make_service(mock_db_session, mock_group_repo, mock_debt_repo)
        data = DebtCreate(
            group_id=GROUP_ID,
            title="Test",
            total_amount=Decimal("100.00"),
            split_type=DebtSplitType.HETEROGENEA,
            participants=[DebtParticipantInput(user_id=OTHER_USER_ID, percentage=None)],
        )

        with pytest.raises(AppException) as exc:
            service.create(data, creator_id=CREATOR_ID)

        assert exc.value.status_code == 422

    def test_create_heterogenea_percentages_not_summing_to_100(
        self, mock_db_session, mock_group_repo, mock_debt_repo
    ):
        group = _make_group_mock(CREATOR_ID, OTHER_USER_ID, THIRD_USER_ID)
        mock_group_repo.get_by_id.return_value = group
        mock_group_repo.get_member.return_value = _make_member(user_id=CREATOR_ID)

        service = _make_service(mock_db_session, mock_group_repo, mock_debt_repo)
        data = DebtCreate(
            group_id=GROUP_ID,
            title="Test",
            total_amount=Decimal("100.00"),
            split_type=DebtSplitType.HETEROGENEA,
            participants=[
                DebtParticipantInput(user_id=OTHER_USER_ID, percentage=Decimal("60.00")),
                DebtParticipantInput(user_id=THIRD_USER_ID, percentage=Decimal("30.00")),
            ],
        )

        with pytest.raises(AppException) as exc:
            service.create(data, creator_id=CREATOR_ID)

        assert exc.value.status_code == 422

    def test_create_participant_not_group_member(
        self, mock_db_session, mock_group_repo, mock_debt_repo
    ):
        group = _make_group_mock(CREATOR_ID, OTHER_USER_ID)
        mock_group_repo.get_by_id.return_value = group

        def get_member_side_effect(group_id, user_id):
            if user_id == CREATOR_ID:
                return _make_member(user_id=CREATOR_ID)
            return None

        mock_group_repo.get_member.side_effect = get_member_side_effect

        service = _make_service(mock_db_session, mock_group_repo, mock_debt_repo)
        data = DebtCreate(
            group_id=GROUP_ID,
            title="Test",
            total_amount=Decimal("100.00"),
            split_type=DebtSplitType.HETEROGENEA,
            participants=[
                DebtParticipantInput(user_id=OTHER_USER_ID, percentage=Decimal("100.00")),
            ],
        )

        with pytest.raises(AppException) as exc:
            service.create(data, creator_id=CREATOR_ID)

        assert exc.value.status_code == 422

    def test_create_homogenea_success(self, mock_db_session, mock_group_repo, mock_debt_repo):
        group = _make_group_mock(CREATOR_ID, OTHER_USER_ID)
        debt = _make_debt()
        mock_group_repo.get_by_id.return_value = group
        mock_group_repo.get_member.return_value = _make_member()
        mock_debt_repo.insert.return_value = None
        mock_db_session.commit.return_value = None
        mock_db_session.refresh.return_value = None

        service = _make_service(mock_db_session, mock_group_repo, mock_debt_repo)
        data = DebtCreate(
            group_id=GROUP_ID,
            title="Almoço",
            total_amount=Decimal("100.00"),
            split_type=DebtSplitType.HOMOGENEA,
            participants=[DebtParticipantInput(user_id=OTHER_USER_ID)],
        )

        service.create(data, creator_id=CREATOR_ID)

        mock_debt_repo.insert.assert_called_once()
        mock_db_session.commit.assert_called_once()

    def test_create_heterogenea_success(self, mock_db_session, mock_group_repo, mock_debt_repo):
        group = _make_group_mock(CREATOR_ID, OTHER_USER_ID, THIRD_USER_ID)
        mock_group_repo.get_by_id.return_value = group
        mock_group_repo.get_member.return_value = _make_member()
        mock_db_session.commit.return_value = None
        mock_db_session.refresh.return_value = None

        service = _make_service(mock_db_session, mock_group_repo, mock_debt_repo)
        data = DebtCreate(
            group_id=GROUP_ID,
            title="Jantar",
            total_amount=Decimal("100.00"),
            split_type=DebtSplitType.HETEROGENEA,
            participants=[
                DebtParticipantInput(user_id=OTHER_USER_ID, percentage=Decimal("70.00")),
                DebtParticipantInput(user_id=THIRD_USER_ID, percentage=Decimal("30.00")),
            ],
        )

        service.create(data, creator_id=CREATOR_ID)

        mock_debt_repo.insert.assert_called_once()


class TestDebtServiceListByGroup:

    def test_list_not_member(self, mock_db_session, mock_group_repo, mock_debt_repo):
        mock_group_repo.get_member.return_value = None

        service = _make_service(mock_db_session, mock_group_repo, mock_debt_repo)

        with pytest.raises(AppException) as exc:
            service.list_by_group(GROUP_ID, current_user_id=CREATOR_ID)

        assert exc.value.status_code == 403

    def test_list_success(self, mock_db_session, mock_group_repo, mock_debt_repo):
        mock_group_repo.get_member.return_value = _make_member()
        mock_debt_repo.list_by_group.return_value = [_make_debt(), _make_debt()]

        service = _make_service(mock_db_session, mock_group_repo, mock_debt_repo)
        result = service.list_by_group(GROUP_ID, current_user_id=CREATOR_ID)

        assert len(result) == 2
        mock_debt_repo.list_by_group.assert_called_once_with(GROUP_ID)


class TestDebtServiceGetById:

    def test_get_debt_not_found(self, mock_db_session, mock_group_repo, mock_debt_repo):
        mock_debt_repo.get_by_id.return_value = None

        service = _make_service(mock_db_session, mock_group_repo, mock_debt_repo)

        with pytest.raises(AppException) as exc:
            service.get_by_id(DEBT_ID, current_user_id=CREATOR_ID)

        assert exc.value.status_code == 404

    def test_get_debt_user_not_member(self, mock_db_session, mock_group_repo, mock_debt_repo):
        mock_debt_repo.get_by_id.return_value = _make_debt()
        mock_group_repo.get_member.return_value = None

        service = _make_service(mock_db_session, mock_group_repo, mock_debt_repo)

        with pytest.raises(AppException) as exc:
            service.get_by_id(DEBT_ID, current_user_id=OTHER_USER_ID)

        assert exc.value.status_code == 403

    def test_get_debt_success(self, mock_db_session, mock_group_repo, mock_debt_repo):
        debt = _make_debt()
        mock_debt_repo.get_by_id.return_value = debt
        mock_group_repo.get_member.return_value = _make_member()

        service = _make_service(mock_db_session, mock_group_repo, mock_debt_repo)
        result = service.get_by_id(DEBT_ID, current_user_id=CREATOR_ID)

        assert result is debt


class TestDebtServiceUpdate:

    def test_update_debt_not_found(self, mock_db_session, mock_group_repo, mock_debt_repo):
        mock_debt_repo.get_by_id.return_value = None

        service = _make_service(mock_db_session, mock_group_repo, mock_debt_repo)

        with pytest.raises(AppException) as exc:
            service.update(DEBT_ID, DebtUpdate(title="new"), current_user_id=CREATOR_ID)

        assert exc.value.status_code == 404

    def test_update_not_creator(self, mock_db_session, mock_group_repo, mock_debt_repo):
        mock_debt_repo.get_by_id.return_value = _make_debt(creator_id=CREATOR_ID)

        service = _make_service(mock_db_session, mock_group_repo, mock_debt_repo)

        with pytest.raises(AppException) as exc:
            service.update(DEBT_ID, DebtUpdate(title="new"), current_user_id=OTHER_USER_ID)

        assert exc.value.status_code == 403

    def test_update_non_monetary_allowed_even_when_paid(
        self, mock_db_session, mock_group_repo, mock_debt_repo
    ):
        debt = _make_debt(creator_id=CREATOR_ID)
        debt.participants = [_make_participant(status=ParticipantStatus.PAGO.value)]
        mock_debt_repo.get_by_id.return_value = debt
        mock_debt_repo.update.return_value = debt

        service = _make_service(mock_db_session, mock_group_repo, mock_debt_repo)
        result = service.update(
            DEBT_ID, DebtUpdate(title="updated title"), current_user_id=CREATOR_ID
        )

        assert result.title == "updated title"
        mock_debt_repo.update.assert_called_once_with(debt)

    def test_update_monetary_blocked_when_participant_not_pendente(
        self, mock_db_session, mock_group_repo, mock_debt_repo
    ):
        debt = _make_debt(creator_id=CREATOR_ID)
        debt.participants = [_make_participant(status=ParticipantStatus.PAGO.value)]
        mock_debt_repo.get_by_id.return_value = debt

        service = _make_service(mock_db_session, mock_group_repo, mock_debt_repo)

        with pytest.raises(AppException) as exc:
            service.update(
                DEBT_ID, DebtUpdate(total_amount=Decimal("50.00")), current_user_id=CREATOR_ID
            )

        assert exc.value.status_code == 422

    def test_update_monetary_success_all_pendente(
        self, mock_db_session, mock_group_repo, mock_debt_repo
    ):
        debt = _make_debt(creator_id=CREATOR_ID)
        debt.participants = [_make_participant(status=ParticipantStatus.PENDENTE.value)]
        mock_debt_repo.get_by_id.return_value = debt
        mock_debt_repo.update.return_value = debt
        mock_group_repo.get_member.return_value = _make_member()

        service = _make_service(mock_db_session, mock_group_repo, mock_debt_repo)
        result = service.update(
            DEBT_ID,
            DebtUpdate(
                total_amount=Decimal("200.00"),
                participants=[DebtParticipantInput(user_id=OTHER_USER_ID)],
            ),
            current_user_id=CREATOR_ID,
        )

        assert result.total_amount == Decimal("200.00")
        assert len(result.participants) == 1
        assert result.participants[0].amount == Decimal("200.00")
        mock_debt_repo.update.assert_called_once_with(debt)

    def test_update_heterogenea_missing_percentage(
        self, mock_db_session, mock_group_repo, mock_debt_repo
    ):
        debt = _make_debt(creator_id=CREATOR_ID)
        debt.participants = [_make_participant(status=ParticipantStatus.PENDENTE.value)]
        mock_debt_repo.get_by_id.return_value = debt
        mock_group_repo.get_member.return_value = _make_member()

        service = _make_service(mock_db_session, mock_group_repo, mock_debt_repo)

        with pytest.raises(AppException) as exc:
            service.update(
                DEBT_ID,
                DebtUpdate(
                    split_type=DebtSplitType.HETEROGENEA,
                    participants=[DebtParticipantInput(user_id=OTHER_USER_ID, percentage=None)],
                ),
                current_user_id=CREATOR_ID,
            )

        assert exc.value.status_code == 422


class TestDebtServiceDelete:

    def test_delete_debt_not_found(self, mock_db_session, mock_group_repo, mock_debt_repo):
        mock_debt_repo.get_by_id.return_value = None

        service = _make_service(mock_db_session, mock_group_repo, mock_debt_repo)

        with pytest.raises(AppException) as exc:
            service.delete(DEBT_ID, current_user_id=CREATOR_ID)

        assert exc.value.status_code == 404

    def test_delete_not_creator(self, mock_db_session, mock_group_repo, mock_debt_repo):
        debt = _make_debt(creator_id=CREATOR_ID)
        mock_debt_repo.get_by_id.return_value = debt

        service = _make_service(mock_db_session, mock_group_repo, mock_debt_repo)

        with pytest.raises(AppException) as exc:
            service.delete(DEBT_ID, current_user_id=OTHER_USER_ID)

        assert exc.value.status_code == 403

    @pytest.mark.parametrize(
        "status",
        [ParticipantStatus.PAGO.value, ParticipantStatus.CONFIRMADO.value],
    )
    def test_delete_blocked_when_payment_sent_or_confirmed(
        self, mock_db_session, mock_group_repo, mock_debt_repo, status
    ):
        debt = _make_debt(creator_id=CREATOR_ID)
        debt.participants = [_make_participant(status=status)]
        mock_debt_repo.get_by_id.return_value = debt

        service = _make_service(mock_db_session, mock_group_repo, mock_debt_repo)

        with pytest.raises(AppException) as exc:
            service.delete(DEBT_ID, current_user_id=CREATOR_ID)

        assert exc.value.status_code == 422
        mock_debt_repo.delete.assert_not_called()

    def test_delete_success_with_pending_participants(
        self, mock_db_session, mock_group_repo, mock_debt_repo
    ):
        debt = _make_debt(creator_id=CREATOR_ID)
        debt.participants = [_make_participant(status=ParticipantStatus.PENDENTE.value)]
        mock_debt_repo.get_by_id.return_value = debt

        service = _make_service(mock_db_session, mock_group_repo, mock_debt_repo)
        service.delete(DEBT_ID, current_user_id=CREATOR_ID)

        mock_debt_repo.delete.assert_called_once_with(debt)

    def test_delete_success(self, mock_db_session, mock_group_repo, mock_debt_repo):
        debt = _make_debt(creator_id=CREATOR_ID)
        debt.participants = []
        mock_debt_repo.get_by_id.return_value = debt

        service = _make_service(mock_db_session, mock_group_repo, mock_debt_repo)
        service.delete(DEBT_ID, current_user_id=CREATOR_ID)

        mock_debt_repo.delete.assert_called_once_with(debt)


class TestDebtServiceUploadProof:

    def _make_file(self, content_type: str = "image/jpeg", filename: str = "proof.jpg"):
        f = Mock()
        f.content_type = content_type
        f.filename = filename
        f.file = Mock()
        f.file.read.return_value = b"content"
        return f

    def test_upload_debt_not_found(self, mock_db_session, mock_group_repo, mock_debt_repo):
        mock_debt_repo.get_by_id.return_value = None

        service = _make_service(mock_db_session, mock_group_repo, mock_debt_repo)

        with pytest.raises(AppException) as exc:
            service.upload_proof(DEBT_ID, current_user_id=OTHER_USER_ID, file=self._make_file())

        assert exc.value.status_code == 404

    def test_upload_user_not_participant(self, mock_db_session, mock_group_repo, mock_debt_repo):
        mock_debt_repo.get_by_id.return_value = _make_debt()
        mock_debt_repo.get_participant.return_value = None

        service = _make_service(mock_db_session, mock_group_repo, mock_debt_repo)

        with pytest.raises(AppException) as exc:
            service.upload_proof(DEBT_ID, current_user_id=OTHER_USER_ID, file=self._make_file())

        assert exc.value.status_code == 403

    def test_upload_invalid_file_type(self, mock_db_session, mock_group_repo, mock_debt_repo):
        mock_debt_repo.get_by_id.return_value = _make_debt()
        mock_debt_repo.get_participant.return_value = _make_participant()

        service = _make_service(mock_db_session, mock_group_repo, mock_debt_repo)

        with pytest.raises(AppException) as exc:
            service.upload_proof(
                DEBT_ID, current_user_id=OTHER_USER_ID, file=self._make_file(content_type="text/plain")
            )

        assert exc.value.status_code == 422

    @patch("app.services.debt_service.get_storage")
    def test_upload_success(self, mock_get_storage, mock_db_session, mock_group_repo, mock_debt_repo):
        participant = _make_participant()
        mock_debt_repo.get_by_id.return_value = _make_debt()
        mock_debt_repo.get_participant.return_value = participant

        mock_get_storage.return_value.upload.return_value = "https://pub-xxxx.r2.dev/debts/key.jpg"

        service = _make_service(mock_db_session, mock_group_repo, mock_debt_repo)
        result = service.upload_proof(
            DEBT_ID, current_user_id=OTHER_USER_ID, file=self._make_file()
        )

        assert result.has_proof is True
        assert result.status == ParticipantStatus.PAGO.value
        assert result.proof_url == "https://pub-xxxx.r2.dev/debts/key.jpg"
        mock_get_storage.return_value.upload.assert_called_once()
        mock_debt_repo.update_participant.assert_called_once_with(participant)

    @patch("app.services.debt_service.get_storage")
    def test_upload_exceeds_size_limit(self, mock_get_storage, mock_db_session, mock_group_repo, mock_debt_repo):
        mock_debt_repo.get_by_id.return_value = _make_debt()
        mock_debt_repo.get_participant.return_value = _make_participant()

        oversized = self._make_file()
        oversized.file.read.return_value = b"x" * (5 * 1024 * 1024 + 1)

        service = _make_service(mock_db_session, mock_group_repo, mock_debt_repo)

        with pytest.raises(AppException) as exc:
            service.upload_proof(DEBT_ID, current_user_id=OTHER_USER_ID, file=oversized)

        assert exc.value.status_code == 422
        mock_get_storage.return_value.upload.assert_not_called()


class TestDebtServiceConfirmPayment:

    def test_confirm_debt_not_found(self, mock_db_session, mock_group_repo, mock_debt_repo):
        mock_debt_repo.get_by_id.return_value = None

        service = _make_service(mock_db_session, mock_group_repo, mock_debt_repo)

        with pytest.raises(AppException) as exc:
            service.confirm_payment(DEBT_ID, participant_user_id=OTHER_USER_ID, current_user_id=CREATOR_ID)

        assert exc.value.status_code == 404

    def test_confirm_not_creator(self, mock_db_session, mock_group_repo, mock_debt_repo):
        mock_debt_repo.get_by_id.return_value = _make_debt(creator_id=CREATOR_ID)

        service = _make_service(mock_db_session, mock_group_repo, mock_debt_repo)

        with pytest.raises(AppException) as exc:
            service.confirm_payment(DEBT_ID, participant_user_id=OTHER_USER_ID, current_user_id=OTHER_USER_ID)

        assert exc.value.status_code == 403

    def test_confirm_participant_not_found(self, mock_db_session, mock_group_repo, mock_debt_repo):
        mock_debt_repo.get_by_id.return_value = _make_debt(creator_id=CREATOR_ID)
        mock_debt_repo.get_participant.return_value = None

        service = _make_service(mock_db_session, mock_group_repo, mock_debt_repo)

        with pytest.raises(AppException) as exc:
            service.confirm_payment(DEBT_ID, participant_user_id=OTHER_USER_ID, current_user_id=CREATOR_ID)

        assert exc.value.status_code == 404

    def test_confirm_participant_has_not_paid(self, mock_db_session, mock_group_repo, mock_debt_repo):
        mock_debt_repo.get_by_id.return_value = _make_debt(creator_id=CREATOR_ID)
        mock_debt_repo.get_participant.return_value = _make_participant(
            status=ParticipantStatus.PENDENTE.value
        )

        service = _make_service(mock_db_session, mock_group_repo, mock_debt_repo)

        with pytest.raises(AppException) as exc:
            service.confirm_payment(DEBT_ID, participant_user_id=OTHER_USER_ID, current_user_id=CREATOR_ID)

        assert exc.value.status_code == 422

    def test_confirm_success_debt_marked_paid_when_all_confirmed(
        self, mock_db_session, mock_group_repo, mock_debt_repo
    ):
        participant = _make_participant(status=ParticipantStatus.PAGO.value)
        debt = _make_debt(creator_id=CREATOR_ID)
        debt.participants = [participant]
        mock_debt_repo.get_by_id.return_value = debt
        mock_debt_repo.get_participant.return_value = participant

        service = _make_service(mock_db_session, mock_group_repo, mock_debt_repo)
        result = service.confirm_payment(
            DEBT_ID, participant_user_id=OTHER_USER_ID, current_user_id=CREATOR_ID
        )

        assert result.status == ParticipantStatus.CONFIRMADO.value
        assert debt.status == "pago"
        mock_db_session.commit.assert_called_once()

    def test_confirm_success_debt_not_fully_paid(
        self, mock_db_session, mock_group_repo, mock_debt_repo
    ):
        paid_participant = _make_participant(user_id=OTHER_USER_ID, status=ParticipantStatus.PAGO.value)
        pending_participant = _make_participant(user_id=THIRD_USER_ID, status=ParticipantStatus.PENDENTE.value)
        debt = _make_debt(creator_id=CREATOR_ID)
        debt.participants = [paid_participant, pending_participant]
        mock_debt_repo.get_by_id.return_value = debt
        mock_debt_repo.get_participant.return_value = paid_participant

        service = _make_service(mock_db_session, mock_group_repo, mock_debt_repo)
        service.confirm_payment(
            DEBT_ID, participant_user_id=OTHER_USER_ID, current_user_id=CREATOR_ID
        )

        assert debt.status == "pendente"
        mock_db_session.commit.assert_not_called()


class TestDebtServiceGetProof:

    def test_get_proof_debt_not_found(self, mock_db_session, mock_group_repo, mock_debt_repo):
        mock_debt_repo.get_by_id.return_value = None

        service = _make_service(mock_db_session, mock_group_repo, mock_debt_repo)

        with pytest.raises(AppException) as exc:
            service.get_proof(DEBT_ID, participant_user_id=OTHER_USER_ID, current_user_id=CREATOR_ID)

        assert exc.value.status_code == 404

    def test_get_proof_requester_not_member(self, mock_db_session, mock_group_repo, mock_debt_repo):
        mock_debt_repo.get_by_id.return_value = _make_debt()
        mock_group_repo.get_member.return_value = None

        service = _make_service(mock_db_session, mock_group_repo, mock_debt_repo)

        with pytest.raises(AppException) as exc:
            service.get_proof(DEBT_ID, participant_user_id=OTHER_USER_ID, current_user_id=CREATOR_ID)

        assert exc.value.status_code == 403

    def test_get_proof_participant_has_no_proof(self, mock_db_session, mock_group_repo, mock_debt_repo):
        mock_debt_repo.get_by_id.return_value = _make_debt()
        mock_group_repo.get_member.return_value = _make_member()
        mock_debt_repo.get_participant.return_value = _make_participant(proof_url=None)

        service = _make_service(mock_db_session, mock_group_repo, mock_debt_repo)

        with pytest.raises(AppException) as exc:
            service.get_proof(DEBT_ID, participant_user_id=OTHER_USER_ID, current_user_id=CREATOR_ID)

        assert exc.value.status_code == 404

    def test_get_proof_participant_not_found(self, mock_db_session, mock_group_repo, mock_debt_repo):
        mock_debt_repo.get_by_id.return_value = _make_debt()
        mock_group_repo.get_member.return_value = _make_member()
        mock_debt_repo.get_participant.return_value = None

        service = _make_service(mock_db_session, mock_group_repo, mock_debt_repo)

        with pytest.raises(AppException) as exc:
            service.get_proof(DEBT_ID, participant_user_id=OTHER_USER_ID, current_user_id=CREATOR_ID)

        assert exc.value.status_code == 404

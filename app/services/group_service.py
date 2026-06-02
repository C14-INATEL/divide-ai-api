import uuid
from sqlalchemy.orm import Session
from app.repositories.group_repository import GroupRepository
from app.repositories.user_repository import UserRepository
from app.schemas.group import GroupCreate, GroupUpdate
from app.models.group import Group
from app.models.group_member import GroupMember
from app.exceptions import AppException
from app.models.debt_participant import DebtParticipant
from app.models.debt import Debt
from sqlalchemy import and_


class GroupService:
    def __init__(self, db: Session):
        self.repo = GroupRepository(db)
        self.user_repo = UserRepository(db)
        self.db = db

    def create(self, data: GroupCreate, creator_id: uuid.UUID) -> Group:
        group = self.repo.create(
            name=data.name, creator_id=creator_id, description=data.description
        )
        self.repo.add_member(group_id=group.id, user_id=creator_id)

        added: set[uuid.UUID] = {creator_id}
        for user_id in data.added_users:
            if user_id in added:
                continue
            user = self.user_repo.get_by_id(user_id)
            if not user:
                raise AppException(
                    status_code=404, detail=f"Usuário não encontrado: {user_id}"
                )
            self.repo.add_member(group_id=group.id, user_id=user_id)
            added.add(user_id)

        created = self.repo.get_by_id(group.id)
        if not created:
            raise AppException(status_code=404, detail="Grupo não encontrado")
        created.is_owner = True
        return created

    def get_by_id(self, group_id: uuid.UUID, current_user_id: uuid.UUID) -> Group:
        group = self.repo.get_by_id(group_id)
        if not group:
            raise AppException(status_code=404, detail="Grupo não encontrado")
        member = self.repo.get_member(group_id, current_user_id)
        if not member:
            raise AppException(status_code=403, detail="Você não é membro deste grupo")
        group.is_owner = group.creator_id == current_user_id
        return group

    def list_by_user(self, user_id: uuid.UUID) -> list[Group]:
        groups = self.repo.get_groups_by_user(user_id)
        for group in groups:
            group.is_owner = group.creator_id == user_id
        return groups

    def update(
        self, group_id: uuid.UUID, data: GroupUpdate, current_user_id: uuid.UUID
    ) -> Group:
        group = self.repo.get_by_id(group_id)
        if not group:
            raise AppException(status_code=404, detail="Grupo não encontrado")
        if group.creator_id != current_user_id:
            raise AppException(
                status_code=403, detail="Apenas o criador pode editar o grupo"
            )
        if data.name is not None:
            group.name = data.name
        if data.description is not None:
            group.description = data.description
        updated = self.repo.update(group)
        updated.is_owner = updated.creator_id == current_user_id
        return updated

    def delete(self, group_id: uuid.UUID, current_user_id: uuid.UUID) -> None:
        group = self.repo.get_by_id(group_id)
        if not group:
            raise AppException(status_code=404, detail="Grupo não encontrado")
        if group.creator_id != current_user_id:
            raise AppException(
                status_code=403, detail="Apenas o criador pode excluir o grupo"
            )
        self.repo.delete(group)

    def add_member(
        self,
        group_id: uuid.UUID,
        user_id_to_add: uuid.UUID,
        current_user_id: uuid.UUID,
    ) -> GroupMember:
        group = self.repo.get_by_id(group_id)
        if not group:
            raise AppException(status_code=404, detail="Grupo não encontrado")
        if group.creator_id != current_user_id:
            raise AppException(
                status_code=403, detail="Apenas o criador pode adicionar membros"
            )
        user = self.user_repo.get_by_id(user_id_to_add)
        if not user:
            raise AppException(status_code=404, detail="Usuário não encontrado")
        existing = self.repo.get_member(group_id, user_id_to_add)
        if existing:
            raise AppException(status_code=400, detail="Usuário já é membro do grupo")
        return self.repo.add_member(group_id=group_id, user_id=user_id_to_add)

    def remove_member(
        self,
        group_id: uuid.UUID,
        user_id_to_remove: uuid.UUID,
        current_user_id: uuid.UUID,
    ) -> None:
        group = self.repo.get_by_id(group_id)
        if not group:
            raise AppException(status_code=404, detail="Grupo não encontrado")
        if group.creator_id != current_user_id:
            raise AppException(
                status_code=403, detail="Apenas o criador pode remover membros"
            )
        if user_id_to_remove == group.creator_id:
            raise AppException(
                status_code=400, detail="Não é possível remover o criador do grupo"
            )
        member = self.repo.get_member(group_id, user_id_to_remove)
        if not member:
            raise AppException(
                status_code=404, detail="Usuário não é membro deste grupo"
            )
        # check if user has pending or paid (but not confirmed) debts in this group
        pending = (
            self.db.query(DebtParticipant)
            .join(Debt, Debt.id == DebtParticipant.debt_id)
            .filter(
                DebtParticipant.user_id == user_id_to_remove,
                Debt.group_id == group_id,
                DebtParticipant.status.in_(["pendente", "pago"]),
            )
            .all()
        )
        debt_ids = []
        try:
            debt_ids = [str(p.debt_id) for p in pending]
        except TypeError:
            debt_ids = []

        if debt_ids:
            raise AppException(
                status_code=422,
                detail=(
                    "Usuário possui pagamentos em aberto; remova/certeifique as dívidas: "
                    + ", ".join(debt_ids)
                ),
            )

        self.repo.remove_member(member)

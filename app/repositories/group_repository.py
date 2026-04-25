import uuid
from sqlalchemy.orm import Session, selectinload
from app.models.group import Group
from app.models.group_member import GroupMember


class GroupRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, name: str, creator_id: uuid.UUID) -> Group:
        group = Group(name=name, creator_id=creator_id)
        self.db.add(group)
        self.db.flush()
        self.db.refresh(group)
        return group

    def get_by_id(self, group_id: uuid.UUID) -> Group | None:
        return (
            self.db.query(Group)
            .options(selectinload(Group.members).selectinload(GroupMember.user))
            .filter(Group.id == group_id)
            .first()
        )

    def get_groups_by_user(self, user_id: uuid.UUID) -> list[Group]:
        return (
            self.db.query(Group)
            .options(selectinload(Group.members).selectinload(GroupMember.user))
            .join(GroupMember, GroupMember.group_id == Group.id)
            .filter(GroupMember.user_id == user_id)
            .all()
        )

    def update(self, group: Group) -> Group:
        self.db.commit()
        self.db.refresh(group)
        return group

    def delete(self, group: Group) -> None:
        self.db.delete(group)
        self.db.commit()

    def add_member(self, group_id: uuid.UUID, user_id: uuid.UUID) -> GroupMember:
        member = GroupMember(group_id=group_id, user_id=user_id)
        self.db.add(member)
        self.db.flush()
        self.db.refresh(member)
        return member

    def get_member(self, group_id: uuid.UUID, user_id: uuid.UUID) -> GroupMember | None:
        return (
            self.db.query(GroupMember)
            .filter(GroupMember.group_id == group_id, GroupMember.user_id == user_id)
            .first()
        )

    def remove_member(self, member: GroupMember) -> None:
        self.db.delete(member)
        self.db.commit()

"""Integration tests for deleting a group and its cascading children.

These run against a real (in-memory SQLite) database so they exercise the
actual ORM unit-of-work and ON DELETE CASCADE behavior. Mocked repositories
cannot catch this class of bug.

Regression guard for the error:

    AssertionError: Dependency rule on column 'groups.id' tried to blank-out
    primary key column 'group_members.group_id' on instance '<GroupMember ...>'

which happened because the ``Group.members`` relationship lacked
``cascade="all, delete-orphan"`` / ``passive_deletes=True`` and the ORM tried
to NULL out the members' primary-key ``group_id`` instead of deleting them.
"""

import uuid
from decimal import Decimal

from app.models.user import User
from app.models.group import Group
from app.models.group_member import GroupMember
from app.models.debt import Debt
from app.repositories.group_repository import GroupRepository


def _make_user(session, email="creator@example.com") -> User:
    user = User(email=email, name="Creator", password="hashed")
    user.id = uuid.uuid4()
    session.add(user)
    session.flush()
    return user


def _make_debt(group_id: uuid.UUID, creator_id: uuid.UUID) -> Debt:
    debt = Debt(
        group_id=group_id,
        creator_id=creator_id,
        title="Dinner",
        total_amount=Decimal("100.00"),
        split_type="igual",
    )
    debt.id = uuid.uuid4()
    return debt


class TestGroupDeleteCascade:

    def test_delete_group_with_members_does_not_raise(self, db_session):
        """The original crash: deleting a group that has members must succeed."""
        repo = GroupRepository(db_session)
        creator = _make_user(db_session)
        other = _make_user(db_session, email="member@example.com")

        group = repo.create(name="Trip", creator_id=creator.id)
        repo.add_member(group_id=group.id, user_id=creator.id)
        repo.add_member(group_id=group.id, user_id=other.id)
        db_session.commit()

        assert db_session.query(GroupMember).count() == 2

        repo.delete(group)

        assert db_session.query(Group).count() == 0
        # Members are removed along with the group rather than being orphaned.
        assert db_session.query(GroupMember).count() == 0

    def test_delete_group_cascades_to_debts(self, db_session):
        """Debts belonging to the group are removed by the DB-level cascade."""
        repo = GroupRepository(db_session)
        creator = _make_user(db_session)

        group = repo.create(name="Trip", creator_id=creator.id)
        repo.add_member(group_id=group.id, user_id=creator.id)
        db_session.add(_make_debt(group.id, creator.id))
        db_session.commit()

        assert db_session.query(Debt).count() == 1

        repo.delete(group)

        assert db_session.query(Group).count() == 0
        assert db_session.query(Debt).count() == 0

    def test_delete_group_keeps_unrelated_group_members(self, db_session):
        """Deleting one group must not touch members of another group."""
        repo = GroupRepository(db_session)
        creator = _make_user(db_session)

        target = repo.create(name="Target", creator_id=creator.id)
        repo.add_member(group_id=target.id, user_id=creator.id)

        survivor = repo.create(name="Survivor", creator_id=creator.id)
        repo.add_member(group_id=survivor.id, user_id=creator.id)
        db_session.commit()

        repo.delete(target)

        remaining = db_session.query(GroupMember).all()
        assert len(remaining) == 1
        assert remaining[0].group_id == survivor.id

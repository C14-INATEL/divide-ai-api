import uuid
from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.group_service import GroupService
from app.schemas.group import GroupCreate, GroupUpdate, GroupResponse, GroupMemberAdd, GroupMemberOut
from app.models.user import User
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/groups", tags=["groups"])


@router.post("/", response_model=GroupResponse, status_code=201)
def create_group(
    data: GroupCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return GroupService(db).create(data, creator_id=current_user.id)


@router.get("/", response_model=list[GroupResponse])
def list_groups(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return GroupService(db).list_by_user(current_user.id)


@router.get("/{group_id}", response_model=GroupResponse)
def get_group(
    group_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return GroupService(db).get_by_id(group_id, current_user_id=current_user.id)


@router.patch("/{group_id}", response_model=GroupResponse)
def update_group(
    group_id: uuid.UUID,
    data: GroupUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return GroupService(db).update(group_id, data, current_user_id=current_user.id)


@router.delete("/{group_id}", status_code=204)
def delete_group(
    group_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    GroupService(db).delete(group_id, current_user_id=current_user.id)
    return Response(status_code=204)


@router.post("/{group_id}/members", response_model=GroupMemberOut, status_code=201)
def add_member(
    group_id: uuid.UUID,
    data: GroupMemberAdd,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return GroupService(db).add_member(
        group_id=group_id,
        user_id_to_add=data.user_id,
        current_user_id=current_user.id,
    )


@router.delete("/{group_id}/members/{user_id}", status_code=204)
def remove_member(
    group_id: uuid.UUID,
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    GroupService(db).remove_member(
        group_id=group_id,
        user_id_to_remove=user_id,
        current_user_id=current_user.id,
    )
    return Response(status_code=204)

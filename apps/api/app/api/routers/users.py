from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_role
from app.core.database import get_db
from app.models.audit_log import AuditLog
from app.models.user import User, UserRole
from app.schemas.user import UserListItem

router = APIRouter(prefix="/users", tags=["users"])


class RolePatch(BaseModel):
    role: UserRole


class ActivePatch(BaseModel):
    is_active: bool


@router.get("", response_model=list[UserListItem])
async def list_users(
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(require_role(UserRole.admin)),
    db: AsyncSession = Depends(get_db),
) -> list[User]:
    result = await db.execute(select(User).order_by(User.email).limit(limit).offset(offset))
    return result.scalars().all()


@router.patch("/{user_id}/role", response_model=UserListItem)
async def update_role(
    user_id: str,
    body: RolePatch,
    request: Request,
    current_user: User = Depends(require_role(UserRole.admin)),
    db: AsyncSession = Depends(get_db),
) -> User:
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    user.role = body.role
    db.add(
        AuditLog(
            user_id=current_user.id,
            action="update_role",
            entity="user",
            entity_id=str(user.id),
            ip_address=request.client.host if request.client else None,
        )
    )
    await db.flush()
    return user


@router.patch("/{user_id}/active", response_model=UserListItem)
async def update_active(
    user_id: str,
    body: ActivePatch,
    request: Request,
    current_user: User = Depends(require_role(UserRole.admin)),
    db: AsyncSession = Depends(get_db),
) -> User:
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if str(user.id) == str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot deactivate your own account",
        )
    user.is_active = body.is_active
    db.add(
        AuditLog(
            user_id=current_user.id,
            action="update_active",
            entity="user",
            entity_id=str(user.id),
            ip_address=request.client.host if request.client else None,
        )
    )
    await db.flush()
    return user


@router.get("/audit-log")
async def get_audit_log(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    _: User = Depends(require_role(UserRole.admin)),
    db: AsyncSession = Depends(get_db),
) -> list[dict]:
    result = await db.execute(
        select(AuditLog).order_by(AuditLog.created_at.desc()).limit(limit).offset(offset)
    )
    logs = result.scalars().all()
    return [
        {
            "id": str(log.id),
            "user_id": str(log.user_id) if log.user_id else None,
            "action": log.action,
            "entity": log.entity,
            "entity_id": log.entity_id,
            "ip_address": log.ip_address,
            "created_at": log.created_at.isoformat(),
        }
        for log in logs
    ]

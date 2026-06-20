from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.device import Device
from app.models.user import User
from app.schemas.device import DeviceDetail, DeviceListItem

router = APIRouter(prefix="/devices", tags=["devices"])


@router.get("", response_model=list[DeviceListItem])
async def list_devices(
    _: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[Device]:
    result = await db.execute(select(Device).order_by(Device.manufacturer, Device.name))
    return result.scalars().all()


@router.get("/{device_id}", response_model=DeviceDetail)
async def get_device(
    device_id: str,
    _: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Device:
    result = await db.execute(select(Device).where(Device.id == device_id))
    device = result.scalar_one_or_none()
    if not device:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")
    return device

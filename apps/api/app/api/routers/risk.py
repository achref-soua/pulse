from dataclasses import asdict

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.api.deps import get_current_user
from app.clinical.cha2ds2_vasc import CHA2DS2VascInputs, compute_cha2ds2_vasc
from app.clinical.euroscore2 import EuroSCORE2Inputs, compute_euroscore2
from app.clinical.gas import GASInputs, compute_gas
from app.clinical.has_bled import HASBLEDInputs, compute_has_bled
from app.clinical.ifu_fit import DeviceIFU, PatientAnatomy, rank_devices
from app.clinical.news2 import NEWS2Inputs, compute_news2
from app.clinical.rcri import RCRIInputs, compute_rcri
from app.models.user import User

router = APIRouter(prefix="/risk", tags=["risk"])


@router.post("/rcri")
async def rcri_score(body: RCRIInputs, _: User = Depends(get_current_user)):
    return compute_rcri(body)


@router.post("/cha2ds2-vasc")
async def cha2ds2_vasc_score(body: CHA2DS2VascInputs, _: User = Depends(get_current_user)):
    return compute_cha2ds2_vasc(body)


@router.post("/has-bled")
async def has_bled_score(body: HASBLEDInputs, _: User = Depends(get_current_user)):
    return compute_has_bled(body)


@router.post("/news2")
async def news2_score(body: NEWS2Inputs, _: User = Depends(get_current_user)):
    return compute_news2(body)


@router.post("/gas")
async def gas_score(body: GASInputs, _: User = Depends(get_current_user)):
    return compute_gas(body)


@router.post("/euroscore2")
async def euroscore2_score(body: EuroSCORE2Inputs, _: User = Depends(get_current_user)):
    return compute_euroscore2(body)


class IFUFitRequest(BaseModel):
    """Anatomy + device list in a single JSON body."""

    neck_length_mm: float
    neck_angulation_deg: float
    neck_diameter_mm: float
    iliac_access_min_mm: float
    max_diameter_mm: float
    distal_landing_diameter_mm: float | None = None
    devices: list[dict]


@router.post("/ifu-fit")
async def ifu_fit(body: IFUFitRequest, _: User = Depends(get_current_user)):
    anatomy = PatientAnatomy(
        max_diameter_mm=body.max_diameter_mm,
        neck_length_mm=body.neck_length_mm,
        neck_angulation_deg=body.neck_angulation_deg,
        neck_diameter_mm=body.neck_diameter_mm,
        iliac_access_min_mm=body.iliac_access_min_mm,
        distal_landing_diameter_mm=body.distal_landing_diameter_mm,
    )
    device_ifus = [DeviceIFU(**d) for d in body.devices]
    results = rank_devices(anatomy, device_ifus)
    return [asdict(r) for r in results]

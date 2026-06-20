from pydantic import BaseModel


class DeviceListItem(BaseModel):
    id: str
    manufacturer: str
    name: str
    indication: str
    sheath_fr: int
    ifu_proximal_min_mm: float
    ifu_proximal_max_mm: float
    ifu_min_neck_length_mm: float
    ifu_max_neck_angulation_deg: float
    ifu_iliac_min_mm: float
    ifu_iliac_max_mm: float

    model_config = {"from_attributes": True}


class DeviceDetail(DeviceListItem):
    ifu_distal_min_mm: float
    ifu_distal_max_mm: float
    ifu_length_options_mm: list[float]
    contraindications: list[str]
    deployment_steps: list[str]

    model_config = {"from_attributes": True}

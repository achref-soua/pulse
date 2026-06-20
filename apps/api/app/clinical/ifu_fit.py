"""Anatomical IFU-fit engine for EVAR/TEVAR stent-graft selection.

Determines suitability of a patient's aortic anatomy against a device's
Instructions For Use (IFU) envelope, per criterion.
"""

from dataclasses import dataclass, field
from enum import StrEnum


class Suitability(StrEnum):
    suitable = "suitable"
    borderline = "borderline"
    contraindicated = "contraindicated"


@dataclass
class PatientAnatomy:
    max_diameter_mm: float
    neck_length_mm: float
    neck_angulation_deg: float
    neck_diameter_mm: float
    iliac_access_min_mm: float  # minimum iliac diameter (limiting side)
    distal_landing_diameter_mm: float | None = None


@dataclass
class DeviceIFU:
    name: str
    ifu_min_neck_length_mm: float
    ifu_max_neck_angulation_deg: float
    ifu_proximal_min_mm: float  # min aortic neck diameter for proximal fixation
    ifu_proximal_max_mm: float  # max aortic neck diameter for proximal fixation
    ifu_iliac_min_mm: float  # minimum iliac access diameter required
    ifu_iliac_max_mm: float
    ifu_distal_min_mm: float  # distal landing zone diameter range
    ifu_distal_max_mm: float
    oversizing_target_pct: float = 15.0  # typical graft oversizing relative to neck


@dataclass
class CriterionResult:
    name: str
    status: Suitability
    patient_value: float | str
    ifu_threshold: str
    note: str


@dataclass
class IFUFitResult:
    device_name: str
    overall: Suitability
    criteria: list[CriterionResult] = field(default_factory=list)
    recommended_size_note: str = ""


_BORDERLINE_MARGIN = 0.10  # 10% tolerance for borderline classification


def _margin(value: float, threshold: float, direction: str) -> Suitability:
    """Return suitability for a threshold comparison with a 10% borderline band."""
    if direction == "min":
        # value must be >= threshold
        if value >= threshold:
            return Suitability.suitable
        if value >= threshold * (1 - _BORDERLINE_MARGIN):
            return Suitability.borderline
        return Suitability.contraindicated
    else:
        # value must be <= threshold
        if value <= threshold:
            return Suitability.suitable
        if value <= threshold * (1 + _BORDERLINE_MARGIN):
            return Suitability.borderline
        return Suitability.contraindicated


def assess_ifu_fit(anatomy: PatientAnatomy, device: DeviceIFU) -> IFUFitResult:
    criteria: list[CriterionResult] = []

    # 1. Neck length
    neck_len_status = _margin(anatomy.neck_length_mm, device.ifu_min_neck_length_mm, "min")
    criteria.append(
        CriterionResult(
            name="Proximal neck length",
            status=neck_len_status,
            patient_value=anatomy.neck_length_mm,
            ifu_threshold=f"≥ {device.ifu_min_neck_length_mm} mm",
            note="" if neck_len_status == Suitability.suitable else "Insufficient seal zone",
        )
    )

    # 2. Neck angulation
    ang_status = _margin(anatomy.neck_angulation_deg, device.ifu_max_neck_angulation_deg, "max")
    criteria.append(
        CriterionResult(
            name="Neck angulation",
            status=ang_status,
            patient_value=anatomy.neck_angulation_deg,
            ifu_threshold=f"≤ {device.ifu_max_neck_angulation_deg}°",
            note="" if ang_status == Suitability.suitable else "Angulation may compromise seal",
        )
    )

    # 3. Proximal neck diameter (with oversizing)
    target_graft_min = device.ifu_proximal_min_mm * (1 + device.oversizing_target_pct / 100)
    target_graft_max = device.ifu_proximal_max_mm * (1 + device.oversizing_target_pct / 100)
    if anatomy.neck_diameter_mm < device.ifu_proximal_min_mm:
        neck_diam_status = Suitability.contraindicated
        neck_note = "Neck diameter below IFU minimum"
    elif anatomy.neck_diameter_mm > device.ifu_proximal_max_mm:
        neck_diam_status = Suitability.contraindicated
        neck_note = "Neck diameter above IFU maximum"
    else:
        neck_diam_status = Suitability.suitable
        neck_note = f"Target graft: {target_graft_min:.0f}–{target_graft_max:.0f} mm"
    criteria.append(
        CriterionResult(
            name="Proximal neck diameter",
            status=neck_diam_status,
            patient_value=anatomy.neck_diameter_mm,
            ifu_threshold=f"{device.ifu_proximal_min_mm}–{device.ifu_proximal_max_mm} mm",
            note=neck_note,
        )
    )

    # 4. Iliac access
    iliac_status = _margin(anatomy.iliac_access_min_mm, device.ifu_iliac_min_mm, "min")
    criteria.append(
        CriterionResult(
            name="Iliac access diameter",
            status=iliac_status,
            patient_value=anatomy.iliac_access_min_mm,
            ifu_threshold=f"≥ {device.ifu_iliac_min_mm} mm",
            note="" if iliac_status == Suitability.suitable else "Iliac conduit may be required",
        )
    )

    # 5. Distal landing zone (if provided)
    if anatomy.distal_landing_diameter_mm is not None:
        if anatomy.distal_landing_diameter_mm < device.ifu_distal_min_mm:
            distal_status = Suitability.contraindicated
            distal_note = "Distal diameter below IFU minimum"
        elif anatomy.distal_landing_diameter_mm > device.ifu_distal_max_mm:
            distal_status = Suitability.contraindicated
            distal_note = "Distal diameter above IFU maximum"
        else:
            distal_status = Suitability.suitable
            distal_note = ""
        criteria.append(
            CriterionResult(
                name="Distal landing zone",
                status=distal_status,
                patient_value=anatomy.distal_landing_diameter_mm,
                ifu_threshold=f"{device.ifu_distal_min_mm}–{device.ifu_distal_max_mm} mm",
                note=distal_note,
            )
        )

    # Overall verdict
    statuses = {c.status for c in criteria}
    if Suitability.contraindicated in statuses:
        overall = Suitability.contraindicated
    elif Suitability.borderline in statuses:
        overall = Suitability.borderline
    else:
        overall = Suitability.suitable

    return IFUFitResult(
        device_name=device.name,
        overall=overall,
        criteria=criteria,
        recommended_size_note=(
            f"Suggested graft: {anatomy.neck_diameter_mm * (1 + device.oversizing_target_pct / 100):.0f} mm "
            f"(neck {anatomy.neck_diameter_mm:.1f} mm × {100 + device.oversizing_target_pct:.0f}%)"
            if overall != Suitability.contraindicated
            else "Not recommended"
        ),
    )


def rank_devices(anatomy: PatientAnatomy, devices: list[DeviceIFU]) -> list[IFUFitResult]:
    """Rank all devices in the catalog by suitability for the given anatomy."""
    results = [assess_ifu_fit(anatomy, d) for d in devices]
    order = {Suitability.suitable: 0, Suitability.borderline: 1, Suitability.contraindicated: 2}
    return sorted(results, key=lambda r: order[r.overall])

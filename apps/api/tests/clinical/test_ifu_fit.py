"""IFU-fit engine unit tests."""

from app.clinical.ifu_fit import DeviceIFU, PatientAnatomy, Suitability, assess_ifu_fit, rank_devices

_DEVICE = DeviceIFU(
    name="TestGraft",
    ifu_min_neck_length_mm=15.0,
    ifu_max_neck_angulation_deg=60.0,
    ifu_proximal_min_mm=18.0,
    ifu_proximal_max_mm=32.0,
    ifu_iliac_min_mm=7.0,
    ifu_iliac_max_mm=25.0,
    ifu_distal_min_mm=8.0,
    ifu_distal_max_mm=22.0,
)


def test_ideal_anatomy_is_suitable():
    anatomy = PatientAnatomy(
        max_diameter_mm=55.0,
        neck_length_mm=25.0,
        neck_angulation_deg=20.0,
        neck_diameter_mm=24.0,
        iliac_access_min_mm=10.0,
        distal_landing_diameter_mm=12.0,
    )
    result = assess_ifu_fit(anatomy, _DEVICE)
    assert result.overall == Suitability.suitable
    assert all(c.status == Suitability.suitable for c in result.criteria)


def test_short_neck_is_contraindicated():
    anatomy = PatientAnatomy(
        max_diameter_mm=60.0,
        neck_length_mm=5.0,       # well below 15 mm minimum
        neck_angulation_deg=20.0,
        neck_diameter_mm=24.0,
        iliac_access_min_mm=10.0,
    )
    result = assess_ifu_fit(anatomy, _DEVICE)
    assert result.overall == Suitability.contraindicated
    neck_c = next(c for c in result.criteria if c.name == "Proximal neck length")
    assert neck_c.status == Suitability.contraindicated


def test_borderline_neck_length():
    anatomy = PatientAnatomy(
        max_diameter_mm=55.0,
        neck_length_mm=13.6,      # within 10% of 15.0 minimum → borderline
        neck_angulation_deg=20.0,
        neck_diameter_mm=24.0,
        iliac_access_min_mm=10.0,
    )
    result = assess_ifu_fit(anatomy, _DEVICE)
    assert result.overall == Suitability.borderline
    neck_c = next(c for c in result.criteria if c.name == "Proximal neck length")
    assert neck_c.status == Suitability.borderline


def test_rank_devices_orders_by_suitability():
    bad_anatomy = PatientAnatomy(
        max_diameter_mm=55.0, neck_length_mm=5.0, neck_angulation_deg=80.0,
        neck_diameter_mm=24.0, iliac_access_min_mm=10.0,
    )
    good_anatomy = PatientAnatomy(
        max_diameter_mm=55.0, neck_length_mm=25.0, neck_angulation_deg=20.0,
        neck_diameter_mm=24.0, iliac_access_min_mm=10.0,
    )
    device2 = DeviceIFU(
        name="WiderDevice",
        ifu_min_neck_length_mm=5.0,
        ifu_max_neck_angulation_deg=90.0,
        ifu_proximal_min_mm=18.0,
        ifu_proximal_max_mm=32.0,
        ifu_iliac_min_mm=7.0,
        ifu_iliac_max_mm=25.0,
        ifu_distal_min_mm=8.0,
        ifu_distal_max_mm=22.0,
    )
    results = rank_devices(bad_anatomy, [_DEVICE, device2])
    # WiderDevice should rank first for bad anatomy
    assert results[0].device_name == "WiderDevice"

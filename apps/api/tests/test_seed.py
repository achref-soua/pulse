"""Verify seed generator output is internally consistent and idempotent-safe."""

from app.seed.generators import DEVICE_CATALOG, GUIDELINES_CORPUS, LITERATURE_CORPUS, generate_patients


def test_generate_200_patients():
    patients = generate_patients(200)
    assert len(patients) == 200


def test_patient_ids_unique():
    patients = generate_patients(200)
    ids = [p["patient_id"] for p in patients]
    assert len(ids) == len(set(ids))


def test_patient_has_required_fields():
    patients = generate_patients(10)
    required = {
        "patient_id",
        "name",
        "age",
        "sex",
        "mrn",
        "phase",
        "planned_intervention",
        "comorbidities",
        "labs",
        "medications",
        "vitals",
        "note",
    }
    for p in patients:
        missing = required - p.keys()
        assert not missing, f"{p['patient_id']} missing fields: {missing}"


def test_age_range():
    patients = generate_patients(200)
    for p in patients:
        assert 55 <= p["age"] <= 88, f"age {p['age']} out of range"


def test_sex_valid():
    patients = generate_patients(50)
    for p in patients:
        assert p["sex"] in ("M", "F")


def test_phase_valid():
    patients = generate_patients(50)
    valid = {"pre", "intra", "post"}
    for p in patients:
        assert p["phase"] in valid


def test_intervention_valid():
    patients = generate_patients(50)
    valid = {"EVAR", "TEVAR", "open_graft", "surveillance"}
    for p in patients:
        assert p["planned_intervention"] in valid


def test_small_aneurysm_is_surveillance():
    """Patients with diameter < 5.0 mm must be in surveillance."""
    patients = generate_patients(200)
    for p in patients:
        if p.get("max_diameter_mm", 999) < 5.0:
            assert p["planned_intervention"] == "surveillance", (
                f"{p['patient_id']} diameter {p['max_diameter_mm']} but intervention {p['planned_intervention']}"
            )


def test_vitals_is_list():
    patients = generate_patients(10)
    for p in patients:
        assert isinstance(p["vitals"], list)
        assert len(p["vitals"]) >= 2


def test_medications_is_list():
    patients = generate_patients(10)
    for p in patients:
        assert isinstance(p["medications"], list)
        assert len(p["medications"]) >= 1


def test_note_has_body():
    patients = generate_patients(10)
    for p in patients:
        note = p["note"]
        assert "body" in note and len(note["body"]) > 20
        assert "note_type" in note
        assert "author_role" in note


def test_deterministic_output():
    """Running generate_patients twice with the same seed gives identical patient_ids."""
    a = [p["patient_id"] for p in generate_patients(50)]
    b = [p["patient_id"] for p in generate_patients(50)]
    assert a == b


def test_device_catalog_count():
    assert len(DEVICE_CATALOG) >= 12


def test_device_has_ifu_fields():
    required = {
        "manufacturer",
        "name",
        "indication",
        "ifu_proximal_min_mm",
        "ifu_proximal_max_mm",
        "ifu_min_neck_length_mm",
        "ifu_max_neck_angulation_deg",
        "ifu_iliac_min_mm",
        "ifu_iliac_max_mm",
        "deployment_steps",
    }
    for d in DEVICE_CATALOG:
        missing = required - d.keys()
        assert not missing, f"{d['name']} missing: {missing}"


def test_guidelines_corpus():
    assert len(GUIDELINES_CORPUS) >= 6
    for g in GUIDELINES_CORPUS:
        assert "title" in g and "body" in g and "section" in g


def test_literature_corpus():
    assert len(LITERATURE_CORPUS) >= 4
    for ref in LITERATURE_CORPUS:
        assert "title" in ref and "body" in ref

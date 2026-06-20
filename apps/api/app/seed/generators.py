"""Clinically-correlated synthetic data generators.

All data is clearly fictional and for educational/demo purposes only.
"""

import random
from datetime import UTC, datetime, timedelta
from typing import Any

from faker import Faker

fake = Faker()
rng = random.Random(42)  # deterministic seed


# ---------------------------------------------------------------------------
# Device catalog (~12 fictional stent-grafts)
# ---------------------------------------------------------------------------

DEVICE_CATALOG: list[dict[str, Any]] = [
    {
        "manufacturer": "Aortex Medical",
        "name": "EndoFlex AAA-I",
        "indication": "EVAR",
        "ifu_proximal_min_mm": 17.0, "ifu_proximal_max_mm": 31.0,
        "ifu_distal_min_mm": 7.5, "ifu_distal_max_mm": 22.0,
        "ifu_length_options_mm": [80, 100, 120, 140, 160],
        "ifu_min_neck_length_mm": 10.0,
        "ifu_max_neck_angulation_deg": 75.0,
        "ifu_iliac_min_mm": 6.0, "ifu_iliac_max_mm": 25.0,
        "sheath_fr": 18,
        "contraindications": ["Neck thrombus >50%", "Ruptured AAA with unstable haemodynamics (relative)"],
        "deployment_steps": [
            "Bilateral groin access and arteriotomy",
            "Introduce stiff guidewire to thoracic aorta",
            "Road-map fluoroscopy; position main body at renal arteries",
            "Deploy main body; confirm renal patency",
            "Cannulate contralateral gate; deploy iliac limb",
            "Balloon mould proximal and distal seal zones",
            "Completion angiogram; confirm exclusion and no endoleak",
        ],
    },
    {
        "manufacturer": "Aortex Medical",
        "name": "EndoFlex AAA-II Wide Neck",
        "indication": "EVAR",
        "ifu_proximal_min_mm": 19.0, "ifu_proximal_max_mm": 36.0,
        "ifu_distal_min_mm": 7.5, "ifu_distal_max_mm": 22.0,
        "ifu_length_options_mm": [80, 100, 120, 140, 160],
        "ifu_min_neck_length_mm": 15.0,
        "ifu_max_neck_angulation_deg": 60.0,
        "ifu_iliac_min_mm": 7.0, "ifu_iliac_max_mm": 25.0,
        "sheath_fr": 20,
        "contraindications": ["Severe iliac tortuosity", "Calcified iliac stenosis"],
        "deployment_steps": [
            "Bilateral femoral access",
            "Primary wire + sheath positioning",
            "Main body deployment under fluoroscopy",
            "Contralateral limb cannulation and deployment",
            "Proximal extension cuffs if neck seal insufficient",
            "Completion angiogram",
        ],
    },
    {
        "manufacturer": "VascuTech",
        "name": "ThoraShield TEVAR-I",
        "indication": "TEVAR",
        "ifu_proximal_min_mm": 20.0, "ifu_proximal_max_mm": 42.0,
        "ifu_distal_min_mm": 16.0, "ifu_distal_max_mm": 40.0,
        "ifu_length_options_mm": [100, 150, 200],
        "ifu_min_neck_length_mm": 20.0,
        "ifu_max_neck_angulation_deg": 40.0,
        "ifu_iliac_min_mm": 7.5, "ifu_iliac_max_mm": 28.0,
        "sheath_fr": 22,
        "contraindications": ["Aortic diameter < 20 mm or > 42 mm at intended landing", "< 20 mm healthy aorta proximal to aneurysm"],
        "deployment_steps": [
            "Left brachial/radial access for diagnostic catheter",
            "Femoral access for main delivery sheath",
            "Position under fluoroscopic and TOE guidance",
            "Deploy graft covering at least 20 mm healthy aorta proximally",
            "Balloon mould if required",
            "Completion angiogram; assess spinal perfusion",
        ],
    },
    {
        "manufacturer": "VascuTech",
        "name": "ThoraShield TEVAR-II Tapered",
        "indication": "TEVAR",
        "ifu_proximal_min_mm": 22.0, "ifu_proximal_max_mm": 40.0,
        "ifu_distal_min_mm": 14.0, "ifu_distal_max_mm": 36.0,
        "ifu_length_options_mm": [100, 150, 200, 250],
        "ifu_min_neck_length_mm": 20.0,
        "ifu_max_neck_angulation_deg": 45.0,
        "ifu_iliac_min_mm": 8.0, "ifu_iliac_max_mm": 28.0,
        "sheath_fr": 22,
        "contraindications": ["Significant aortic thrombus at landing zones"],
        "deployment_steps": [
            "Bilateral femoral and left brachial access",
            "Stiff wire support from brachial approach",
            "Accurate proximal positioning to preserve left subclavian",
            "Sequential deployment from proximal to distal",
            "Post-dilatation with compliant balloon",
        ],
    },
    {
        "manufacturer": "OmniGraft",
        "name": "AortaFit Low Profile",
        "indication": "EVAR",
        "ifu_proximal_min_mm": 16.0, "ifu_proximal_max_mm": 30.0,
        "ifu_distal_min_mm": 7.0, "ifu_distal_max_mm": 20.0,
        "ifu_length_options_mm": [80, 100, 120, 140],
        "ifu_min_neck_length_mm": 10.0,
        "ifu_max_neck_angulation_deg": 75.0,
        "ifu_iliac_min_mm": 5.5, "ifu_iliac_max_mm": 20.0,
        "sheath_fr": 14,
        "contraindications": ["Neck diameter < 16 mm"],
        "deployment_steps": [
            "Percutaneous femoral access (Proglide closure)",
            "Low-profile sheath advancement",
            "Main body positioning at renal level",
            "Contralateral gate catheterisation via wire technique",
            "Sequential limb deployment",
            "Completion run",
        ],
    },
    {
        "manufacturer": "OmniGraft",
        "name": "AortaFit Fenestrated",
        "indication": "EVAR",
        "ifu_proximal_min_mm": 20.0, "ifu_proximal_max_mm": 36.0,
        "ifu_distal_min_mm": 7.5, "ifu_distal_max_mm": 22.0,
        "ifu_length_options_mm": [100, 120, 140, 160],
        "ifu_min_neck_length_mm": 4.0,
        "ifu_max_neck_angulation_deg": 45.0,
        "ifu_iliac_min_mm": 7.0, "ifu_iliac_max_mm": 25.0,
        "sheath_fr": 20,
        "contraindications": ["Urgent/emergency — requires custom manufacturing"],
        "deployment_steps": [
            "Custom device ordered after CT planning",
            "Bilateral femoral + renal access",
            "Fenestration alignment under fluoroscopy",
            "Stent reinforcement of visceral vessels",
            "Main body deployment",
            "Iliac limb deployment",
            "Completion angiogram with selective visceral runs",
        ],
    },
    {
        "manufacturer": "Aortex Medical",
        "name": "EndoFlex Aortic Cuff Extension",
        "indication": "EVAR",
        "ifu_proximal_min_mm": 17.0, "ifu_proximal_max_mm": 36.0,
        "ifu_distal_min_mm": 17.0, "ifu_distal_max_mm": 36.0,
        "ifu_length_options_mm": [30, 40, 50],
        "ifu_min_neck_length_mm": 10.0,
        "ifu_max_neck_angulation_deg": 60.0,
        "ifu_iliac_min_mm": 6.0, "ifu_iliac_max_mm": 25.0,
        "sheath_fr": 16,
        "contraindications": [],
        "deployment_steps": ["Position at intended overlap zone", "Deploy cuff", "Post-dilate"],
    },
    {
        "manufacturer": "VascuTech",
        "name": "ThoraShield Branched",
        "indication": "TEVAR",
        "ifu_proximal_min_mm": 26.0, "ifu_proximal_max_mm": 46.0,
        "ifu_distal_min_mm": 20.0, "ifu_distal_max_mm": 42.0,
        "ifu_length_options_mm": [150, 200],
        "ifu_min_neck_length_mm": 25.0,
        "ifu_max_neck_angulation_deg": 30.0,
        "ifu_iliac_min_mm": 9.0, "ifu_iliac_max_mm": 30.0,
        "sheath_fr": 24,
        "contraindications": ["Requires hybrid OR and cardiac surgery backup"],
        "deployment_steps": [
            "Median sternotomy or left thoracotomy for debranching",
            "Antegrade delivery via ascending aorta",
            "Branched component deployment",
            "Completion angiogram",
        ],
    },
    {
        "manufacturer": "NovaSeal",
        "name": "InfraFix Modular",
        "indication": "EVAR",
        "ifu_proximal_min_mm": 18.0, "ifu_proximal_max_mm": 32.0,
        "ifu_distal_min_mm": 8.0, "ifu_distal_max_mm": 22.0,
        "ifu_length_options_mm": [80, 100, 120, 140, 160, 180],
        "ifu_min_neck_length_mm": 10.0,
        "ifu_max_neck_angulation_deg": 70.0,
        "ifu_iliac_min_mm": 6.5, "ifu_iliac_max_mm": 24.0,
        "sheath_fr": 18,
        "contraindications": ["Hostile abdomen (relative)", "Infection"],
        "deployment_steps": [
            "Standard bilateral femoral access",
            "Main body and ipsilateral limb deployment as one unit",
            "Contralateral limb extension deployment",
            "Completion angiogram",
        ],
    },
    {
        "manufacturer": "NovaSeal",
        "name": "InfraFix Unibody",
        "indication": "EVAR",
        "ifu_proximal_min_mm": 18.0, "ifu_proximal_max_mm": 30.0,
        "ifu_distal_min_mm": 9.0, "ifu_distal_max_mm": 22.0,
        "ifu_length_options_mm": [90, 110, 130],
        "ifu_min_neck_length_mm": 15.0,
        "ifu_max_neck_angulation_deg": 65.0,
        "ifu_iliac_min_mm": 7.0, "ifu_iliac_max_mm": 22.0,
        "sheath_fr": 16,
        "contraindications": ["Iliac diameter discrepancy > 4 mm"],
        "deployment_steps": [
            "Single main femoral access + contralateral femoral snare",
            "Main body advance and deploy",
            "Completion run",
        ],
    },
    {
        "manufacturer": "ThoraCraft",
        "name": "DescendingAorta XL",
        "indication": "TEVAR",
        "ifu_proximal_min_mm": 24.0, "ifu_proximal_max_mm": 44.0,
        "ifu_distal_min_mm": 20.0, "ifu_distal_max_mm": 40.0,
        "ifu_length_options_mm": [100, 150, 200, 250],
        "ifu_min_neck_length_mm": 20.0,
        "ifu_max_neck_angulation_deg": 40.0,
        "ifu_iliac_min_mm": 8.0, "ifu_iliac_max_mm": 30.0,
        "sheath_fr": 22,
        "contraindications": ["Contained rupture — relative"],
        "deployment_steps": [
            "Left brachial and femoral access",
            "Aortography; mark coeliac and left subclavian",
            "Deploy graft under hypotension protocol (MAP 60–70)",
            "Confirm coeliac patency",
            "Completion angiogram",
        ],
    },
    {
        "manufacturer": "ThoraCraft",
        "name": "DescendingAorta Slim",
        "indication": "TEVAR",
        "ifu_proximal_min_mm": 20.0, "ifu_proximal_max_mm": 36.0,
        "ifu_distal_min_mm": 16.0, "ifu_distal_max_mm": 34.0,
        "ifu_length_options_mm": [100, 150, 200],
        "ifu_min_neck_length_mm": 20.0,
        "ifu_max_neck_angulation_deg": 45.0,
        "ifu_iliac_min_mm": 7.5, "ifu_iliac_max_mm": 26.0,
        "sheath_fr": 20,
        "contraindications": [],
        "deployment_steps": [
            "Femoral + brachial access",
            "Standard TEVAR deployment",
            "Post-dilation if required",
            "Completion imaging",
        ],
    },
]


# ---------------------------------------------------------------------------
# Knowledge-base corpora (guidelines + literature)
# ---------------------------------------------------------------------------

GUIDELINES_CORPUS: list[dict[str, str]] = [
    {
        "title": "AAA Surveillance Intervals",
        "section": "surveillance",
        "body": (
            "Asymptomatic AAA surveillance intervals by diameter: <3.0 cm — no follow-up; "
            "3.0–3.9 cm — 3-yearly ultrasound; 4.0–4.9 cm — annual ultrasound; "
            "5.0–5.4 cm — 6-monthly ultrasound or CT. "
            "Growth rate ≥1 cm/year is an additional indication for intervention. "
            "Symptomatic AAA of any size warrants urgent assessment."
        ),
        "source": "Synthetic guideline — educational only",
    },
    {
        "title": "EVAR vs Open Repair Indications",
        "section": "intervention",
        "body": (
            "EVAR is preferred when anatomy is suitable (IFU-conformant neck, adequate iliac access). "
            "Elective repair is generally recommended for AAA ≥5.5 cm in men or ≥5.0 cm in women. "
            "Open repair is preferred for younger, fit patients with hostile EVAR anatomy, "
            "juxtarenal AAA not amenable to fenestrated EVAR, or when long-term surveillance compliance is poor. "
            "EVAR confers lower 30-day mortality but equivalent long-term survival with ongoing surveillance requirements."
        ),
        "source": "Synthetic guideline — educational only",
    },
    {
        "title": "TEVAR Indications — Descending Thoracic Aorta",
        "section": "intervention",
        "body": (
            "TEVAR is the preferred approach for descending thoracic aortic aneurysm (DTAA) ≥6 cm in diameter "
            "or rapidly enlarging (>1 cm/year). Type B aortic dissection: TEVAR for complicated dissection "
            "(malperfusion, uncontrolled pain, rapid expansion). "
            "Minimum 20 mm healthy aorta proximal and distal to aneurysm required for seal. "
            "CSF drainage recommended for coverage >20 cm, prior AAA repair, or planned left subclavian coverage."
        ),
        "source": "Synthetic guideline — educational only",
    },
    {
        "title": "Periprocedural Anticoagulation in AFib",
        "section": "anticoagulation",
        "body": (
            "For patients on warfarin: consider bridging with LMWH for CHA₂DS₂-VASc ≥3 "
            "undergoing procedures with moderate-high bleeding risk. "
            "For DOACs: hold apixaban/rivaroxaban ≥24 h (≥48 h if CrCl <30 ml/min); "
            "hold dabigatran ≥48 h (≥72 h if CrCl <30 ml/min). "
            "Resume anticoagulation within 24–48 h post-procedure when haemostasis secured."
        ),
        "source": "Synthetic guideline — educational only",
    },
    {
        "title": "Post-EVAR Surveillance Protocol",
        "section": "postop",
        "body": (
            "Standard post-EVAR surveillance: CT angiography at 1 month, 12 months, then annually if stable. "
            "Doppler ultrasound ± plain X-ray acceptable at intermediate time points if no endoleak on first scan. "
            "Type I or III endoleak requires prompt intervention. "
            "Type II endoleak: observe if sac stable; treat if sac growth >5 mm. "
            "Sac shrinkage or stability is the goal; sac growth warrants further investigation."
        ),
        "source": "Synthetic guideline — educational only",
    },
    {
        "title": "Statin Therapy in Aortic Aneurysm",
        "section": "medical",
        "body": (
            "Statin therapy is recommended for all patients with AAA regardless of lipid levels, "
            "for cardiovascular risk reduction and evidence of slowing aneurysm growth rate. "
            "Beta-blockers do not reduce AAA growth rate in randomised trials. "
            "ACE inhibitors/ARBs have cardiovascular benefit; some evidence for AAA growth benefit. "
            "Smoking cessation is the most effective lifestyle intervention for AAA progression."
        ),
        "source": "Synthetic guideline — educational only",
    },
    {
        "title": "Glycaemic Management Perioperatively",
        "section": "perioperative",
        "body": (
            "Target glucose 6–10 mmol/L (108–180 mg/dL) intraoperatively and in the first 24 h post-op. "
            "Avoid hypoglycaemia (glucose <4 mmol/L); associated with increased mortality. "
            "Insulin-dependent diabetic patients: omit long-acting insulin morning of surgery "
            "if glucose <10 mmol/L; halve if glucose 10–15 mmol/L. "
            "VRIII (variable rate IV insulin infusion) for glucose >12 mmol/L or if nil by mouth >12 h."
        ),
        "source": "Synthetic guideline — educational only",
    },
    {
        "title": "Renal Protection in Contrast Nephropathy",
        "section": "renal",
        "body": (
            "For patients with eGFR <60 mL/min: minimise contrast volume; use iso-osmolar contrast; "
            "pre-hydrate with IV 0.9% NaCl at 1 mL/kg/h for 12 h pre- and 12 h post-procedure. "
            "Hold metformin 48 h before contrast if eGFR <60 and restart only when renal function confirmed stable. "
            "ACE inhibitors/ARBs: consider holding 24–48 h pre-procedure in high-risk patients. "
            "Monitor creatinine at 24 h and 48 h post-contrast."
        ),
        "source": "Synthetic guideline — educational only",
    },
]

LITERATURE_CORPUS: list[dict[str, str]] = [
    {
        "title": "Endovascular vs Open Repair of AAA: 15-Year Follow-Up",
        "section": "outcomes",
        "body": (
            "Pooled data from randomised trials (EVAR-1, DREAM, OVER) at 15-year follow-up: "
            "EVAR associated with lower 30-day mortality (1.2% vs 4.6%) but no long-term survival advantage. "
            "EVAR patients require ongoing surveillance; late rupture rate 1.2% vs 0.3% with open repair. "
            "Reintervention rate significantly higher with EVAR. "
            "Conclusion: EVAR suitable for patients with limited life expectancy or high surgical risk; "
            "open repair preferred for fit patients with long life expectancy."
        ),
        "source": "Synthetic literature summary — educational only",
    },
    {
        "title": "TEVAR Outcomes in Descending Thoracic Aneurysm",
        "section": "outcomes",
        "body": (
            "Registry data (n=2,800) for elective TEVAR for descending TAA: "
            "30-day mortality 2.1%; spinal cord ischaemia 3.1% (paraplegia in 1.2%). "
            "CSF drainage reduced spinal cord ischaemia incidence by 47% in high-risk cases. "
            "5-year freedom from aneurysm-related death 88%. "
            "Retrograde type A dissection: 0.9% — most serious TEVAR-specific complication."
        ),
        "source": "Synthetic literature summary — educational only",
    },
    {
        "title": "Fenestrated EVAR for Juxtarenal AAA: Early and Mid-Term Results",
        "section": "complex",
        "body": (
            "Single-centre series (n=340) of fenestrated EVAR for juxtarenal and pararenal AAA: "
            "Technical success 97.1%; 30-day mortality 1.5%. "
            "Target vessel patency at 3 years: 96.4% for renal arteries. "
            "Reintervention rate 18% at 5 years (mainly limb occlusion and endoleak). "
            "Longer planning time (custom device): mean 6.2 weeks. "
            "Conclusion: F-EVAR is a valid alternative to open repair for complex neck anatomy."
        ),
        "source": "Synthetic literature summary — educational only",
    },
    {
        "title": "Type II Endoleak After EVAR: Natural History and Management",
        "section": "complications",
        "body": (
            "Meta-analysis (n=3,200 patients): Type II endoleak incidence 25% at 1 year. "
            "Spontaneous resolution in 52% at 2 years. "
            "Sac growth ≥5 mm in persistent type II endoleak: 18% at 5 years. "
            "Embolisation of feeding vessels (lumbar arteries, IMA) achieves technical success 85% "
            "with resolution of sac growth in 70%. "
            "Laparoscopic clipping offers durable alternative for failed catheter-based treatment."
        ),
        "source": "Synthetic literature summary — educational only",
    },
    {
        "title": "NEWS2 in Post-Operative Aortic Surgery Patients",
        "section": "monitoring",
        "body": (
            "Retrospective cohort (n=480): NEWS2 score ≥5 within 48 h of EVAR/TEVAR "
            "associated with ICU admission (OR 4.2, 95% CI 2.1–8.4) and 30-day mortality (OR 6.8). "
            "Respiratory rate and SpO2 components most predictive. "
            "NEWS2-triggered critical care outreach review reduced 30-day mortality by 31% "
            "in those with scores ≥7 vs standard monitoring."
        ),
        "source": "Synthetic literature summary — educational only",
    },
]


# ---------------------------------------------------------------------------
# Patient generators
# ---------------------------------------------------------------------------

def _weighted_choice(items: list, weights: list) -> Any:
    return rng.choices(items, weights=weights, k=1)[0]


def _comorbidity_profile(age: int, sex: str) -> dict[str, bool]:
    """Generate correlated comorbidities."""
    age_risk = (age - 55) / 33  # 0–1 scale over 55–88
    smoke = rng.random() < 0.45 + 0.1 * age_risk  # smoking strongly ↑ with AAA
    htn = rng.random() < 0.55 + 0.15 * age_risk
    dm = rng.random() < 0.25 + 0.1 * age_risk
    ckd = rng.random() < 0.20 + 0.15 * age_risk
    cad = rng.random() < 0.30 + 0.15 * age_risk
    chf = rng.random() < 0.10 + 0.10 * age_risk if cad else rng.random() < 0.05
    afib = rng.random() < 0.15 + 0.15 * age_risk
    copd = rng.random() < 0.20 if smoke else rng.random() < 0.08
    return {
        "htn": htn, "dm": dm,
        "insulin_dependent": dm and rng.random() < 0.30,
        "ckd": ckd, "copd": copd, "cad": cad,
        "prior_mi": cad and rng.random() < 0.45,
        "afib": afib,
        "cvd_stroke": rng.random() < 0.08 + 0.05 * age_risk,
        "chf": chf,
        "smoking_current": smoke and rng.random() < 0.50,
        "smoking_former": smoke,
    }


def _anatomy(intervention: str) -> dict[str, Any]:
    """Generate aortic anatomy; bias toward IFU-suitable with some borderline/contraindicated."""
    bucket = rng.choices(["suitable", "borderline", "contraindicated"], weights=[0.55, 0.30, 0.15])[0]
    if intervention in ("EVAR", "surveillance"):
        aneurysm_type = _weighted_choice(
            ["infrarenal_AAA", "juxtarenal_AAA"],
            [0.80, 0.20],
        )
        if bucket == "suitable":
            diameter = rng.uniform(5.0, 7.5)
            neck_len = rng.uniform(15, 35)
            neck_ang = rng.uniform(5, 55)
            neck_diam = rng.uniform(18, 30)
            iliac = rng.uniform(8, 18)
        elif bucket == "borderline":
            diameter = rng.uniform(4.5, 6.5)
            neck_len = rng.uniform(8, 16)
            neck_ang = rng.uniform(50, 72)
            neck_diam = rng.uniform(14, 20)
            iliac = rng.uniform(5.5, 8.0)
        else:
            diameter = rng.uniform(4.5, 8.0)
            neck_len = rng.uniform(2, 9)
            neck_ang = rng.uniform(70, 110)
            neck_diam = rng.uniform(13, 17)
            iliac = rng.uniform(4.0, 6.5)
    else:  # TEVAR
        aneurysm_type = _weighted_choice(["TAA", "ascending"], [0.85, 0.15])
        if bucket == "suitable":
            diameter = rng.uniform(5.5, 8.0)
            neck_len = rng.uniform(22, 40)
            neck_ang = rng.uniform(5, 35)
            neck_diam = rng.uniform(22, 38)
            iliac = rng.uniform(9, 20)
        elif bucket == "borderline":
            diameter = rng.uniform(5.0, 7.0)
            neck_len = rng.uniform(16, 24)
            neck_ang = rng.uniform(35, 48)
            neck_diam = rng.uniform(18, 24)
            iliac = rng.uniform(7, 9.5)
        else:
            diameter = rng.uniform(5.0, 8.0)
            neck_len = rng.uniform(5, 18)
            neck_ang = rng.uniform(45, 80)
            neck_diam = rng.uniform(15, 22)
            iliac = rng.uniform(5, 8.0)

    return {
        "aneurysm_type": aneurysm_type,
        "location": "infrarenal" if "AAA" in aneurysm_type else "descending thoracic",
        "max_diameter_mm": round(diameter, 1),
        "neck_length_mm": round(neck_len, 1),
        "neck_angulation_deg": round(neck_ang, 1),
        "neck_diameter_mm": round(neck_diam, 1),
        "iliac_access_min_mm": round(iliac, 1),
        "iliac_access_max_mm": round(iliac + rng.uniform(2, 6), 1),
        "tortuosity": rng.choice(["mild", "moderate", "severe"]),
    }


def _labs(comorbidities: dict[str, bool]) -> dict[str, Any]:
    ckd = comorbidities["ckd"]
    dm = comorbidities["dm"]
    return {
        "creatinine": round(rng.uniform(130, 280) if ckd else rng.uniform(60, 110), 1),
        "egfr": round(rng.uniform(15, 45) if ckd else rng.uniform(60, 90), 1),
        "hb": round(rng.uniform(8.5, 11.5) if ckd else rng.uniform(12.0, 16.5), 1),
        "platelets": round(rng.uniform(100, 450), 0),
        "inr": round(rng.uniform(1.8, 3.2) if comorbidities.get("afib") else rng.uniform(0.9, 1.2), 1),
        "hba1c": round(rng.uniform(7.5, 11.0) if dm else rng.uniform(4.5, 6.0), 1),
        "bnp": round(rng.uniform(200, 1200) if comorbidities.get("chf") else rng.uniform(10, 100), 1),
        "unit": "SI",
    }


def _medications(comorbidities: dict[str, bool]) -> list[dict[str, str]]:
    meds = []
    if comorbidities.get("afib"):
        meds.append({"name": "Apixaban", "med_class": "anticoagulant", "dose": "5mg", "route": "oral"})
    if comorbidities.get("cad") or comorbidities.get("prior_mi"):
        meds.append({"name": "Aspirin", "med_class": "antiplatelet", "dose": "75mg", "route": "oral"})
        meds.append({"name": "Atorvastatin", "med_class": "statin", "dose": "40mg", "route": "oral"})
    if comorbidities.get("htn"):
        meds.append({"name": "Ramipril", "med_class": "ACEi/ARB", "dose": "5mg", "route": "oral"})
    if comorbidities.get("chf"):
        meds.append({"name": "Bisoprolol", "med_class": "beta_blocker", "dose": "2.5mg", "route": "oral"})
        meds.append({"name": "Furosemide", "med_class": "diuretic", "dose": "40mg", "route": "oral"})
    if not meds:
        meds.append({"name": "Aspirin", "med_class": "antiplatelet", "dose": "75mg", "route": "oral"})
    return meds


def _vitals_series(phase: str, n_readings: int = 5) -> list[dict[str, Any]]:
    """Generate a time series of vitals. Post-op patients may have a deteriorating trend."""
    base_time = datetime.now(UTC) - timedelta(hours=n_readings * 6)
    readings = []
    deteriorating = phase == "post" and rng.random() < 0.20

    for i in range(n_readings):
        drift = i * 0.3 if deteriorating else 0
        readings.append({
            "taken_at": base_time + timedelta(hours=i * 6),
            "rr": int(rng.gauss(16 + drift, 2)),
            "spo2": round(rng.gauss(96 - drift * 0.5, 1.0), 1),
            "on_oxygen": deteriorating and i > 2,
            "systolic_bp": int(rng.gauss(130 - drift * 5, 10)),
            "heart_rate": int(rng.gauss(72 + drift * 2, 8)),
            "temp_c": round(rng.gauss(37.0 + drift * 0.1, 0.3), 1),
            "consciousness": "A" if not deteriorating or i < 4 else rng.choice(["A", "V"]),
        })
    return readings


def _note(patient_id: str, name: str, phase: str, comorbidities: dict, anatomy: dict) -> dict[str, Any]:
    note_type_map = {
        "pre": "pre_op_assessment",
        "intra": "op_note",
        "post": "progress",
    }
    note_type = note_type_map[phase]
    comorb_list = [k for k, v in comorbidities.items() if v and k not in ("insulin_dependent",)]
    comorb_str = ", ".join(comorb_list[:4]) or "no significant comorbidities"

    if phase == "pre":
        body = (
            f"Pre-operative assessment for {name} ({patient_id}). "
            f"Presenting with {anatomy['aneurysm_type'].replace('_', ' ')} "
            f"max diameter {anatomy['max_diameter_mm']} mm. "
            f"Relevant comorbidities: {comorb_str}. "
            f"Neck length {anatomy['neck_length_mm']} mm, angulation {anatomy['neck_angulation_deg']}°, "
            f"iliac access {anatomy['iliac_access_min_mm']} mm. "
            f"Discussed risks and benefits of planned intervention with patient; consent obtained."
        )
    elif phase == "intra":
        body = (
            f"Operative note — {name} ({patient_id}). "
            f"Procedure performed under general anaesthesia. "
            f"Access obtained bilaterally. Main body deployed under fluoroscopic guidance. "
            f"Contralateral limb deployed successfully. "
            f"Completion angiography confirmed aneurysm exclusion. No immediate endoleak. "
            f"Patient tolerated procedure well; transferred to recovery."
        )
    else:
        body = (
            f"Post-operative progress note — {name} ({patient_id}). "
            f"Day {rng.randint(1, 5)} post-procedure. Wound sites clean. "
            f"Tolerating oral diet. Observations stable (see vitals). "
            f"Duplex pending for endoleak surveillance. "
            f"Discharge planning commenced; plan to follow up in 4-6 weeks with CT."
        )

    return {
        "note_type": note_type,
        "author_role": "surgeon",
        "timestamp": datetime.now(UTC) - timedelta(days=rng.randint(0, 30)),
        "body": body,
    }


def generate_patients(n: int = 200) -> list[dict[str, Any]]:
    """Generate n clinically-correlated synthetic patients."""
    patients = []
    for i in range(1, n + 1):
        age = rng.randint(55, 88)
        sex = rng.choices(["M", "F"], weights=[0.75, 0.25])[0]
        phase = rng.choices(["pre", "intra", "post"], weights=[0.50, 0.15, 0.35])[0]
        intervention = rng.choices(
            ["EVAR", "TEVAR", "open_graft", "surveillance"],
            weights=[0.45, 0.20, 0.10, 0.25],
        )[0]

        # Guideline-consistent: surveillance if small, repair if large
        anatomy = _anatomy(intervention)
        if anatomy["max_diameter_mm"] < 5.0 and intervention != "surveillance":
            intervention = "surveillance"
        if anatomy["max_diameter_mm"] >= 5.5 and intervention == "surveillance":
            intervention = rng.choices(["EVAR", "TEVAR", "open_graft"], weights=[0.6, 0.25, 0.15])[0]

        comorbidities = _comorbidity_profile(age, sex)
        labs = _labs(comorbidities)
        medications = _medications(comorbidities)
        vitals = _vitals_series(phase, n_readings=rng.randint(3, 8) if phase == "post" else 2)
        note = _note(f"P{i:03d}", fake.name(), phase, comorbidities, anatomy)

        patient = {
            "patient_id": f"P{i:03d}",
            "name": fake.name(),
            "age": age,
            "sex": sex,
            "mrn": f"MRN{i:06d}",
            "phase": phase,
            "planned_intervention": intervention,
            "surgery_date": (datetime.now(UTC) - timedelta(days=rng.randint(1, 60))).date() if phase != "pre" else None,
            **anatomy,
            "comorbidities": comorbidities,
            "labs": labs,
            "medications": medications,
            "vitals": vitals,
            "note": note,
        }
        patients.append(patient)
    return patients

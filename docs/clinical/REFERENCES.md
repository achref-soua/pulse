# Clinical References

All calculator coefficients and scoring criteria used in Pulse are sourced
from the references below. The LLM never computes a score; it calls the
deterministic calculator tool which is unit-tested against these references.

---

## RCRI — Revised Cardiac Risk Index (Lee Index)

**Source:** Lee TH, Marcantonio ER, Mangione CM, et al. *Derivation and
prospective validation of a simple index for prediction of cardiac risk of
major noncardiac surgery.* Circulation. 1999;100(10):1043-1049.

Criteria (1 point each, 6 factors):
1. High-risk surgery (intraperitoneal, intrathoracic, suprainguinal vascular)
2. Ischemic heart disease
3. Congestive heart failure
4. Cerebrovascular disease
5. Diabetes on insulin
6. Preoperative serum creatinine > 177 µmol/L (> 2.0 mg/dL)

Risk classes: 0 pts → <1%; 1 pt → 1%; 2 pts → 2.4%; ≥3 pts → 5.4%

---

## CHA₂DS₂-VASc

**Source:** Lip GY, Nieuwlaat R, Pisters R, Lane DA, Crijns HJ. *Refining
clinical risk stratification for predicting stroke and thromboembolism in
atrial fibrillation using a novel risk factor-based approach.* Chest.
2010;137(2):263-272.

Points: CHF(1), HTN(1), Age≥75(2), DM(1), Stroke/TIA(2), Vascular disease(1),
Age 65-74(1), Sex (female)(1). Max 9.

---

## HAS-BLED

**Source:** Pisters R, Lane DA, Nieuwlaat R, et al. *A novel user-friendly
score (HAS-BLED) to assess 1-year risk of major bleeding in patients with
atrial fibrillation.* Chest. 2010;138(5):1093-1100.

Points: HTN(1), Renal/Liver dysfunction(1 each), Stroke hx(1), Bleeding
predisposition(1), Labile INR(1), Elderly >65(1), Drugs/alcohol(1 each). Max 9.

---

## NEWS2 — National Early Warning Score 2

**Source:** Royal College of Physicians. *National Early Warning Score (NEWS) 2.*
London: RCP, 2017. https://www.rcplondon.ac.uk/projects/outputs/national-early-warning-score-news-2

Parameters: Respiration rate, SpO2 (Scale 1), Supplemental O2, Systolic BP,
Heart rate, Consciousness (AVPU → GCS), Temperature.

Response thresholds: 0-4 (low), 5-6 or any single ≥3 (medium), ≥7 (high).

---

## GAS — Glasgow Aneurysm Score

**Source:** Samy AK, Murray G, MacBain G. *Glasgow aneurysm score.*
Cardiovasc Surg. 1994;2(1):41-44.

Formula: Age + (17 × shock) + (7 × myocardial disease) +
         (10 × cerebrovascular disease) + (14 × renal disease)

---

## EuroSCORE II

**Source:** Nashef SA, Roques F, Sharples LD, et al. *EuroSCORE II.*
Eur J Cardiothorac Surg. 2012;41(4):734-745.

Official calculator: https://www.euroscore.org/calc.html

> **Note:** EuroSCORE II uses a logistic regression model with ~18 predictor
> variables and a set of published coefficients. Pulse implements this as an
> "educational estimate" (clearly labeled in the UI) using the published
> coefficients from the 2012 paper. Validation cases are tested against the
> official online calculator before any release.

---

## IFU-Fit Engine — Device suitability for EVAR/TEVAR

Criteria derived from generalised IFU envelopes representative of commercial
aortic stent-graft devices. The specific per-device IFU values in the seed
catalog are fictional but structured to match the format of real IFU documents.

**Reference structure:**
- Proximal neck length (mm): minimum required by device
- Proximal neck angulation (°): maximum tolerated
- Neck diameter (mm): proximal fixation zone range
- Iliac access diameter (mm): minimum outer diameter for sheath delivery
- Distal landing zone diameter (mm): range for distal fixation

Suitability: **suitable** = all criteria pass; **borderline** = 1-2 criteria
at threshold ±10%; **contraindicated** = any criterion clearly outside IFU.

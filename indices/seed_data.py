"""Seed data generator for the Pravaah patient journey system.

Generates 8 patients with distinct clinical story arcs, 7 hospital wards
with capacity data, and 48 hours of vitals at 15-minute intervals
(192 readings per patient, 1536 total).
"""

import random
from datetime import datetime, timedelta, timezone

from config import settings


# ---------------------------------------------------------------------------
# Patients
# ---------------------------------------------------------------------------

def get_patients():
    """Return a list of 8 patient dicts with distinct story arcs."""
    now = datetime.now(timezone.utc)
    return [
        {
            "patient_id": "PAT-001",
            "name": "Rajesh Kumar",
            "age": 67,
            "diagnosis": "Pneumonia with COPD exacerbation",
            "severity": "critical",
            "ward": "ICU",
            "admitted_at": (now - timedelta(hours=72)).isoformat(),
            "comorbidities": ["COPD", "hypertension", "type-2 diabetes"],
            "status": "admitted",
            "attending_physician": "Dr. Anil Mehta",
            "notes": (
                "Deteriorating course. Increasing oxygen requirements and "
                "rising inflammatory markers. Guardian alert trigger candidate."
            ),
        },
        {
            "patient_id": "PAT-002",
            "name": "Ananya Sharma",
            "age": 34,
            "diagnosis": "Post-appendectomy recovery",
            "severity": "low",
            "ward": "surgical",
            "admitted_at": (now - timedelta(hours=60)).isoformat(),
            "comorbidities": [],
            "status": "admitted",
            "attending_physician": "Dr. Sneha Kulkarni",
            "notes": (
                "Uncomplicated laparoscopic appendectomy. Recovering well, "
                "tolerating oral feeds. Clean discharge candidate."
            ),
        },
        {
            "patient_id": "PAT-003",
            "name": "Vikram Patel",
            "age": 72,
            "diagnosis": "Congestive heart failure (NYHA Class III)",
            "severity": "high",
            "ward": "cardiac",
            "admitted_at": (now - timedelta(hours=96)).isoformat(),
            "comorbidities": ["atrial fibrillation", "chronic kidney disease", "hypertension"],
            "status": "admitted",
            "attending_physician": "Dr. Ravi Shankar",
            "notes": (
                "Slowly improving on IV diuretics. Still requires oxygen "
                "supplementation. Not ready for discharge."
            ),
        },
        {
            "patient_id": "PAT-004",
            "name": "Meera Reddy",
            "age": 45,
            "diagnosis": "Diabetic Ketoacidosis (DKA)",
            "severity": "high",
            "ward": "ICU",
            "admitted_at": (now - timedelta(hours=50)).isoformat(),
            "comorbidities": ["type-1 diabetes", "hypothyroidism"],
            "status": "admitted",
            "attending_physician": "Dr. Priya Venkatesh",
            "notes": (
                "Rapid recovery from DKA. Anion gap closed, glucose stabilising "
                "on subcutaneous insulin. ICU transfer-out candidate."
            ),
        },
        {
            "patient_id": "PAT-005",
            "name": "Priya Nair",
            "age": 28,
            "diagnosis": "Normal vaginal delivery",
            "severity": "low",
            "ward": "maternity",
            "admitted_at": (now - timedelta(hours=36)).isoformat(),
            "comorbidities": [],
            "status": "admitted",
            "attending_physician": "Dr. Kavitha Menon",
            "notes": (
                "Uncomplicated delivery, mother and baby doing well. "
                "Normal vitals throughout. Easy discharge."
            ),
        },
        {
            "patient_id": "PAT-006",
            "name": "Suresh Iyer",
            "age": 78,
            "diagnosis": "Right hip fracture (intertrochanteric)",
            "severity": "moderate",
            "ward": "orthopedic",
            "admitted_at": (now - timedelta(hours=80)).isoformat(),
            "comorbidities": ["osteoporosis", "benign prostatic hyperplasia"],
            "status": "admitted",
            "attending_physician": "Dr. Ashok Nair",
            "notes": (
                "Post-operative day 3 after hip hemiarthroplasty. Vitals "
                "stable but mobility severely limited. Deferred discharge "
                "until physiotherapy goals met."
            ),
        },
        {
            "patient_id": "PAT-007",
            "name": "Amit Joshi",
            "age": 55,
            "diagnosis": "Acute ST-elevation myocardial infarction (STEMI)",
            "severity": "critical",
            "ward": "emergency",
            "admitted_at": (now - timedelta(hours=4)).isoformat(),
            "comorbidities": ["smoking", "hyperlipidemia", "family history of CAD"],
            "status": "admitted",
            "attending_physician": "Dr. Sanjay Gupta",
            "notes": (
                "Arrived via ambulance 4 hours ago with crushing chest pain. "
                "Emergency PCI performed, stent deployed to LAD. Hemodynamically "
                "unstable. Emergency triage."
            ),
        },
        {
            "patient_id": "PAT-008",
            "name": "Lakshmi Devi",
            "age": 62,
            "diagnosis": "Severe persistent asthma with acute exacerbation",
            "severity": "moderate",
            "ward": "respiratory",
            "admitted_at": (now - timedelta(hours=52)).isoformat(),
            "comorbidities": ["GERD", "obesity", "allergic rhinitis"],
            "status": "admitted",
            "attending_physician": "Dr. Mohan Rao",
            "notes": (
                "Admitted for acute asthma exacerbation. Appeared to be "
                "improving on nebulisation and steroids. Guardian 'wow moment' "
                "candidate - subtle hidden deterioration."
            ),
        },
    ]


# ---------------------------------------------------------------------------
# Hospital ward capacity
# ---------------------------------------------------------------------------

def get_capacity_data():
    """Return a list of 7 ward capacity dicts."""
    now = datetime.now(timezone.utc).isoformat()
    wards = [
        {
            "ward": "ICU",
            "ward_name": "Intensive Care Unit",
            "total_beds": 12,
            "occupied_beds": 11,
            "ventilators_total": 8,
            "ventilators_in_use": 6,
            "nurses_on_duty": 14,
            "doctors_on_duty": 4,
        },
        {
            "ward": "surgical",
            "ward_name": "General Surgical Ward",
            "total_beds": 30,
            "occupied_beds": 22,
            "ventilators_total": 0,
            "ventilators_in_use": 0,
            "nurses_on_duty": 10,
            "doctors_on_duty": 3,
        },
        {
            "ward": "cardiac",
            "ward_name": "Cardiac Care Unit",
            "total_beds": 20,
            "occupied_beds": 16,
            "ventilators_total": 4,
            "ventilators_in_use": 2,
            "nurses_on_duty": 8,
            "doctors_on_duty": 3,
        },
        {
            "ward": "emergency",
            "ward_name": "Emergency Department",
            "total_beds": 15,
            "occupied_beds": 12,
            "ventilators_total": 3,
            "ventilators_in_use": 1,
            "nurses_on_duty": 12,
            "doctors_on_duty": 5,
        },
        {
            "ward": "maternity",
            "ward_name": "Maternity Ward",
            "total_beds": 10,
            "occupied_beds": 4,
            "ventilators_total": 0,
            "ventilators_in_use": 0,
            "nurses_on_duty": 6,
            "doctors_on_duty": 2,
        },
        {
            "ward": "orthopedic",
            "ward_name": "Orthopedic Ward",
            "total_beds": 16,
            "occupied_beds": 10,
            "ventilators_total": 0,
            "ventilators_in_use": 0,
            "nurses_on_duty": 6,
            "doctors_on_duty": 2,
        },
        {
            "ward": "respiratory",
            "ward_name": "Respiratory Medicine Ward",
            "total_beds": 14,
            "occupied_beds": 9,
            "ventilators_total": 3,
            "ventilators_in_use": 1,
            "nurses_on_duty": 6,
            "doctors_on_duty": 2,
        },
    ]

    # Derive computed fields
    for w in wards:
        w["available_beds"] = w["total_beds"] - w["occupied_beds"]
        w["occupancy_rate"] = round(w["occupied_beds"] / w["total_beds"], 3)
        w["staffing_ratio"] = round(w["nurses_on_duty"] / max(w["occupied_beds"], 1), 2)
        w["updated_at"] = now

    return wards


# ---------------------------------------------------------------------------
# Vitals generation helpers
# ---------------------------------------------------------------------------

def _lerp(start, end, t):
    """Linear interpolation from start to end where t goes from 0.0 to 1.0."""
    return start + (end - start) * t


def _noise(scale=1.0):
    """Return random noise in [-scale, +scale] using a uniform distribution."""
    return random.uniform(-scale, scale)


def _clamp(value, lo, hi):
    """Clamp value to [lo, hi]."""
    return max(lo, min(hi, value))


def _make_vital(timestamp, patient_id, ward, hr, sys_bp, dia_bp, o2, temp, rr, pain):
    """Build a single vitals document dict."""
    return {
        "@timestamp": timestamp.isoformat(),
        "patient_id": patient_id,
        "ward": ward,
        "heart_rate": round(_clamp(hr, 30, 200), 1),
        "systolic_bp": round(_clamp(sys_bp, 60, 250), 1),
        "diastolic_bp": round(_clamp(dia_bp, 30, 150), 1),
        "oxygen_saturation": round(_clamp(o2, 50, 100), 1),
        "temperature": round(_clamp(temp, 35.0, 42.0), 1),
        "respiratory_rate": round(_clamp(rr, 8, 45), 1),
        "pain_score": int(_clamp(pain, 0, 10)),
    }


# ---------------------------------------------------------------------------
# Per-patient vitals generators
# ---------------------------------------------------------------------------

def _vitals_pat001(timestamps):
    """PAT-001 Rajesh Kumar - Deteriorating.

    HR rises from ~88 to ~115, O2 drops from ~93 to ~86, temp rises to 39.5,
    respiratory rate climbs. Pain increases. BP becomes increasingly unstable.
    """
    docs = []
    n = len(timestamps)
    for i, ts in enumerate(timestamps):
        t = i / (n - 1)  # 0.0 -> 1.0

        hr = _lerp(88, 115, t) + _noise(3)
        sys_bp = _lerp(130, 145, t) + _noise(5)
        dia_bp = _lerp(82, 90, t) + _noise(3)
        o2 = _lerp(93, 86, t) + _noise(1.0)
        temp = _lerp(37.8, 39.5, t) + _noise(0.15)
        rr = _lerp(20, 30, t) + _noise(1.5)
        pain = _lerp(4, 8, t) + _noise(0.5)

        docs.append(_make_vital(ts, "PAT-001", "ICU", hr, sys_bp, dia_bp, o2, temp, rr, pain))
    return docs


def _vitals_pat002(timestamps):
    """PAT-002 Ananya Sharma - Recovering post-appendectomy.

    HR drops from ~95 to ~75, O2 improves from ~94 to ~98, temp normalises
    from 37.6 to 36.8. Pain resolves from 5 to 1.
    """
    docs = []
    n = len(timestamps)
    for i, ts in enumerate(timestamps):
        t = i / (n - 1)

        hr = _lerp(95, 75, t) + _noise(2)
        sys_bp = _lerp(125, 118, t) + _noise(4)
        dia_bp = _lerp(80, 75, t) + _noise(3)
        o2 = _lerp(94, 98, t) + _noise(0.5)
        temp = _lerp(37.6, 36.8, t) + _noise(0.1)
        rr = _lerp(18, 15, t) + _noise(1)
        pain = _lerp(5, 1, t) + _noise(0.4)

        docs.append(_make_vital(ts, "PAT-002", "surgical", hr, sys_bp, dia_bp, o2, temp, rr, pain))
    return docs


def _vitals_pat003(timestamps):
    """PAT-003 Vikram Patel - Slowly improving heart failure.

    HR drops from ~100 to ~90 with occasional dips/spikes. O2 fluctuates
    between 90-94. Still on supplemental O2, not discharge-ready.
    """
    docs = []
    n = len(timestamps)
    for i, ts in enumerate(timestamps):
        t = i / (n - 1)

        # Occasional "dips" - every ~6 hours there is a brief worsening
        dip = 0
        if (i % 24) in (0, 1, 2):  # 3 readings every 24 readings (~6 hours)
            dip = 1.0

        hr = _lerp(100, 90, t) + _noise(4) + dip * random.uniform(5, 10)
        sys_bp = _lerp(140, 132, t) + _noise(6)
        dia_bp = _lerp(88, 82, t) + _noise(4)
        o2 = _lerp(90, 94, t) + _noise(1.2) - dip * random.uniform(1, 3)
        temp = _lerp(37.4, 37.0, t) + _noise(0.15)
        rr = _lerp(22, 19, t) + _noise(1.5) + dip * random.uniform(1, 3)
        pain = _lerp(3, 2, t) + _noise(0.5)

        docs.append(_make_vital(ts, "PAT-003", "cardiac", hr, sys_bp, dia_bp, o2, temp, rr, pain))
    return docs


def _vitals_pat004(timestamps):
    """PAT-004 Meera Reddy - Rapid DKA recovery.

    Starts ICU-level bad (HR ~120, O2 ~90, temp 38.5, RR 28) and quickly
    normalises over 48 hours using an exponential-decay curve.
    """
    docs = []
    n = len(timestamps)
    for i, ts in enumerate(timestamps):
        t = i / (n - 1)
        # Use a faster-than-linear curve so most recovery happens early
        # t_fast goes from 0 to 1 but front-loaded (square root curve)
        t_fast = t ** 0.5

        hr = _lerp(120, 78, t_fast) + _noise(2.5)
        sys_bp = _lerp(100, 120, t_fast) + _noise(4)
        dia_bp = _lerp(60, 76, t_fast) + _noise(3)
        o2 = _lerp(90, 98, t_fast) + _noise(0.6)
        temp = _lerp(38.5, 36.9, t_fast) + _noise(0.12)
        rr = _lerp(28, 16, t_fast) + _noise(1.2)
        pain = _lerp(6, 1, t_fast) + _noise(0.4)

        docs.append(_make_vital(ts, "PAT-004", "ICU", hr, sys_bp, dia_bp, o2, temp, rr, pain))
    return docs


def _vitals_pat005(timestamps):
    """PAT-005 Priya Nair - Normal delivery, consistently normal vitals.

    Minor natural physiological variation around normal values.
    """
    docs = []
    for ts in timestamps:
        hr = 76 + _noise(4)
        sys_bp = 115 + _noise(5)
        dia_bp = 72 + _noise(3)
        o2 = 98 + _noise(0.5)
        temp = 36.7 + _noise(0.15)
        rr = 15 + _noise(1)
        pain = 1 + _noise(0.5)

        docs.append(_make_vital(ts, "PAT-005", "maternity", hr, sys_bp, dia_bp, o2, temp, rr, pain))
    return docs


def _vitals_pat006(timestamps):
    """PAT-006 Suresh Iyer - Hip fracture, vitals stable but pain moderate.

    Vitals are normal and stable. Pain stays moderate (4-6) reflecting
    mobility limitations not captured in other vitals.
    """
    docs = []
    n = len(timestamps)
    for i, ts in enumerate(timestamps):
        t = i / (n - 1)

        hr = 74 + _noise(3)
        sys_bp = 135 + _noise(5)  # slightly elevated for age
        dia_bp = 80 + _noise(3)
        o2 = 96 + _noise(0.5)
        temp = 36.9 + _noise(0.1)
        rr = 16 + _noise(1)
        # Pain stays moderate, slight improvement over time
        pain = _lerp(6, 4, t) + _noise(0.6)

        docs.append(_make_vital(ts, "PAT-006", "orthopedic", hr, sys_bp, dia_bp, o2, temp, rr, pain))
    return docs


def _vitals_pat007(timestamps):
    """PAT-007 Amit Joshi - Acute MI, only last 4 hours of data.

    Abnormal cardiac vitals: high HR, BP fluctuations, elevated troponin
    implied by severity. Only the last 16 readings (4 hours) have data.
    """
    docs = []
    # Only generate data for the last 4 hours = 16 readings at 15-min intervals
    # The total 48h window has 192 readings; last 16 are indices 176..191
    cutoff = len(timestamps) - 16

    for i, ts in enumerate(timestamps):
        if i < cutoff:
            # No data for this patient before 4 hours ago - skip
            continue

        # Progress within the 4-hour window (0.0 -> 1.0)
        t = (i - cutoff) / 15

        # Post-PCI: starts very unstable, slight stabilisation
        hr = _lerp(118, 105, t) + _noise(6)
        # BP fluctuates wildly post-MI
        sys_bp = _lerp(90, 105, t) + _noise(12)
        dia_bp = _lerp(55, 65, t) + _noise(8)
        o2 = _lerp(89, 93, t) + _noise(1.5)
        temp = 37.2 + _noise(0.2)
        rr = _lerp(24, 21, t) + _noise(2)
        pain = _lerp(9, 7, t) + _noise(0.5)

        docs.append(_make_vital(ts, "PAT-007", "emergency", hr, sys_bp, dia_bp, o2, temp, rr, pain))
    return docs


def _vitals_pat008(timestamps):
    """PAT-008 Lakshmi Devi - Hidden deterioration (Guardian wow moment).

    Looks normal for first 44 hours, then SUBTLE deterioration in last 4
    hours. O2 drops slowly from 96 to 91, respiratory rate creeps from
    16 to 22. Changes are gradual enough a busy doctor might miss them
    but a monitoring agent would catch the trend.
    """
    docs = []
    n = len(timestamps)
    # Last 4 hours = last 16 readings. The transition point:
    deterioration_start = n - 16

    for i, ts in enumerate(timestamps):
        if i < deterioration_start:
            # Normal-looking phase (first 44 hours)
            # Slight general improvement to make it look like she is getting better
            t_norm = i / deterioration_start
            hr = _lerp(82, 78, t_norm) + _noise(3)
            sys_bp = 122 + _noise(5)
            dia_bp = 76 + _noise(3)
            o2 = _lerp(95, 96, t_norm) + _noise(0.5)
            temp = _lerp(37.3, 37.0, t_norm) + _noise(0.1)
            rr = _lerp(17, 16, t_norm) + _noise(1)
            pain = 2 + _noise(0.4)
        else:
            # Subtle deterioration phase (last 4 hours)
            t_det = (i - deterioration_start) / 15

            # HR creeps up slightly
            hr = _lerp(78, 88, t_det) + _noise(2)
            # BP stays mostly stable (making it harder to notice)
            sys_bp = 122 + _noise(5)
            dia_bp = 76 + _noise(3)
            # O2 drops slowly - the key signal
            o2 = _lerp(96, 91, t_det) + _noise(0.4)
            # Temp barely rises
            temp = _lerp(37.0, 37.4, t_det) + _noise(0.1)
            # Respiratory rate creeps up - the other key signal
            rr = _lerp(16, 22, t_det) + _noise(0.8)
            # Pain increases slightly
            pain = _lerp(2, 4, t_det) + _noise(0.4)

        docs.append(_make_vital(ts, "PAT-008", "respiratory", hr, sys_bp, dia_bp, o2, temp, rr, pain))
    return docs


# ---------------------------------------------------------------------------
# Main vitals generator
# ---------------------------------------------------------------------------

def generate_vitals(patients):
    """Generate 48 hours of vitals at 15-minute intervals for all patients.

    Returns a list of vitals dicts. Each dict has @timestamp, patient_id,
    ward, and all vital sign fields.

    Parameters
    ----------
    patients : list[dict]
        The patient list from get_patients(). Used only for validation /
        logging; the actual generation is hard-coded per patient arc.
    """
    now = datetime.now(timezone.utc)
    # Round 'now' down to the nearest 15-minute boundary for clean timestamps
    now = now.replace(second=0, microsecond=0)
    now = now.replace(minute=(now.minute // 15) * 15)

    # 48 hours at 15-min intervals = 192 timestamps
    total_readings = 192
    timestamps = [
        now - timedelta(minutes=15 * (total_readings - 1 - i))
        for i in range(total_readings)
    ]

    # Set the random seed for reproducibility during development
    random.seed(42)

    patient_ids = {p["patient_id"] for p in patients}
    print(f"  Generating vitals for {len(patient_ids)} patients, "
          f"{total_readings} readings each ...")

    all_vitals = []

    # Generate per-patient vitals using dedicated story-arc generators
    generators = {
        "PAT-001": _vitals_pat001,
        "PAT-002": _vitals_pat002,
        "PAT-003": _vitals_pat003,
        "PAT-004": _vitals_pat004,
        "PAT-005": _vitals_pat005,
        "PAT-006": _vitals_pat006,
        "PAT-007": _vitals_pat007,
        "PAT-008": _vitals_pat008,
    }

    for pid, gen_fn in generators.items():
        docs = gen_fn(timestamps)
        print(f"    {pid}: {len(docs)} vitals generated")
        all_vitals.extend(docs)

    print(f"  Total vitals documents: {len(all_vitals)}")
    return all_vitals


# ---------------------------------------------------------------------------
# Seed everything
# ---------------------------------------------------------------------------

def seed_all(client):
    """Seed all sample data into Elasticsearch using the PravaahClient.

    Parameters
    ----------
    client : utils.api_client.PravaahClient
        An initialised client instance.
    """
    print("\n=== Seeding Pravaah sample data ===\n")

    # 1. Index patients
    patients = get_patients()
    print(f"[1/3] Indexing {len(patients)} patients -> {settings.INDEX_PATIENTS}")
    result = client.bulk_index(settings.INDEX_PATIENTS, patients)
    print(f"  Done: {result}\n")

    # 2. Index ward capacity
    capacity = get_capacity_data()
    print(f"[2/3] Indexing {len(capacity)} ward capacity docs -> {settings.INDEX_CAPACITY}")
    result = client.bulk_index(settings.INDEX_CAPACITY, capacity)
    print(f"  Done: {result}\n")

    # 3. Generate and index vitals in batches of 500
    print(f"[3/3] Generating and indexing vitals -> {settings.INDEX_VITALS}")
    vitals = generate_vitals(patients)

    batch_size = 500
    total = len(vitals)
    indexed = 0

    for batch_start in range(0, total, batch_size):
        batch_end = min(batch_start + batch_size, total)
        batch = vitals[batch_start:batch_end]
        result = client.bulk_index(settings.INDEX_VITALS, batch, op_type="create")
        indexed += len(batch)
        print(f"  Batch {batch_start // batch_size + 1}: "
              f"indexed {len(batch)} docs ({indexed}/{total} total)")

    print(f"\n  Vitals indexing complete: {indexed} documents indexed.")
    print("\n=== Seeding complete ===\n")

    return {
        "patients": len(patients),
        "capacity": len(capacity),
        "vitals": indexed,
    }

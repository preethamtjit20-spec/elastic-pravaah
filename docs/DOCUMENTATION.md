# Pravaah: Technical Documentation
## Multi-Agent Patient Journey Orchestrator

---

## Table of Contents
1. [The Story](#the-story)
2. [System Architecture](#system-architecture)
3. [Data Model](#data-model)
4. [Agent Deep Dives](#agent-deep-dives)
5. [ES|QL Query Catalog](#esql-query-catalog)
6. [The Guardian Effect](#the-guardian-effect)
7. [Setup Guide](#setup-guide)
8. [Demo Walkthrough](#demo-walkthrough)

---

## The Story

### The Problem We're Solving

In a busy 200-bed hospital, a 62-year-old woman named Lakshmi is admitted for severe asthma. Her vitals look normal. Nurses check on her every 4 hours. Her oxygen saturation reads 96% — perfectly fine. Her respiratory rate is 16 — textbook normal.

But something is happening that no one can see.

Over the next 4 hours, her O2 drops to 95... then 93... then 91. Her respiratory rate creeps from 16 to 18... to 20... to 22. Each individual reading looks "acceptable." No alarm fires. No alert triggers. The trend is invisible to any single snapshot.

**This is the gap Pravaah fills.**

Pravaah (Sanskrit: प्रवाह, meaning "flow") is a multi-agent AI system that doesn't just look at numbers — it looks at trajectories. It compares the last 3 hours against the prior 3 hours. It spots the trend that humans miss. And when it does, it raises a critical alert with veto power over any discharge recommendation.

### Why Multi-Agent?

A single AI agent trying to handle triage, recovery tracking, capacity planning, discharge decisions, AND safety monitoring would be overwhelmed and unfocused. Each of these domains has its own:
- **Data requirements** (different queries, different time windows)
- **Reasoning frameworks** (MEWS scoring vs. recovery slopes vs. 7-point checklists)
- **Risk tolerances** (triage can be aggressive; discharge must be conservative)

By splitting into 5 specialists + 1 orchestrator, each agent can deeply focus on its domain while the orchestrator ensures they collaborate effectively.

---

## System Architecture

> Reference: See `docs/diagrams/architecture.drawio` for the full visual diagram.

### Components

**User Layer:**
- Kibana Chat Interface — natural language interaction with any agent
- Dashboard — real-time visualization of patient vitals, ward occupancy, severity distribution

**Agent Layer (6 agents):**

| Agent | Role | Key Capability | Tools Used |
|-------|------|----------------|------------|
| Triage | Emergency severity assessment | MEWS scoring (0-15 scale) | execute_esql, search |
| Recovery | Trajectory analysis | Weighted Recovery Score (0-100%) | execute_esql, search |
| Capacity | Ward optimization | Zone-based occupancy management | execute_esql, search |
| Discharge | Readiness evaluation | Conservative 7-point checklist | execute_esql, search |
| Guardian | Safety oversight | 3-hour window deterioration detection | execute_esql, search |
| Orchestrator | 5-phase coordination | All specialist reasoning in sequence | execute_esql, search, get_document_by_id |

**Data Layer (Elasticsearch):**
- 1 Time Series Data Stream (TSDS) for high-frequency vitals
- 4 regular indices for structured records
- ES|QL as the universal query language

---

## Data Model

### metrics-patient-vitals (TSDS)
The crown jewel of our data architecture. A Time Series Data Stream that stores vital signs at **15-minute intervals** with patient_id and ward as routing dimensions.

| Field | Type | TSDS Role |
|-------|------|-----------|
| @timestamp | date | Time key |
| patient_id | keyword | Dimension |
| ward | keyword | Dimension |
| heart_rate | float | Gauge metric |
| systolic_bp | float | Gauge metric |
| diastolic_bp | float | Gauge metric |
| oxygen_saturation | float | Gauge metric |
| temperature | float | Gauge metric |
| respiratory_rate | float | Gauge metric |
| pain_score | integer | Gauge metric |

**Why TSDS?** Time Series Data Streams provide automatic time-based rollover, optimized storage through doc-value-only fields, and efficient time-range queries. For 1,360 vital readings across 8 patients, TSDS gives us sub-second query performance on temporal aggregations.

### patients
8 patients with carefully designed clinical story arcs:

| Patient | Diagnosis | Story Arc | Demo Purpose |
|---------|-----------|-----------|--------------|
| PAT-001 | Pneumonia + COPD | Deteriorating | Guardian alert trigger |
| PAT-002 | Post-appendectomy | Recovering steadily | Clean discharge candidate |
| PAT-003 | Heart Failure | Slowly improving | Not ready for discharge |
| PAT-004 | Diabetic Ketoacidosis | Rapid recovery | ICU transfer-out candidate |
| PAT-005 | Normal delivery | Normal vitals | Easy discharge |
| PAT-006 | Hip fracture | Stable but immobile | Deferred (mobility criterion) |
| PAT-007 | Acute MI (STEMI) | Just admitted (4h) | Emergency triage showcase |
| PAT-008 | Severe Asthma | Hidden deterioration | Guardian "wow moment" |

### hospital-capacity
7 wards with realistic occupancy scenarios:
- ICU at 92% (11/12 beds) — triggers red zone protocols
- Maternity at 40% — green zone, comfortable capacity
- Others ranging from 62-80%

### agent-decisions
Audit trail that captures every agent decision for compliance and review. Populated as agents interact with patients.

### discharge-plans
Tracks the 7-point discharge criteria for each patient being evaluated.

---

## Agent Deep Dives

### Triage Agent: MEWS Scoring

The Modified Early Warning Score is a clinically validated rapid assessment tool. Our implementation scores 5 vital parameters on a 0-3 scale:

**Scoring Table:**

| Parameter | 0 (Normal) | 1 (Mild) | 2 (Moderate) | 3 (Severe) |
|-----------|------------|----------|--------------|------------|
| Heart Rate | 51-100 | 41-50 or 101-110 | <=40 or 111-129 | >=130 |
| Systolic BP | 101-199 | 81-100 | 71-80 or >=200 | <=70 |
| Resp. Rate | 9-14 | 15-20 | 21-29 | <=8 or >=30 |
| Temperature | 35-38.4 | <=35 or >=38.5 | >=39 | -- |
| O2 Saturation | >=96 | 94-95 | 92-93 | <92 |

**Interpretation:** 0-3 Low, 4-6 Medium, 7-10 High (ICU candidate), 11+ Critical (activate rapid response).

**Example - PAT-007 (Amit Joshi, Acute MI):**
With HR ~125, Systolic BP fluctuating 85-165, RR ~24, the MEWS score typically comes out 7-9, flagging for HIGH severity and ICU admission.

### Recovery Agent: Weighted Score

Instead of asking "is this patient better?", we quantify it. The Weighted Recovery Score combines 6 vital parameters into a single 0-100% metric:

| Component | Weight | Target Range | Why This Weight |
|-----------|--------|-------------|-----------------|
| O2 Saturation | 25% | >=96% | Most critical for respiratory/cardiac |
| Heart Rate | 20% | 60-100 bpm | Core cardiovascular indicator |
| Temperature | 20% | 36.1-37.2C | Infection marker |
| Resp. Rate | 15% | 12-20/min | Respiratory compensation indicator |
| Pain Score | 10% | <=3 | Patient comfort and healing |
| Blood Pressure | 10% | 90-140 systolic | Hemodynamic stability |

**Classification:** >=80% Excellent, 60-79% Good, 40-59% Fair, <40% Poor

**Example - PAT-002 (Ananya Sharma, post-appendectomy):**
After 48h of recovery, her vitals have normalized: HR ~75, O2 ~98%, Temp ~36.8. Recovery score: ~85% (Excellent). She's a discharge candidate.

### Capacity Agent: Zone Management

Real-time awareness of hospital resources using a traffic-light zone system:

| Zone | Occupancy | Protocol |
|------|-----------|----------|
| RED | >90% | Overflow: divert non-critical, accelerate discharges, emergency transfers |
| YELLOW | 75-90% | Selective: prioritize critical/high severity admissions only |
| GREEN | <75% | Normal: accept all appropriate admissions |

**Staffing Ratios (nurse:patient):**
- ICU: 1:2 ideal, 1:3 acceptable, >1:3 unsafe
- General: 1:4 ideal, 1:6 acceptable
- Emergency: 1:3 ideal, 1:4 acceptable

### Discharge Agent: 7-Point Conservative Checklist

The most conservative agent by design. ALL 7 criteria must pass:

1. Vitals stable 24h (HR 60-100, BP 90-140/60-90, O2 >=95, Temp <37.5, RR 12-20)
2. No fever 24h (max temp < 37.5C)
3. Pain controlled (max pain <= 3)
4. Mobility adequate for home care
5. Oral medications tolerated
6. Follow-up appointment scheduled
7. Patient educated on home care and warning signs

**Conservative Principle:** "When in doubt, do NOT discharge. A false 'safe to discharge' is far more dangerous than keeping a patient an extra day."

### Guardian Agent: The Safety Net

**This is the most important agent in the system.**

While other agents look at current values, the Guardian looks at **trends over time**. It compares two 3-hour windows:

```
Prior window (3-6h ago)  vs  Recent window (0-3h ago)
```

**Deterioration thresholds (difference between windows):**
- Heart Rate: increase > 10 bpm
- O2 Saturation: decrease > 2%
- Temperature: increase > 0.5C
- Respiratory Rate: increase > 4 breaths/min
- Systolic BP: decrease > 15 mmHg

**Escalation rules:**
- 0 trends: STABLE
- 1 trend: WATCH (increase monitoring)
- 2+ trends: CRITICAL (immediate alert + discharge veto)

**The Veto Power:** Guardian can unilaterally block any discharge recommendation. This is a deliberate design choice — safety must never be overridden by convenience.

---

## The Guardian Effect: PAT-008 Deep Dive

This is Pravaah's signature moment.

**Patient:** Lakshmi Devi, 62, Severe Asthma
**Ward:** Respiratory

**What a human sees (snapshot at any given time):**
- O2: 93% — "Slightly below normal but acceptable for an asthma patient"
- RR: 20 — "Upper end of normal but not alarming"
- HR: 88 — "Normal"

**What Guardian sees (3-hour window comparison):**

| Vital | Prior 3h Avg | Recent 3h Avg | Change | Threshold | Alert? |
|-------|-------------|---------------|--------|-----------|--------|
| O2 Sat | 95.2% | 91.8% | -3.4% | >2% decrease | YES |
| Resp Rate | 17.1 | 21.4 | +4.3 | >4 increase | YES |
| Heart Rate | 82.5 | 87.2 | +4.7 | >10 increase | No |
| Temperature | 37.1 | 37.3 | +0.2 | >0.5 increase | No |
| Systolic BP | 128 | 125 | -3 | >15 decrease | No |

**Result:** 2 deterioration trends detected simultaneously (O2 + Respiratory Rate)

**Guardian's response:**
> CRITICAL ALERT: Patient PAT-008 showing concurrent deterioration in oxygen saturation (-3.4%) and respiratory rate (+4.3/min) over the last 3 hours. VETO any pending discharge. Recommend immediate physician review and possible intervention escalation.

**Why this matters:** Each individual reading was "acceptable." No traditional threshold alarm would have fired. But the *trajectory* reveals a patient whose respiratory function is declining. Without Pravaah, this might not be caught until O2 drops below 90% — potentially hours later, potentially too late.

---

## ES|QL Query Catalog

13 queries organized by agent domain. Here are the key ones:

### Deterioration Detection (Guardian's core query)
```esql
FROM metrics-patient-vitals
| WHERE patient_id == "PAT-008"
  AND @timestamp > NOW() - 6 hours
| EVAL window = CASE(
    @timestamp > NOW() - 3 hours, "recent",
    "prior")
| STATS
    avg_hr = AVG(heart_rate),
    avg_o2 = AVG(oxygen_saturation),
    avg_temp = AVG(temperature),
    avg_rr = AVG(respiratory_rate),
    avg_systolic = AVG(systolic_bp),
    readings = COUNT(*)
  BY window
| SORT window ASC
```

### Hourly Recovery Trend
```esql
FROM metrics-patient-vitals
| WHERE patient_id == "PAT-002"
| EVAL bucket = DATE_TRUNC(1 hour, @timestamp)
| STATS
    avg_hr = AVG(heart_rate),
    avg_o2 = AVG(oxygen_saturation),
    avg_temp = AVG(temperature),
    avg_rr = AVG(respiratory_rate),
    avg_pain = AVG(pain_score),
    readings = COUNT(*)
  BY bucket
| SORT bucket ASC
```

### Hospital-Wide Critical Scan
```esql
FROM metrics-patient-vitals
| STATS
    latest_hr = MAX(heart_rate),
    latest_o2 = MIN(oxygen_saturation),
    latest_temp = MAX(temperature),
    latest_rr = MAX(respiratory_rate),
    latest_time = MAX(@timestamp)
  BY patient_id, ward
| WHERE latest_hr > 110 OR latest_o2 < 92
  OR latest_temp > 38.5 OR latest_rr > 25
| SORT latest_o2 ASC
```

---

## Setup Guide

### Prerequisites
- Elasticsearch 8.x (Cloud or self-hosted)
- Kibana with Agent Builder enabled
- Python 3.9+
- An LLM connector configured in Kibana

### Quick Start
```bash
git clone https://github.com/preethamtjit20-spec/elastic-pravaah.git
cd elastic-pravaah
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your credentials
python setup.py --setup    # Creates indices + seeds data
python setup.py --agents   # Shows agent configs for Kibana UI
```

### Creating Agents
For each agent, go to Kibana > Agent Builder > New Agent:
1. Set Agent ID, Display Name, Description
2. Paste Custom Instructions from `agent-instructions/*.txt`
3. Enable tools: execute_esql, search, get_index_mapping
4. Save

---

## Demo Walkthrough

### Scenario 1: Emergency Triage
**Input:** "Assess patient PAT-007 for emergency triage"
**Agent:** Triage Agent
**What happens:** Agent queries patient record + latest vitals via ES|QL, calculates MEWS score, flags as HIGH severity, recommends ICU admission.

### Scenario 2: Recovery Tracking
**Input:** "Analyze recovery trajectory for PAT-002"
**Agent:** Recovery Agent
**What happens:** Agent fetches 48h hourly trends, computes weighted recovery score (~85%), classifies as Excellent, suggests discharge evaluation.

### Scenario 3: The Guardian Catches Hidden Deterioration
**Input:** "Run safety assessment for PAT-008"
**Agent:** Guardian Agent
**What happens:** Agent compares 3h windows, detects O2 drop (-3.4%) and RR increase (+4.3), raises CRITICAL ALERT, vetoes any discharge.

### Scenario 4: Capacity Crisis
**Input:** "ICU is almost full, where do we place a new critical patient?"
**Agent:** Capacity Agent
**What happens:** Agent checks all wards, identifies ICU at 92% (RED zone), suggests PAT-004 (rapid recovery) as transfer-out candidate.

### Scenario 5: Full Orchestrated Journey
**Input:** "Run complete patient journey for PAT-002"
**Agent:** Pravaah Orchestrator
**What happens:** All 5 phases execute in sequence. Triage confirms low severity. Recovery shows 85% score. Capacity shows surgical ward in yellow zone. Discharge checklist passes 7/7. Guardian clears safety. Final recommendation: APPROVED for discharge.

---

## Elastic Products Used

| Product | How We Use It | Why It Matters |
|---------|---------------|----------------|
| **Agent Builder** | 6 agents with custom instructions and tool access | Natural language interface to complex clinical logic |
| **ES\|QL** | 13 analytical queries across 5 indices | Real-time patient data analysis without complex DSL |
| **TSDS** | 1,360 vital sign readings at 15-min intervals | Optimized time-series storage and querying |
| **Search** | Patient record lookups, ward capacity checks | Sub-second access to structured clinical data |
| **Kibana Dashboards** | Real-time monitoring command center | Visual overview of hospital status |

---

*Built for the Elasticsearch Agent Builder Hackathon by Preetham S*

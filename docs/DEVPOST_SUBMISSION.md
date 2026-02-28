# Pravaah - Devpost Submission

## Project Title
Pravaah: Multi-Agent Patient Journey Orchestrator

![Architecture](https://github.com/user-attachments/assets/5dbaa890-fded-4e8a-b3d5-a2620a3ca43f)

## Tagline (one line)
6 AI agents that never sleep, never forget, and never miss a deteriorating patient — powered entirely by Elasticsearch.

---

## Inspiration

At 3 AM in a busy hospital ward, a nurse checks on Lakshmi, a 62-year-old asthma patient. Oxygen saturation: 93%. "A bit low for her, but she has asthma," the nurse notes. Respiratory rate: 20. "Upper normal." She moves on to the next patient.

What the nurse can't see — what no human can see in a single snapshot — is that 3 hours ago, Lakshmi's O2 was 96% and her respiratory rate was 16. The trend is invisible in the moment but unmistakable in the data: this patient is deteriorating.

**Every year, thousands of patients experience "failure to rescue" — preventable deaths where warning signs existed in the data but weren't caught in time.**

We built Pravaah because we believe AI agents shouldn't just answer questions. They should watch, analyze, and protect — even when no one asks them to.

---

## What It Does

Pravaah (Sanskrit: प्रवाह, "flow") orchestrates **6 specialist AI agents** that collaborate to manage the entire patient journey through a hospital — from emergency triage to safe discharge:

### The Agents

🔴 **Triage Agent** — Assesses emergency patients using the clinically-validated MEWS (Modified Early Warning Score) methodology. Scores 5 vital parameters on a 0-3 scale and recommends severity classification and ward placement.

📈 **Recovery Trend Agent** — Analyzes 48 hours of vital sign trends to compute a Weighted Recovery Score (0-100%). Doesn't just say "getting better" — quantifies exactly how much, across 6 weighted parameters.

🏥 **Capacity Agent** — Real-time hospital bed management with zone-based protocols (Red/Yellow/Green). Monitors nurse-to-patient ratios, ventilator availability, and recommends optimal placement or transfers.

📋 **Discharge Decision Agent** — The most conservative agent. Uses a strict 7-point checklist where ALL criteria must pass. When in doubt, it does NOT discharge. Patient safety over bed availability, always.

🛡️ **Guardian Safety Agent** — *The star of the system.* Compares 3-hour vital sign windows to detect deterioration trends that look normal in isolation. Has unilateral **veto power** over all discharge decisions. The last line of defense.

🎯 **Pravaah Orchestrator** — The master coordinator. Runs all 5 phases (triage → recovery → capacity → discharge → safety) for comprehensive patient assessments in a single conversation.

### The "Wow Moment"

Patient PAT-008's O2 drops from 96% to 91% over 4 hours. Her respiratory rate climbs from 16 to 22. No single reading triggers an alarm. But the Guardian Agent's 3-hour window comparison catches it immediately:

> **🚨 CRITICAL ALERT: 2 deterioration trends detected. O2 saturation declining -3.4%. Respiratory rate increasing +4.3/min. VETO any pending discharge. Immediate physician review required.**

---

## How We Built It

### 100% Elastic Stack

Every component runs on Elasticsearch products — no external databases, no separate ML models, no third-party orchestration frameworks.

**Data Layer:**
- **Time Series Data Stream (TSDS)** for 1,360 vital sign readings at 15-minute intervals — optimized for temporal queries
- **4 regular indices** for patients, hospital capacity, agent decisions (audit trail), and discharge plans
- **ES|QL** as the universal query language — 13 analytical queries power all agent decisions

**Agent Layer:**
- **Kibana Agent Builder** hosts all 6 agents with custom instructions and platform tools
- Each agent has embedded ES|QL queries in its instructions — it knows exactly what data to fetch and how to analyze it
- **platform.core.execute_esql** is the primary tool — agents write and execute queries in real-time

**Visualization:**
- **Kibana Dashboard** as the command center — ward occupancy bars, severity donuts, vital sign trend lines, patient tables

### Technical Highlights

1. **3-Hour Window Comparison** — The Guardian's core innovation. Uses ES|QL's CASE() function to split 6 hours of data into "prior" and "recent" windows, then compares averages to detect trends.

2. **Weighted Recovery Score** — A composite metric combining 6 vital parameters with clinically-informed weights (O2 Sat at 25%, Heart Rate at 20%, etc.) into a single 0-100% score.

3. **MEWS Implementation** — A clinically-validated scoring system translated into agent reasoning, giving structured emergency assessments in seconds.

4. **Conservative Discharge Protocol** — All 7 criteria must pass. The system is deliberately designed to err on the side of keeping patients rather than releasing them prematurely.

5. **Audit Trail** — Every agent decision is logged to the `agent-decisions` index with timestamp, reasoning, confidence score, and review status.

---

## Challenges We Ran Into

1. **TSDS Write Constraints** — Data streams require `create` op_type (not `index`) and have a look-back time window. We needed to configure `index.look_back_time: 72h` to seed our 48-hour historical data.

2. **Agent Builder Tool Model** — We initially designed 17 custom tools before discovering that Agent Builder uses built-in platform tools. We pivoted to embedding ES|QL queries directly in agent instructions, which actually resulted in a cleaner, more maintainable design.

3. **Balancing Sensitivity vs. Specificity** — The Guardian Agent's deterioration thresholds needed careful tuning. Too sensitive = alert fatigue. Too relaxed = missed deteriorations. We landed on clinically-informed thresholds (e.g., >2% O2 drop, >10 bpm HR increase).

---

## Accomplishments We're Proud Of

- **The Guardian catches what humans miss** — PAT-008's subtle deterioration is invisible in any single vitals check but immediately obvious to the Guardian's window comparison
- **6 agents, 1 conversation** — The Orchestrator can run a complete 5-phase assessment in a single chat interaction
- **Clinically grounded** — MEWS scoring, nurse-to-patient ratios, and the 7-point discharge checklist are all based on real clinical frameworks
- **Full audit trail** — Every decision is logged with reasoning and confidence, enabling accountability and review
- **Pure Elastic Stack** — No external dependencies beyond Elasticsearch and Kibana

---

## What We Learned

- **ES|QL is powerful for real-time clinical analytics** — Window comparisons, hourly bucketing, and multi-metric aggregations all work naturally in ES|QL
- **TSDS is perfect for medical telemetry** — Sub-second queries across 1,360 readings with automatic time-based optimization
- **Agent Builder enables rapid prototyping** — From concept to working multi-agent system in a single hackathon sprint
- **The best AI systems are opinionated** — The Guardian's veto power and the Discharge agent's conservatism are deliberate design choices, not bugs

---

## What's Next

1. **Real-time ingestion** — Connect to actual hospital monitoring systems (HL7/FHIR) for live vital sign streaming
2. **More agents** — Pharmacy interaction checker, lab result interpreter, family notification agent
3. **Machine learning integration** — Train anomaly detection models on the TSDS data for even earlier deterioration detection
4. **Multi-hospital support** — Federated agent system across hospital networks
5. **Regulatory compliance** — HIPAA-compliant deployment with role-based access to agent interactions

---

## Built With

- Elasticsearch 8.11
- Kibana Agent Builder
- ES|QL
- Time Series Data Streams (TSDS)
- Kibana Dashboards
- Python 3.x
- Rich (CLI framework)

---

## Links

- **GitHub:** https://github.com/preethamtjit20-spec/elastic-pravaah

---

## Team

**Preetham S** — Solo developer
Built with assistance from Claude (Anthropic) for code generation and documentation.

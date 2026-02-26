# Pravaah: Multi-Agent Patient Journey Orchestrator

> *Pravaah* (Sanskrit: "flow") -- an AI-powered patient care system where 5 specialist agents collaborate through Elasticsearch to orchestrate the entire hospital journey, from emergency triage to safe discharge.

**Elasticsearch Agent Builder Hackathon Submission**

## The Problem

Hospital patient care involves dozens of decisions across fragmented systems -- triage scoring in one tool, bed management in another, discharge checklists on paper. Critical patterns get missed when no single system connects the dots. A patient's oxygen saturation dropping subtly from 96% to 91% over 4 hours might not trigger any alarm, but it should.

## The Solution

Pravaah orchestrates **6 AI agents** that collaborate through Elasticsearch, each bringing specialist reasoning to patient care decisions:

| Agent | Role | Superpower |
|-------|------|------------|
| **Triage** | MEWS-based severity scoring | Standardized emergency assessment in seconds |
| **Recovery** | Weighted recovery trajectory | Computes recovery slope from 48h of vitals |
| **Capacity** | Ward occupancy optimization | Real-time bed/staff/ventilator awareness |
| **Discharge** | Conservative 7-point checklist | No patient leaves until ALL criteria pass |
| **Guardian** | Deterioration detection (veto power) | Catches hidden trends other agents miss |
| **Orchestrator** | Coordinates all 5 phases | Full patient journey in one conversation |

## Architecture

```
[User / Kibana Chat] --> Pravaah Orchestrator Agent
                              |
        +----------+----------+----------+----------+
        |          |          |          |          |
   [Triage]  [Recovery]  [Capacity] [Discharge] [Guardian]
    Agent      Agent       Agent      Agent       Agent
        |          |          |          |          |
        +----+-----+----+----+-----+----+-----+----+
             |           |         |         |
     ES|QL Tools   Workflow Tools  Search   TSDS
             |           |         |         |
        [==========================================]
        [           Elasticsearch                  ]
        [  TSDS: vitals | Indices: patients,       ]
        [  capacity, decisions, discharge-plans     ]
        [==========================================]
```

## Elastic Products Used

- **Agent Builder** -- 6 agents with custom system prompts and specialized tool access
- **ES|QL** -- 13 query tools for real-time clinical data analysis
- **Workflows** -- 4 automated workflows for decision logging, alerts, and state updates
- **Time Series Data Streams (TSDS)** -- 1,500+ patient vitals readings at 15-min intervals
- **Elasticsearch** -- 5 indices powering the entire data layer

## The "Wow Moment": Guardian Catches Hidden Deterioration

Patient PAT-008 (Lakshmi Devi, 62, severe asthma) appears stable. Her vitals look normal to the eye. But the Guardian Agent's 3-hour window comparison detects:

- O2 saturation: subtle drop from 96% to 91% over 4 hours
- Respiratory rate: creeping up from 16 to 22 breaths/min
- Two deterioration criteria triggered simultaneously

**Result**: Critical alert raised, discharge blocked, immediate physician review recommended. This is the kind of pattern a busy ward might miss but an always-watching AI agent catches every time.

## Quick Start

### Prerequisites

- Elasticsearch 8.x deployment (Cloud or self-hosted)
- Kibana with Agent Builder enabled
- An LLM connector configured in Kibana (Stack Management > Connectors)
- Python 3.9+

### Setup

```bash
# Clone the repository
git clone https://github.com/your-username/elastic-pravaah.git
cd elastic-pravaah

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your Elasticsearch, Kibana, and connector details

# Run full setup (creates indices, seeds data, registers agents)
python setup.py --setup

# Run demo scenarios
python setup.py --demo

# Clean up when done
python setup.py --teardown
```

### Demo Scenarios

| # | Scenario | Agent | What It Shows |
|---|----------|-------|---------------|
| 1 | Emergency Triage (PAT-007) | Triage | MEWS scoring for acute MI |
| 2 | Recovery Analysis (PAT-002) | Recovery | 48h vital trends and recovery score |
| 3 | Hidden Deterioration (PAT-008) | Guardian | Subtle pattern detection ("wow moment") |
| 4 | Capacity Crisis | Capacity | ICU overflow management |
| 5 | Full Journey (PAT-002) | Orchestrator | All 5 phases through one agent |

## Project Structure

```
elastic-pravaah/
├── setup.py                   # Master setup + demo runner
├── config/settings.py         # Environment configuration
├── utils/api_client.py        # ES + Kibana API client
├── indices/
│   ├── templates.py           # 5 index schemas (1 TSDS + 4 regular)
│   └── seed_data.py           # 8 patients, 1500+ vitals, 7 wards
├── tools/
│   ├── esql_tools.py          # 13 ES|QL tool definitions
│   └── workflow_tools.py      # 4 workflow tool definitions
├── workflows/
│   ├── log_agent_decision.yaml
│   ├── critical_alert.yaml
│   ├── update_discharge_status.yaml
│   └── update_capacity.yaml
├── agents/
│   ├── triage.py              # MEWS-based triage scoring
│   ├── recovery.py            # Weighted recovery trajectory
│   ├── capacity.py            # Ward occupancy optimization
│   ├── discharge.py           # 7-point discharge checklist
│   ├── guardian.py            # Safety oversight with veto power
│   └── orchestrator.py        # 5-phase master coordinator
└── demo/scenarios.py          # 5 demo scenarios
```

## Sample Data

8 patients with distinct clinical story arcs, each designed to showcase different agent capabilities:

| Patient | Diagnosis | Story Arc |
|---------|-----------|-----------|
| PAT-001 | Pneumonia + COPD | Deteriorating (Guardian trigger) |
| PAT-002 | Post-appendectomy | Recovering (discharge candidate) |
| PAT-003 | Heart Failure | Slowly improving (not ready) |
| PAT-004 | Diabetic Ketoacidosis | Rapid recovery (ICU transfer out) |
| PAT-005 | Normal delivery | Normal vitals (easy discharge) |
| PAT-006 | Hip fracture | Stable but immobile (deferred) |
| PAT-007 | Acute MI | Just admitted 4h ago (emergency) |
| PAT-008 | Severe Asthma | Hidden deterioration (wow moment) |

## License

Apache 2.0 -- see [LICENSE](LICENSE)

#!/usr/bin/env python3
"""Create Kibana dashboards for Pravaah via Saved Objects API."""

import json
import requests
from config import settings

KIBANA_URL = settings.KIBANA_URL
API_KEY = settings.KIBANA_API_KEY


def headers():
    return {
        "Authorization": f"ApiKey {API_KEY}",
        "Content-Type": "application/json",
        "kbn-xsrf": "true",
    }


def create_data_views():
    """Create data views for each index."""
    data_views = [
        {
            "name": "Patients",
            "title": "patients",
            "timeFieldName": "admitted_at",
        },
        {
            "name": "Patient Vitals",
            "title": "metrics-patient-vitals",
            "timeFieldName": "@timestamp",
        },
        {
            "name": "Hospital Capacity",
            "title": "hospital-capacity",
            "timeFieldName": "updated_at",
        },
        {
            "name": "Agent Decisions",
            "title": "agent-decisions",
            "timeFieldName": "timestamp",
        },
        {
            "name": "Discharge Plans",
            "title": "discharge-plans",
            "timeFieldName": "updated_at",
        },
    ]

    created = {}
    for dv in data_views:
        print(f"  Creating data view: {dv['name']} ...")
        resp = requests.post(
            f"{KIBANA_URL}/api/data_views/data_view",
            headers=headers(),
            json={"data_view": dv},
            timeout=30,
        )
        if resp.status_code in (200, 409):
            result = resp.json()
            dv_id = result.get("data_view", {}).get("id", "existing")
            created[dv["title"]] = dv_id
            print(f"    OK: {dv_id}")
        else:
            print(f"    Error ({resp.status_code}): {resp.text[:200]}")
            # Try to find existing
            try:
                search_resp = requests.get(
                    f"{KIBANA_URL}/api/data_views",
                    headers=headers(),
                    timeout=30,
                )
                if search_resp.status_code == 200:
                    for existing in search_resp.json().get("data_view", []):
                        if existing.get("title") == dv["title"]:
                            created[dv["title"]] = existing["id"]
                            print(f"    Found existing: {existing['id']}")
                            break
            except Exception:
                pass

    return created


def create_dashboard(data_view_ids):
    """Create the main Pravaah dashboard with panels."""

    vitals_dv = data_view_ids.get("metrics-patient-vitals", "metrics-patient-vitals")
    patients_dv = data_view_ids.get("patients", "patients")
    capacity_dv = data_view_ids.get("hospital-capacity", "hospital-capacity")
    decisions_dv = data_view_ids.get("agent-decisions", "agent-decisions")

    # Build dashboard panels using Lens
    panels = []

    # Panel 1: Patient Count (metric)
    panels.append({
        "type": "lens",
        "gridData": {"x": 0, "y": 0, "w": 8, "h": 8, "i": "panel_1"},
        "panelIndex": "panel_1",
        "embeddableConfig": {
            "attributes": {
                "title": "Total Patients",
                "visualizationType": "lnsMetric",
                "state": {
                    "datasourceStates": {
                        "formBased": {
                            "layers": {
                                "layer1": {
                                    "columns": {
                                        "col1": {
                                            "operationType": "count",
                                            "label": "Patients",
                                            "dataType": "number",
                                            "sourceField": "___records___",
                                        }
                                    },
                                    "columnOrder": ["col1"],
                                    "indexPatternId": patients_dv,
                                }
                            }
                        }
                    },
                    "visualization": {
                        "layerId": "layer1",
                        "accessor": "col1",
                    },
                },
                "references": [
                    {"type": "index-pattern", "id": patients_dv, "name": "indexpattern-datasource-layer-layer1"}
                ],
            },
        },
    })

    # Panel 2: Ward Occupancy (bar chart)
    panels.append({
        "type": "lens",
        "gridData": {"x": 8, "y": 0, "w": 20, "h": 8, "i": "panel_2"},
        "panelIndex": "panel_2",
        "embeddableConfig": {
            "attributes": {
                "title": "Ward Occupancy Rate (%)",
                "visualizationType": "lnsXY",
                "state": {
                    "datasourceStates": {
                        "formBased": {
                            "layers": {
                                "layer1": {
                                    "columns": {
                                        "col_ward": {
                                            "operationType": "terms",
                                            "sourceField": "ward",
                                            "label": "Ward",
                                            "dataType": "string",
                                            "params": {"size": 10, "orderDirection": "desc", "orderBy": {"type": "column", "columnId": "col_rate"}},
                                        },
                                        "col_rate": {
                                            "operationType": "max",
                                            "sourceField": "occupancy_rate",
                                            "label": "Occupancy %",
                                            "dataType": "number",
                                        },
                                    },
                                    "columnOrder": ["col_ward", "col_rate"],
                                    "indexPatternId": capacity_dv,
                                }
                            }
                        }
                    },
                    "visualization": {
                        "layers": [{
                            "layerId": "layer1",
                            "seriesType": "bar_horizontal",
                            "xAccessor": "col_ward",
                            "accessors": ["col_rate"],
                        }],
                        "preferredSeriesType": "bar_horizontal",
                    },
                },
                "references": [
                    {"type": "index-pattern", "id": capacity_dv, "name": "indexpattern-datasource-layer-layer1"}
                ],
            },
        },
    })

    # Panel 3: Patient severity breakdown (donut)
    panels.append({
        "type": "lens",
        "gridData": {"x": 28, "y": 0, "w": 20, "h": 8, "i": "panel_3"},
        "panelIndex": "panel_3",
        "embeddableConfig": {
            "attributes": {
                "title": "Patients by Severity",
                "visualizationType": "lnsPie",
                "state": {
                    "datasourceStates": {
                        "formBased": {
                            "layers": {
                                "layer1": {
                                    "columns": {
                                        "col_severity": {
                                            "operationType": "terms",
                                            "sourceField": "severity",
                                            "label": "Severity",
                                            "dataType": "string",
                                            "params": {"size": 5},
                                        },
                                        "col_count": {
                                            "operationType": "count",
                                            "label": "Count",
                                            "dataType": "number",
                                            "sourceField": "___records___",
                                        },
                                    },
                                    "columnOrder": ["col_severity", "col_count"],
                                    "indexPatternId": patients_dv,
                                }
                            }
                        }
                    },
                    "visualization": {
                        "layers": [{
                            "layerId": "layer1",
                            "primaryGroups": ["col_severity"],
                            "metric": "col_count",
                        }],
                        "shape": "donut",
                    },
                },
                "references": [
                    {"type": "index-pattern", "id": patients_dv, "name": "indexpattern-datasource-layer-layer1"}
                ],
            },
        },
    })

    # Create the dashboard
    dashboard_body = {
        "attributes": {
            "title": "Pravaah - Patient Journey Command Center",
            "description": "Multi-agent patient monitoring: vitals, capacity, severity, and agent decisions",
            "panelsJSON": json.dumps(panels),
            "timeRestore": True,
            "timeTo": "now",
            "timeFrom": "now-48h",
            "refreshInterval": {"pause": False, "value": 30000},
            "kibanaSavedObjectMeta": {
                "searchSourceJSON": json.dumps({"query": {"query": "", "language": "kuery"}, "filter": []})
            },
        },
    }

    print("  Creating dashboard ...")
    resp = requests.post(
        f"{KIBANA_URL}/api/saved_objects/dashboard",
        headers=headers(),
        json=dashboard_body,
        timeout=30,
    )

    if resp.status_code in (200, 201):
        dashboard_id = resp.json().get("id", "unknown")
        print(f"  Dashboard created: {dashboard_id}")
        print(f"\n  Open it at: {KIBANA_URL}/app/dashboards#/view/{dashboard_id}")
        return dashboard_id
    else:
        print(f"  Error ({resp.status_code}): {resp.text[:500]}")
        return None


def main():
    print("=== Creating Pravaah Kibana Dashboard ===\n")

    print("[1/2] Creating data views ...")
    dv_ids = create_data_views()
    print(f"  Created {len(dv_ids)} data views\n")

    print("[2/2] Creating dashboard ...")
    dashboard_id = create_dashboard(dv_ids)

    if dashboard_id:
        print(f"\n=== Done! ===")
        print(f"Open your dashboard in Kibana:")
        print(f"  Kibana > Dashboards > 'Pravaah - Patient Journey Command Center'")
    else:
        print("\nDashboard creation via API had issues.")
        print("You can create it manually - see instructions below.\n")
        print_manual_instructions()


def print_manual_instructions():
    """Fallback: print instructions for manual dashboard creation."""
    print("""
=== Manual Dashboard Creation ===

1. Go to Kibana > Dashboards > Create dashboard

2. Add these visualizations:

   a) METRIC: Total Patients
      - Index: patients
      - Metric: Count

   b) BAR CHART: Ward Occupancy
      - Index: hospital-capacity
      - X-axis: ward (Terms)
      - Y-axis: Max of occupancy_rate

   c) DONUT: Patients by Severity
      - Index: patients
      - Slice by: severity (Terms)
      - Size: Count

   d) LINE CHART: Heart Rate Over Time (per patient)
      - Index: metrics-patient-vitals
      - X-axis: @timestamp
      - Y-axis: Avg heart_rate
      - Break down by: patient_id

   e) LINE CHART: O2 Saturation Over Time
      - Index: metrics-patient-vitals
      - X-axis: @timestamp
      - Y-axis: Avg oxygen_saturation
      - Break down by: patient_id

   f) TABLE: Patient List
      - Index: patients
      - Columns: patient_id, name, age, diagnosis, severity, ward

   g) TABLE: Agent Decisions Log
      - Index: agent-decisions
      - Columns: timestamp, agent_name, patient_id, decision_type, action

3. Set time range to "Last 48 hours"
4. Save as "Pravaah - Patient Journey Command Center"
""")


if __name__ == "__main__":
    main()

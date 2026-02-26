"""Elasticsearch index templates and schemas for Pravaah."""

from config import settings


def vitals_index_template():
    """TSDS template for metrics-patient-vitals data stream."""
    return {
        "index_patterns": ["metrics-patient-vitals*"],
        "data_stream": {},
        "priority": 500,
        "template": {
            "settings": {
                "index.mode": "time_series",
                "index.routing_path": ["patient_id", "ward"],
                "index.look_back_time": "72h",
            },
            "mappings": {
                "properties": {
                    "@timestamp": {"type": "date"},
                    "patient_id": {
                        "type": "keyword",
                        "time_series_dimension": True,
                    },
                    "ward": {
                        "type": "keyword",
                        "time_series_dimension": True,
                    },
                    "heart_rate": {
                        "type": "float",
                        "time_series_metric": "gauge",
                    },
                    "systolic_bp": {
                        "type": "float",
                        "time_series_metric": "gauge",
                    },
                    "diastolic_bp": {
                        "type": "float",
                        "time_series_metric": "gauge",
                    },
                    "oxygen_saturation": {
                        "type": "float",
                        "time_series_metric": "gauge",
                    },
                    "temperature": {
                        "type": "float",
                        "time_series_metric": "gauge",
                    },
                    "respiratory_rate": {
                        "type": "float",
                        "time_series_metric": "gauge",
                    },
                    "pain_score": {
                        "type": "integer",
                        "time_series_metric": "gauge",
                    },
                },
            },
        },
    }


def patients_index():
    """Schema for patients index."""
    return {
        "mappings": {
            "properties": {
                "patient_id": {"type": "keyword"},
                "name": {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
                "age": {"type": "integer"},
                "diagnosis": {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
                "severity": {"type": "keyword"},  # critical, high, moderate, low
                "ward": {"type": "keyword"},
                "admitted_at": {"type": "date"},
                "comorbidities": {"type": "keyword"},  # array of keywords
                "status": {"type": "keyword"},  # admitted, discharged, transferred
                "attending_physician": {"type": "keyword"},
                "notes": {"type": "text"},
            }
        }
    }


def capacity_index():
    """Schema for hospital-capacity index."""
    return {
        "mappings": {
            "properties": {
                "ward": {"type": "keyword"},
                "ward_name": {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
                "total_beds": {"type": "integer"},
                "occupied_beds": {"type": "integer"},
                "available_beds": {"type": "integer"},
                "occupancy_rate": {"type": "float"},
                "ventilators_total": {"type": "integer"},
                "ventilators_in_use": {"type": "integer"},
                "nurses_on_duty": {"type": "integer"},
                "doctors_on_duty": {"type": "integer"},
                "staffing_ratio": {"type": "float"},  # nurse-to-patient
                "updated_at": {"type": "date"},
            }
        }
    }


def decisions_index():
    """Schema for agent-decisions audit log index."""
    return {
        "mappings": {
            "properties": {
                "timestamp": {"type": "date"},
                "agent_name": {"type": "keyword"},
                "patient_id": {"type": "keyword"},
                "decision_type": {"type": "keyword"},
                "action": {"type": "keyword"},
                "reasoning": {"type": "text"},
                "confidence": {"type": "float"},
                "risk_level": {"type": "keyword"},
                "requires_review": {"type": "boolean"},
                "metadata": {"type": "object", "enabled": False},
            }
        }
    }


def discharge_index():
    """Schema for discharge-plans index."""
    return {
        "mappings": {
            "properties": {
                "patient_id": {"type": "keyword"},
                "created_at": {"type": "date"},
                "updated_at": {"type": "date"},
                "status": {"type": "keyword"},  # pending, approved, discharged, deferred
                "target_discharge_date": {"type": "date"},
                # 7-point criteria checklist
                "vitals_stable": {"type": "boolean"},
                "no_fever_24h": {"type": "boolean"},
                "pain_controlled": {"type": "boolean"},
                "mobility_adequate": {"type": "boolean"},
                "oral_medication_tolerated": {"type": "boolean"},
                "follow_up_scheduled": {"type": "boolean"},
                "patient_educated": {"type": "boolean"},
                "criteria_met_count": {"type": "integer"},
                "criteria_total": {"type": "integer"},
                "discharge_notes": {"type": "text"},
                "approved_by": {"type": "keyword"},
            }
        }
    }


# -- Setup / Teardown ----------------------------------------------------


def create_all_indices(client):
    """Create all indices and data streams."""
    results = {}

    # 1. TSDS: create index template then data stream
    print("  Creating TSDS template: metrics-patient-vitals ...")
    results["vitals_template"] = client.put_index_template(
        "metrics-patient-vitals",
        vitals_index_template(),
    )
    print("  Creating data stream: metrics-patient-vitals ...")
    results["vitals_stream"] = client.create_data_stream(settings.INDEX_VITALS)

    # 2. Regular indices
    for name, schema_fn in [
        (settings.INDEX_PATIENTS, patients_index),
        (settings.INDEX_CAPACITY, capacity_index),
        (settings.INDEX_DECISIONS, decisions_index),
        (settings.INDEX_DISCHARGE, discharge_index),
    ]:
        print(f"  Creating index: {name} ...")
        results[name] = client.create_index(name, schema_fn())

    return results


def delete_all_indices(client):
    """Delete all indices and data streams."""
    results = {}

    # Data stream first (depends on template)
    print("  Deleting data stream: metrics-patient-vitals ...")
    results["vitals_stream"] = client.delete_data_stream(settings.INDEX_VITALS)
    print("  Deleting index template: metrics-patient-vitals ...")
    results["vitals_template"] = client.delete_index_template("metrics-patient-vitals")

    for name in [
        settings.INDEX_PATIENTS,
        settings.INDEX_CAPACITY,
        settings.INDEX_DECISIONS,
        settings.INDEX_DISCHARGE,
    ]:
        print(f"  Deleting index: {name} ...")
        results[name] = client.delete_index(name)

    return results

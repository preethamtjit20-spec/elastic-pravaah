"""4 workflow tool definitions for Pravaah agents.

Each workflow tool wraps a YAML workflow definition and makes it
available as a tool in the Agent Builder.
"""

import yaml
import os

WORKFLOW_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "workflows")


def _load_workflow_yaml(filename):
    """Load a workflow YAML file and return its contents."""
    path = os.path.join(WORKFLOW_DIR, filename)
    with open(path, "r") as f:
        return yaml.safe_load(f)


def _workflow_tool(name, description, workflow_filename, parameters=None):
    """Helper to build a workflow tool definition."""
    workflow_def = _load_workflow_yaml(workflow_filename)
    tool = {
        "name": name,
        "description": description,
        "type": "workflow",
        "configuration": {
            "workflow": workflow_def,
        },
    }
    if parameters:
        tool["parameters"] = parameters
    return tool


# ========================================================================
# WORKFLOW TOOLS (4)
# ========================================================================


def log_decision():
    """Tool to log any agent decision to the audit trail."""
    return _workflow_tool(
        name="log_decision",
        description=(
            "Log an agent decision to the agent-decisions audit index. "
            "Every significant decision made by any agent should be logged "
            "for traceability and compliance. Records the agent name, "
            "patient ID, decision type, reasoning, and confidence score."
        ),
        workflow_filename="log_agent_decision.yaml",
        parameters=[
            {"name": "agent_name", "type": "string", "description": "Agent making the decision", "required": True},
            {"name": "patient_id", "type": "string", "description": "Patient ID", "required": True},
            {"name": "decision_type", "type": "string", "description": "Type: triage, recovery_assessment, capacity_check, discharge_evaluation, safety_alert", "required": True},
            {"name": "action", "type": "string", "description": "Action taken or recommended", "required": True},
            {"name": "reasoning", "type": "string", "description": "Detailed reasoning", "required": True},
            {"name": "confidence", "type": "number", "description": "Confidence 0.0-1.0", "required": True},
            {"name": "risk_level", "type": "string", "description": "Risk: low, moderate, high, critical", "required": False},
            {"name": "requires_review", "type": "boolean", "description": "Needs human review?", "required": False},
        ],
    )


def raise_critical_alert():
    """Tool to raise a critical alert requiring immediate review."""
    return _workflow_tool(
        name="raise_critical_alert",
        description=(
            "SAFETY-CRITICAL: Raise an alert requiring immediate human review. "
            "Used when an agent detects a dangerous situation such as patient "
            "deterioration, unsafe discharge conditions, or capacity emergencies. "
            "Always sets requires_review=true and risk_level=critical."
        ),
        workflow_filename="critical_alert.yaml",
        parameters=[
            {"name": "agent_name", "type": "string", "description": "Agent raising the alert", "required": True},
            {"name": "patient_id", "type": "string", "description": "Patient ID", "required": True},
            {"name": "alert_type", "type": "string", "description": "Alert type: deterioration_detected, safety_veto, critical_vitals, capacity_emergency", "required": True},
            {"name": "reasoning", "type": "string", "description": "Why this alert was raised", "required": True},
            {"name": "recommended_action", "type": "string", "description": "What should be done immediately", "required": True},
            {"name": "confidence", "type": "number", "description": "Confidence 0.0-1.0", "required": True},
        ],
    )


def update_discharge():
    """Tool to create or update a discharge plan."""
    return _workflow_tool(
        name="update_discharge",
        description=(
            "Create or update a discharge plan for a patient with a 7-point "
            "criteria assessment. Evaluates: vitals stability, fever-free status, "
            "pain control, mobility, oral medication tolerance, follow-up scheduling, "
            "and patient education."
        ),
        workflow_filename="update_discharge_status.yaml",
        parameters=[
            {"name": "patient_id", "type": "string", "description": "Patient ID", "required": True},
            {"name": "status", "type": "string", "description": "Status: pending, approved, discharged, deferred", "required": True},
            {"name": "vitals_stable", "type": "boolean", "description": "Vitals stable 24+ hours?", "required": True},
            {"name": "no_fever_24h", "type": "boolean", "description": "No fever in 24h?", "required": True},
            {"name": "pain_controlled", "type": "boolean", "description": "Pain score < 4?", "required": True},
            {"name": "mobility_adequate", "type": "boolean", "description": "Can mobilize for home care?", "required": True},
            {"name": "oral_medication_tolerated", "type": "boolean", "description": "Tolerating oral meds?", "required": True},
            {"name": "follow_up_scheduled", "type": "boolean", "description": "Follow-up scheduled?", "required": True},
            {"name": "patient_educated", "type": "boolean", "description": "Patient educated?", "required": True},
            {"name": "target_discharge_date", "type": "string", "description": "Target date (ISO format)", "required": False},
            {"name": "discharge_notes", "type": "string", "description": "Additional notes", "required": False},
        ],
    )


def update_ward_capacity():
    """Tool to update ward capacity after admission/transfer/discharge."""
    return _workflow_tool(
        name="update_ward_capacity",
        description=(
            "Update ward bed capacity when a patient is admitted, transferred, "
            "or discharged. Automatically recalculates available beds and "
            "occupancy rate."
        ),
        workflow_filename="update_capacity.yaml",
        parameters=[
            {"name": "ward", "type": "string", "description": "Ward name (e.g., ICU, surgical)", "required": True},
            {"name": "occupied_beds", "type": "number", "description": "New occupied bed count", "required": True},
            {"name": "total_beds", "type": "number", "description": "Total beds in ward", "required": True},
            {"name": "ventilators_in_use", "type": "number", "description": "Ventilators in use", "required": False},
            {"name": "notes", "type": "string", "description": "Reason for update", "required": False},
        ],
    )


# ========================================================================
# Registry
# ========================================================================


def all_tools():
    """Return all 4 workflow tool definitions."""
    return [
        log_decision(),
        raise_critical_alert(),
        update_discharge(),
        update_ward_capacity(),
    ]


WORKFLOW_TOOL_NAMES = [
    "log_decision",
    "raise_critical_alert",
    "update_discharge",
    "update_ward_capacity",
]

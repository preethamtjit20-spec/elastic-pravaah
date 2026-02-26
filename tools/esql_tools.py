"""13 ES|QL tool definitions for Pravaah agents.

Each function returns a tool definition dict that can be registered
with Kibana's Agent Builder API.
"""


def _esql_tool(name, description, query, parameters=None):
    """Helper to build an ES|QL tool definition."""
    tool = {
        "name": name,
        "description": description,
        "type": "esql",
        "configuration": {
            "query": query,
        },
    }
    if parameters:
        tool["parameters"] = parameters
    return tool


# ========================================================================
# TRIAGE TOOLS (3)
# ========================================================================


def latest_vitals():
    """Get the most recent vitals for a specific patient."""
    return _esql_tool(
        name="latest_vitals",
        description=(
            "Retrieve the most recent vital signs for a specific patient. "
            "Returns heart_rate, systolic_bp, diastolic_bp, oxygen_saturation, "
            "temperature, respiratory_rate, and pain_score."
        ),
        query=(
            "FROM metrics-patient-vitals "
            "| WHERE patient_id == ?patient_id "
            "| SORT @timestamp DESC "
            "| LIMIT 1"
        ),
        parameters=[
            {
                "name": "patient_id",
                "type": "string",
                "description": "Patient ID (e.g., PAT-001)",
                "required": True,
            }
        ],
    )


def patient_record():
    """Get the full patient record from the patients index."""
    return _esql_tool(
        name="patient_record",
        description=(
            "Retrieve the full patient record including demographics, diagnosis, "
            "severity, ward assignment, comorbidities, and status."
        ),
        query=(
            "FROM patients "
            "| WHERE patient_id == ?patient_id "
            "| LIMIT 1"
        ),
        parameters=[
            {
                "name": "patient_id",
                "type": "string",
                "description": "Patient ID (e.g., PAT-001)",
                "required": True,
            }
        ],
    )


def ward_patients_by_severity():
    """List all patients in a ward sorted by severity."""
    return _esql_tool(
        name="ward_patients_by_severity",
        description=(
            "List all patients in a specific ward, sorted by severity "
            "(critical first, then high, moderate, low). Useful for triage "
            "prioritization and ward overview."
        ),
        query=(
            "FROM patients "
            "| WHERE ward == ?ward AND status == \"admitted\" "
            "| EVAL severity_rank = CASE("
            "    severity == \"critical\", 1, "
            "    severity == \"high\", 2, "
            "    severity == \"moderate\", 3, "
            "    4) "
            "| SORT severity_rank ASC "
            "| DROP severity_rank"
        ),
        parameters=[
            {
                "name": "ward",
                "type": "string",
                "description": "Ward name (e.g., ICU, surgical, cardiac, emergency)",
                "required": True,
            }
        ],
    )


# ========================================================================
# RECOVERY TOOLS (2)
# ========================================================================


def vitals_trend():
    """Get hourly-bucketed vital sign trends for a patient."""
    return _esql_tool(
        name="vitals_trend",
        description=(
            "Get hourly-averaged vital sign trends for a patient over the last "
            "48 hours. Returns time-bucketed averages of all vital signs, useful "
            "for spotting recovery trajectories or deterioration patterns."
        ),
        query=(
            "FROM metrics-patient-vitals "
            "| WHERE patient_id == ?patient_id "
            "| EVAL bucket = DATE_TRUNC(1 hour, @timestamp) "
            "| STATS "
            "    avg_hr = AVG(heart_rate), "
            "    avg_systolic = AVG(systolic_bp), "
            "    avg_diastolic = AVG(diastolic_bp), "
            "    avg_o2 = AVG(oxygen_saturation), "
            "    avg_temp = AVG(temperature), "
            "    avg_rr = AVG(respiratory_rate), "
            "    avg_pain = AVG(pain_score), "
            "    readings = COUNT(*) "
            "  BY bucket "
            "| SORT bucket ASC"
        ),
        parameters=[
            {
                "name": "patient_id",
                "type": "string",
                "description": "Patient ID (e.g., PAT-002)",
                "required": True,
            }
        ],
    )


def vitals_statistics():
    """Get min/max/avg statistics for a patient's vitals."""
    return _esql_tool(
        name="vitals_statistics",
        description=(
            "Get overall vital sign statistics (min, max, average) for a patient "
            "over the entire admission period. Useful for understanding the range "
            "of values and overall recovery trajectory."
        ),
        query=(
            "FROM metrics-patient-vitals "
            "| WHERE patient_id == ?patient_id "
            "| STATS "
            "    min_hr = MIN(heart_rate), max_hr = MAX(heart_rate), avg_hr = AVG(heart_rate), "
            "    min_systolic = MIN(systolic_bp), max_systolic = MAX(systolic_bp), avg_systolic = AVG(systolic_bp), "
            "    min_o2 = MIN(oxygen_saturation), max_o2 = MAX(oxygen_saturation), avg_o2 = AVG(oxygen_saturation), "
            "    min_temp = MIN(temperature), max_temp = MAX(temperature), avg_temp = AVG(temperature), "
            "    min_rr = MIN(respiratory_rate), max_rr = MAX(respiratory_rate), avg_rr = AVG(respiratory_rate), "
            "    min_pain = MIN(pain_score), max_pain = MAX(pain_score), avg_pain = AVG(pain_score), "
            "    total_readings = COUNT(*)"
        ),
        parameters=[
            {
                "name": "patient_id",
                "type": "string",
                "description": "Patient ID",
                "required": True,
            }
        ],
    )


# ========================================================================
# CAPACITY TOOLS (3)
# ========================================================================


def ward_status():
    """Get capacity status for all wards."""
    return _esql_tool(
        name="ward_status",
        description=(
            "Get current capacity status for ALL hospital wards including "
            "bed counts, occupancy rate, ventilator availability, and staffing "
            "ratios. Essential for placement and transfer decisions."
        ),
        query=(
            "FROM hospital-capacity "
            "| SORT occupancy_rate DESC"
        ),
    )


def specific_ward():
    """Get detailed info for a specific ward."""
    return _esql_tool(
        name="specific_ward",
        description=(
            "Get detailed capacity information for a specific ward including "
            "all bed counts, ventilator status, and staffing levels."
        ),
        query=(
            "FROM hospital-capacity "
            "| WHERE ward == ?ward "
            "| LIMIT 1"
        ),
        parameters=[
            {
                "name": "ward",
                "type": "string",
                "description": "Ward name (e.g., ICU, surgical, cardiac)",
                "required": True,
            }
        ],
    )


def patients_in_ward():
    """List all admitted patients in a specific ward."""
    return _esql_tool(
        name="patients_in_ward",
        description=(
            "List all currently admitted patients in a specific ward with "
            "their diagnosis and severity. Useful for capacity planning and "
            "understanding ward composition."
        ),
        query=(
            "FROM patients "
            "| WHERE ward == ?ward AND status == \"admitted\" "
            "| KEEP patient_id, name, age, diagnosis, severity, admitted_at"
        ),
        parameters=[
            {
                "name": "ward",
                "type": "string",
                "description": "Ward name",
                "required": True,
            }
        ],
    )


# ========================================================================
# DISCHARGE TOOLS (2)
# ========================================================================


def readiness_check():
    """Check discharge readiness for a patient."""
    return _esql_tool(
        name="readiness_check",
        description=(
            "Check the current discharge readiness for a patient. Returns "
            "the discharge plan with all 7 criteria assessments, criteria "
            "met count, current status, and target discharge date."
        ),
        query=(
            "FROM discharge-plans "
            "| WHERE patient_id == ?patient_id "
            "| SORT updated_at DESC "
            "| LIMIT 1"
        ),
        parameters=[
            {
                "name": "patient_id",
                "type": "string",
                "description": "Patient ID",
                "required": True,
            }
        ],
    )


def recent_vitals_stability():
    """Check vital sign stability over the last 24 hours."""
    return _esql_tool(
        name="recent_vitals_stability",
        description=(
            "Analyze vital sign stability over the last 24 hours for discharge "
            "evaluation. Returns standard deviation and range of key vitals - "
            "low variance indicates stability suitable for discharge."
        ),
        query=(
            "FROM metrics-patient-vitals "
            "| WHERE patient_id == ?patient_id "
            "  AND @timestamp > NOW() - 24 hours "
            "| STATS "
            "    avg_hr = AVG(heart_rate), "
            "    min_hr = MIN(heart_rate), max_hr = MAX(heart_rate), "
            "    avg_o2 = AVG(oxygen_saturation), "
            "    min_o2 = MIN(oxygen_saturation), max_o2 = MAX(oxygen_saturation), "
            "    avg_temp = AVG(temperature), "
            "    min_temp = MIN(temperature), max_temp = MAX(temperature), "
            "    avg_rr = AVG(respiratory_rate), "
            "    min_rr = MIN(respiratory_rate), max_rr = MAX(respiratory_rate), "
            "    max_pain = MAX(pain_score), "
            "    readings = COUNT(*)"
        ),
        parameters=[
            {
                "name": "patient_id",
                "type": "string",
                "description": "Patient ID",
                "required": True,
            }
        ],
    )


# ========================================================================
# GUARDIAN TOOLS (3)
# ========================================================================


def deterioration_check():
    """Compare recent 3h window vs prior 3h to detect deterioration."""
    return _esql_tool(
        name="deterioration_check",
        description=(
            "CRITICAL SAFETY TOOL: Compare the most recent 3-hour window of "
            "vitals against the prior 3-hour window to detect deterioration. "
            "A worsening trend (rising HR, falling O2, rising temp/RR) signals "
            "danger even if absolute values seem acceptable."
        ),
        query=(
            "FROM metrics-patient-vitals "
            "| WHERE patient_id == ?patient_id "
            "  AND @timestamp > NOW() - 6 hours "
            "| EVAL window = CASE("
            "    @timestamp > NOW() - 3 hours, \"recent\", "
            "    \"prior\") "
            "| STATS "
            "    avg_hr = AVG(heart_rate), "
            "    avg_o2 = AVG(oxygen_saturation), "
            "    avg_temp = AVG(temperature), "
            "    avg_rr = AVG(respiratory_rate), "
            "    avg_systolic = AVG(systolic_bp), "
            "    avg_pain = AVG(pain_score), "
            "    readings = COUNT(*) "
            "  BY window "
            "| SORT window ASC"
        ),
        parameters=[
            {
                "name": "patient_id",
                "type": "string",
                "description": "Patient ID to check for deterioration",
                "required": True,
            }
        ],
    )


def recent_decisions():
    """Get recent agent decisions for a patient."""
    return _esql_tool(
        name="recent_decisions",
        description=(
            "Retrieve recent agent decisions for a patient from the audit log. "
            "Useful for understanding what assessments have already been made "
            "and ensuring consistency across agent recommendations."
        ),
        query=(
            "FROM agent-decisions "
            "| WHERE patient_id == ?patient_id "
            "| SORT timestamp DESC "
            "| LIMIT 10"
        ),
        parameters=[
            {
                "name": "patient_id",
                "type": "string",
                "description": "Patient ID",
                "required": True,
            }
        ],
    )


def critical_patients_scan():
    """Scan all patients for potential deterioration across the hospital."""
    return _esql_tool(
        name="critical_patients_scan",
        description=(
            "PROACTIVE SAFETY SCAN: Get the latest vitals for ALL admitted "
            "patients, flagging any with concerning values (HR > 110, O2 < 92, "
            "temp > 38.5, RR > 25). Used by Guardian agent for hospital-wide "
            "safety monitoring."
        ),
        query=(
            "FROM metrics-patient-vitals "
            "| STATS "
            "    latest_hr = MAX(heart_rate), "
            "    latest_o2 = MIN(oxygen_saturation), "
            "    latest_temp = MAX(temperature), "
            "    latest_rr = MAX(respiratory_rate), "
            "    latest_time = MAX(@timestamp) "
            "  BY patient_id, ward "
            "| WHERE latest_hr > 110 OR latest_o2 < 92 "
            "  OR latest_temp > 38.5 OR latest_rr > 25 "
            "| SORT latest_o2 ASC"
        ),
    )


# ========================================================================
# Registry
# ========================================================================


def all_tools():
    """Return all 13 ES|QL tool definitions."""
    return [
        # Triage (3)
        latest_vitals(),
        patient_record(),
        ward_patients_by_severity(),
        # Recovery (2)
        vitals_trend(),
        vitals_statistics(),
        # Capacity (3)
        ward_status(),
        specific_ward(),
        patients_in_ward(),
        # Discharge (2)
        readiness_check(),
        recent_vitals_stability(),
        # Guardian (3)
        deterioration_check(),
        recent_decisions(),
        critical_patients_scan(),
    ]


# Tool groupings by agent
TRIAGE_TOOLS = ["latest_vitals", "patient_record", "ward_patients_by_severity"]
RECOVERY_TOOLS = ["vitals_trend", "vitals_statistics"]
CAPACITY_TOOLS = ["ward_status", "specific_ward", "patients_in_ward"]
DISCHARGE_TOOLS = ["readiness_check", "recent_vitals_stability"]
GUARDIAN_TOOLS = ["deterioration_check", "recent_decisions", "critical_patients_scan"]

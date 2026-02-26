"""Configuration settings loaded from environment variables."""

import os
from dotenv import load_dotenv

load_dotenv()

# Kibana
KIBANA_URL = os.getenv("KIBANA_URL", "").rstrip("/")
KIBANA_API_KEY = os.getenv("KIBANA_API_KEY", "")

# Elasticsearch
ES_URL = os.getenv("ES_URL", "").rstrip("/")
ES_API_KEY = os.getenv("ES_API_KEY", "")

# LLM Connector (created in Kibana Stack Management > Connectors)
LLM_CONNECTOR_ID = os.getenv("LLM_CONNECTOR_ID", "")

# Index names
INDEX_VITALS = "metrics-patient-vitals"
INDEX_PATIENTS = "patients"
INDEX_CAPACITY = "hospital-capacity"
INDEX_DECISIONS = "agent-decisions"
INDEX_DISCHARGE = "discharge-plans"

# Agent Builder API paths
AGENT_API = "/api/security_ai_assistant/current_user/conversations"
TOOLS_API = "/api/fleet/agent_policies"

# Timeouts
REQUEST_TIMEOUT = 30


def validate():
    """Check that required env vars are set."""
    missing = []
    if not ES_URL:
        missing.append("ES_URL")
    if not ES_API_KEY:
        missing.append("ES_API_KEY")
    if missing:
        raise EnvironmentError(
            f"Missing required environment variables: {', '.join(missing)}. "
            f"Copy .env.example to .env and fill in values."
        )

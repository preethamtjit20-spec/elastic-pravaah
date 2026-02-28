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
    """Check that required env vars are set and basic sanity checks pass."""
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

    # Sanity checks to prevent misuse
    if not ES_URL.startswith("https://"):
        raise ValueError("ES_URL must use HTTPS for secure communication.")
    if KIBANA_URL and not KIBANA_URL.startswith("https://"):
        raise ValueError("KIBANA_URL must use HTTPS for secure communication.")
    if len(ES_API_KEY) < 20:
        raise ValueError("ES_API_KEY looks too short - check your API key.")


def redacted_key(key):
    """Return a redacted version of an API key for safe logging."""
    if not key or len(key) < 8:
        return "***"
    return key[:4] + "..." + key[-4:]

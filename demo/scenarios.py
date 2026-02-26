"""5 demo scenarios showcasing Pravaah's multi-agent orchestration.

Each scenario sends a natural language prompt to a specific agent
(or the orchestrator) via the Agent Builder converse API and displays
the response.
"""

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

console = Console()


# ========================================================================
# Scenario definitions
# ========================================================================

SCENARIOS = [
    {
        "id": 1,
        "title": "Emergency Triage - Acute MI (PAT-007)",
        "description": (
            "Amit Joshi, 55, just arrived in the emergency department 4 hours ago "
            "with crushing chest pain. The Triage Agent assesses severity using "
            "MEWS scoring and recommends immediate care pathway."
        ),
        "agent": "triage-agent",
        "message": (
            "Urgent triage needed for patient PAT-007. This is a 55-year-old male "
            "who presented to the emergency department approximately 4 hours ago "
            "with acute chest pain and suspected myocardial infarction. Please "
            "retrieve his vitals, calculate his MEWS score, assess severity, "
            "and recommend the appropriate care pathway and ward placement."
        ),
    },
    {
        "id": 2,
        "title": "Recovery Analysis - Post-Appendectomy (PAT-002)",
        "description": (
            "Ananya Sharma, 34, is recovering from an appendectomy. The Recovery "
            "Agent analyzes her 48-hour vital sign trends to compute a recovery "
            "score and estimate time to discharge."
        ),
        "agent": "recovery-agent",
        "message": (
            "Please analyze the recovery trajectory for patient PAT-002. She is "
            "a 34-year-old female recovering from a post-appendectomy in the "
            "surgical ward. Review her vital sign trends over the past 48 hours, "
            "compute her weighted recovery score, and provide a recovery status "
            "classification with estimated days to full recovery."
        ),
    },
    {
        "id": 3,
        "title": "Guardian Catches Hidden Deterioration (PAT-008)",
        "description": (
            "Lakshmi Devi, 62, has severe asthma and appears stable. But the "
            "Guardian Agent's 3-hour window comparison catches a subtle "
            "deterioration pattern that might be missed by routine monitoring. "
            "This is the 'wow moment' demo."
        ),
        "agent": "guardian-agent",
        "message": (
            "Run a safety assessment for patient PAT-008. She is a 62-year-old "
            "female with severe asthma in the respiratory ward. Compare her "
            "recent 3-hour vital sign window against her prior 3-hour window "
            "to check for any deterioration trends. Also run a hospital-wide "
            "critical patient scan to see if there are any other patients "
            "of concern."
        ),
    },
    {
        "id": 4,
        "title": "Capacity Crisis - ICU Full",
        "description": (
            "The ICU is at 92% occupancy (11/12 beds). A new critical patient "
            "needs ICU admission. The Capacity Agent evaluates options: find a "
            "bed, recommend transfers, or identify overflow solutions."
        ),
        "agent": "capacity-agent",
        "message": (
            "We have a capacity situation. A new critical patient requires ICU "
            "admission but the ICU is nearly full. Please check the current "
            "capacity across all wards, evaluate ICU bed availability, review "
            "which ICU patients might be candidates for step-down transfer "
            "to free up beds, and recommend the best course of action. "
            "Consider patient PAT-004 (diabetic ketoacidosis, rapid recovery) "
            "as a potential transfer-out candidate."
        ),
    },
    {
        "id": 5,
        "title": "Full Orchestrated Journey - PAT-002 Discharge",
        "description": (
            "The Pravaah Orchestrator runs all 5 phases for Ananya Sharma's "
            "discharge evaluation: triage review, recovery analysis, capacity "
            "impact, discharge checklist, and safety clearance. This demonstrates "
            "the full multi-agent collaboration through a single orchestrator."
        ),
        "agent": "pravaah-orchestrator",
        "message": (
            "Run a complete patient journey assessment for PAT-002 (Ananya Sharma, "
            "34, post-appendectomy, surgical ward). She has been recovering well "
            "and we need to evaluate her for potential discharge. Please execute "
            "all five phases:\n\n"
            "1. TRIAGE REVIEW: Verify current severity and vital signs\n"
            "2. RECOVERY ANALYSIS: Compute her recovery score and trajectory\n"
            "3. CAPACITY CHECK: Assess if her bed is needed urgently\n"
            "4. DISCHARGE EVALUATION: Run the 7-point discharge checklist\n"
            "5. SAFETY REVIEW: Guardian check for any hidden deterioration\n\n"
            "Provide a comprehensive summary with your final recommendation."
        ),
    },
]


# ========================================================================
# Runner
# ========================================================================


def run_scenario(client, scenario, agent_ids):
    """Run a single demo scenario.

    Args:
        client: PravaahClient instance
        scenario: Scenario dict from SCENARIOS
        agent_ids: Dict mapping agent names to their registered IDs
    """
    console.print()
    console.print(Panel(
        f"[bold]{scenario['title']}[/bold]\n\n{scenario['description']}",
        title=f"Scenario {scenario['id']}",
        border_style="cyan",
    ))

    agent_name = scenario["agent"]
    agent_id = agent_ids.get(agent_name)

    if not agent_id:
        console.print(f"[red]Agent '{agent_name}' not found in registered agents.[/red]")
        console.print(f"[dim]Available agents: {list(agent_ids.keys())}[/dim]")
        return None

    console.print(f"\n[dim]Sending to {agent_name} (ID: {agent_id})...[/dim]")
    console.print(f"[dim]Message: {scenario['message'][:100]}...[/dim]\n")

    try:
        response = client.converse(agent_id, scenario["message"])
        reply = response.get("message", response.get("response", str(response)))

        console.print(Panel(
            Markdown(reply) if isinstance(reply, str) else str(reply),
            title=f"Agent Response: {agent_name}",
            border_style="green",
        ))
        return response

    except Exception as e:
        console.print(f"[red]Error running scenario: {e}[/red]")
        return None


def run_all_scenarios(client, agent_ids):
    """Run all 5 demo scenarios in sequence."""
    console.print(Panel(
        "[bold cyan]Pravaah Multi-Agent Patient Journey Demo[/bold cyan]\n\n"
        "Running 5 scenarios to demonstrate multi-agent collaboration\n"
        "using Elasticsearch Agent Builder, ES|QL, Workflows, and TSDS.",
        border_style="bold cyan",
    ))

    results = []
    for scenario in SCENARIOS:
        result = run_scenario(client, scenario, agent_ids)
        results.append({"scenario": scenario["id"], "result": result})

        if scenario["id"] < len(SCENARIOS):
            console.print("\n[dim]--- Proceeding to next scenario ---[/dim]\n")

    # Summary
    console.print(Panel(
        "[bold]Demo Complete[/bold]\n\n"
        f"Scenarios run: {len(results)}\n"
        f"Successful: {sum(1 for r in results if r['result'] is not None)}\n"
        f"Failed: {sum(1 for r in results if r['result'] is None)}",
        title="Summary",
        border_style="bold green",
    ))

    return results

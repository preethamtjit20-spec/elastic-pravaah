#!/usr/bin/env python3
"""Pravaah: Multi-Agent Patient Journey Orchestrator - Setup & Demo Runner.

Usage:
    python setup.py --setup      Create indices and seed sample data
    python setup.py --agents     Print agent configurations for Kibana Agent Builder UI
    python setup.py --teardown   Delete all indices
    python setup.py --all        Run setup + print agent configs
"""

import argparse
import sys
import time

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.markdown import Markdown

from utils.api_client import PravaahClient
from indices.templates import create_all_indices, delete_all_indices
from indices.seed_data import seed_all
from agents import triage, recovery, capacity, discharge, guardian, orchestrator

console = Console()

AGENT_MODULES = [triage, recovery, capacity, discharge, guardian, orchestrator]


# ========================================================================
# Setup: Create indices + seed data
# ========================================================================


def do_setup():
    """Create Elasticsearch indices and seed sample data."""
    console.print(Panel(
        "[bold cyan]Pravaah Setup[/bold cyan]\n"
        "Creating Elasticsearch indices and seeding sample data.",
        border_style="cyan",
    ))

    client = PravaahClient()

    # Step 1: Create indices
    console.print("\n[bold]Step 1/2: Creating Elasticsearch indices...[/bold]")
    try:
        create_all_indices(client)
        console.print("[green]  All indices created successfully.[/green]")
    except Exception as e:
        console.print(f"[red]  Error creating indices: {e}[/red]")
        raise

    # Step 2: Seed data
    console.print("\n[bold]Step 2/2: Seeding sample data...[/bold]")
    try:
        seed_results = seed_all(client)
        console.print(f"[green]  Data seeded: {seed_results}[/green]")
    except Exception as e:
        console.print(f"[red]  Error seeding data: {e}[/red]")
        raise

    # Allow data to be indexed
    console.print("[dim]  Waiting for indexing to complete...[/dim]")
    time.sleep(3)

    # Summary
    console.print(Panel(
        "[bold green]Data setup complete![/bold green]\n\n"
        "Indices created:\n"
        "  - metrics-patient-vitals (TSDS - time series data stream)\n"
        "  - patients (8 patient records)\n"
        "  - hospital-capacity (7 ward records)\n"
        "  - agent-decisions (audit log - empty)\n"
        "  - discharge-plans (empty)\n\n"
        "Next step: Run [cyan]python setup.py --agents[/cyan] to see\n"
        "how to create agents in the Kibana Agent Builder UI.",
        border_style="green",
    ))


# ========================================================================
# Agents: Print configs for manual Kibana UI creation
# ========================================================================


def do_agents():
    """Print agent configurations for creating in Kibana Agent Builder UI."""
    console.print(Panel(
        "[bold cyan]Pravaah Agent Configurations[/bold cyan]\n\n"
        "Create each agent in Kibana:\n"
        "  Agent Builder > Agents > New Agent\n\n"
        "For each agent below, fill in:\n"
        "  1. Agent ID\n"
        "  2. Custom Instructions (paste the full text)\n"
        "  3. Display Name\n"
        "  4. Enable the listed Tools (in the Tools tab)",
        border_style="cyan",
    ))

    # Summary table
    summary = Table(title="Agent Summary")
    summary.add_column("#", style="dim")
    summary.add_column("Agent ID", style="cyan")
    summary.add_column("Display Name", style="bold")
    summary.add_column("Tools to Enable", style="green")
    summary.add_column("Instructions Length", style="dim")

    for i, mod in enumerate(AGENT_MODULES, 1):
        defn = mod.definition()
        summary.add_row(
            str(i),
            defn["agent_id"],
            defn["display_name"],
            ", ".join(t.replace("platform.core.", "") for t in defn["tools"]),
            f"{len(defn['custom_instructions'])} chars",
        )
    console.print(summary)

    # Detailed configs
    for i, mod in enumerate(AGENT_MODULES, 1):
        defn = mod.definition()
        console.print(f"\n{'='*70}")
        console.print(Panel(
            f"[bold]Agent ID:[/bold] {defn['agent_id']}\n"
            f"[bold]Display Name:[/bold] {defn['display_name']}\n"
            f"[bold]Display Description:[/bold] {defn['display_description']}\n\n"
            f"[bold]Tools to enable (in Tools tab):[/bold]\n"
            + "\n".join(f"  - {t}" for t in defn["tools"]),
            title=f"Agent {i}/{len(AGENT_MODULES)}: {defn['display_name']}",
            border_style="cyan",
        ))

        console.print("\n[bold]Custom Instructions (copy everything below between the lines):[/bold]")
        console.print("-" * 70)
        console.print(defn["custom_instructions"])
        console.print("-" * 70)

    console.print(Panel(
        "[bold green]All agent configs printed![/bold green]\n\n"
        "For each agent:\n"
        "1. Go to Kibana > Agent Builder > New Agent\n"
        "2. Set the Agent ID\n"
        "3. Paste Custom Instructions\n"
        "4. Set Display Name and Description\n"
        "5. Go to Tools tab and enable the listed platform tools\n"
        "6. Click Save\n\n"
        "Then test by clicking 'Save and chat' on any agent!",
        border_style="green",
    ))


# ========================================================================
# Teardown: Delete indices
# ========================================================================


def do_teardown():
    """Delete all Elasticsearch indices."""
    console.print(Panel(
        "[bold red]Pravaah Teardown[/bold red]\n"
        "Deleting all Elasticsearch indices.\n"
        "(Agents created in Kibana UI must be deleted manually.)",
        border_style="red",
    ))

    client = PravaahClient()

    console.print("\n[bold]Deleting indices...[/bold]")
    try:
        delete_all_indices(client)
        console.print("[green]  All indices deleted.[/green]")
    except Exception as e:
        console.print(f"[red]  Error deleting indices: {e}[/red]")

    console.print(Panel(
        "[bold green]Teardown complete.[/bold green]\n\n"
        "Note: Delete agents manually in Kibana:\n"
        "  Agent Builder > Agents > select agent > Delete",
        border_style="green",
    ))


# ========================================================================
# CLI
# ========================================================================


def main():
    parser = argparse.ArgumentParser(
        description="Pravaah: Multi-Agent Patient Journey Orchestrator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python setup.py --setup      Create indices + seed data\n"
            "  python setup.py --agents     Print agent configs for Kibana UI\n"
            "  python setup.py --teardown   Delete all indices\n"
            "  python setup.py --all        Setup + print agent configs\n"
        ),
    )
    parser.add_argument("--setup", action="store_true", help="Create indices and seed sample data")
    parser.add_argument("--agents", action="store_true", help="Print agent configurations for Kibana UI")
    parser.add_argument("--teardown", action="store_true", help="Delete all indices")
    parser.add_argument("--all", action="store_true", help="Run setup + print agent configs")

    args = parser.parse_args()

    if not any([args.setup, args.agents, args.teardown, args.all]):
        parser.print_help()
        sys.exit(0)

    console.print(Panel(
        "[bold]Pravaah[/bold] - Multi-Agent Patient Journey Orchestrator\n"
        "[dim]Elasticsearch Agent Builder Hackathon Submission[/dim]",
        border_style="bold blue",
    ))

    try:
        if args.all:
            do_setup()
            console.print("\n")
            do_agents()
        else:
            if args.setup:
                do_setup()
            if args.agents:
                do_agents()
            if args.teardown:
                do_teardown()
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user.[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n[red]Fatal error: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()

import typer
import yaml
import json
from pathlib import Path
from rich import print
from rich.table import Table
from rich.console import Console
from agentos.cli.client import AgentOSClient

app = typer.Typer(help="Manage the Agent Registry.")
console = Console()
client = AgentOSClient()

@app.command("list")
def list_agents():
    """List all registered agents."""
    try:
        agents = client.list_agents()
        if not agents:
            print("[yellow]No agents registered yet.[/yellow]")
            return

        table = Table(title="AgentOS Registry")
        table.add_column("ID", style="cyan", no_wrap=True)
        table.add_column("Name", style="green")
        table.add_column("Version", style="magenta")
        table.add_column("Model", style="blue")
        table.add_column("Status", style="yellow")

        for agent in agents:
            table.add_row(
                agent["id"],
                agent["name"],
                agent.get("version", "N/A"),
                agent.get("model", "N/A"),
                agent.get("status", "active")
            )

        console.print(table)
    except Exception as e:
        print(f"[red]Error fetching agents:[/red] {e}")

@app.command("register")
def register_agent(file_path: Path = typer.Argument(..., help="Path to agent configuration file (YAML/JSON)")):
    """Register a new agent from a configuration file."""
    if not file_path.exists():
        print(f"[red]Error:[/red] File {file_path} not found.")
        return

    try:
        content = file_path.read_text()
        if file_path.suffix in [".yaml", ".yml"]:
            data = yaml.safe_load(content)
        else:
            data = json.loads(content)

        response = client.register_agent(data)
        print(f"[green]Success![/green] Agent [bold]{response['name']}[/bold] registered with ID: [cyan]{response['id']}[/cyan]")
    except Exception as e:
        print(f"[red]Error registering agent:[/red] {e}")

if __name__ == "__main__":
    app()

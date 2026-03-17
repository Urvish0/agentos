import typer
from rich.console import Console
from rich.table import Table
from ..client import AgentOSClient

app = typer.Typer(help="Manage AgentOS plugins")
console = Console()

@app.command("list")
def list_plugins():
    """List all loaded plugins on the AgentOS backend."""
    client = AgentOSClient()
    try:
        plugins = client.list_plugins()
        
        if not plugins:
            console.print("[yellow]No plugins loaded.[/yellow]")
            return

        table = Table(title="Loaded Plugins")
        table.add_column("Name", style="cyan")
        table.add_column("Type", style="magenta")
        table.add_column("Version", style="green")
        
        for p in plugins:
            table.add_row(p["name"], p["type"], p["version"])
            
        console.print(table)
    except Exception as e:
        console.print(f"[red]Error fetching plugins:[/red] {e}")

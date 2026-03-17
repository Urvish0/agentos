import typer
from rich.console import Console
from rich.table import Table
from ..client import AgentOSClient
import asyncio

plugins_app = typer.Typer(help="Manage AgentOS plugins")
console = Console()

@plugins_app.command("list")
def list_plugins():
    """List all loaded plugins."""
    client = AgentOSClient()
    try:
        plugins = client.list_plugins_sync()
        
        if not plugins:
            console.print("[yellow]No plugins registered or loaded.[/yellow]")
            return

        table = Table(title="AgentOS Plugins")
        table.add_column("Name", style="cyan")
        table.add_column("Type", style="magenta")
        table.add_column("Version", style="green")
        table.add_column("Enabled", style="yellow")
        table.add_column("Status", style="blue")

        for p in plugins:
            status = p.get("status", "active")
            enabled_text = "Yes" if p.get("enabled", True) else "No"
            
            table.add_row(
                str(p.get("name", "N/A")),
                str(p.get("type", "N/A")),
                str(p.get("version", "N/A")),
                enabled_text,
                str(status)
            )
        
        console.print(table)
    except Exception as e:
        console.print(f"[red]Error fetching plugins:[/red] {e}")

@plugins_app.command("enable")
def enable_plugin(name: str):
    """Enable a plugin."""
    client = AgentOSClient()
    try:
        result = client.update_plugin_state_sync(name, True)
        if result.get("status") == "success":
            console.print(f"Plugin '[cyan]{name}[/cyan]' enabled successfully.")
        else:
            console.print(f"[red]Failed to enable plugin '[cyan]{name}[/cyan]':[/red] {result.get('message')}")
    except Exception as e:
        console.print(f"[red]Error enabling plugin '[cyan]{name}[/cyan]':[/red] {e}")

@plugins_app.command("disable")
def disable_plugin(name: str):
    """Disable a plugin."""
    client = AgentOSClient()
    try:
        result = client.update_plugin_state_sync(name, False)
        if result.get("status") == "success":
            console.print(f"Plugin '[cyan]{name}[/cyan]' disabled successfully.")
        else:
            console.print(f"[red]Failed to disable plugin '[cyan]{name}[/cyan]':[/red] {result.get('message')}")
    except Exception as e:
        console.print(f"[red]Error disabling plugin '[cyan]{name}[/cyan]':[/red] {e}")

@plugins_app.command("install")
def install_plugin(path: str):
    """Install a plugin from a local file path."""
    client = AgentOSClient()
    try:
        result = client.install_plugin_sync(path)
        if result.get("status") == "success":
            console.print(f"Plugin installed to: [green]{result.get('destination')}[/green]")
            console.print("Restart the server to load the new plugin.")
        else:
            console.print(f"[red]Failed to install plugin:[/red] {result.get('message')}")
    except Exception as e:
        console.print(f"[red]Error installing plugin:[/red] {e}")

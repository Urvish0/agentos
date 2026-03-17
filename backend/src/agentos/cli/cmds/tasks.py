import typer
import time
from rich import print
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from agentos.cli.client import AgentOSClient

app = typer.Typer(help="Execute and monitor agent tasks.")
client = AgentOSClient()

@app.command("run")
def run_task(
    agent_id: str = typer.Argument(..., help="UUID of the agent to run"),
    input_text: str = typer.Option(..., "--input", "-i", help="Goal or prompt for the agent"),
    poll_interval: float = typer.Option(2.0, "--poll", help="Polling interval in seconds")
):
    """Execute an agent goal and monitor progress."""
    try:
        print(f"🚀 Submitting task to agent [cyan]{agent_id}[/cyan]...")
        task = client.create_task(agent_id, input_text)
        task_id = task["id"]
        print(f"✅ Task created! ID: [bold]{task_id}[/bold]")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            status_task = progress.add_task(description="Agent thinking...", total=None)
            
            while True:
                task_data = client.get_task(task_id)
                status = task_data["status"]
                
                if status == "completed":
                    progress.update(status_task, description="Done!")
                    print(Panel(task_data["output"], title="[green]Final Output[/green]", border_style="green"))
                    break
                elif status == "failed":
                    progress.update(status_task, description="Failed.")
                    print(f"[red]Task failed:[/red] {task_data.get('error', 'Unknown error')}")
                    break
                elif status == "cancelled":
                    progress.update(status_task, description="Cancelled.")
                    print("[yellow]Task was cancelled.[/yellow]")
                    break
                
                time.sleep(poll_interval)

    except Exception as e:
        print(f"[red]Error running task:[/red] {e}")

@app.command("status")
def task_status(task_id: str = typer.Argument(..., help="UUID of the task")):
    """Get the current status of a task."""
    try:
        task_data = client.get_task(task_id)
        print(Panel.fit(
            f"ID: {task_data['id']}\n"
            f"Agent ID: {task_data['agent_id']}\n"
            f"Status: [bold]{task_data['status']}[/bold]\n"
            f"Created: {task_data['created_at']}\n"
            f"Tokens: {task_data['total_tokens']}\n"
            f"Time: {task_data['execution_time_ms']}ms",
            title=f"Task Status"
        ))
        if task_data["output"]:
            print(Panel(task_data["output"], title="Output", border_style="blue"))
        if task_data["error"]:
            print(Panel(task_data["error"], title="Error", border_style="red"))
    except Exception as e:
        print(f"[red]Error fetching task status:[/red] {e}")

@app.command("trace")
def task_trace(task_id: str = typer.Argument(..., help="UUID of the task")):
    """Get the trace URL for a task."""
    try:
        trace_url = client.get_trace_url(task_id)
        print(f"🔍 [bold]Trace URL:[/bold] [link={trace_url}]{trace_url}[/link]")
    except Exception as e:
        # Fallback if trace endpoint is not yet fully implemented or fails
        print(f"[yellow]Could not fetch trace URL:[/yellow] {e}")

@app.command("cancel")
def cancel_task(task_id: str = typer.Argument(..., help="UUID of the task")):
    """Cancel a running task."""
    try:
        client.cancel_task(task_id)
        print(f"[green]Successfully requested cancellation for task {task_id}[/green]")
    except Exception as e:
        print(f"[red]Error cancelling task:[/red] {e}")

if __name__ == "__main__":
    app()

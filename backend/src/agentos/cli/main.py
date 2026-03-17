import typer
from agentos.cli.cmds.agents import app as agents_app
from agentos.cli.cmds.tasks import app as tasks_app
from agentos.cli.cmds.plugins import plugins_app

app = typer.Typer(help="AgentOS CLI: Manage your AI agents and tasks from the terminal.")

# Register sub-commands
app.add_typer(agents_app, name="agents")
app.add_typer(tasks_app, name="tasks")
app.add_typer(plugins_app, name="plugins")

if __name__ == "__main__":
    app()

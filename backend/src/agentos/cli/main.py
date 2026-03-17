import typer
from agentos.cli.cmds import init, agents, tasks, plugins

app = typer.Typer(
    name="agentos",
    help="AgentOS CLI: Manage your AI agents and tasks from the terminal.",
    add_completion=False,
)

# Register sub-commands
app.add_typer(init.app, name="init")
app.add_typer(agents.app, name="agents")
app.add_typer(tasks.app, name="tasks")
app.add_typer(plugins.app, name="plugins")

if __name__ == "__main__":
    app()

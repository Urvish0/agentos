import pytest
from typer.testing import CliRunner
from agentos.cli.main import app
import os

runner = CliRunner()

def test_cli_help():
    """Verify that the help command works."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Manage your AI agents and tasks from the terminal" in result.stdout

def test_init_command(tmp_path):
    """Verify that agentos init creates the agent.yaml file."""
    # Change to a temp directory for testing
    os.chdir(tmp_path)
    result = runner.invoke(app, ["init"])
    assert result.exit_code == 0
    assert "Created agent.yaml template" in result.stdout
    assert (tmp_path / "agent.yaml").exists()

def test_agents_list_help():
    """Verify that the agent list help works."""
    result = runner.invoke(app, ["agents", "list", "--help"])
    assert result.exit_code == 0
    assert "List all registered agents" in result.stdout

def test_tasks_run_help():
    """Verify that the task run help works."""
    result = runner.invoke(app, ["tasks", "run", "--help"])
    assert result.exit_code == 0
    assert "Execute an agent goal" in result.stdout

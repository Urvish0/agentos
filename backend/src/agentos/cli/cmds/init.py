import typer
import yaml
from rich import print
from pathlib import Path

app = typer.Typer(help="Initialize AgentOS local configurations.")

SAMPLE_AGENT_YAML = """
name: "ResearchAgent"
description: "An agent that performs web research and summarizes findings."
version: "0.1.0"
model: "llama-3.3-70b-versatile"
system_prompt: "You are a professional researcher. Use the available tools to provide detailed, accurate reports."
temperature: 0.7
tools: "['web_search', 'read_file', 'write_file']"
"""

@app.callback(invoke_without_command=True)
def main():
    """Generates a sample agent.yaml template in the current directory."""
    target_file = Path("agent.yaml")
    if target_file.exists():
        print(f"[yellow]Warning:[/yellow] {target_file} already exists. Skipping.")
        return

    target_file.write_text(SAMPLE_AGENT_YAML.strip())
    print(f"[green]Success![/green] Created [bold]{target_file}[/bold] template.")
    print("Edit this file and run [bold]agentos agents register agent.yaml[/bold] to get started.")

if __name__ == "__main__":
    app()

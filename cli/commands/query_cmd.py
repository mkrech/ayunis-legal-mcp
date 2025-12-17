# ABOUTME: Query command implementation
# ABOUTME: Retrieves legal texts by code, section, and sub-section

import typer
from typing import Optional
from cli.client import LegalMCPClient
from cli.config import get_api_url
from cli.output import print_query_results, print_json, console

app = typer.Typer()


@app.command()
def query_texts(
    code: str = typer.Option(..., "--code", "-c", help="Legal code (e.g., bgb)"),
    section: Optional[str] = typer.Option(None, "--section", "-s", help="Section filter (e.g., '§ 1')"),
    sub_section: Optional[str] = typer.Option(None, "--sub-section", help="Sub-section filter"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    api_url: str = typer.Option(None, "--api-url", envvar="LEGAL_API_BASE_URL")
):
    """Query legal texts by code, section, and sub-section"""
    url = api_url or get_api_url()

    with LegalMCPClient(url) as client:
        # Health check - fail gracefully if Store API is not running
        if not client.health_check():
            console.print(f"[red]Error: Store API not reachable at {url}[/red]")
            console.print("[yellow]Make sure the Store API is running: docker-compose up -d[/yellow]")
            raise typer.Exit(1)

        try:
            results = client.query_texts(code, section, sub_section)

            if json_output:
                print_json(results)
            else:
                print_query_results(results)

        except Exception as e:
            console.print(f"[red]Error:[/red] {e}")
            raise typer.Exit(1)

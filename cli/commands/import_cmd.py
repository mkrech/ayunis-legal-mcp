# ABOUTME: Import command implementation
# ABOUTME: Handles importing legal codes from gesetze-im-internet.de

import typer
from typing import List
import httpx
from cli.client import LegalMCPClient
from cli.config import get_api_url
from cli.output import print_json, console

app = typer.Typer()


@app.command()
def import_codes(
    codes: List[str] = typer.Option(..., "--code", "-c", help="Legal code to import (can be repeated)"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    api_url: str = typer.Option(None, "--api-url", envvar="LEGAL_API_BASE_URL")
):
    """Import one or more legal codes"""
    url = api_url or get_api_url()

    with LegalMCPClient(url) as client:
        # Health check - fail gracefully if Store API is not running
        if not client.health_check():
            console.print(f"[red]Error: Store API not reachable at {url}[/red]")
            console.print("[yellow]Make sure the Store API is running: docker-compose up -d[/yellow]")
            raise typer.Exit(1)

        results = []

        for code in codes:
            try:
                with console.status(f"[cyan]Importing {code}...", spinner="dots"):
                    result = client.import_code(code)
                    results.append({"code": code, "success": True, "result": result})

                if not json_output:
                    console.print(f"[green]✓[/green] Imported {code}")

            except httpx.HTTPStatusError as e:
                # Validation errors (400, 404) - fail fast
                if e.response.status_code in [400, 404]:
                    if not json_output:
                        console.print(f"[red]✗[/red] Invalid code: {code}")
                        error_detail = e.response.json().get('detail', str(e))
                        console.print(f"[yellow]Error: {error_detail}[/yellow]")
                    if json_output:
                        print_json({"code": code, "success": False, "error": str(e)})
                    raise typer.Exit(1)

                # Network/server errors (500, etc.)
                else:
                    if not json_output:
                        console.print(f"[red]✗[/red] Server error importing {code}")
                        error_detail = e.response.json().get('detail', str(e))
                        console.print(f"[yellow]Error: {error_detail}[/yellow]")
                        console.print("[yellow]Make sure Ollama is running and the database is accessible[/yellow]")
                    if json_output:
                        print_json({"code": code, "success": False, "error": str(e)})
                    raise typer.Exit(1)

            except Exception as e:
                # Other errors (network timeouts, connection errors)
                if not json_output:
                    console.print(f"[red]✗[/red] Failed to import {code}: {e}")
                if json_output:
                    print_json({"code": code, "success": False, "error": str(e)})
                raise typer.Exit(1)

        if json_output:
            print_json(results)
        else:
            # Print summary
            console.print(f"\n[bold green]Success:[/bold green] Imported {len(codes)} code(s)")

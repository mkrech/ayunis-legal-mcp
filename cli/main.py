# ABOUTME: CLI entry point and main application setup
# ABOUTME: Defines Typer app and registers command groups

import typer
from cli.commands import list_cmd
from cli.commands.import_cmd import import_codes
from cli.commands.query_cmd import query_texts
from cli.commands.search_cmd import search_texts

app = typer.Typer(
    name="legal-mcp",
    help="CLI for managing German legal texts",
    no_args_is_help=True
)

# Register command groups
app.add_typer(list_cmd.app, name="list", help="List codes")

# Register direct commands
app.command(name="import", help="Import one or more legal codes")(import_codes)
app.command(name="query", help="Query legal texts by code, section, and sub-section")(query_texts)
app.command(name="search", help="Perform semantic search on legal texts")(search_texts)


if __name__ == "__main__":
    app()

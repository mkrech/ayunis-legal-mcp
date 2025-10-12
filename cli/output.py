# ABOUTME: Output formatting utilities
# ABOUTME: Handles table rendering and JSON output

import json
from typing import Any, List
from rich.console import Console
from rich.table import Table

console = Console()


def print_json(data: Any):
    """
    Print data as formatted JSON

    Args:
        data: Data to output as JSON (will be serialized)
    """
    console.print_json(json.dumps(data))


def print_codes_list(codes: List[str]):
    """
    Print codes list as table

    Args:
        codes: List of legal code identifiers
    """
    table = Table(title=f"Imported Codes (Count: {len(codes)})")
    table.add_column("Code", style="cyan")

    for code in codes:
        table.add_row(code)

    console.print(table)


def print_catalog(catalog: dict):
    """
    Print catalog as table with code and title columns only

    Args:
        catalog: Catalog response with 'count' and 'entries' fields
    """
    entries = catalog.get("entries", [])
    table = Table(title=f"Available Legal Codes (Count: {catalog['count']})")
    table.add_column("Code", style="cyan")
    table.add_column("Title", style="white")

    for entry in entries:
        table.add_row(entry["code"], entry["title"])

    console.print(table)


def print_query_results(results: dict):
    """
    Print query results as table with truncated text

    Args:
        results: Query response with 'count' and 'results' fields
    """
    items = results.get("results", [])
    table = Table(title=f"Query Results (Count: {results['count']})")
    table.add_column("Section", style="cyan")
    table.add_column("Sub-Section", style="yellow")
    table.add_column("Text", style="white", no_wrap=False)

    for item in items:
        # Truncate text to 100 characters for table display
        text = item["text"]
        display_text = text[:100] + "..." if len(text) > 100 else text
        table.add_row(item["section"], item["sub_section"], display_text)

    console.print(table)


def print_search_results(results: dict):
    """
    Print search results as table with similarity scores and truncated text

    Args:
        results: Search response with 'query', 'code', 'count', and 'results' fields
    """
    items = results.get("results", [])
    table = Table(
        title=f"Search Results for '{results['query']}' in {results['code']} (Count: {results['count']})"
    )
    table.add_column("Section", style="cyan")
    table.add_column("Sub-Section", style="yellow")
    table.add_column("Similarity", style="green")
    table.add_column("Text", style="white", no_wrap=False)

    for item in items:
        # Truncate text to 80 characters for table display
        text = item["text"]
        display_text = text[:80] + "..." if len(text) > 80 else text
        table.add_row(
            item["section"],
            item["sub_section"],
            f"{item['similarity_score']:.3f}",
            display_text
        )

    console.print(table)

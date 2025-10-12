# ABOUTME: Tests for query CLI command
# ABOUTME: Validates query behavior with mocked client

import pytest
from unittest.mock import MagicMock, patch
import typer
from typer.testing import CliRunner
from cli.commands.query_cmd import query_texts


runner = CliRunner()

# Create a Typer app for testing that wraps the command function
_test_app = typer.Typer()
_test_app.command()(query_texts)


@patch("cli.commands.query_cmd.LegalMCPClient")
def test_query_all_texts_success(mock_client_class):
    """Test querying all texts for a code"""
    # Setup mock client with context manager support
    mock_client = MagicMock()
    mock_client.health_check.return_value = True
    mock_client.query_texts.return_value = {
        "code": "bgb",
        "count": 2,
        "results": [
            {"section": "§ 1", "sub_section": "", "text": "Sample text 1"},
            {"section": "§ 2", "sub_section": "", "text": "Sample text 2"}
        ]
    }
    mock_client.__enter__.return_value = mock_client
    mock_client.__exit__.return_value = None
    mock_client_class.return_value = mock_client

    # Run command
    result = runner.invoke(_test_app, ["bgb"])

    # Verify success
    assert result.exit_code == 0
    assert "§ 1" in result.stdout
    assert "§ 2" in result.stdout
    mock_client.query_texts.assert_called_once_with("bgb", None, None)


@patch("cli.commands.query_cmd.LegalMCPClient")
def test_query_with_section_filter(mock_client_class):
    """Test querying texts with section filter"""
    # Setup mock client with context manager support
    mock_client = MagicMock()
    mock_client.health_check.return_value = True
    mock_client.query_texts.return_value = {
        "code": "bgb",
        "count": 1,
        "results": [
            {"section": "§ 1", "sub_section": "", "text": "Sample text"}
        ]
    }
    mock_client.__enter__.return_value = mock_client
    mock_client.__exit__.return_value = None
    mock_client_class.return_value = mock_client

    # Run command
    result = runner.invoke(_test_app, ["bgb", "--section", "§ 1"])

    # Verify success
    assert result.exit_code == 0
    assert "§ 1" in result.stdout
    mock_client.query_texts.assert_called_once_with("bgb", "§ 1", None)


@patch("cli.commands.query_cmd.LegalMCPClient")
def test_query_with_section_and_subsection(mock_client_class):
    """Test querying texts with section and sub-section filters"""
    # Setup mock client with context manager support
    mock_client = MagicMock()
    mock_client.health_check.return_value = True
    mock_client.query_texts.return_value = {
        "code": "bgb",
        "count": 1,
        "results": [
            {"section": "§ 1", "sub_section": "1", "text": "Sample text"}
        ]
    }
    mock_client.__enter__.return_value = mock_client
    mock_client.__exit__.return_value = None
    mock_client_class.return_value = mock_client

    # Run command
    result = runner.invoke(_test_app, ["bgb", "--section", "§ 1", "--sub-section", "1"])

    # Verify success
    assert result.exit_code == 0
    assert "§ 1" in result.stdout
    mock_client.query_texts.assert_called_once_with("bgb", "§ 1", "1")


@patch("cli.commands.query_cmd.LegalMCPClient")
def test_query_api_unreachable(mock_client_class):
    """Test query command when API is unreachable"""
    # Setup mock client with context manager support
    mock_client = MagicMock()
    mock_client.health_check.return_value = False
    mock_client.__enter__.return_value = mock_client
    mock_client.__exit__.return_value = None
    mock_client_class.return_value = mock_client

    # Run command
    result = runner.invoke(_test_app, ["bgb"])

    # Verify failure
    assert result.exit_code == 1
    assert "Error: Store API not reachable" in result.stdout


@patch("cli.commands.query_cmd.LegalMCPClient")
def test_query_with_json_output(mock_client_class):
    """Test query command with JSON output"""
    # Setup mock client with context manager support
    mock_client = MagicMock()
    mock_client.health_check.return_value = True
    mock_client.query_texts.return_value = {
        "code": "bgb",
        "count": 1,
        "results": [
            {"section": "§ 1", "sub_section": "", "text": "Sample text"}
        ]
    }
    mock_client.__enter__.return_value = mock_client
    mock_client.__exit__.return_value = None
    mock_client_class.return_value = mock_client

    # Run command with --json flag
    result = runner.invoke(_test_app, ["bgb", "--json"])

    # Verify success and JSON output
    assert result.exit_code == 0
    assert "§ 1" in result.stdout


@patch("cli.commands.query_cmd.LegalMCPClient")
def test_query_with_custom_api_url(mock_client_class):
    """Test query command with custom API URL"""
    # Setup mock client with context manager support
    mock_client = MagicMock()
    mock_client.health_check.return_value = True
    mock_client.query_texts.return_value = {
        "code": "bgb",
        "count": 1,
        "results": [
            {"section": "§ 1", "sub_section": "", "text": "Sample text"}
        ]
    }
    mock_client.__enter__.return_value = mock_client
    mock_client.__exit__.return_value = None
    mock_client_class.return_value = mock_client

    # Run command with custom API URL
    custom_url = "http://custom:9999"
    result = runner.invoke(_test_app, ["bgb", "--api-url", custom_url])

    # Verify client was initialized with custom URL
    mock_client_class.assert_called_with(custom_url)
    assert result.exit_code == 0


@patch("cli.commands.query_cmd.LegalMCPClient")
def test_query_handles_exception(mock_client_class):
    """Test query command handles exceptions gracefully"""
    # Setup mock client that raises exception with context manager support
    mock_client = MagicMock()
    mock_client.health_check.return_value = True
    mock_client.query_texts.side_effect = Exception("Network error")
    mock_client.__enter__.return_value = mock_client
    mock_client.__exit__.return_value = None
    mock_client_class.return_value = mock_client

    # Run command
    result = runner.invoke(_test_app, ["bgb"])

    # Verify failure
    assert result.exit_code == 1
    assert "Error:" in result.stdout

# ABOUTME: Tests for import CLI command
# ABOUTME: Validates import behavior with mocked client

import pytest
from unittest.mock import MagicMock, patch
import typer
from typer.testing import CliRunner
from cli.commands.import_cmd import import_codes


runner = CliRunner()

# Create a Typer app for testing that wraps the command function
_test_app = typer.Typer()
_test_app.command()(import_codes)


@patch("cli.commands.import_cmd.LegalMCPClient")
def test_import_single_code_success(mock_client_class):
    """Test importing a single code successfully"""
    # Setup mock client with context manager support
    mock_client = MagicMock()
    mock_client.health_check.return_value = True
    mock_client.import_code.return_value = {
        "message": "Successfully imported bgb",
        "texts_imported": 2385,
        "code": "bgb"
    }
    mock_client.__enter__.return_value = mock_client
    mock_client.__exit__.return_value = None
    mock_client_class.return_value = mock_client

    # Run command
    result = runner.invoke(_test_app, ["--code", "bgb"])

    # Verify success
    assert result.exit_code == 0
    assert "bgb" in result.stdout
    mock_client.import_code.assert_called_once_with("bgb")


@patch("cli.commands.import_cmd.LegalMCPClient")
def test_import_multiple_codes_success(mock_client_class):
    """Test importing multiple codes successfully"""
    # Setup mock client with context manager support
    mock_client = MagicMock()
    mock_client.health_check.return_value = True
    mock_client.import_code.side_effect = [
        {"message": "Successfully imported bgb", "texts_imported": 2385, "code": "bgb"},
        {"message": "Successfully imported stgb", "texts_imported": 358, "code": "stgb"}
    ]
    mock_client.__enter__.return_value = mock_client
    mock_client.__exit__.return_value = None
    mock_client_class.return_value = mock_client

    # Run command
    result = runner.invoke(_test_app, ["--code", "bgb", "--code", "stgb"])

    # Verify success
    assert result.exit_code == 0
    assert "bgb" in result.stdout
    assert "stgb" in result.stdout
    assert mock_client.import_code.call_count == 2


@patch("cli.commands.import_cmd.LegalMCPClient")
def test_import_api_unreachable(mock_client_class):
    """Test import command when API is unreachable"""
    # Setup mock client with context manager support
    mock_client = MagicMock()
    mock_client.health_check.return_value = False
    mock_client.__enter__.return_value = mock_client
    mock_client.__exit__.return_value = None
    mock_client_class.return_value = mock_client

    # Run command
    result = runner.invoke(_test_app, ["--code", "bgb"])

    # Verify failure
    assert result.exit_code == 1
    assert "Error: Store API not reachable" in result.stdout


@patch("cli.commands.import_cmd.LegalMCPClient")
def test_import_with_json_output(mock_client_class):
    """Test import command with JSON output"""
    # Setup mock client with context manager support
    mock_client = MagicMock()
    mock_client.health_check.return_value = True
    mock_client.import_code.return_value = {
        "message": "Successfully imported bgb",
        "texts_imported": 2385,
        "code": "bgb"
    }
    mock_client.__enter__.return_value = mock_client
    mock_client.__exit__.return_value = None
    mock_client_class.return_value = mock_client

    # Run command with --json flag
    result = runner.invoke(_test_app, ["--code", "bgb", "--json"])

    # Verify success and JSON output
    assert result.exit_code == 0
    assert "bgb" in result.stdout


@patch("cli.commands.import_cmd.LegalMCPClient")
def test_import_validation_error_404(mock_client_class):
    """Test import command with 404 validation error"""
    import httpx

    # Setup mock client with context manager support
    mock_client = MagicMock()
    mock_client.health_check.return_value = True

    # Create a mock 404 response
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_response.json.return_value = {"detail": "Code not found"}

    mock_client.import_code.side_effect = httpx.HTTPStatusError(
        "404 Not Found",
        request=MagicMock(),
        response=mock_response
    )
    mock_client.__enter__.return_value = mock_client
    mock_client.__exit__.return_value = None
    mock_client_class.return_value = mock_client

    # Run command
    result = runner.invoke(_test_app, ["--code", "invalid"])

    # Verify failure
    assert result.exit_code == 1
    assert "Error" in result.stdout or "error" in result.stdout.lower()


@patch("cli.commands.import_cmd.LegalMCPClient")
def test_import_server_error_500(mock_client_class):
    """Test import command with 500 server error"""
    import httpx

    # Setup mock client with context manager support
    mock_client = MagicMock()
    mock_client.health_check.return_value = True

    # Create a mock 500 response
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.json.return_value = {"detail": "Internal server error"}

    mock_client.import_code.side_effect = httpx.HTTPStatusError(
        "500 Internal Server Error",
        request=MagicMock(),
        response=mock_response
    )
    mock_client.__enter__.return_value = mock_client
    mock_client.__exit__.return_value = None
    mock_client_class.return_value = mock_client

    # Run command
    result = runner.invoke(_test_app, ["--code", "bgb"])

    # Verify failure
    assert result.exit_code == 1
    assert "Error" in result.stdout or "error" in result.stdout.lower()


@patch("cli.commands.import_cmd.LegalMCPClient")
def test_import_with_custom_api_url(mock_client_class):
    """Test import command with custom API URL"""
    # Setup mock client with context manager support
    mock_client = MagicMock()
    mock_client.health_check.return_value = True
    mock_client.import_code.return_value = {
        "message": "Successfully imported bgb",
        "texts_imported": 2385,
        "code": "bgb"
    }
    mock_client.__enter__.return_value = mock_client
    mock_client.__exit__.return_value = None
    mock_client_class.return_value = mock_client

    # Run command with custom API URL
    custom_url = "http://custom:9999"
    result = runner.invoke(_test_app, ["--code", "bgb", "--api-url", custom_url])

    # Verify client was initialized with custom URL
    mock_client_class.assert_called_with(custom_url)
    assert result.exit_code == 0

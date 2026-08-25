import pytest
from typer.testing import CliRunner
from cli.main import app

runner = CliRunner()

def test_cli_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Scapper" in result.stdout

def test_cli_jobs_help():
    result = runner.invoke(app, ["jobs", "--help"])
    assert result.exit_code == 0
    assert "list" in result.stdout

def test_cli_discovery_help():
    result = runner.invoke(app, ["discovery", "--help"])
    assert result.exit_code == 0
    assert "collect" in result.stdout

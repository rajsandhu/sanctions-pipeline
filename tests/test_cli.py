from typer.testing import CliRunner
from sanctions_pipeline.cli import app
import re

runner = CliRunner()


def _strip_ansi(text: str) -> str:
    """Remove ANSI escape codes from text."""
    return re.sub(r"\x1b\[[0-9;]*m", "", text)


def test_cli_root_help():
    res = runner.invoke(app, ["--help"])
    assert res.exit_code == 0
    output = _strip_ansi(res.output).lower()
    assert "sanctions" in output or "pipeline" in output


def test_cli_transform_help():
    res = runner.invoke(app, ["transform", "--help"])
    assert res.exit_code == 0
    output = _strip_ansi(res.output).lower()
    assert "--input" in output and "--output" in output

from typer.testing import CliRunner
from sanctions_pipeline.cli import app

runner = CliRunner()


def test_cli_root_help():
    res = runner.invoke(app, ["--help"])
    assert res.exit_code == 0
    assert "Sanctions pipeline" in res.output or "Sanctions" in res.output


def test_cli_transform_help():
    res = runner.invoke(app, ["transform", "--help"])
    assert res.exit_code == 0
    assert "--input" in res.output and "--output" in res.output
